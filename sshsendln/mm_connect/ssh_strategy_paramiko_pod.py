import re
import socket
import time
# from io import StringIO
from typing import Any, Dict, Optional, Pattern, Union

import paramiko

from .exceptions import CommandError, ConnectionError


class ParamikoSSHSessionStrategyPod:
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        bastion_user: str,
        logout_command: str = "exit",
        command_prompt: str = "$",
        timeout: float = 30,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.bastion_user = bastion_user
        self.logout_command = logout_command
        self.command_prompt = command_prompt
        self.timeout = timeout

    def start_session(
        self,
        parent_client: Optional[paramiko.SSHClient] = None,
    ) -> paramiko.SSHClient:
        if not parent_client:
            raise ValueError("No active session to disconnect from")

        try:
            # client = paramiko.SSHClient()
            # client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            shell = parent_client.invoke_shell()
            shell.settimeout(self.timeout)

            command = f"oc login -u admin -p `cat /home/{self.bastion_user}/`"
            shell.send(command.encode("utf-8") + b"\n")
            prompt = ">"
            # session.prompt()

            command = f"_fetch_running_pod_name({self.hostname})"
            shell.send(command.encode("utf-8") + b"\n")
            prompt = ">"
            pod_name = self._read_all(shell, prompt, self.timeout)
            # pod_name = self._clean_command_output(pod_name, command)

            command = f"oc exec -it -n {self.hostname} {pod_name} -- "
            shell.send(command.encode("utf-8") + b"\n")
            prompt = ">"
            # session.expect("USERNAME :")

            command = f"{self.username}"
            shell.send(command.encode("utf-8") + b"\n")
            prompt = ">"
            # session.expect("PASSWORD :")

            command = f"{self.password}"
            shell.send(command.encode("utf-8") + b"\n")
            prompt = ">"
            # session.expect(rf"\[{self.hostname}\]")

            # command = f"inhibit msg"
            # shell.send(command.encode("utf-8") + b"\n")
            # prompt = ">"
            # session.expect(rf"\[{self.hostname}\]")

            return parent_client
        except paramiko.AuthenticationException as e:
            raise ConnectionError(f"Authentication failed") from e
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH error occurred") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out") from e
        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {e}") from e

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
