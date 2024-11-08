import pexpect


def ssh_ls_command(
    hostname: str, username: str, password: str, timeout: int = 30
) -> str:
    # SSHコマンドを実行する
    ssh_command = f"ssh {username}@{hostname}"

    # pexpect.spawnを使ってSSHセッションを開始
    session = pexpect.spawn(ssh_command, timeout=timeout)

    # "password:"のプロンプトが表示されたら、パスワードを送信
    session.expect("password: ")
    session.sendline(password)

    print(0)
    # print(f'hohoho1: {session.before.decode("utf-8")}', flush=True)

    # コマンドプロンプトが表示されるまで待機
    # session.expect([r"\$ ", "# "])
    session.expect([r"pi@raspberrypi:.*\$"])
    # session.expect([r"password:"], timeout=10)
    print(1)

    # lsコマンドを送信
    session.sendline("ls")
    print(f'2: {session.before.decode("utf-8")}')

    # lsコマンドの結果を受信
    session.expect([r"pi@raspberrypi:.*\$"])

    # session.beforeにはlsコマンドの出力が入っている
    result = session.before.decode("utf-8")

    # SSHセッションを終了
    session.sendline("exit")
    session.close()

    return result


if __name__ == "__main__":
    # 接続情報を設定
    hostname = "192.168.1.1"
    username = "pi"
    password = "pi"

    # lsコマンドを発行して、応答を取得
    response = ssh_ls_command(hostname, username, password)

    # 応答を表示
    print(response)
