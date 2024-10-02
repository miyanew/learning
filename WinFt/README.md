# ファイル転送スクリプト

- SSHサーバ、WindowsPC、S3ストレージ間でファイル転送を行う。

## 概要

以下の3つのノード間でファイルを転送する

1. SSHサーバ
1. WindowsPC
1. S3ストレージ

```
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

このスクリプトは、以下のファイル転送操作を実行できます

1. WindowsPC ← SSHサーバ （Get）
1. WindowsPC → SSHサーバ （Put）
1. WindowsPC ← S3ストレージ （Get）
1. WindowsPC → S3ストレージ （Put）
1. SSHサーバ → S3ストレージ （1. → 4.）
1. S3ストレージ → SSHサーバ （3. → 2.）

## 動作環境

- Windows10/11
- WinSCP
- AWS CLI

## 実行方法

1. envファイルを作成する

2. コンソール画面から実行する

```
ProjectRoot> powershell -ExecutionPolicy ByPass .\src\GetR.ps1 "*" 
```

## 参考URL

[Windows commands \| Microsoft Learn](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands)

[WinSCP: Scripting and Task Automation](https://winscp.net/eng/docs/scripting)

[s3 — AWS CLI 1\.34\.31 Command Reference](https://docs.aws.amazon.com/cli/latest/reference/s3/)
