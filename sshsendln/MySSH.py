from pexpect import TIMEOUT, pxssh
from typing import Optional


class MySsh:
    def __init__(self, ssh_config: dict):
        self.host_name = next(iter(ssh_config.keys()))
        self.ip_address = ssh_config["ip_address"]
        self.user_name = ssh_config["user_name"]
        self.password = ssh_config["password"]
        self.session: Optional[pxssh.pxssh] = None

    def __enter__(self):
        self.session = self._login()
        if self.session is None:
            raise ConnectionError("Failed to establish SSH connection")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self._logout()

    def _login(self) -> Optional[pxssh.pxssh]:
        try:
            session = pxssh.pxssh()
            session.login(
                server=self.ip_address,
                username=self.user_name,
                password=self.password,
                login_timeout=5,
            )
            return session
        except pxssh.ExceptionPxssh:
            return None

    def _logout(self) -> None:
        self.session.logout()
        self.session.close()

    def sendln(self, command: str, timeout: int = 30) -> str:
        expect_strs = [r"\$", pxssh.TIMEOUT, pxssh.EOF]
        self.session.sendline(command)
        try:
            i = self.session.expect(expect_strs, timeout=timeout)
            if i == 0:
                resp = self.session.before.decode("utf-8").strip()
                return "\n".join(resp.splitlines()[1:-1])
            elif i == 1:
                raise TimeoutError("Command execution timed out")
            else:
                raise EOFError("SSH connection closed unexpectedly")
        except pxssh.TIMEOUT:
            raise TimeoutError("Command execution timed out")
        except pxssh.EOF:
            raise EOFError("SSH connection closed unexpectedly")
