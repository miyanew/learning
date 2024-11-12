import socket
from io import StringIO
from typing import Any, Dict, Optional

import paramiko

from .exceptions import CommandError, ConnectionError

DEFAULT_TIMEOUT = 30.0


class NewSessionStrategy:
    def __init__(
        self,
        host_name: str,
        ip_address: str,
        username: str,
        password: str,
        key_filename: str,
        port: Optional[int] = None,
        timeout: Optional[float] = None,
    ):
        self.host_name = host_name
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port if port else 22
        self.timeout = timeout if timeout else DEFAULT_TIMEOUT

    def start_session(
        self,
        parent_client: Optional[paramiko.SSHClient] = None,
    ) -> paramiko.SSHClient:
        """SSHセッションを開始する

        Args:
            parent_client: 多段接続時の親クライアント（オプション）

        Returns:
            設定済みのSSHクライアント

        Raises:
            ConnectionError: 接続に失敗した場合
        """
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            sock = None
            if parent_client:
                sock = self._setup_multi_hop_connection(parent_client)

            connect_kwargs: Dict[str, Any] = {
                "hostname": self.ip_address,
                "username": self.username,
                "port": self.port,
                "timeout": self.timeout,
                "sock": sock,
            }

            if self.key_filename:
                if parent_client:
                    connect_kwargs["pkey"] = self._get_remote_key(
                        parent_client, self.key_filename
                    )
                else:
                    connect_kwargs["pkey"] = paramiko.RSAKey.from_private_key_file(
                        self.key_filename
                    )
            elif self.password:
                connect_kwargs["password"] = self.password

            client.connect(**connect_kwargs)
            return client
        except paramiko.AuthenticationException as e:
            raise ConnectionError(f"Authentication failed: {e}") from e
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {e}") from e

    def _setup_multi_hop_connection(
        self,
        parent_client: paramiko.SSHClient,
    ) -> Optional[paramiko.Channel]:
        """多段接続のためのチャンネル設定を行う

        Args:
            parent_client: 親となるSSH接続のクライアント

        Returns:
            設定されたSSHチャンネル

        Raises:
            ConnectionError: チャンネル設定に失敗した場合
        """
        transport = parent_client.get_transport()
        if transport is None:
            raise ConnectionError("Parent client transport is not available")

        try:
            dest_addr = (self.ip_address, self.port)
            local_addr = ("local_host", 0)
            return transport.open_channel("direct-tcpip", dest_addr, local_addr)
        except paramiko.SSHException as e:
            raise ConnectionError(f"Failed to open channel: {e}") from e

    def _get_remote_key(
        self,
        parent_client: paramiko.SSHClient,
        key_path: str,
    ) -> paramiko.RSAKey:
        _, stdout, stderr = parent_client.exec_command(f"cat {key_path}")
        private_key_content = stdout.read().decode()
        error = stderr.read().decode()
        if error:
            raise Exception(f"Failed to read private key from remote host: {error}")
        return paramiko.RSAKey.from_private_key(StringIO(private_key_content))

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
    ) -> str:
        if not client:
            raise ConnectionError("No active session to send command to")

        try:
            _, stdout, stderr = client.exec_command(command, timeout=timeout)
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0 or error:
                raise CommandError(
                    f"Command failed with exit status {exit_status}. Error: {error}"
                )

            return output.strip()
        except paramiko.SSHException as e:
            raise CommandError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise CommandError(f"executing the command error occurred: {e}") from e
