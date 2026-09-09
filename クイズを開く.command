#!/bin/sh
# ダブルクリックするとローカルサーバーが起動し、ブラウザでクイズが開く。
# 終わるときは、開いたターミナルのウィンドウで Ctrl+C を押すか、ウィンドウを閉じる。
cd "$(dirname "$0")" || exit 1
python3 serve.py 8765 &
SRV=$!
sleep 1
open "http://localhost:8765"
wait $SRV
