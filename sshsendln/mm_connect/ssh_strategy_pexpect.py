import pexpect


class PexpectSSHSessionStrategy:
    def __init__(
        self,
        ip_address: str,
        username: str,
        password: str,
        password_prompt: str,
        key_filename: str,
        command_prompt: str,
        logout_command: str,
    ):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.password_prompt = password_prompt
        self.key_filename = key_filename
        self.command_prompt = command_prompt
        self.logout_command = logout_command

    def connect(self, session: pexpect.spawn) -> pexpect.spawn:
        try:
            print(f"connected_{self.ip_address}_{self.key_filename}")
            return self._establish_connection(session)
        except pexpect.TIMEOUT as e:
            raise ConnectionError("Connection timed out") from e
        except pexpect.EOF as e:
            raise ConnectionError("SSH session was terminated unexpectedly") from e
        except Exception as e:
            raise ConnectionError(f"Failed to establish SSH connection: {e}") from e

    def _establish_connection(self, session: pexpect.spawn) -> pexpect.spawn:
        try:
            connect_command = self._generate_connect_command()
            spawn_obj = self._initialize_session(session, connect_command)
            self._authenticate(spawn_obj)
            return spawn_obj
        except Exception as e:
            raise ConnectionError(f"Login failed: {e}") from e

    def _generate_connect_command(self) -> str:
        command = f"ssh -o StrictHostKeyChecking=no {self.username}@{self.ip_address}"
        if self.key_filename:
            command += f" -i {self.key_filename}"
        return command

    def _initialize_session(
        self, session: pexpect.spawn, command: str
    ) -> pexpect.spawn:
        if session:
            session.sendline(command)
            return session
        else:
            return pexpect.spawn(command)

    def _authenticate(self, spawn_obj: pexpect.spawn) -> None:
        index = spawn_obj.expect(
            [
                self.command_prompt,
                self.password_prompt,
                "Are you sure you want to continue connecting",
                pexpect.EOF,
                pexpect.TIMEOUT,
            ]
        )

        if index == 0:
            return
        elif index == 1:
            self._handle_password_prompt(spawn_obj)
        elif index == 2:
            self._handle_host_key_prompt(spawn_obj)
        else:
            raise ConnectionError("Unexpected response during SSH connection")

    def _handle_password_prompt(self, spawn_obj: pexpect.spawn) -> None:
        spawn_obj.sendline(self.password)
        index = spawn_obj.expect([self.command_prompt, pexpect.EOF, pexpect.TIMEOUT])
        if index != 0:
            raise ConnectionError("Failed to get command prompt after password login")

    def _handle_host_key_prompt(self, spawn_obj: pexpect.spawn) -> None:
        spawn_obj.sendline("yes")
        index = spawn_obj.expect(
            [self.command_prompt, self.password_prompt, pexpect.EOF, pexpect.TIMEOUT]
        )
        if index == 1:
            self._handle_password_prompt(spawn_obj)
        if index != 0:
            raise ConnectionError(
                "Failed to get command prompt after accepting host key"
            )

    def disconnect(self, session: pexpect.spawn) -> None:
        if not session:
            raise ValueError("No active sessions to logout from")

        try:
            self._terminate_session(session)
            session.close()
        except pexpect.TIMEOUT as e:
            raise ConnectionError("Disconnect timed out") from e
        except pexpect.EOF as e:
            raise ConnectionError("SSH session was terminated unexpectedly") from e
        except Exception as e:
            raise ConnectionError(f"Failed to finish SSH connection: {e}") from e

    def _terminate_session(self, session: pexpect.spawn) -> None:
        session.sendline(self.logout_command)
        index = session.expect([pexpect.EOF, pexpect.TIMEOUT])
        if index != 0:
            raise ConnectionError("Logout command did not complete successfully")

    def send_command(
        self, session: pexpect.spawn, command: str, timeout: float = 10
    ) -> str:
        if not session:
            raise ValueError("No active session to send command to")

        try:
            session.sendline(command)
            index = session.expect(
                [self.command_prompt, pexpect.EOF, pexpect.TIMEOUT], timeout
            )

            if index == 0:
                return session.before.decode(encoding="utf-8")
            elif index == 1:
                raise EOFError("SSH session was terminated unexpectedly")
            elif index == 2:
                raise TimeoutError("Command execution timed out")

        except pexpect.TIMEOUT as e:
            raise TimeoutError(f"Command execution timed out: {e}") from e
        except pexpect.EOF as e:
            raise EOFError(f"SSH session was terminated unexpectedly: {e}") from e
        except Exception as e:
            raise RuntimeError(
                f"An error occurred while executing the command: {e}"
            ) from e
