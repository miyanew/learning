import contextlib
import os
from typing import List

import paramiko

from exceptions import AuthenticationError, CollectionError


class FileCollector:
    def __init__(self, ssh_config):
        self.ssh_config = ssh_config

    def collect_file(self, host, remote_path, local_dir):
        pass

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

    @contextlib.contextmanager
    def _sftp_session(self, host):
        session = None
        try:
            session = self._create_ssh_session(host)
            sftp = session.open_sftp()
            yield sftp
        finally:
            if session:
                sftp.close()
                session.close()

    def _create_ssh_session(self, host) -> paramiko.SSHClient:
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
