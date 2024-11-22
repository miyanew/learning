import os
from typing import Dict, List

import paramiko

from exceptions import AuthenticationError, CollectionError


class FileCollector:
    def __init__(self, ssh_config):
        self.ssh_config = ssh_config
        self.sessions: Dict[str, paramiko.SSHClient] = {}
        self.sftp_sessions: Dict[str, paramiko.SFTPClient] = {}
        self._collected_files: List[str] = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._close_all_sessions()

    def collect_file(self, host: str, remote_path: str, local_dir: str):
        try:
            local_file = os.path.basename(remote_path)
            local_path = os.path.join(local_dir, local_file)

            sftp = self._get_sftp_session(host)
            sftp.get(remote_path, local_path)
        except (ConnectionError, AuthenticationError) as e:
            raise ConnectionError(f"Host connection error: {e}")
        except Exception as e:
            raise CollectionError(f"Collection failed: {host}: {remote_path}, {e}")

    @property
    def collected_files(self) -> List[str]:
        return self._collected_files

    def _get_sftp_session(self, host: str) -> paramiko.SFTPClient:
        try:
            if host not in self.sftp_sessions:
                if host not in self.sessions:
                    self.sessions[host] = self._create_ssh_session(host)
        except Exception as e:
            raise ConnectionError(f"SSH connection failed for {host}: {e}")

        try:
            self.sftp_sessions[host] = self.sessions[host].open_sftp()
            self.sftp_sessions[host].get_channel().settimeout(60)
        except Exception as e:
            raise ConnectionError(f"SFTP connection failed for {host}: {e}")
        return self.sftp_sessions[host]

    def _create_ssh_session(self, host: str) -> paramiko.SSHClient:
        session = paramiko.SSHClient()
        session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        host_conf = self.ssh_config[host]
        if not host_conf or not host_conf["key_filename"]:
            raise AuthenticationError(
                f"Key authentication is required for host: {host}"
            )

        session.connect(
            hostname=host_conf["ip_address"],
            port=host_conf["port"],
            username=host_conf["username"],
            key_filename=host_conf["key_filename"],
        )
        return session

    def _close_all_sessions(self):
        for sftp in self.sftp_sessions.values():
            sftp.close()
        self.sftp_sessions.clear()

        for session in self.sessions.values():
            session.close()
        self.sessions.clear()
