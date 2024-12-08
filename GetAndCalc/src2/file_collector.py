import os
import socket
from typing import Dict, List

import paramiko

from exceptions import CollectionError, SSHConfigurationError


class Error(Exception):
    """Base-class for all exceptions raised by this module."""

    pass


class FileCollector:
    def __init__(self, ssh_config):
        self.ssh_config = ssh_config
        self.ssh_timeout = 20
        self.ssh_sessions: Dict[str, paramiko.SSHClient] = {}
        self.sftp_timeout = 20
        self.sftp_sessions: Dict[str, paramiko.SFTPClient] = {}
        self._collected_files: List[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_all_sessions()

    def collect_file(self, host: str, remote_path: str, local_dir: str):
        """
        指定されたホストからファイルを収集する

        Raises:
            ConnectionError: SSH接続またはSFTP接続のエラー
            CollectionError: ファイル収集中のエラー
        """
        try:
            local_file = os.path.basename(remote_path)
            local_path = os.path.join(local_dir, local_file)

            sftp = self._get_sftp_session(host)
            try:
                sftp.stat(remote_path)
            except FileNotFoundError:
                raise FileNotFoundError(f"Remote file does not exist: {remote_path}")

            sftp.get(remote_path, local_path)

            self._collected_files.append(local_path)
        except (ConnectionError, SSHConfigurationError) as e:
            raise ConnectionError(str(e))
        except FileNotFoundError as e:
            raise CollectionError(str(e))
        except Exception as e:
            raise CollectionError(f"Collection failed: {host}: {remote_path}, {e}")

    @property
    def collected_files(self) -> List[str]:
        """収集されたファイルのリストを返す"""
        return self._collected_files

    def _get_sftp_session(self, host: str) -> paramiko.SFTPClient:
        """
        指定されたホストのSFTPセッションを取得または作成する

        Raises:
            ConnectionError: SSH接続またはSFTP接続のエラー
        """
        try:
            if host not in self.sftp_sessions:
                if host not in self.ssh_sessions:
                    self.ssh_sessions[host] = self._create_ssh_session(host)
        except Exception as e:
            raise ConnectionError(f"SSH connection failed for {host}: {e}")

        try:
            self.sftp_sessions[host] = self.ssh_sessions[host].open_sftp()
            self.sftp_sessions[host].get_channel().settimeout(self.sftp_timeout)
        except Exception as e:
            raise ConnectionError(f"SFTP connection failed for {host}: {e}")
        return self.sftp_sessions[host]

    def _create_ssh_session(self, host: str) -> paramiko.SSHClient:
        """
        指定されたホストのSSHセッションを作成する

        Raises:
            SSHConfigurationError: SSHコンフィグの不備
            ConnectionError: SSH接続に失敗したエラー（タイムアウトを含む）
        """
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        host_conf = self.ssh_config[host]
        if not host_conf or not host_conf["key_filename"]:
            raise SSHConfigurationError(f"Not set SSH Configuration for {host}")

        try:
            session.connect(
                hostname=host_conf["ip_address"],
                port=host_conf["port"],
                username=host_conf["username"],
                key_filename=host_conf["key_filename"],
                timeout=self.ssh_timeout,
            )
        except FileNotFoundError as e:
            raise SSHConfigurationError(f"SSH key file does not exist: {e}")
        except socket.timeout as e:
            raise ConnectionError(f"Connection to {host} timed out: {e}")
        except Exception as e:
            raise ConnectionError(f"Unexpected Connection error: {e}")
        return session

    def _close_all_sessions(self):
        """すべてのSFTPセッションとSSHセッションを閉じる"""
        for sftp in self.sftp_sessions.values():
            sftp.close()
        self.sftp_sessions.clear()

        for session in self.ssh_sessions.values():
            session.close()
        self.ssh_sessions.clear()
