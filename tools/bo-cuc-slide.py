#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh bộ KHUNG + MASK cho các bố cục "mặt / slide / cả hai" của bài giảng có slide.

Kết quả ghi vào do-hoa-chung/bo-cuc/:
  bo-cuc.json                  ← toạ độ ô [slot] từng bố cục (assemble.py đọc file này)
  <bo-cuc>-<theme>-khung.png   ← nền + bóng đổ (RGBA 1920x1080), phủ slide/mặt lên trên
  mask-<w>x<h>-r<r>.png        ← mask bo góc (ảnh xám) cho từng ô

Bố cục (khung ngang 1920x1080, thiết kế tối giản theo brand.json):
  mat        : mặt toàn khung (như dựng bài thường) - không cần khung
  slide      : slide toàn khung trên nền giấy, không có mặt (nội dung dày, sơ đồ, số liệu)
  ca-hai     : slide chính 1392x783 bên trái, mặt 4:5 nhỏ (~6% diện tích) góc dưới phải,
               dải dưới 903-1080 để trống cho pill/caption
  chia-doi   : mặt bên trái (816x900), slide bên phải (888x500) - slide đơn giản, cả hai đều rõ
  mat-chinh  : mặt toàn khung, slide là thẻ nhỏ 600x338 góc trên phải (từ khoá, ảnh, trích dẫn)

Chạy: python3 tools/bo-cuc-slide.py [--out do-hoa-chung/bo-cuc]
Chạy lại an toàn (ghi đè). Cần Pillow: pip install pillow --break-system-packages
"""
import argparse
import json
import os

# Thư viện Python cài riêng vào tools/pylib (tools/cai-dat.py lo việc này) - VM Cowork
# không giữ pip install qua các phiên, nên thư viện phải nằm trong thư mục xưởng.
import sys as _sys
_sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylib"))
from PIL import Image, ImageDraw, ImageFilter

W, H = 1920, 1080
PALETTE = {
    "light": {"bg": "#FAF7F1", "ink": "#23282D", "line": "#D8D2C6", "accent": "#2F5D50"},
    "dark": {"bg": "#15181C", "ink": "#F2EEE5", "line": "#3A3F45", "accent": "#C7A97B"},
}


def nap_palette_brand():
    """Ghi đè PALETTE bằng brand/brand.json (ở gốc xưởng) để khung slide cùng màu với đồ họa."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = os.path.join(root, "brand", "brand.json")
    if not os.path.isfile(p):
        return
    try:
        with open(p, encoding="utf-8") as f:
            pals = json.load(f).get("palettes") or {}
    except (OSError, ValueError):
        return
    for theme in ("light", "dark"):
        for k in ("bg", "ink", "line", "accent"):
            v = (pals.get(theme) or {}).get(k)
            if v:
                PALETTE[theme][k] = v


nap_palette_brand()

# Toạ độ ô. face_aspect = tỉ lệ w/h vùng crop khuôn mặt cho ô đó.
LAYOUTS = {
    "mat": {"mo_ta": "mặt toàn khung", "slide": None, "face": {"x": 0, "y": 0, "w": W, "h": H, "r": 0}},
    "slide": {"mo_ta": "slide toàn khung trên nền giấy", "slide": {"x": 0, "y": 0, "w": W, "h": H, "r": 0}, "face": None},
    "ca-hai": {
        "mo_ta": "slide chính + mặt nhỏ góc dưới phải",
        "slide": {"x": 96, "y": 120, "w": 1392, "h": 783, "r": 20},
        "face": {"x": 1504, "y": 463, "w": 352, "h": 440, "r": 20},
        "vung_trong": "dải y 903-1080 dành cho pill/caption",
    },
    "chia-doi": {
        "mo_ta": "mặt trái, slide phải, cân bằng",
        "slide": {"x": 960, "y": 290, "w": 888, "h": 500, "r": 20},
        "face": {"x": 72, "y": 90, "w": 816, "h": 900, "r": 24},
    },
    "mat-chinh": {
        "mo_ta": "mặt toàn khung, slide là thẻ nhỏ góc trên phải",
        "slide": {"x": 1248, "y": 72, "w": 600, "h": 338, "r": 16},
        "face": {"x": 0, "y": 0, "w": W, "h": H, "r": 0},
        "khung_trong_suot": True,
    },
}


def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, w - 1, h - 1], radius=r, fill=255)
    return m


def shadow_layer(slot, spread=28, offset=(0, 14), alpha=70):
    """Bóng đổ mềm quanh một ô (vẽ lên lớp RGBA toàn khung)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pad = spread * 3
    box = Image.new("L", (slot["w"] + 2 * pad, slot["h"] + 2 * pad), 0)
    ImageDraw.Draw(box).rounded_rectangle(
        [pad, pad, pad + slot["w"] - 1, pad + slot["h"] - 1], radius=slot["r"], fill=alpha)
    box = box.filter(ImageFilter.GaussianBlur(spread))
    sh = Image.new("RGBA", box.size, (0, 0, 0, 255))
    sh.putalpha(box)
    layer.alpha_composite(sh, (slot["x"] - pad + offset[0], slot["y"] - pad + offset[1]))
    return layer


def hairline(layer, slot, color):
    """Viền 1.5px rất mảnh quanh ô (giúp thẻ slide nổi trên nền video thật)."""
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([slot["x"] - 1, slot["y"] - 1, slot["x"] + slot["w"], slot["y"] + slot["h"]],
                        radius=slot["r"] + 1, outline=color, width=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join("do-hoa-chung", "bo-cuc"))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)

    masks = set()
    for name, lay in LAYOUTS.items():
        for key in ("slide", "face"):
            s = lay.get(key)
            if s and s["r"] > 0:
                masks.add((s["w"], s["h"], s["r"]))
        for theme, pal in PALETTE.items():
            if name in ("mat", "slide"):
                continue  # không cần khung: assemble tự pad nền bằng màu bg
            if lay.get("khung_trong_suot"):
                khung = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            else:
                khung = Image.new("RGBA", (W, H), pal["bg"])
            for key in ("slide", "face"):
                s = lay.get(key)
                if s and s["r"] > 0:
                    khung.alpha_composite(shadow_layer(s, alpha=90 if theme == "light" else 120))
            if lay.get("khung_trong_suot"):
                hairline(khung, lay["slide"], (255, 255, 255, 140))
            khung.save(os.path.join(args.out, f"{name}-{theme}-khung.png"))
    for w, h, r in sorted(masks):
        rounded_mask(w, h, r).save(os.path.join(args.out, f"mask-{w}x{h}-r{r}.png"))

    spec = {"_ghi_chu": "Toạ độ ô theo khung 1920x1080. assemble.py đọc file này; đổi bố cục thì sửa "
                        "tools/bo-cuc-slide.py rồi chạy lại để sinh khung/mask khớp.",
            "size": [W, H], "palette": PALETTE, "layouts": LAYOUTS}
    with open(os.path.join(args.out, "bo-cuc.json"), "w", encoding="utf-8") as f:
        json.dump(spec, f, ensure_ascii=False, indent=1)
    print(f"✓ {args.out}: {len(LAYOUTS)} bố cục, {len(masks)} mask, khung 2 theme")


if __name__ == "__main__":
    main()
