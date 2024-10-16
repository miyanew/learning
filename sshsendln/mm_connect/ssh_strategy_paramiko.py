import paramiko


class ParamikoSSHSessionStrategy:
    def __init__(
        self, ip_address: str, username: str, password: str, key_filename: str
    ):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.key_filename = key_filename

    def connect(self, client: paramiko.SSHClient) -> paramiko.SSHClient:
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if self.key_filename:
                client.connect(
                    self.ip_address,
                    username=self.username,
                    key_filename=self.key_filename,
                )
            else:
                client.connect(
                    self.ip_address, username=self.username, password=self.password
                )
            return client
        except paramiko.AuthenticationException as e:
            raise ConnectionError("Authentication failed") from e
        except paramiko.SSHException as e:
            raise ConnectionError("SSH error occurred") from e
        except Exception as e:
            raise ConnectionError(f"Failed to establish SSH connection: {e}") from e

    def disconnect(self, client: paramiko.SSHClient) -> None:
        try:
            client.close()
        except Exception as e:
            raise ConnectionError(f"Failed to close SSH connection: {e}") from e

    def send_command(
        self, client: paramiko.SSHClient, command: str, timeout: float = 10
    ) -> str:
        if not client:
            raise ValueError("No active session to send command to")

        try:
            stdin, stdout, stderr = client.exec_command(command, timeout=timeout)
            output = stdout.read().decode("utf-8")
            error = stderr.read().decode("utf-8")

            if error:
                raise RuntimeError(f"Command execution error: {error}")

            return output.strip()
        except paramiko.SSHException as e:
            raise RuntimeError(f"SSH error occurred while executing the command: {e}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while executing the command: {e}")
