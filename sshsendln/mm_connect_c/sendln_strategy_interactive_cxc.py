import socket

import paramiko

from .exceptions import CommandError, ConnectionError


class InteractiveCxcStrategy:
    def __init__(self, session_strategy):
        self.session_strategy = session_strategy

    def send_command(
        self,
        shell: paramiko.Channel,
        command: str,
        timeout: float,
    ) -> str:
        if not shell:
            raise ConnectionError("No active session to send command to")

        prompt = self.session_strategy.host_name

        try:
            shell.settimeout(timeout)

            shell.send(command.encode("utf-8") + b"\r\n")
            resp = self.session_strategy._read_all(shell, prompt)

            return self._format_response(resp)
        except paramiko.SSHException as e:
            raise CommandError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise CommandError(f"executing the command error occurred: {e}") from e

    def _format_response(self, resp: str) -> str:
        lines = resp.splitlines()
        result = "\n".join(lines[1:-1])
        return result.strip()
