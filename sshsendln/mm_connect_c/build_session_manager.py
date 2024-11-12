from .config_loader import load_json_file
from .session_manager_bastion import BastionNode
from .session_manager_target import TargetNode


class BuildSessionManager:
    def __init__(self, config_file):
        self.ssh_configs = load_json_file(config_file)
        self.session_manager = None

    def build(self, host_name: str):
        nodes = []
        host_config = self.get_config(host_name)

        bastion_names = host_config.get("bastions", [])
        if bastion_names:
            nodes = self.create_bastions(bastion_names)

        target_node = TargetNode(host_name, host_config, nodes).build()
        nodes.append(target_node)
        self.establish_connection(nodes)
        return target_node

    def get_config(self, host_name):
        return self.ssh_configs[host_name]

    def create_bastions(self, host_names):
        bastions = []
        for host_name in host_names:
            bastions.append(BastionNode(host_name, self.ssh_configs[host_name]).build())
        return bastions

    def establish_connection(self, nodes) -> None:
        ini_host, *remaining_hosts = nodes

        try:
            if remaining_hosts:
                for host in remaining_hosts:
                    ini_host.add(host)
                ini_host.connect_all()
            else:
                ini_host.connect()
        except Exception as e:
            raise ConnectionError(f"Failed to establish connection: {e}")
