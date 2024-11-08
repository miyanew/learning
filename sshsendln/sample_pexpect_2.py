#!/usr/bin/env python3
import sys
from typing import Tuple

import pexpect


def ssh_command(host: str, user: str, password: str, command: str) -> Tuple[int, str]:
    """
    SSHでRaspberry Piに接続してコマンドを実行する

    Args:
        host: ホスト名またはIPアドレス
        user: SSHユーザー名
        password: SSHパスワード
        command: 実行するコマンド

    Returns:
        Tuple[int, str]: 終了コードと実行結果
    """

    # SSH接続文字列の作成
    ssh_newkey = "Are you sure you want to continue connecting"
    ssh_command = f"ssh {user}@{host}"

    # SSH接続の開始
    child = pexpect.spawn(ssh_command)
    child.timeout = 10  # タイムアウトを10秒に設定

    try:
        i = child.expect([pexpect.TIMEOUT, ssh_newkey, "[P|p]assword: "])

        if i == 0:  # Timeout
            return -1, "SSH接続がタイムアウトしました"

        if i == 1:  # SSH key warning
            child.sendline("yes")
            i = child.expect([pexpect.TIMEOUT, "[P|p]assword: "])
            if i == 0:
                return -1, "SSHキーの承認後にタイムアウトしました"

        # パスワードの送信
        child.sendline(password)

        # # バナーメッセージをスキップしてプロンプトを待機
        # # 複数のパターンを指定して、どれかにマッチするまで待機
        # i = child.expect([
        #     pexpect.TIMEOUT,
        #     'Last login:.*\r\n',  # ログインメッセージ
        #     '\r\n$',              # プロンプト
        #     '~\$'                 # ホームディレクトリのプロンプト
        # ])

        i = child.expect([pexpect.TIMEOUT, "pi@raspberrypi:.*\$"])
        if i == 0:
            return -1, "コマンド実行がタイムアウトしました"

        # コマンドの実行
        child.sendline(command)

        # コマンド自体のエコーバックをスキップ
        child.expect(command + "\r\n")

        # コマンドの実行結果を取得
        # プロンプトが表示されるまでの出力を取得
        i = child.expect([pexpect.TIMEOUT, "pi@raspberrypi:.*\$"])
        if i == 0:
            return -1, "コマンド実行がタイムアウトしました"

        # 実行結果の取得とクリーンアップ
        result = child.before.decode("utf-8")
        # 余分な改行を削除
        result = result.strip()

        # 接続のクローズ
        child.sendline("exit")
        child.close()

        return 0, result

    except pexpect.EOF:
        return -1, "SSH接続が予期せず終了しました"
    except pexpect.TIMEOUT:
        return -1, "コマンド実行中にタイムアウトしました"
    except Exception as e:
        return -1, f"エラーが発生しました: {str(e)}"


def main():
    # 接続情報の設定
    HOST = "192.168.1.1"  # Raspberry PiのIPアドレス
    USER = "pi"  # SSHユーザー名
    PASSWORD = "pi"  # SSHパスワード
    COMMAND = "ls -la"  # 実行するコマンド

    # コマンドの実行
    exit_code, output = ssh_command(HOST, USER, PASSWORD, COMMAND)

    if exit_code == 0:
        print("コマンド実行結果:")
        print(output)
    else:
        print(f"エラー: {output}")


if __name__ == "__main__":
    main()
