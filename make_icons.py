"""
ホーム画面用のアプリアイコンを作る。
背景は紺→梅色のグラデーション、まわりに8グループの色の点を並べ、中央に「坂」。

    python3 make_icons.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = os.path.join(BASE, "icons")
os.makedirs(ICON_DIR, exist_ok=True)

# 8グループの色(Excel・アプリと同じ)
GROUP_COLORS = ["#7030A0", "#548235", "#F4B6C2", "#A9D18E",
                "#9DC3E6", "#F0537D", "#7FD9B0", "#FFD966"]

JP_FONT = "/System/Library/Fonts/Hiragino Sans GB.ttc"

def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def make(size):
    # 大きめに描いてから縮小する(輪郭をなめらかにするため)
    S = size * 4
    img = Image.new("RGB", (S, S), (38, 49, 79))
    d = ImageDraw.Draw(img)

    # 斜めのグラデーション(紺 → 紫 → 梅色)
    # 小さい画像で1ピクセルずつ作ってから拡大すると、境目のないなめらかな傾斜になる
    c1, c2, c3 = (38, 49, 79), (58, 45, 68), (200, 110, 140)
    N = 64
    grad = Image.new("RGB", (N, N))
    px = grad.load()
    for y in range(N):
        for x in range(N):
            t = (x + y) / (2 * (N - 1))          # 左上=0, 右下=1
            if t < 0.6:
                u, a, b = t / 0.6, c1, c2
            else:
                u, a, b = (t - 0.6) / 0.4, c2, c3
            px[x, y] = tuple(int(a[k] + (b[k] - a[k]) * u) for k in range(3))
    img = grad.resize((S, S), Image.BICUBIC)
    d = ImageDraw.Draw(img)

    # 中央に「坂」
    try:
        font = ImageFont.truetype(JP_FONT, int(S * 0.46), index=1)  # index1 = W6(太め)
    except Exception:
        font = ImageFont.truetype(JP_FONT, int(S * 0.46))
    text = "坂"
    box = d.textbbox((0, 0), text, font=font)
    d.text((S/2 - (box[0] + box[2]) / 2, S/2 - (box[1] + box[3]) / 2 - S * 0.045),
           text, font=font, fill=(255, 255, 255))

    # 下部に8グループの色の点を並べる
    n = len(GROUP_COLORS)
    r = S * 0.032
    gap = S * 0.019
    total = n * (r * 2) + (n - 1) * gap
    x = S / 2 - total / 2 + r
    y = S * 0.80
    for c in GROUP_COLORS:
        d.ellipse([x - r, y - r, x + r, y + r], fill=hex2rgb(c))
        x += r * 2 + gap

    return img.resize((size, size), Image.LANCZOS)


if __name__ == "__main__":
    for s in (180, 192, 512):
        p = os.path.join(ICON_DIR, f"icon-{s}.png")
        make(s).save(p)
        print("saved:", p)
