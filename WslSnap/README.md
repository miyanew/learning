
## 概要

数GBサイズのファイル出力を伴うWSL環境のスナップショット取得と環境構築を簡略にした。

[WSL の基本的なコマンド](https://learn.microsoft.com/ja-jp/windows/wsl/basic-commands#export-a-distribution)より

- wsl --export (エクスポートするWSL環境名) (スナップショット名)
- wsl --import (新WSL環境名) (インストール先ディレクトリ) (スナップショット名)

## 実行方法

ProjectRoot> powershell -ExecutionPolicy ByPass .\src\WslClone.ps1 **コピー元の環境名** **コピー先の環境名**

`wsl -l -v` で環境名を確認できる。

## ディレクトリ構成

ProjectRoot/
  ├── src/
  │   └── WslClone.ps1
  ├── bin/
  │   └── WslClone.cmd
  ├── snapshot/
  ├── distribution/
  └── README.md
