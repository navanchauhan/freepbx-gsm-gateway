from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import hashlib
import hmac
import json
import queue
import threading
import urllib.error
import urllib.request
import uuid


@dataclass(frozen=True)
class MessageEvent:
    id: str
    type: str
    occurred_at: str
    payload: dict

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "occurred_at": self.occurred_at,
            **self.payload,
        }


class EventBroker:
    def __init__(self, *, max_queue_size: int = 256) -> None:
        self._max_queue_size = max_queue_size
        self._lock = threading.Lock()
        self._subscribers: dict[str, tuple[queue.Queue[MessageEvent], frozenset[str] | None]] = {}

    def subscribe(self, *, event_types: list[str] | None = None) -> tuple[str, queue.Queue[MessageEvent]]:
        subscription_id = str(uuid.uuid4())
        subscriber_queue: queue.Queue[MessageEvent] = queue.Queue(maxsize=self._max_queue_size)
        normalized = frozenset(event_types) if event_types else None
        with self._lock:
            self._subscribers[subscription_id] = (subscriber_queue, normalized)
        return subscription_id, subscriber_queue

    def unsubscribe(self, subscription_id: str) -> None:
        with self._lock:
            self._subscribers.pop(subscription_id, None)

    def publish(self, event: MessageEvent) -> None:
        with self._lock:
            subscribers = list(self._subscribers.values())

        for subscriber_queue, event_types in subscribers:
            if event_types is not None and event.type not in event_types:
                continue
            self._enqueue_nonblocking(subscriber_queue, event)

    @staticmethod
    def _enqueue_nonblocking(
        subscriber_queue: queue.Queue[MessageEvent],
        event: MessageEvent,
    ) -> None:
        try:
            subscriber_queue.put_nowait(event)
            return
        except queue.Full:
            pass

        try:
            subscriber_queue.get_nowait()
        except queue.Empty:
            pass

        try:
            subscriber_queue.put_nowait(event)
        except queue.Full:
            pass


class WebhookDispatcher:
    def __init__(
        self,
        *,
        store,
        timeout_seconds: float = 5.0,
        max_queue_size: int = 256,
    ) -> None:
        self.store = store
        self.timeout_seconds = timeout_seconds
        self._queue: queue.Queue[MessageEvent | None] = queue.Queue(maxsize=max_queue_size)
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread is not None and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._run,
            name="sms-api-webhook-dispatcher",
            daemon=True,
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        try:
            self._queue.put_nowait(None)
        except queue.Full:
            pass
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        self._thread = None

    def enqueue(self, event: MessageEvent) -> None:
        try:
            self._queue.put_nowait(event)
        except queue.Full:
            print(f"[webhooks] dropping event {event.id}: delivery queue is full")

    def _run(self) -> None:
        while not self._stop_event.is_set():
            try:
                event = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            if event is None:
                continue

            try:
                self._deliver(event)
            except Exception as exc:
                print(f"[webhooks] delivery worker failed for {event.id}: {exc}")

    def _deliver(self, event: MessageEvent) -> None:
        subscriptions = self.store.list_webhook_subscriptions(active_only=True)
        if not subscriptions:
            return

        body = json.dumps(event.as_dict(), separators=(",", ":"), sort_keys=True).encode("utf-8")
        for subscription in subscriptions:
            if subscription["event_types"] and event.type not in subscription["event_types"]:
                continue
            self._deliver_to_subscription(subscription=subscription, event=event, body=body)

    def _deliver_to_subscription(self, *, subscription: dict, event: MessageEvent, body: bytes) -> None:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "sim7600-sms-api/1.0",
            "X-SMS-API-Event-Id": event.id,
            "X-SMS-API-Event-Type": event.type,
        }
        secret = subscription.get("secret") or ""
        if secret:
            digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
            headers["X-SMS-API-Signature-256"] = f"sha256={digest}"

        request = urllib.request.Request(
            subscription["target_url"],
            data=body,
            headers=headers,
            method="POST",
        )

        delivered_at = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                status_code = getattr(response, "status", 200)
                if 200 <= status_code < 300:
                    self.store.record_webhook_delivery_result(
                        subscription_id=subscription["id"],
                        success=True,
                        delivered_at=delivered_at,
                        status_code=status_code,
                        message=None,
                    )
                    return

                self.store.record_webhook_delivery_result(
                    subscription_id=subscription["id"],
                    success=False,
                    delivered_at=delivered_at,
                    status_code=status_code,
                    message=f"Non-success HTTP status {status_code}",
                )
        except urllib.error.HTTPError as exc:
            self.store.record_webhook_delivery_result(
                subscription_id=subscription["id"],
                success=False,
                delivered_at=delivered_at,
                status_code=exc.code,
                message=exc.reason,
            )
        except urllib.error.URLError as exc:
            self.store.record_webhook_delivery_result(
                subscription_id=subscription["id"],
                success=False,
                delivered_at=delivered_at,
                status_code=None,
                message=str(exc.reason),
            )
        except Exception as exc:
            self.store.record_webhook_delivery_result(
                subscription_id=subscription["id"],
                success=False,
                delivered_at=delivered_at,
                status_code=None,
                message=str(exc),
            )
