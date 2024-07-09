#!/bin/bash

# 引数がない場合はエラーメッセージを表示して終了
if [ $# -eq 0 ]; then
    echo "使用方法: $0 <Pythonファイル1> [<Pythonファイル2> ...]"
    exit 1
fi

# 各引数（Pythonファイル）に対してチェックを実行
for file in "$@"; do
    if [ -f "$file" ]; then
        echo "Checking $file..."
        echo "== isort --diff =="
        isort "$file" --diff

        echo "== flake8 =="
        flake8 "$file"

        echo "== black --diff =="
        black "$file" --diff
        echo "------------------------"
    else
        echo "エラー: $file は存在しないか、通常のファイルではありません。"
    fi
done
