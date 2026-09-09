"""
クイズをローカルサイトとして開くための簡易サーバー。

使い方(ターミナル):
    python3 serve.py
    → ブラウザで http://localhost:8765 を開く

同じWi-Fiにいるスマホから遊ぶ場合は、起動時に表示される
「スマホから」のURLをスマホのブラウザに入力する。

クイズ画面から送られた「問題の報告」は reports.jsonl に1行ずつ追記される。
(サーバーを使わず index.html を直接開いた場合は、報告はブラウザ内にだけ保存される)
"""
import http.server
import json
import os
import socket
import socketserver
import sys

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
ROOT = os.path.dirname(os.path.abspath(__file__))
REPORT_FILE = os.path.join(ROOT, "reports.jsonl")

# python3 -m http.server は起動時に getcwd() を呼ぶため環境によっては落ちる。
# ここでは先に chdir してから起動することで、その問題を避けている。
os.chdir(ROOT)


class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # データ更新がすぐ反映されるようキャッシュを切る
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass  # アクセスログは出さない

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path.rstrip("/") != "/report":
            self.send_error(404)
            return
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n > 200_000:
                self._json(413, {"ok": False, "error": "too large"})
                return
            rec = json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception as e:
            self._json(400, {"ok": False, "error": str(e)})
            return
        try:
            with open(REPORT_FILE, "a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        except Exception as e:
            self._json(500, {"ok": False, "error": str(e)})
            return
        print(f"報告を受け付けました → {os.path.basename(REPORT_FILE)}"
              f"（{rec.get('kind','')}／{rec.get('question','')[:40]}）")
        self._json(200, {"ok": True})

    def do_GET(self):
        if self.path.rstrip("/") == "/reports":
            rows = []
            if os.path.exists(REPORT_FILE):
                with open(REPORT_FILE, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                rows.append(json.loads(line))
                            except Exception:
                                pass
            self._json(200, rows)
            return
        super().do_GET()


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


class Server(socketserver.TCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with Server(("", PORT), Handler) as httpd:
        print(f"坂道クイズを起動しました  →  http://localhost:{PORT}")
        ip = local_ip()
        if ip:
            print(f"スマホから(同じWi-Fi)      →  http://{ip}:{PORT}")
        print("終了する時は Ctrl+C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n終了しました")
