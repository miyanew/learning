import re
import socket
import time
# from io import StringIO
from typing import Optional

import paramiko

from .exceptions import CommandError, ConnectionError

DEFAULT_TIMEOUT = 30.0


class InvokeShellStrategy:
    def __init__(
        self,
        host_name: str,
        ip_address: str,
        username: str,
        password: str,
        key_filename: str,
        prompt_host: str,
        port: Optional[int] = None,
        timeout: Optional[float] = None,
    ):
        self.host_name = host_name
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.prompt_host = prompt_host
        self.port = port if port else 22
        self.timeout = timeout if timeout else DEFAULT_TIMEOUT

    def start_session(
        self,
        parent_client: Optional[paramiko.SSHClient] = None,
    ) -> paramiko.Channel:
        if not parent_client:
            raise ValueError("No active session to disconnect from")

        try:
            shell = parent_client.invoke_shell()
            shell.settimeout(self.timeout)

            if self.key_filename:
                command = (
                    f"ssh -i {self.key_filename} {self.username}@{self.ip_address}"
                )
                shell.send(command.encode("utf-8") + b"\r\n")
                self._read_all(shell, self.prompt_host)
            else:
                command = f"ssh {self.username}@{self.ip_address}"
                shell.send(command.encode("utf-8") + b"\r\n")
                self._read_all(shell, "assword:")
                shell.send(self.password.encode("utf-8") + b"\r\n")
                self._read_all(shell, self.prompt_host)

            return shell
        except paramiko.AuthenticationException as e:
            raise ConnectionError(f"Authentication failed: {e}") from e
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {e}") from e

    # def _get_remote_key(
    #     self,
    #     parent_client: paramiko.SSHClient,
    #     key_path: str,
    # ) -> paramiko.RSAKey:
    #     stdin, stdout, stderr = parent_client.exec_command(f"cat {key_path}")
    #     private_key_content = stdout.read().decode()
    #     error = stderr.read().decode()
    #     if error:
    #         raise Exception(f"Failed to read private key from remote host: {error}")
    #     return paramiko.RSAKey.from_private_key(StringIO(private_key_content))

    def end_session(self, client: paramiko.SSHClient) -> None:
        """SSHセッションを切断します"""
        if not client:
            raise ValueError("No active session to disconnect from")

        try:
            transport = client.get_transport()
            if transport and transport.is_active():
                transport.close()
            client.close()
        except Exception as e:
            raise ConnectionError(f"Failed to close SSH connection: {e}") from e

    def send_command(
        self,
        client: paramiko.SSHClient,
        command: str,
        timeout: float = DEFAULT_TIMEOUT,
        expected_str: Optional[str] = None,
    ) -> str:
        if not client:
            raise ConnectionError("No active session to send command to")

        try:
            shell = client.invoke_shell()
            shell.settimeout(timeout)

            # 初期メッセージを破棄
            _ = self._read_all(shell, expected_str, timeout)

            shell.send(command.encode("utf-8") + b"\r\n")
            resp = self._read_all(shell, expected_str, timeout)

            return self._format_response(resp)
        except paramiko.SSHException as e:
            raise CommandError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise CommandError(f"executing the command error occurred: {e}") from e

    def _read_all(
        self,
        shell: paramiko.Channel,
        expected_str: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
        buffer_size: int = 1024,
    ) -> str:
        resp = ""
        start_time = time.time()

        more_pattern = re.compile(r"\x1b\[7m--More--\x1b\[27m")

        while True:
            if shell.recv_ready():
                chunk = shell.recv(buffer_size).decode("utf-8")
                resp += chunk

                if expected_str:
                    re.compile(expected_str).search(chunk)
                    break

                if more_pattern.search(chunk):
                    shell.send(b" ")  # スペースを送信して次ページを表示
            elif time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for: {expected_str}")
            else:
                time.sleep(0.01)
                shell.send(b" ")  # スペースを送信して受信済みページを表示

        return resp

    def _format_response(self, resp: str) -> str:
        lines = resp.splitlines()
        result = "\n".join(lines[1:-1])
        return result.strip()
