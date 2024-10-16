from netmiko import ConnectHandler


class NetmikoSSHSessionStrategy:
    def __init__(
        self,
        ip_address: str,
        username: str,
        password: str,
        device_type: str,
        key_filename: str = None,
    ):
        self.ip_address = ip_address
        self.username = username
        self.password = password
        self.device_type = device_type
        self.key_filename = key_filename

    def connect(self) -> ConnectHandler:
        try:
            connection_params = {
                "device_type": self.device_type,
                "ip": self.ip_address,
                "username": self.username,
                "password": self.password,
            }
            if self.key_filename:
                connection_params["use_keys"] = True
                connection_params["key_file"] = self.key_filename
            else:
                connection_params["use_keys"] = False

            net_connect = ConnectHandler(**connection_params)
            return net_connect
        except Exception as e:
            raise ConnectionError(f"Failed to establish SSH connection: {e}") from e

    def disconnect(self, net_connect: ConnectHandler) -> None:
        try:
            net_connect.disconnect()
        except Exception as e:
            raise ConnectionError(f"Failed to close SSH connection: {e}") from e
