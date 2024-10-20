# めも

## パッケージ管理

- [Python でパッケージを開発して配布する標準的な方法 2023 年編](https://qiita.com/propella/items/5cd89caee6379920d889)

- [Pythonのパッケージ周りのベストプラクティスを理解する](https://www.m3tech.blog/entry/python-packaging)

- [2024-06-04 ばんくしさんによる「ゼロから作る自作 Python Package Manager 入門」がほんとよい！ 写経を積みます](https://nikkie-ftnext.hatenablog.com/entry/vaaaaanquish-python-package-manager-diy-introduction-is-awesome)
  - 2023-09-12 Pythonのパッケージ管理の中級者の壁を超える stapy#98
  - https://speakerdeck.com/vaaaaanquish/pythonnopatukeziguan-li-nozhong-ji-zhe-nobi-wochao-eru-stapy-number-98
  - PythonのPackage Managerを深く知るためのリンク集
  - https://gist.github.com/vaaaaanquish/1ad9639d77e3a5f0e9fb0e1f8134bc06
  - 2021-03-29 pipとpipenvとpoetryの技術的・歴史的背景とその展望
  - https://vaaaaaanquish.hatenablog.com/entry/2021/03/29/221715

## ProxyJump

- [多段 ssh するなら ProxyCommand じゃなくて ProxyJump を使おう](https://zenn.dev/kariya_mitsuru/articles/ed76b4b27ac0fc)
  - ssh_config(5) を熟読するといい?

- 設定例

``` text
~/.ssh/config
Host target-server
    HostName target.example.com
    ProxyJump jumphost.example.com
    User username
```
