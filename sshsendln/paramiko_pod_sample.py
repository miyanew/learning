import paramiko
from io import StringIO
from typing import Optional, Tuple, Union, Dict
import select

class PodSession:
    def __init__(self, channel: paramiko.Channel):
        self.channel = channel
        # 標準入出力とエラー出力のバッファ
        self.stdout_buffer = ""
        self.stderr_buffer = ""

    def send_command(self, command: str, timeout: float = 30.0) -> Tuple[str, str]:
        """
        ポッドにコマンドを送信し、結果を取得

        Args:
            command: 実行するコマンド
            timeout: タイムアウト時間（秒）

        Returns:
            Tuple[str, str]: (標準出力, 標準エラー出力)
        """
        if not command.endswith('\n'):
            command += '\n'
        
        self.channel.send(command)
        return self._read_output(timeout)

    def _read_output(self, timeout: float) -> Tuple[str, str]:
        """
        チャンネルから出力を読み取る
        """
        stdout_data = []
        stderr_data = []
        
        while True:
            if self.channel.exit_status_ready():
                break
                
            readers, _, _ = select.select([self.channel], [], [], timeout)
            if not readers:
                raise TimeoutError("Command timed out")

            if self.channel.recv_ready():
                stdout_data.append(self.channel.recv(4096).decode('utf-8'))
            if self.channel.recv_stderr_ready():
                stderr_data.append(self.channel.recv_stderr(4096).decode('utf-8'))

        return ''.join(stdout_data), ''.join(stderr_data)

    def close(self):
        """セッションを終了"""
        if self.channel and not self.channel.closed:
            self.channel.close()


class FlexiblePodClient:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.pod_sessions: Dict[str, PodSession] = {}

    def connect(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22
    ) -> None:
        """SSH接続を確立"""
        try:
            connect_kwargs = {
                'hostname': hostname,
                'username': username,
                'port': port
            }

            if key_path:
                key = paramiko.RSAKey.from_private_key_file(key_path)
                connect_kwargs['pkey'] = key
            elif password:
                connect_kwargs['password'] = password
            else:
                raise ValueError("Either password or key_path must be provided")

            self.client.connect(**connect_kwargs)

        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {str(e)}")

    def create_pod_session(
        self,
        pod_name: str,
        namespace: str = 'default',
        container: Optional[str] = None,
        shell: str = '/bin/bash'
    ) -> PodSession:
        """
        ポッドへの新しいセッションを作成

        Args:
            pod_name: ポッド名
            namespace: 名前空間
            container: コンテナ名（省略時は最初のコンテナ）
            shell: 使用するシェル

        Returns:
            PodSession: ポッドセッション
        """
        try:
            # oc execコマンドの構築
            exec_command = f"oc exec -n {namespace} {pod_name}"
            if container:
                exec_command += f" -c {container}"
            exec_command += f" -it -- {shell}"

            # インタラクティブセッションの作成
            channel = self.client.get_transport().open_session()
            channel.get_pty()
            channel.exec_command(exec_command)

            # 新しいセッションの作成と保存
            session = PodSession(channel)
            self.pod_sessions[pod_name] = session

            # プロンプトが表示されるまで待機
            stdout, _ = session._read_output(timeout=5.0)
            
            return session

        except Exception as e:
            raise Exception(f"Failed to create pod session: {str(e)}")

    def get_session(self, pod_name: str) -> Optional[PodSession]:
        """
        既存のポッドセッションを取得

        Args:
            pod_name: ポッド名

        Returns:
            Optional[PodSession]: 存在する場合はセッション、存在しない場合はNone
        """
        return self.pod_sessions.get(pod_name)

    def close_session(self, pod_name: str):
        """
        特定のポッドセッションを終了

        Args:
            pod_name: ポッド名
        """
        session = self.pod_sessions.get(pod_name)
        if session:
            session.close()
            del self.pod_sessions[pod_name]

    def close_all(self):
        """全ての接続を終了"""
        for session in self.pod_sessions.values():
            session.close()
        self.pod_sessions.clear()
        self.client.close()


# 使用例
def usage_examples():
    try:
        # 踏み台サーバへの接続
        client = FlexiblePodClient()
        client.connect(
            hostname="192.168.1.1",
            username="user",
            password="password"
        )

        # 複数のポッドへの接続
        pod1_session = client.create_pod_session(
            pod_name="my-pod-1",
            namespace="my-namespace",
            container="main-container"
        )
        
        pod2_session = client.create_pod_session(
            pod_name="my-pod-2",
            namespace="my-namespace"
        )

        # 個別のポッドでコマンド実行
        out1, err1 = pod1_session.send_command("ps aux")
        print(f"Pod 1 processes:\n{out1}")

        out2, err2 = pod2_session.send_command("df -h")
        print(f"Pod 2 disk usage:\n{out2}")

        # 特定のセッションを取得して操作
        session = client.get_session("my-pod-1")
        if session:
            out, err = session.send_command("ls -la")
            print(f"Pod 1 files:\n{out}")

        # 個別のセッション終了
        client.close_session("my-pod-1")

    except Exception as e:
        print(f"Error: {str(e)}")
    
    finally:
        # 全ての接続を終了
        client.close_all()

if __name__ == "__main__":
    usage_examples()
