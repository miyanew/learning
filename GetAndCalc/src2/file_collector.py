import os
from typing import Dict, List

import paramiko

from exceptions import AuthenticationError, CollectionError, SFTPConnectionError


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
        except Exception as e:
            raise CollectionError(
                f"Unexpected error while collecting {remote_path}: {e}"
            ) from e

    @property
    def collected_files(self) -> List[str]:
        return self._collected_files

    def _get_sftp_session(self, host: str) -> paramiko.SFTPClient:
        if host not in self.sftp_sessions:
            if host not in self.sessions:
                self.sessions[host] = self._create_ssh_session(host)
            try:
                self.sftp_sessions[host] = self.sessions[host].open_sftp()
                self.sftp_sessions[host].get_channel().settimeout(60)
            except paramiko.SSHException as e:
                raise SFTPConnectionError(
                    f"SFTP connection failed for {host}: {e}"
                ) from e
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

    # def collect_files(self, sftp_configs) -> List[str]:
    #     local_paths = []
    #     try:
    #         for host, config in sftp_configs.items():
    #             with self._sftp_session(host) as sftp:
    #                 remote_path = os.path.join(
    #                     config["remote_dir"], config["remote_file"]
    #                 )
    #                 local_path = os.path.join(config["local_dir"], config["local_file"])

    #                 os.makedirs(config["local_dir"], exist_ok=True)

    #                 sftp.get(remote_path, local_path)
    #                 local_paths.append(local_path)
    #     except Exception as e:
    #         raise CollectionError(f"Failed to collect files: {str(e)}") from e

    #     return local_paths

    # @contextlib.contextmanager
    # def _sftp_session(self, host):
    #     session = None
    #     try:
    #         session = self._create_ssh_session(host)
    #         sftp = session.open_sftp()
    #         yield sftp
    #     finally:
    #         if session:
    #             sftp.close()
    #             session.close()
