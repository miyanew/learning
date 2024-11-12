import socket
from typing import Optional

import paramiko

from .exceptions import CommandError, ConnectionError

DEFAULT_TIMEOUT = 30.0


class GeneralSendCommandStrategy:
    def send_command(
        self,
        client: paramiko.SSHClient,
        command: str,
        timeout: Optional[float] = DEFAULT_TIMEOUT,
    ) -> str:
        if not client:
            raise ConnectionError("No active session to send command to")

        try:
            _, stdout, stderr = client.exec_command(command, timeout=timeout)
            resp = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0 or error:
                raise CommandError(
                    f"Command failed with exit status {exit_status}. Error: {error}"
                )

            return resp.strip()
        except paramiko.SSHException as e:
            raise CommandError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise CommandError(f"executing the command error occurred: {e}") from e
