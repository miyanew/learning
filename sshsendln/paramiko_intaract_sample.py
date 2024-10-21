import paramiko
from io import StringIO
from typing import Optional, Tuple, Union, Dict
import select
import re
import time

class InteractiveSSHClient:
    def __init__(self, prompt_pattern: str = r'[\$#>] *$'):
        """
        Args:
            prompt_pattern: プロンプトを検出する正規表現パターン
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.prompt_pattern = prompt_pattern
        self.channel: Optional[paramiko.Channel] = None
        self.buffer = ""
        
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
        SSHの接続を確立する
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
            return self.client

        except Exception as e:
            raise Exception(f"Failed to establish SSH connection: {str(e)}")

    def _get_remote_key(
        self,
        via_client: paramiko.SSHClient,
        key_path: str
    ) -> paramiko.RSAKey:
        """経由サーバから秘密鍵を読み取る"""
        stdin, stdout, stderr = via_client.exec_command(f"cat {key_path}")
        private_key_content = stdout.read().decode()
        error = stderr.read().decode()

        if error:
            raise Exception(f"Failed to read private key from remote host: {error}")

        return paramiko.RSAKey.from_private_key(StringIO(private_key_content))

    def get_interactive_shell(
        self,
        terminal_type: str = 'vt100',
        width: int = 80,
        height: int = 24,
        timeout: float = 30
    ) -> paramiko.Channel:
        """
        インタラクティブシェルを取得する

        Args:
            terminal_type: 端末タイプ
            width: 端末の幅
            height: 端末の高さ
            timeout: タイムアウト時間（秒）

        Returns:
            paramiko.Channel: シェルチャンネル
        """
        try:
            self.channel = self.client.invoke_shell(
                term=terminal_type,
                width=width,
                height=height
            )
            self.channel.settimeout(timeout)
            
            # 初期プロンプトを待機
            self._wait_for_prompt(timeout)
            return self.channel

        except Exception as e:
            raise Exception(f"Failed to get interactive shell: {str(e)}")

    def _wait_for_prompt(self, timeout: float = 30) -> str:
        """
        プロンプトが表示されるまで待機

        Args:
            timeout: タイムアウト時間（秒）

        Returns:
            str: 受信したデータ
        """
        if not self.channel:
            raise Exception("No active channel")

        start_time = time.time()
        while True:
            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for prompt")

            if self.channel.recv_ready():
                chunk = self.channel.recv(4096).decode('utf-8', errors='ignore')
                self.buffer += chunk

                # プロンプトを検出
                if re.search(self.prompt_pattern, self.buffer.split('\n')[-1].strip()):
                    output = self.buffer
                    self.buffer = ""
                    return output

            time.sleep(0.1)

    def send_command(
        self,
        command: str,
        timeout: float = 30,
        expect_string: Optional[str] = None
    ) -> str:
        """
        コマンドを送信し、結果を取得

        Args:
            command: 実行するコマンド
            timeout: タイムアウト時間（秒）
            expect_string: 待機する文字列（指定時はプロンプトの代わりに使用）

        Returns:
            str: コマンドの出力
        """
        if not self.channel:
            raise Exception("No active channel")

        # コマンドの送信
        self.channel.send(command + '\n')
        
        # 出力の取得
        if expect_string:
            pattern = expect_string
            self.buffer = ""
            start_time = time.time()
            
            while True:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Timeout waiting for expected string")

                if self.channel.recv_ready():
                    chunk = self.channel.recv(4096).decode('utf-8', errors='ignore')
                    self.buffer += chunk
                    
                    if expect_string in self.buffer:
                        output = self.buffer
                        self.buffer = ""
                        return output

                time.sleep(0.1)
        else:
            return self._wait_for_prompt(timeout)

    def close(self):
        """接続を終了"""
        if self.channel:
            self.channel.close()
        self.client.close()


# 使用例
def usage_examples():
    try:
        # 最初のホップ
        first_hop = InteractiveSSHClient()
        first_client = first_hop.connect(
            hostname="192.168.1.1",
            username="pi",
            password="pi"
        )
        first_shell = first_hop.get_interactive_shell()

        # 基本的なコマンド実行
        output = first_hop.send_command("ls -la")
        print("First hop ls output:", output)

        # expectパターンを使用したコマンド実行
        output = first_hop.send_command("sudo su -", expect_string="Password:")
        print("Sudo prompt:", output)
        
        # パスワード入力
        output = first_hop.send_command("pi")
        print("After sudo:", output)

        # 2番目のホップ
        second_hop = InteractiveSSHClient()
        second_client = second_hop.connect(
            hostname="192.168.1.2",
            username="pi",
            key_path="/home/pi/.ssh/id_rsa",
            via_client=first_client,
            remote_key_path=True
        )
        second_shell = second_hop.get_interactive_shell()

        # 2番目のホップでコマンド実行
        output = second_hop.send_command("whoami")
        print("Second hop user:", output)

        # OCコマンドの実行例
        output = second_hop.send_command("oc login -u admin -p admin")
        print("OC login result:", output)

        output = second_hop.send_command(
            "oc exec -it my-pod -- /bin/bash",
            expect_string="#"
        )
        print("Pod shell:", output)

        # ポッド内でコマンド実行
        output = second_hop.send_command("ps aux")
        print("Pod processes:", output)

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    
    finally:
        # 接続のクリーンアップ
        second_hop.close()
        first_hop.close()

if __name__ == "__main__":
    usage_examples()