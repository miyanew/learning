import os
import sys
import unittest
from unittest.mock import Mock, patch
from pexpect import TIMEOUT, pxssh

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))

from MySSH import MySsh


class TestMySsh(unittest.TestCase):
    def setUp(self):
        self.ssh_config = {
            "host_name": "test_host",
            "ip_address": "192.168.1.1",
            "user_name": "test_user",
            "password": "test_password",
        }

    @patch("pexpect.pxssh.pxssh")
    def test_successful_login(self, mock_pxssh):
        mock_session = Mock()
        mock_pxssh.return_value = mock_session

        with MySsh(self.ssh_config) as ssh:
            self.assertIsNotNone(ssh.session)

        mock_session.login.assert_called_once_with(
            server="192.168.1.1",
            username="test_user",
            password="test_password",
            login_timeout=5,
        )
        mock_session.logout.assert_called_once()
        mock_session.close.assert_called_once()

    @patch("pexpect.pxssh.pxssh")
    def test_failed_login(self, mock_pxssh):
        mock_pxssh.side_effect = pxssh.ExceptionPxssh("Login failed")

        with self.assertRaises(ConnectionError):
            with MySsh(self.ssh_config):
                pass

    @patch("pexpect.pxssh.pxssh")
    def test_sendln_success(self, mock_pxssh):
        mock_session = Mock()
        mock_pxssh.return_value = mock_session
        mock_session.expect.return_value = 0
        mock_session.before = b"command output\nline1\nline2\n[PEXPECT]"

        with MySsh(self.ssh_config) as ssh:
            result = ssh.sendln("test_command")

        self.assertEqual(result, "line1\nline2")
        mock_session.sendline.assert_called_once_with("test_command")
        mock_session.expect.assert_called_once()

    @patch("pexpect.pxssh.pxssh")
    def test_sendln_timeout(self, mock_pxssh):
        mock_session = Mock()
        mock_pxssh.return_value = mock_session
        mock_session.expect.return_value = 1

        with MySsh(self.ssh_config) as ssh:
            with self.assertRaises(TimeoutError):
                ssh.sendln("test_command")

    @patch("pexpect.pxssh.pxssh")
    def test_sendln_eof(self, mock_pxssh):
        mock_session = Mock()
        mock_pxssh.return_value = mock_session
        mock_session.expect.return_value = 2

        with MySsh(self.ssh_config) as ssh:
            with self.assertRaises(EOFError):
                ssh.sendln("test_command")


if __name__ == "__main__":
    unittest.main()
