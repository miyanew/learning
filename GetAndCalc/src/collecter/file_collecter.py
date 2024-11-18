import os

import paramiko

from ..exceptions import AuthenticationError, CollectionError


class FileCollector:
    def __init__(self, ssh_config):
        self.ssh_config = ssh_config

    def collect_files(self, sftp_configs) -> None:
        try:
            sftp_sessions = {}
            enabled_configs = [config for config in sftp_configs if config["enabled"]]
            for config in enabled_configs:
                session = sftp_sessions.get(config["host"])

                if session is None:
                    session = paramiko.SSHClient()
                    session.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    host_conf = self.ssh_config[config["host"]]
                    if not host_conf or not host_conf.key_filename:
                        raise AuthenticationError(
                            f"Key authentication is required for host: {config['host']}"
                        )

                    session.connect(
                        host_conf.ip_address,
                        port=host_conf.port,
                        username=host_conf.username,
                        key_filename=host_conf.key_filename,
                    )

                    sftp_sessions[config["host"]] = session

                sftp = session.open_sftp()
                remote_path = os.path.join(config["remote_dir"], config["remote_file"])
                local_path = os.path.join(config["local_dir"], config["local_file"])
                sftp.get(remote_path, local_path)
                # sftp.close()
        except Exception as e:
            raise CollectionError(f"Failed to collect files: {str(e)}") from e
        finally:
            for session in sftp_sessions.values():
                session.close()
