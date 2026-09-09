"""
index.html と quiz_data.js を1ファイルにまとめて、
Claude Artifact(ネット上に置ける形)用の artifact.html を作る。

    python3 build_artifact.py

Artifact は1ファイルしか置けないため、
・quiz_data.js を中に埋め込む
・別ファイルが必要な機能(ホーム画面用の設定・オフライン対応・アイコン)は外す
という変換をしている。ローカル版(index.html)はそのまま全機能が使える。
"""
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC_HTML = os.path.join(BASE, "index.html")
SRC_DATA = os.path.join(BASE, "quiz_data.js")
OUT = os.path.join(BASE, "artifact.html")

html = open(SRC_HTML, encoding="utf-8").read()
data = open(SRC_DATA, encoding="utf-8").read()

# 1. <title> より前(doctype・html・head開始・viewport)を落とす
html = html[html.index("<title>"):]

# 2. 別ファイルが要る指定を外す(Artifactには置けないため)
html = re.sub(r'<!-- ホーム画面に追加してアプリのように使うための設定 -->\s*', "", html)
for pat in [r'<link rel="manifest"[^>]*>\s*',
            r'<link rel="apple-touch-icon"[^>]*>\s*',
            r'<meta name="apple-mobile-web-app-[^>]*>\s*',
            r'<meta name="mobile-web-app-capable"[^>]*>\s*']:
    html = re.sub(pat, "", html)

# 3. head/body のタグを外す(Artifact側が用意してくれるため)
for tag in ["</head>", "<body>", "</body>", "</html>"]:
    html = html.replace(tag, "")

# 4. quiz_data.js を埋め込む
marker = '<script src="quiz_data.js"></script>'
assert marker in html, "quiz_data.js の読み込み行が見つかりません"
html = html.replace(marker, "<script>\n" + data + "</script>")

# 5. オフライン対応(sw.js)の登録を外す。ファイルを置けないため。
html = re.sub(
    r'/\* オフラインでも遊べるようにする.*?\n\}\n',
    "/* オフライン対応(sw.js)はローカル版のみ。Artifactでは1ファイルしか置けないため外している */\n",
    html, flags=re.S)

# 6. iPhone向けの案内文を、Artifact版の実態に合わせる
html = html.replace(
    "<b>ホーム画面に追加すると、アプリのように使えます</b><br>\n       下の共有ボタン <b>⬆︎</b> →「ホーム画面に追加」",
    "<b>ホーム画面に追加できます</b><br>\n       下の共有ボタン <b>⬆︎</b> →「ホーム画面に追加」")

open(OUT, "w", encoding="utf-8").write(html.strip() + "\n")

size = os.path.getsize(OUT)
print(f"saved: {OUT}  ({size/1024:.0f} KB)")
assert "<html" not in html and "<head>" not in html, "head/htmlタグが残っています"
assert "window.QUIZ_DATA" in html, "データが埋め込まれていません"
assert 'src="quiz_data.js"' not in html, "外部読み込みが残っています"
print("チェックOK: 単体で動く1ファイルになっています")
