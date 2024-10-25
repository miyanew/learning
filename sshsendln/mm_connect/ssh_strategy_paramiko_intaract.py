import re
import socket
import time
from io import StringIO
from typing import Any, Dict, Optional, Pattern, Union

import paramiko

from .exceptions import CommandError, ConnectionError


class ParamikoSSHIntaractSessionStrategy:
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
            raise ConnectionError(f"Authentication failed") from e
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH error occurred") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out") from e
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
        stdin, stdout, stderr = parent_client.exec_command(f"cat {key_path}")
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
        prompt: Union[str, bytes] = r"[#\$>]",
        timeout: float = 30.0,
    ) -> str:
        if not client:
            raise ConnectionError("No active session to send command to")

        try:
            shell = client.invoke_shell()
            shell.settimeout(timeout)

            # initial_output = self._read_all(shell, self.command_prompt, timeout)
            # print(f"Initial output: {initial_output}") # デバッグ用

            shell.send(command.encode("utf-8") + b"\n")
            output = self._read_all(shell, prompt, timeout)

            return self._clean_command_output(output, command)
        except paramiko.SSHException as e:
            raise CommandError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out") from e
        except Exception as e:
            raise CommandError(f"executing the command error occurred: {e}") from e

    def _read_all(
        self,
        shell: paramiko.Channel,
        prompt: Union[str, bytes],
        timeout: float = 30.0,
        buffer_size: int = 1024,
    ) -> str:
        output: str = ""
        start_time: float = time.time()
        prompt_str: str = prompt if isinstance(prompt, str) else prompt.decode("utf-8")
        prompt_pattern: Pattern[str] = re.compile(prompt_str)
        more_pattern = re.compile(r"\x1b\[7m--More--\x1b\[27m")

        while True:
            if shell.recv_ready():
                chunk = shell.recv(buffer_size).decode("utf-8")
                output += chunk
                if more_pattern.search(chunk):
                    shell.send(" ".encode("utf-8"))  # スペースを送信して次ページを表示
                elif prompt_pattern.search(output):
                    break
            elif time.time() - start_time > timeout:
                break
            else:
                time.sleep(0.1)
        return output

    def _clean_command_output(self, output: str, command: str) -> str:
        """コマンド実行結果から不要な行を除去する

        Args:
            output: コマンド実行の生出力
            command: 実行したコマンド

        Returns:
            整形済みの出力テキスト
        """
        lines = output.splitlines()

        # コマンド行を除去
        if lines and lines[0].strip() == command.strip():
            lines = lines[1:]

        # 最後のプロンプト行を除去
        if lines and re.match(r"[#\$>]", lines[-1]):
            lines = lines[:-1]

        return "\n".join(lines).strip()
