
## 概要

数GBサイズのファイル出力をともなうWSL環境のスナップショット取得と環境構築をまとめて実行する。

[WSL の基本的なコマンド](https://learn.microsoft.com/ja-jp/windows/wsl/basic-commands#export-a-distribution)より

- wsl --export (エクスポートするWSL環境名) (スナップショット名)
- wsl --import (新WSL環境名) (インストール先ディレクトリ) (スナップショット名)

## 実行方法

ProjectRoot> powershell -ExecutionPolicy ByPass .\src\WslClone.ps1 **コピー元の環境名** **コピー先の環境名**

`wsl -l -v` で環境名を確認できる。

## ディレクトリ構成

```
ProjectRoot/
  ├── src/
  │   └── WslClone.ps1
  ├── bin/
  │   └── WslClone.cmd
  ├── snapshot/
  ├── distribution/
  └── README.md
```

## 参考URL

[クラスについて \- PowerShell \| Microsoft Learn](https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.core/about/about_classes?view=powershell-7.4)

[自動変数について \- PowerShell \| Microsoft Learn](https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.core/about/about_automatic_variables?view=powershell-7.4#psscriptroot)
