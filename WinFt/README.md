# ファイル転送スクリプト

- WindowsPC、SSHサーバ（Linux）、S3ストレージ間でファイルを転送する。

## 概要

以下の3つのノード間でファイルを転送する

1. WindowsPC
1. SSHサーバ
1. S3ストレージ

  ```text
  ┌─────────────┐      1. Get        ┌─────────────┐
  │             │ <───────────────── │             │
  │  WindowsPC  │ ─────────────────> │  SSH Server │
  │             │      2. Put        │             │
  │             │                    └─────────────┘
  │             │      3. Get        ┌─────────────┐
  │             │ <───────────────── │             │
  │             │ ─────────────────> │ S3 Storage  │
  │             │      4. Put        │             │
  └─────────────┘                    └─────────────┘
  ```

このスクリプトは、以下のファイル転送操作を実行できる

1. WindowsPC ← SSHサーバ （Get）
1. WindowsPC → SSHサーバ （Put）
1. WindowsPC ← S3ストレージ （Get）
1. WindowsPC → S3ストレージ （Put）
1. SSHサーバ → S3ストレージ （1. & 4.）
1. S3ストレージ → SSHサーバ （3. & 2.）

## 動作環境

- Windows10/11
- WinSCP
- AWS CLI

## 実行方法

1. アプリルートに `.env` ファイルを作成する

  ```text
  AppRoot/
    ├── src/
    ├── bin/
    └── .env
  ```

  ```text
  # .env
  [local]
  WINSCP_PATH=
  LOCAL_DIR=
  
  [SSH Server]
  SSH_SERVER_IP=
  SSH_SERVER_ACCOUNT=
  SSH_SERVER_PASSWORD=
  
  [S3]
  BUCKET_NAME=
  OBJECT_PATH=
  REGION=
  PROFILE=
  ```

1. PowerShellのコンソール画面から実行する

  ```PowerShell
  # アプリルートから実行する場合
  AppRoot> powershell -ExecutionPolicy ByPass .\src\SvToS3.ps1 "*" 
  ```

## 参考URL

[Windows commands \| Microsoft Learn](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)

[WinSCP: Scripting and Task Automation](https://winscp.net/eng/docs/scripting)

[s3 — AWS CLI 1\.34\.31 Command Reference](https://docs.aws.amazon.com/cli/latest/reference/s3/)
