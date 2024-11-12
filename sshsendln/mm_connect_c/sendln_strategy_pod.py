import socket

import paramiko

from .exceptions import CommandError, ConnectionError


class SendLineStrategyPod:
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

        prompt = rf"\[{self.session_strategy.hostname}\]"

        try:
            shell.settimeout(timeout)

            self.session_strategy.send_line(shell, command)
            resp = self.session_strategy.read_until_match(shell, prompt, command)

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
