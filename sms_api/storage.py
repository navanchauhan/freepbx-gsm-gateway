from __future__ import annotations

from pathlib import Path
import sqlite3
import threading
import uuid


class SmsStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self._lock = threading.Lock()
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.db_path,
            timeout=30.0,
            isolation_level=None,
            check_same_thread=False,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    def _initialize(self) -> None:
        with self._lock, self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS chats (
                    id TEXT PRIMARY KEY,
                    from_number TEXT NOT NULL,
                    to_number TEXT NOT NULL,
                    display_name TEXT NOT NULL,
                    service TEXT NOT NULL DEFAULT 'SMS',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(from_number, to_number)
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id TEXT PRIMARY KEY,
                    chat_id TEXT NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                    idempotency_key TEXT UNIQUE,
                    direction TEXT NOT NULL CHECK(direction IN ('inbound', 'outbound')),
                    sender_handle TEXT NOT NULL,
                    body TEXT NOT NULL,
                    service TEXT NOT NULL DEFAULT 'SMS',
                    preferred_service TEXT,
                    delivery_status TEXT NOT NULL,
                    is_read INTEGER NOT NULL DEFAULT 0,
                    is_delivered INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    sent_at TEXT,
                    delivered_at TEXT,
                    read_at TEXT,
                    error_message TEXT
                );

                CREATE TABLE IF NOT EXISTS attachments (
                    id TEXT PRIMARY KEY,
                    message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
                    part_index INTEGER NOT NULL,
                    kind TEXT NOT NULL,
                    mime_type TEXT NOT NULL,
                    filename TEXT,
                    relative_path TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_chats_updated_at
                    ON chats(updated_at DESC, id DESC);

                CREATE INDEX IF NOT EXISTS idx_messages_chat_id_created_at
                    ON messages(chat_id, created_at ASC, id ASC);

                CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_idempotency_key
                    ON messages(idempotency_key)
                    WHERE idempotency_key IS NOT NULL;

                CREATE INDEX IF NOT EXISTS idx_attachments_message_id_part_index
                    ON attachments(message_id, part_index ASC, id ASC);
                """
            )
            self._ensure_column(connection, "messages", "transport_key", "TEXT")
            self._ensure_column(connection, "messages", "raw_pdu_hex", "TEXT")
            self._ensure_column(connection, "messages", "content_location", "TEXT")
            connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS idx_messages_transport_key
                    ON messages(transport_key)
                    WHERE transport_key IS NOT NULL
                """
            )

    @staticmethod
    def _ensure_column(connection: sqlite3.Connection, table_name: str, column_name: str, column_type: str) -> None:
        columns = {
            row["name"]
            for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
        }
        if column_name not in columns:
            connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")

    def get_or_create_chat(
        self,
        *,
        from_number: str,
        to_number: str,
        created_at: str,
        service: str = "SMS",
    ) -> tuple[dict, bool]:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM chats
                WHERE from_number = ? AND to_number = ?
                """,
                (from_number, to_number),
            ).fetchone()
            if row is not None:
                if service == "MMS" and row["service"] != "MMS":
                    connection.execute(
                        """
                        UPDATE chats
                        SET service = 'MMS', updated_at = ?
                        WHERE id = ?
                        """,
                        (created_at, row["id"]),
                    )
                    row = connection.execute("SELECT * FROM chats WHERE id = ?", (row["id"],)).fetchone()
                return dict(row), False

            chat_id = str(uuid.uuid4())
            connection.execute(
                """
                INSERT INTO chats (id, from_number, to_number, display_name, service, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (chat_id, from_number, to_number, to_number, service, created_at, created_at),
            )
            row = connection.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
            return dict(row), True

    def get_chat(self, chat_id: str) -> dict | None:
        with self._lock, self._connect() as connection:
            row = connection.execute("SELECT * FROM chats WHERE id = ?", (chat_id,)).fetchone()
            return dict(row) if row is not None else None

    def list_chats(
        self,
        *,
        from_number: str | None,
        to_number: str | None,
        limit: int,
        offset: int,
    ) -> list[dict]:
        query = "SELECT * FROM chats"
        params: list[object] = []
        conditions: list[str] = []

        if from_number is not None:
            conditions.append("from_number = ?")
            params.append(from_number)
        if to_number is not None:
            conditions.append("to_number = ?")
            params.append(to_number)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY updated_at DESC, id DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._lock, self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def list_messages(self, *, chat_id: str, limit: int, offset: int) -> list[dict]:
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                """
                SELECT *
                FROM messages
                WHERE chat_id = ?
                ORDER BY created_at ASC, id ASC
                LIMIT ? OFFSET ?
                """,
                (chat_id, limit, offset),
            ).fetchall()
            return [dict(row) for row in rows]

    def list_attachments_for_message_ids(self, message_ids: list[str]) -> dict[str, list[dict]]:
        if not message_ids:
            return {}

        placeholders = ",".join("?" for _ in message_ids)
        with self._lock, self._connect() as connection:
            rows = connection.execute(
                f"""
                SELECT *
                FROM attachments
                WHERE message_id IN ({placeholders})
                ORDER BY message_id ASC, part_index ASC, id ASC
                """,
                message_ids,
            ).fetchall()

        result: dict[str, list[dict]] = {message_id: [] for message_id in message_ids}
        for row in rows:
            result.setdefault(row["message_id"], []).append(dict(row))
        return result

    def get_message_by_idempotency_key(self, idempotency_key: str) -> dict | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM messages
                WHERE idempotency_key = ?
                """,
                (idempotency_key,),
            ).fetchone()
            return dict(row) if row is not None else None

    def get_message_by_transport_key(self, transport_key: str) -> dict | None:
        with self._lock, self._connect() as connection:
            row = connection.execute(
                """
                SELECT *
                FROM messages
                WHERE transport_key = ?
                """,
                (transport_key,),
            ).fetchone()
            return dict(row) if row is not None else None

    def create_outbound_message(
        self,
        *,
        chat_id: str,
        sender_handle: str,
        body: str,
        preferred_service: str | None,
        idempotency_key: str | None,
        created_at: str,
    ) -> dict:
        return self._create_message(
            chat_id=chat_id,
            direction="outbound",
            sender_handle=sender_handle,
            body=body,
            service="SMS",
            preferred_service=preferred_service,
            idempotency_key=idempotency_key,
            transport_key=None,
            raw_pdu_hex=None,
            content_location=None,
            delivery_status="queued",
            is_delivered=False,
            is_read=False,
            created_at=created_at,
            sent_at=created_at,
        )

    def create_inbound_message(
        self,
        *,
        local_number: str,
        remote_number: str,
        body: str,
        created_at: str,
        service: str = "SMS",
        transport_key: str | None = None,
        raw_pdu_hex: str | None = None,
        content_location: str | None = None,
        attachments: list[dict] | None = None,
    ) -> tuple[dict, dict]:
        chat, _ = self.get_or_create_chat(
            from_number=local_number,
            to_number=remote_number,
            created_at=created_at,
            service=service,
        )
        message = self._create_message(
            chat_id=chat["id"],
            direction="inbound",
            sender_handle=remote_number,
            body=body,
            service=service,
            preferred_service=None,
            idempotency_key=None,
            transport_key=transport_key,
            raw_pdu_hex=raw_pdu_hex,
            content_location=content_location,
            delivery_status="delivered",
            is_delivered=True,
            is_read=False,
            created_at=created_at,
            sent_at=created_at,
            delivered_at=created_at,
            attachments=attachments or [],
        )
        updated_chat = self.get_chat(chat["id"])
        return updated_chat, message

    def _create_message(
        self,
        *,
        chat_id: str,
        direction: str,
        sender_handle: str,
        body: str,
        service: str,
        preferred_service: str | None,
        idempotency_key: str | None,
        transport_key: str | None,
        raw_pdu_hex: str | None,
        content_location: str | None,
        delivery_status: str,
        is_delivered: bool,
        is_read: bool,
        created_at: str,
        sent_at: str | None,
        delivered_at: str | None = None,
        read_at: str | None = None,
        attachments: list[dict] | None = None,
    ) -> dict:
        message_id = str(uuid.uuid4())

        with self._lock, self._connect() as connection:
            connection.execute(
                """
                INSERT INTO messages (
                    id,
                    chat_id,
                    idempotency_key,
                    direction,
                    sender_handle,
                    body,
                    service,
                    preferred_service,
                    transport_key,
                    raw_pdu_hex,
                    content_location,
                    delivery_status,
                    is_read,
                    is_delivered,
                    created_at,
                    updated_at,
                    sent_at,
                    delivered_at,
                    read_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    message_id,
                    chat_id,
                    idempotency_key,
                    direction,
                    sender_handle,
                    body,
                    service,
                    preferred_service,
                    transport_key,
                    raw_pdu_hex,
                    content_location,
                    delivery_status,
                    int(is_read),
                    int(is_delivered),
                    created_at,
                    created_at,
                    sent_at,
                    delivered_at,
                    read_at,
                ),
            )
            connection.execute(
                """
                UPDATE chats
                SET updated_at = ?, service = CASE WHEN service = 'MMS' OR ? = 'MMS' THEN 'MMS' ELSE service END
                WHERE id = ?
                """,
                (created_at, service, chat_id),
            )
            self._insert_attachments(
                connection,
                message_id=message_id,
                created_at=created_at,
                attachments=attachments or [],
            )
            row = connection.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
            return dict(row)

    @staticmethod
    def _insert_attachments(
        connection: sqlite3.Connection,
        *,
        message_id: str,
        created_at: str,
        attachments: list[dict],
    ) -> None:
        for part_index, attachment in enumerate(attachments):
            connection.execute(
                """
                INSERT INTO attachments (
                    id,
                    message_id,
                    part_index,
                    kind,
                    mime_type,
                    filename,
                    relative_path,
                    size_bytes,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    message_id,
                    part_index,
                    attachment["kind"],
                    attachment["mime_type"],
                    attachment.get("filename"),
                    attachment["relative_path"],
                    int(attachment["size_bytes"]),
                    created_at,
                ),
            )
