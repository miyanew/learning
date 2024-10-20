import socket
import paramiko
from typing import Optional, Any, Dict
from .exceptions import ConnectionError, CommandError


class ParamikoSFTPSessionStrategy:
    def __init__(
        self,
        ip_address: str,
        username: str,
        password: str,
        key_filename: str,
        port: int = 22,
        timeout: float = 30,
    ):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.key_filename = key_filename
        self.port = port
        self.timeout = timeout
        self._transport = None

    def start_session(
        self, transport: Optional[paramiko.Transport] = None
    ) -> paramiko.SFTPClient:
        """SFTPセッションを確立します"""
        try:
            return self._establish_session(transport)
        except paramiko.AuthenticationException as e:
            raise ConnectionError("Authentication failed") from e
        except paramiko.SSHException as e:
            raise ConnectionError("SFTP error occurred") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out") from e
        except Exception as e:
            raise ConnectionError(f"Failed to establish SFTP connection: {e}") from e

    def _establish_session(
        self, transport: Optional[paramiko.Transport]
    ) -> paramiko.SFTPClient:
        if transport:
            return self._create_multi_hop_session(transport)
        else:
            return self._create_direct_session()

    def _create_direct_session(self) -> paramiko.SFTPClient:
        """直接のSFTP接続を確立します"""
        transport = self._create_transport()
        self._establish_connection(transport)
        return self._create_sftp_client(transport)

    def _create_multi_hop_session(
        self, transport: paramiko.Transport
    ) -> paramiko.SFTPClient:
        """多段SFTP接続を確立します"""
        sock = self._create_tunnel_sock(transport)
        try:
            new_transport = self._create_transport(sock)
            self._establish_connection(new_transport)
            return self._create_sftp_client(new_transport)
        except Exception as e:
            sock.close()
            raise ConnectionError(f"Failed to establish multi-hop connection: {e}")

    def _create_tunnel_sock(self, transport: paramiko.Transport) -> paramiko.Channel:
        """多段SFTP接続用のトンネルソケットを作成します"""
        try:
            return transport.open_channel(
                "direct-tcpip",
                (self.ip_address, self.port),
                ("", 0),
            )
        except Exception as e:
            raise ConnectionError(
                f"Failed to create tunnel for multi-hop connection: {e}"
            )

    def _create_transport(
        self, sock: Optional[socket.socket] = None
    ) -> paramiko.Transport:
        """新しいTransportを作成します"""
        if sock:
            transport = paramiko.Transport(sock)
        else:
            transport = paramiko.Transport((self.ip_address, self.port))

        transport.set_keepalive(60)
        self._transport = transport
        return transport

    def _establish_connection(self, transport: paramiko.Transport) -> None:
        """Transportの接続を確立します"""
        try:
            if self.key_filename:
                pkey = paramiko.RSAKey.from_private_key_file(self.key_filename)
                transport.connect(username=self.username, pkey=pkey)
            else:
                transport.connect(username=self.username, password=self.password)
        except Exception as e:
            transport.close()
            raise ConnectionError(f"Failed to connect transport: {e}") from e

    def _create_sftp_client(self, transport: paramiko.Transport) -> paramiko.SFTPClient:
        """SFTPクライアントを作成します"""
        try:
            client = paramiko.SFTPClient.from_transport(transport)
            client.get_channel().settimeout(self.timeout)
            return client
        except Exception as e:
            transport.close()
            raise ConnectionError(f"Failed to create SFTP client: {e}") from e

    def end_session(self, client: paramiko.SFTPClient) -> None:
        """SFTPセッションを切断します"""
        if not client:
            raise ValueError("No active session to disconnect from")

        try:
            self._terminate_transport(client)
            self._close_sftp_session(client)
        except Exception as e:
            raise ConnectionError(f"Failed to close SFTP connection: {e}") from e

    def _terminate_transport(self, client: paramiko.SFTPClient) -> None:
        """SFTP基底のトランスポート層を切断します"""
        try:
            channel = client.get_channel()
            if channel is None:
                raise ValueError("No active channel found")

            transport = channel.get_transport()
            if transport and transport.is_active():
                transport.close()
        except Exception as e:
            raise ConnectionError(f"Failed to terminate SFTP transport: {e}")

    def _close_sftp_session(self, client: paramiko.SFTPClient) -> None:
        """SFTPセッションのリソースを解放します"""
        try:
            client.close()
        except Exception as e:
            raise ConnectionError(f"Failed to close SFTP session: {e}")

    def send_command(self, client: paramiko.SFTPClient, command: str) -> str:
        """
        SFTPコマンドを実行するためには、SSHClientが必要です。
        ここではSFTPクライアントから新しいSSHセッションを作成してコマンドを実行します。
        """
        if not client:
            raise ConnectionError("No active SFTP session")

        try:
            # SFTPクライアントの基となるTransportを取得
            transport = client.get_channel().get_transport()

            # 新しいSSHセッションを開く
            session = transport.open_session()
            session.settimeout(self.timeout)

            session.exec_command(command)
            output = session.makefile("rb", -1).read().decode("utf-8")
            error = session.makefile_stderr("rb", -1).read().decode("utf-8")

            exit_status = session.recv_exit_status()
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
                f"An error occurred during command execution: {e}"
            ) from e
        finally:
            if "session" in locals():
                session.close()
