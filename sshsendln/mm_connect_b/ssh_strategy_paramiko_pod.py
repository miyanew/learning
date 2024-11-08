import re
import socket
import time

from typing import Optional

import paramiko
from .exceptions import ConnectionError


class ParamikoSSHSessionStrategyPod:
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        bastion_user: str,
        timeout: float,
    ):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.bastion_user = bastion_user
        self.timeout = timeout if timeout else 30.0

    def start_session(
        self,
        parent_client: Optional[paramiko.SSHClient] = None,
    ) -> paramiko.Channel:
        if not parent_client:
            raise ValueError("No active session to disconnect from")

        try:
            prompt_bastion = r"\[.+@.+\]\$"
            shell = parent_client.invoke_shell()
            shell.settimeout(self.timeout)

            command = f"oc login -u admin -p `cat /home/{self.bastion_user}/`"
            self._send_line(shell, command)

            self._read_until_match(shell, prompt_bastion, command)
            command = f"oc get pods -n {self.hostname} | grep userinterface | grep Running | cut -d' ' -f1 | head -1"
            self._send_line(shell, command)
            resp = self._read_until_match(shell, prompt_bastion, command)
            pod_name = [
                ln.strip()
                for ln in resp.splitlines()
                if not re.search(prompt_bastion, ln)
            ][-1]

            command = f"oc exec -it -n {self.hostname} {pod_name} -- /apps/pkg --c"
            self._send_line(shell, command)
            self._read_until_match(shell, "USERNAME :")
            self._send_line(shell, self.username)
            self._read_until_match(shell, "PASSWORD :")
            self._send_line(shell, self.password)

            prompt_host = rf"\[{self.hostname}\]"
            self._read_until_match(shell, prompt_host)
            self._send_line(shell, "INH-MSG:ALL;")
            self._read_until_match(shell, "PASSWORD :")
            self._send_line(shell, self.password)
            self._read_until_match(shell, rf"\[{self.hostname}\]")

            return shell
        except paramiko.AuthenticationException as e:
            raise ConnectionError(f"Authentication failed: {e}") from e
        except paramiko.SSHException as e:
            raise ConnectionError(f"SSH error occurred: {e}") from e
        except socket.timeout as e:
            raise ConnectionError(f"Connection timed out: {e}") from e
        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {e}") from e

    def _send_line(self, shell: paramiko.Channel, command: str) -> None:
        shell.send(f"{command}\r\n".encode("utf-8"))

    def _read_until_match(
        self,
        shell: paramiko.Channel,
        expected_str: str,
        command: Optional[str] = None,
        timeout: float = 30.0,
        buffer_size: int = 1024,
    ) -> str:
        resp = ""
        start_time: float = time.time()

        echo_back_pattern = (
            re.compile(re.escape(command)) if command else None
        )
        rtrv_cmd_pattern = (
            re.compile(re.escape(command))
            if command and ("RTRV-" in command)
            else None
        )

        expected_pattern = re.compile(expected_str)
        expected_str_found = False
        sleep_count = 0

        while True:
            if shell.recv_ready():
                chunk = shell.recv(buffer_size)
                resp += chunk.decode("utf-8")

                if expected_pattern.search(resp):
                    if echo_back_pattern:
                        if echo_back_pattern.search(resp) and (not expected_str_found):
                            expected_str_found = True
                            continue

                    if rtrv_cmd_pattern:
                        if rtrv_cmd_pattern.search(resp) and (" : COMPLD" not in resp):
                            continue

                        if not f"[{self.hostname}]" in resp.splitlines()[-1]:
                            continue

                    break
            elif time.time() - start_time > timeout:
                raise TimeoutError(f"Timeout waiting for: {expected_str}")
            else:
                time.sleep(0.1)
                sleep_count += 1
                if sleep_count % 5 == 0:
                    shell.send(b" ")

        return resp

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

    # def send_command(
    #     self,
    #     shell: paramiko.Channel,
    #     command: str,
    #     timeout: float = 30.0,
    #     expected_str: Optional[str] = None,
    # ) -> str:
    #     if not shell:
    #         raise ConnectionError("No active session to send command to")
        
    #     if not expected_str:
    #         prompt = rf"\[{self.hostname}\]"
    #         expected_str = prompt

    #     try:
    #         shell.settimeout(timeout)

    #         shell.send(f"{command}\r\n".encode("utf-8"))
    #         resp = self._read_until_match(shell, expected_str, command)

    #         return self._format_command_response(resp)
    #     except paramiko.SSHException as e:
    #         raise CommandError(f"SSH error occurred: {e}") from e
    #     except socket.timeout as e:
    #         raise ConnectionError(f"Connection timed out: {e}") from e
    #     except Exception as e:
    #         raise CommandError(f"executing the command error occurred: {e}") from e

    # def _format_command_response(self, resp: str) -> str:
    #     lines = resp.splitlines()
    #     result = "\n".join(lines[1:-1])
    #     return result.strip()
