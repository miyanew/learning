import paramiko
from io import StringIO
from typing import Optional, Tuple, Union
from paramiko.sftp_client import SFTPClient

class FlexibleSFTPClient:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.sftp: Optional[SFTPClient] = None

    def connect(
        self,
        hostname: str,
        username: str,
        password: Optional[str] = None,
        key_path: Optional[str] = None,
        port: int = 22,
        via_client: Optional[paramiko.SSHClient] = None,
        remote_key_path: bool = False
    ) -> SFTPClient:
        """
        柔軟なSSH/SFTP接続を確立する

        Args:
            hostname: 接続先ホスト名またはIP
            username: ユーザー名
            password: パスワード（パスワード認証の場合）
            key_path: 秘密鍵のパス（公開鍵認証の場合）
            port: ポート番号（デフォルト: 22）
            via_client: 経由する既存のSSHクライアント（多段接続の場合）
            remote_key_path: key_pathが経由サーバ上のパスかどうか

        Returns:
            paramiko.sftp_client.SFTPClient: 確立された接続

        Raises:
            Exception: 接続に失敗した場合
        """
        try:
            sock = None
            if via_client:
                transport = via_client.get_transport()
                dest_addr = (hostname, port)
                local_addr = ('localhost', 0)
                sock = transport.open_channel("direct-tcpip", dest_addr, local_addr)

            connect_kwargs = {
                'hostname': hostname,
                'username': username,
                'port': port,
                'sock': sock
            }

            if key_path:
                if via_client and remote_key_path:
                    key = self._get_remote_key(via_client, key_path)
                else:
                    key = paramiko.RSAKey.from_private_key_file(key_path)
                connect_kwargs['pkey'] = key
            elif password:
                connect_kwargs['password'] = password
            else:
                raise ValueError("Either password or key_path must be provided")

            self.client.connect(**connect_kwargs)
            self.sftp = self.client.open_sftp()
            return self.sftp

        except Exception as e:
            raise Exception(f"Failed to establish SSH/SFTP connection: {str(e)}")

    def _get_remote_key(
        self,
        via_client: paramiko.SSHClient,
        key_path: str
    ) -> paramiko.RSAKey:
        """経由サーバから秘密鍵を読み取る"""
        sftp = via_client.open_sftp()
        try:
            with sftp.file(key_path, 'r') as remote_file:
                private_key_content = remote_file.read().decode()
            return paramiko.RSAKey.from_private_key(StringIO(private_key_content))
        finally:
            sftp.close()

    def send_command(
        self,
        command: str,
        timeout: int = 30,
        get_pty: bool = False
    ) -> Tuple[str, str]:
        """
        コマンドを実行し、その出力を返す

        Args:
            command: 実行するコマンド
            timeout: コマンドのタイムアウト時間（秒）
            get_pty: 擬似端末を割り当てるかどうか

        Returns:
            Tuple[str, str]: (標準出力, 標準エラー出力)
        """
        try:
            stdin, stdout, stderr = self.client.exec_command(
                command,
                timeout=timeout,
                get_pty=get_pty
            )
            
            out = stdout.read().decode('utf-8').strip()
            err = stderr.read().decode('utf-8').strip()
            
            return out, err
        except Exception as e:
            raise Exception(f"Command execution failed: {str(e)}")

    def get(
        self,
        remotepath: str,
        localpath: str
    ) -> None:
        """
        リモートファイルをローカルにダウンロードする

        Args:
            remotepath: リモートファイルパス
            localpath: ローカルファイルパス
        """
        if not self.sftp:
            raise Exception("SFTP connection not established")
        self.sftp.get(remotepath, localpath)

    def put(
        self,
        localpath: str,
        remotepath: str
    ) -> None:
        """
        ローカルファイルをリモートにアップロードする

        Args:
            localpath: ローカルファイルパス
            remotepath: リモートファイルパス
        """
        if not self.sftp:
            raise Exception("SFTP connection not established")
        self.sftp.put(localpath, remotepath)

    def listdir(
        self,
        path: str = '.'
    ) -> list:
        """
        指定されたディレクトリの内容をリストアップする

        Args:
            path: リモートディレクトリパス

        Returns:
            list: ファイルとディレクトリのリスト
        """
        if not self.sftp:
            raise Exception("SFTP connection not established")
        return self.sftp.listdir(path)

    def close(self):
        """接続を終了する"""
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()


# 使用例
def usage_examples():
    try:
        # 最初のホップ
        first_hop = FlexibleSFTPClient()
        first_sftp = first_hop.connect(
            hostname="192.168.1.1",
            username="pi",
            password="pi"
        )

        # 2番目のホップ
        second_hop = FlexibleSFTPClient()
        second_sftp = second_hop.connect(
            hostname="192.168.1.2",
            username="pi",
            key_path="/home/pi/.ssh/id_rsa",
            via_client=first_hop.client,
            remote_key_path=True
        )

        # コマンド実行例
        out1, err1 = first_hop.send_command("uname -a")
        print("First hop output:", out1)
        if err1:
            print("First hop error:", err1)

        # ファイル転送例
        second_hop.put("local_file.txt", "/remote/path/file.txt")
        files = second_hop.listdir("/remote/path")
        print("Remote files:", files)
        second_hop.get("/remote/path/result.txt", "downloaded_file.txt")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    
    finally:
        # 接続のクローズ
        second_hop.close()
        first_hop.close()

if __name__ == "__main__":
    usage_examples()
