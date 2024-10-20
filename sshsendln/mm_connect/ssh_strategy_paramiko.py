import socket
import paramiko
from typing import Optional, Any, Dict
from .exceptions import ConnectionError, CommandError


class ParamikoSSHSessionStrategy:
    def __init__(
        self,
        ip_address: str,
        username: str,
        password: str,
        key_filename: str,
        logout_command: str = "exit",
        command_prompt: str = "$",
        port: int = 22,
        timeout: float = 30,
    ):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.logout_command = logout_command
        self.command_prompt = command_prompt
        self.port = port
        self.timeout = timeout

    def start_session(
        self, client: Optional[paramiko.SSHClient] = None
    ) -> paramiko.SSHClient:
        """SSHセッションを確立します"""
        try:
            return self._establish_session(client)
        except paramiko.AuthenticationException as e:
            raise ConnectionError("Authentication failed") from e
        except paramiko.SSHException as e:
            raise ConnectionError("SSH error occurred") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out") from e
        except Exception as e:
            raise ConnectionError(f"Failed to establish SSH connection: {e}") from e

    def _establish_session(
        self, client: Optional[paramiko.SSHClient]
    ) -> paramiko.SSHClient:
        if client:
            return self._create_multi_hop_session(client)
        else:
            return self._create_direct_session()

    def _create_direct_session(self) -> paramiko.SSHClient:
        """直接のSSH接続を確立します"""
        client = self._create_ssh_client()
        self._establish_connection(client)
        return client

    def _create_multi_hop_session(
        self, client: paramiko.SSHClient
    ) -> paramiko.SSHClient:
        """多段SSH接続を確立します"""
        sock = self._create_tunnel_sock(client)
        try:
            new_client = self._create_ssh_client()
            self._establish_connection(new_client, sock)
            return new_client
        except Exception as e:
            sock.close()
            raise ConnectionError(f"Failed to establish multi-hop connection: {e}")

    def _create_tunnel_sock(self, client: paramiko.SSHClient) -> paramiko.Channel:
        """多段SSH接続用のトンネルソケットを作成します"""
        transport = client.get_transport()
        if not transport:
            raise ConnectionError("No transport available in existing connection")

        try:
            return transport.open_channel(
                "direct-tcpip",
                (self.ip_address, 22),
                ("", 0),  # ローカルポートは自動割当
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to create tunnel for multi-hop connection: {e}"
            )

    def _create_ssh_client(self) -> paramiko.SSHClient:
        """新しいSSHクライアントを作成します"""
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        return client

    def _establish_connection(
        self,
        client: paramiko.SSHClient,
        sock: Optional[Any] = None,
    ) -> None:
        """クライアントの接続を確立します"""
        try:
            connect_kwargs = self._build_connect_kwargs(sock)
            client.connect(**connect_kwargs)
        except Exception as e:
            if sock:
                sock.close()
            raise ConnectionError(f"Failed to connect: {e}") from e

    def _build_connect_kwargs(self, sock: Optional[Any] = None) -> Dict[str, Any]:
        """
        SSH接続に必要なパラメータを構築します。

        Args:
            sock: 多段SSH接続用のチャネル（オプション）

        Returns:
            Dict[str, Any]: paramiko.SSHClient.connect()に渡すパラメータ
        """
        # 必須パラメータ
        connect_kwargs: Dict[str, Any] = {
            "hostname": self.ip_address,
            "username": self.username,
            "port": self.port,
            "timeout": self.timeout,
            "allow_agent": False,  # SSH agentを使用しない
            "look_for_keys": False,  # システムのキーを自動検索しない
        }

        if self.key_filename:
            connect_kwargs["key_filename"] = self.key_filename
        else:
            connect_kwargs["password"] = self.password

        # 多段SSH接続用のソケット
        if sock:
            connect_kwargs["sock"] = sock

        return connect_kwargs

    def end_session(self, client: paramiko.SSHClient) -> None:
        """SSHセッションを切断します"""
        if not client:
            raise ValueError("No active session to disconnect from")

        try:
            self._terminate_session(client)
            self._close_connection(client)
        except Exception as e:
            raise ConnectionError(f"Failed to close SSH connection: {e}") from e

    def _terminate_session(self, client: paramiko.SSHClient) -> None:
        """SSHセッションを終了し、ログアウトコマンドを実行します"""
        try:
            self.send_command(client, self.logout_command)
        except Exception as e:
            raise ConnectionError(f"Failed to terminate SSH session: {e}")

    def _close_connection(self, client: paramiko.SSHClient) -> None:
        """SSH接続のリソースを解放します"""
        try:
            transport = client.get_transport()
            if transport and transport.is_active():
                transport.close()
            client.close()
        except Exception as e:
            raise ConnectionError(f"Failed to close SSH connection: {e}")

    def send_command(
        self,
        client: paramiko.SSHClient,
        command: str,
    ) -> str:
        if not client:
            raise ConnectionError("No active session to send command to")

        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=self.timeout)
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            exit_status = stdout.channel.recv_exit_status()
            if exit_status != 0 or error:
                raise CommandError(
                    f"Command failed with exit status {exit_status}. Error: {error}"
                )

            return output.strip()
        except paramiko.SSHException as e:
            raise CommandError(
                f"SSH error occurred while executing the command: {e}"
            ) from e
        except Exception as e:
            raise CommandError(
                f"An error occurred while executing the command: {e}"
            ) from e

    # def get_interactive_shell(self, client: paramiko.SSHClient, timeout: float = 30) -> paramiko.Channel:
    #     channel = client.invoke_shell()
    #     channel.settimeout(timeout)

    #     self._wait_for_prompt(channel)
    #     return channel

    # def _wait_for_prompt(self, channel: paramiko.Channel) -> None:
    #     buffer = ""
    #     while not buffer.endswith(self.command_prompt):
    #         if channel.recv_ready():
    #             byte = channel.recv(1)
    #             buffer += byte.decode('utf-8')

    # def send_interactive_command(self, channel: paramiko.Channel, command: str) -> str:
    #     channel.send(command + "\n")
    #     return self._wait_for_prompt(channel)
