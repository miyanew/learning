import paramiko
from io import StringIO
from typing import Optional, Tuple, Union
# import os

class FlexibleSSHClient:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def connect(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22,
        via_client: Optional[paramiko.SSHClient] = None,
        remote_key_path: bool = False
    ) -> paramiko.SSHClient:
        """
        柔軟なSSH接続を確立する

        Args:
            hostname: 接続先ホスト名またはIP
            username: ユーザー名
            password: パスワード（パスワード認証の場合）
            key_path: 秘密鍵のパス（公開鍵認証の場合）
            port: ポート番号（デフォルト: 22）
            via_client: 経由する既存のSSHクライアント（多段接続の場合）
            remote_key_path: key_pathが経由サーバ上のパスかどうか

        Returns:
            paramiko.SSHClient: 確立された接続

        Raises:
            Exception: 接続に失敗した場合
        """
        try:
            # 多段接続の場合のチャンネル設定
            sock = None
            if via_client:
                transport = via_client.get_transport()
                dest_addr = (hostname, port)
                local_addr = ('localhost', 0)
                sock = transport.open_channel("direct-tcpip", dest_addr, local_addr)

            # 認証情報の準備
            connect_kwargs = {
                'hostname': hostname,
                'username': username,
                'port': port,
                'sock': sock
            }

            # 公開鍵認証の処理
            if key_path:
                if via_client and remote_key_path:
                    # 経由サーバから秘密鍵を読み取る
                    key = self._get_remote_key(via_client, key_path)
                else:
                    # ローカルの秘密鍵を読み取る
                    key = paramiko.RSAKey.from_private_key_file(key_path)
                connect_kwargs['pkey'] = key
            elif password:
                # パスワード認証
                connect_kwargs['password'] = password
            else:
                raise ValueError("Either password or key_path must be provided")

            # 接続の確立
            self.client.connect(**connect_kwargs)
            return self.client

        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {str(e)}")

    def _get_remote_key(
        self,
        via_client: paramiko.SSHClient,
        key_path: str
    ) -> paramiko.RSAKey:
        """
        経由サーバから秘密鍵を読み取る

        Args:
            via_client: 経由サーバのSSHクライアント
            key_path: 経由サーバ上の秘密鍵パス

        Returns:
            paramiko.RSAKey: 秘密鍵オブジェクト
        """
        # expanded_key_path = os.path.expanduser(key_path)
        stdin, stdout, stderr = via_client.exec_command(f"cat {key_path}")
        private_key_content = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            raise Exception(f"Failed to read private key from remote host: {error}")

        return paramiko.RSAKey.from_private_key(StringIO(private_key_content))

    def exec_command(
        self,
        command: str
    ) -> Tuple[paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile]:
        """
        コマンドを実行する

        Args:
            command: 実行するコマンド

        Returns:
            Tuple[stdin, stdout, stderr]
        """
        return self.client.exec_command(command)

    def close(self):
        """接続を終了する"""
        self.client.close()


# 使用例
def usage_examples():
    # # 単純なパスワード認証の例
    # ssh1 = FlexibleSSHClient()
    # ssh1.connect(
    #     hostname="192.168.1.100",
    #     username="user1",
    #     password="password123"
    # )

    # # ローカルの秘密鍵を使用した公開鍵認証の例
    # ssh2 = FlexibleSSHClient()
    # ssh2.connect(
    #     hostname="192.168.1.101",
    #     username="user2",
    #     key_path="/home/pi/.ssh/id_rsa"
    # )

    # 多段接続でリモートの秘密鍵を使用する例
    first_hop = FlexibleSSHClient()
    first_client = first_hop.connect(
        hostname="192.168.1.1",
        username="pi",
        password="pi"
    )

    second_hop = FlexibleSSHClient()
    second_client = second_hop.connect(
        hostname="192.168.1.2",
        username="pi",
        key_path="/home/pi/.ssh/id_rsa",
        via_client=first_client,
        remote_key_path=True
    )

    # コマンド実行例
    stdin, stdout, stderr = first_hop.exec_command("uname -n;which scp")
    print(stdout.read().decode())

    stdin, stdout, stderr = second_hop.exec_command("uname -n;which scp")
    print(stdout.read().decode())

    # # 接続のクリーンアップ
    second_hop.close()
    first_hop.close()

if __name__ == "__main__":
    usage_examples()
