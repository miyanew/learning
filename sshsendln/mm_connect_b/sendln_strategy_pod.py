import paramiko
import socket

from typing import Optional
from .exceptions import CommandError, ConnectionError

class SendLineStrategyPod:
    def __init__(self, session_strategy):
        self.session_strategy = session_strategy

    def send_command(
        self,
        shell: paramiko.Channel,
        command: str,
        expected_str: str,
        timeout: float = 30.0,
    ) -> str:
        if not shell:
            raise ConnectionError("No active session to send command to")
        
        # if not expected_str:
        #     prompt = rf"\[{self.hostname}\]"
        #     expected_str = prompt

        try:
            shell.settimeout(timeout)

            shell.send(f"{command}\r\n".encode("utf-8"))
            resp = self.session_strategy._read_until_match(shell, expected_str, command)

            return self._format_command_response(resp)
        except paramiko.SSHException as e:
            raise CommandError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise CommandError(f"executing the command error occurred: {e}") from e

    def _format_command_response(self, resp: str) -> str:
        lines = resp.splitlines()
        result = "\n".join(lines[1:-1])
        return result.strip()
