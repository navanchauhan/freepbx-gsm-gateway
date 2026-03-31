from __future__ import annotations

from dataclasses import dataclass
import socket
from typing import Mapping


class AmiError(RuntimeError):
    pass


@dataclass(frozen=True)
class AmiResponse:
    response: str
    message: str | None
    outputs: list[str]


class AmiClient:
    def __init__(
        self,
        *,
        host: str,
        port: int,
        username: str,
        password: str,
        timeout_seconds: float = 5.0,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout_seconds = timeout_seconds

    def command(self, command: str) -> str:
        try:
            with socket.create_connection((self.host, self.port), self.timeout_seconds) as sock:
                sock.settimeout(self.timeout_seconds)
                reader = sock.makefile("rb")

                banner = reader.readline()
                if not banner:
                    raise AmiError("Asterisk AMI did not send a banner")

                self._send_action(
                    sock,
                    {
                        "Action": "Login",
                        "Username": self.username,
                        "Secret": self.password,
                        "Events": "off",
                    },
                )
                login_response = self._read_response(reader)
                if login_response.response.lower() != "success":
                    raise AmiError(login_response.message or "AMI login failed")

                self._send_action(
                    sock,
                    {
                        "Action": "Command",
                        "Command": command,
                    },
                )
                command_response = self._read_response(reader)

                self._send_action(sock, {"Action": "Logoff"})

                if command_response.response.lower() not in {"success", "follows"}:
                    raise AmiError(command_response.message or f"AMI command failed: {command}")

                return "\n".join(command_response.outputs).strip()
        except OSError as exc:
            raise AmiError(f"Could not reach Asterisk AMI at {self.host}:{self.port}") from exc

    def _read_response(self, reader) -> AmiResponse:
        lines: list[str] = []
        saw_end_command = False

        while True:
            raw_line = reader.readline()
            if not raw_line:
                raise AmiError("AMI connection closed unexpectedly")

            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            if not line:
                if lines and not saw_end_command:
                    break
                if lines and saw_end_command:
                    break
                continue

            lines.append(line)
            if line == "--END COMMAND--":
                saw_end_command = True

        response = "Unknown"
        message = None
        outputs: list[str] = []

        for line in lines:
            if line == "--END COMMAND--":
                continue

            if ": " in line:
                key, value = line.split(": ", 1)
                if key == "Response":
                    response = value
                elif key == "Message":
                    message = value
                elif key == "Output":
                    outputs.append(value)
            else:
                outputs.append(line)

        return AmiResponse(response=response, message=message, outputs=outputs)

    @staticmethod
    def _send_action(sock: socket.socket, fields: Mapping[str, str]) -> None:
        payload = "".join(f"{key}: {value}\r\n" for key, value in fields.items()) + "\r\n"
        sock.sendall(payload.encode("utf-8"))
