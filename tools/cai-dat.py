#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CÀI ĐẶT XƯỞNG PHIM - một lệnh, chạy lại bao nhiêu lần cũng an toàn.

Cách dùng (từ bất kỳ đâu, script tự tìm gốc xưởng):
    python3 tools/cai-dat.py                 # làm tất cả các bước còn thiếu
    python3 tools/cai-dat.py --trang-thai    # chỉ xem bước nào xong, bước nào chưa
    python3 tools/cai-dat.py --model small   # model nhận dạng nhỏ hơn (nhanh, kém chính xác hơn)
    python3 tools/cai-dat.py --model khong   # bỏ qua model (không gỡ băng tại máy)
    python3 tools/cai-dat.py --khong-thu     # bỏ bước dựng thử cuối
    python3 tools/cai-dat.py --khong-loi     # bỏ hai model mốc lời của Bàn dựng (khoảng 450 MB)
    python3 tools/cai-dat.py --danh-dau gioi-thieu   # ghi dấu "đã giới thiệu xưởng cho người dùng" (Claude gọi sau buổi giới thiệu)
    python3 tools/cai-dat.py --dung-xuong --ten-xuong "<tên>" --tien-to <2-6 chữ> --ban-mau <mã commit>
                                             # cá nhân hoá xưởng vừa dựng từ bản thiết kế (DUNG-XUONG.md, bước 3)

Xưởng của người dùng được AI dựng từ BẢN THIẾT KẾ trên GitHub (DUNG-XUONG.md), không phải bản clone:
--dung-xuong bỏ các khối chỉ dành cho bản thiết kế (<!-- BAN-MAU --> ... <!-- /BAN-MAU -->), thay tên bản
thiết kế bằng tên xưởng của người dùng trong tài liệu và skill, tạo cau-hinh.json (kèm tiền tố skill
tienToSkill), README.md của xưởng, hai thư mục Du an/, Thanh pham/ cạnh xưởng, và ghi bản thiết kế đã dựng
từ (repo, commit, ngày) vào tools/.cai-dat.json để lần sau đối chiếu bản mới (HUONG-DAN.md mục Cập nhật xưởng).

Mỗi bước tự bỏ qua nếu đã xong. Bước tải model có thể cần chạy lại nhiều lần
(mỗi lần tải tiếp tối đa ~150 giây rồi thoát mã 2 = "chưa xong, chạy lại y nguyên").
Đây là cách để lệnh chạy an toàn trong môi trường giới hạn 180 giây mỗi lần gọi
(máy ảo Cowork). Trong Terminal thường thì cứ chạy lại tới khi thấy "✓ CÀI XONG".

Các bước:
  1. Kiểm công cụ hệ thống: ffmpeg/ffprobe (bắt buộc), python3, node (tuỳ chọn)
  2. Thư viện Python vào tools/pylib (numpy, scipy, sherpa-onnx, onnxruntime, pillow, python-pptx)
  3. Model nhận dạng giọng nói vào tools/models (silero VAD + Whisper), rồi hai model mốc lời cho
     Bàn dựng và Dựng bằng lời (zipformer tiếng Việt chép nguyên văn, omnilingual CTC căn mốc; Apache 2.0)
  4. Sinh khung/mask bố cục bài giảng có slide (do-hoa-chung/bo-cuc)
  5. Tạo thư mục thư viện (trong repo) và hai thư mục Du an/, Thanh pham/ cạnh repo (tools/cau_hinh.py)
  6. Dựng thử một dự án tổng hợp nhỏ qua cổng nghiệm thu (tools/kiem-tra-xuong.py)
"""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import time
import urllib.request

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
PYLIB = os.path.join(TOOLS, "pylib")
MODELS = os.path.join(TOOLS, "models")
TRANG_THAI = os.path.join(TOOLS, ".cai-dat.json")

# Nguồn model: GitHub releases chính thức của k2-fsa/sherpa-onnx (github thường được phép,
# huggingface hay bị chặn trong máy ảo). Kích cỡ để ước lượng tiến độ.
MODEL_URL = "https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/"
MODEL_INFO = {
    "turbo": {"tar": "sherpa-onnx-whisper-turbo.tar.bz2", "bytes": 563790207,
              "mo_ta": "large-v3-turbo int8 (~1GB sau khi giải nén) - mặc định, chính xác tốt, chạy ổn trên Apple Silicon"},
    "small": {"tar": "sherpa-onnx-whisper-small.tar.bz2", "bytes": 639387718,
              "mo_ta": "small (~370MB int8) - nhanh hơn, kém chính xác hơn với tiếng Việt"},
}
VAD_FILE = "silero_vad.onnx"

PIP_PACKAGES = [
    ("numpy", "numpy"),
    ("scipy", "scipy"),
    ("sherpa_onnx", "sherpa-onnx"),
    ("onnxruntime", "onnxruntime"),
    ("PIL", "pillow"),
    ("pptx", "python-pptx"),
]

NHOM_NHAC = ["thien-ambient", "piano-tinh-lang", "acoustic-am", "nang-luong-nhe", "rieng"]
NHOM_SFX = ["chuyen-canh", "chuong-thien", "nhan-do-hoa"]


# ------------------------------------------------------------------ tiện ích
def doc_trang_thai():
    if os.path.isfile(TRANG_THAI):
        try:
            with open(TRANG_THAI, encoding="utf-8") as f:
                return json.load(f)
        except ValueError:
            pass
    return {}


def ghi_trang_thai(tt):
    tt["cap_nhat"] = time.strftime("%Y-%m-%d %H:%M")
    with open(TRANG_THAI, "w", encoding="utf-8") as f:
        json.dump(tt, f, ensure_ascii=False, indent=1)


def sh(cmd, check=True, quiet=True):
    p = subprocess.run(cmd, capture_output=quiet, text=True)
    if check and p.returncode != 0:
        if quiet:
            print((p.stdout or "")[-1500:], (p.stderr or "")[-1500:])
        raise SystemExit(f"! Lệnh lỗi: {' '.join(cmd)}")
    return p


def ver(cmd):
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        return (p.stdout or p.stderr).splitlines()[0].strip()
    except (OSError, subprocess.TimeoutExpired, IndexError):
        return None


def buoc(n, msg):
    print(f"\n[{n}] {msg}", flush=True)


def ok(msg):
    print(f"  ✓ {msg}", flush=True)


def canh_bao(msg):
    print(f"  ⚠ {msg}", flush=True)


# ------------------------------------------------------------------ bước 1
def b1_cong_cu():
    buoc(1, "Kiểm công cụ hệ thống")
    ff = ver(["ffmpeg", "-version"])
    fp = ver(["ffprobe", "-version"])
    if not ff or not fp:
        print("  ✗ Thiếu ffmpeg/ffprobe - bắt buộc cho mọi việc cắt ghép.")
        print("    Máy ảo Cowork có sẵn ffmpeg; nếu chạy trong Terminal macOS: brew install ffmpeg;")
        print("    Ubuntu/Debian: sudo apt-get install -y ffmpeg")
        raise SystemExit(1)
    ok(ff)
    ok(f"python {platform.python_version()} ({sys.executable})")
    if sys.version_info < (3, 9):
        raise SystemExit("! Cần Python 3.9 trở lên")
    nd = ver(["node", "--version"])
    if nd:
        ok(f"node {nd} (render đồ họa Remotion tại đây được nếu có Chrome/Chromium)")
    else:
        canh_bao("không có node - đồ họa Remotion sẽ render ở sandbox đám mây của Claude (mặc định), không sao")
    for extra, dung_cho in (("soffice", "nhập slide PPTX"), ("pdftoppm", "nhập slide PDF"), ("fc-list", "phụ đề burn-in")):
        if shutil.which(extra):
            ok(f"{extra} có sẵn ({dung_cho})")
        else:
            canh_bao(f"không có {extra} ({dung_cho}) - bước đó sẽ chạy ở sandbox đám mây hoặc bỏ qua")
    return {"ffmpeg": ff, "python": platform.python_version(), "node": nd}


# ------------------------------------------------------------------ bước 2
def _import_tu_pylib(mod):
    code = (f"import sys; sys.path.insert(0, {PYLIB!r}); import {mod}; "
            f"print(getattr({mod}, '__version__', 'ok'))")
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    return p.stdout.strip() if p.returncode == 0 else None


def b2_thu_vien_python():
    buoc(2, f"Thư viện Python vào {os.path.relpath(PYLIB, ROOT)} (máy ảo không giữ pip install qua phiên, nên cài vào thư mục xưởng)")
    os.makedirs(PYLIB, exist_ok=True)
    thieu = []
    for mod, pkg in PIP_PACKAGES:
        v = _import_tu_pylib(mod)
        if v:
            ok(f"{pkg} {v}")
        else:
            thieu.append(pkg)
    if thieu:
        print(f"  → pip install --target pylib {' '.join(thieu)} (một lần, vài phút)", flush=True)
        p = subprocess.run([sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
                            "--upgrade", "--target", PYLIB] + thieu, text=True)
        if p.returncode != 0:
            canh_bao("pip lỗi (mạng bị chặn?). Thử lại sau, hoặc cài tay: "
                     f"python3 -m pip install --target '{PYLIB}' {' '.join(thieu)}")
        for mod, pkg in PIP_PACKAGES:
            if pkg in thieu:
                v = _import_tu_pylib(mod)
                if v:
                    ok(f"{pkg} {v}")
                else:
                    canh_bao(f"{pkg} vẫn chưa nạp được" + (" - gỡ băng tại máy sẽ không chạy" if pkg == "sherpa-onnx" else ""))
    return {p: bool(_import_tu_pylib(m)) for m, p in PIP_PACKAGES}


# ------------------------------------------------------------------ bước 3
def _tai_tiep(url, dst, tong_bytes, ngan_sach_giay):
    """Tải nối tiếp (resume) tới khi đủ hoặc hết ngân sách thời gian. Trả True nếu đủ."""
    co = os.path.getsize(dst) if os.path.isfile(dst) else 0
    if tong_bytes and co >= tong_bytes:
        return True
    het = time.time() + ngan_sach_giay
    if shutil.which("curl"):
        while time.time() < het:
            con = max(15, int(het - time.time()))
            subprocess.run(["curl", "-sL", "-C", "-", "--max-time", str(con), "-o", dst, url])
            co = os.path.getsize(dst) if os.path.isfile(dst) else 0
            if tong_bytes and co >= tong_bytes:
                return True
            if not tong_bytes and co > 0:
                return True
            print(f"    … {co / 1e6:.0f}/{(tong_bytes or 0) / 1e6:.0f} MB", flush=True)
        return False
    # Không có curl: dùng urllib với Range
    while time.time() < het:
        req = urllib.request.Request(url, headers={"Range": f"bytes={co}-"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r, open(dst, "ab") as f:
                t0 = time.time()
                while time.time() < het:
                    chunk = r.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
                    co += len(chunk)
                    if time.time() - t0 > 10:
                        print(f"    … {co / 1e6:.0f}/{(tong_bytes or 0) / 1e6:.0f} MB", flush=True)
                        t0 = time.time()
        except Exception as e:  # noqa: BLE001
            print(f"    (mạng: {e}) thử lại…", flush=True)
            time.sleep(3)
        if tong_bytes and co >= tong_bytes:
            return True
    return False


def b3_model(model, ngan_sach):
    buoc(3, "Model nhận dạng giọng nói (Whisper chạy tại máy, dữ liệu không rời máy)")
    os.makedirs(MODELS, exist_ok=True)
    if model == "khong":
        canh_bao("bỏ qua theo yêu cầu (--model khong): gỡ băng sẽ cần transcript do bạn cung cấp")
        return {"vad": False, "whisper": None}
    vad = os.path.join(MODELS, VAD_FILE)
    if not os.path.isfile(vad) or os.path.getsize(vad) < 600000:
        print("  → tải silero_vad.onnx (0.6 MB)", flush=True)
        if not _tai_tiep(MODEL_URL + VAD_FILE, vad, 643854, min(60, ngan_sach)):
            canh_bao("chưa tải được silero VAD - kiểm tra mạng rồi chạy lại")
            return {"vad": False, "whisper": None}
    ok("silero_vad.onnx")
    info = MODEL_INFO[model]
    d = os.path.join(MODELS, f"sherpa-onnx-whisper-{model}")
    marker = os.path.join(d, ".hoan-tat")
    if os.path.isfile(marker):
        ok(f"whisper-{model} đã có ({info['mo_ta']})")
        return {"vad": True, "whisper": model}
    tar_path = os.path.join(MODELS, info["tar"])
    t0 = time.time()
    co = os.path.getsize(tar_path) if os.path.isfile(tar_path) else 0
    if co < info["bytes"]:
        print(f"  → tải {info['tar']} ({info['bytes'] / 1e6:.0f} MB) - {info['mo_ta']}", flush=True)
        du = _tai_tiep(MODEL_URL + info["tar"], tar_path, info["bytes"], ngan_sach)
        if not du:
            co = os.path.getsize(tar_path) if os.path.isfile(tar_path) else 0
            print(f"\n⏳ Đã tải {co / 1e6:.0f}/{info['bytes'] / 1e6:.0f} MB. CHƯA XONG - chạy lại y nguyên lệnh này để tải tiếp.")
            print("   (Cách khác: tự tải file bằng trình duyệt từ\n   "
                  f"{MODEL_URL}{info['tar']}\n   rồi thả vào tools/models/ và chạy lại.)")
            raise SystemExit(2)
    # Giải nén cần ~45-90 giây liên tục (bz2 chậm). Nếu lần chạy này đã tốn quá nửa ngân sách
    # cho việc tải thì để lần sau giải nén, tránh bị ngắt giữa chừng trong môi trường 180 giây.
    con_lai = ngan_sach - (time.time() - t0)
    if con_lai < min(90, ngan_sach * 0.6):
        print("\n⏳ Đã tải xong, CHƯA giải nén - chạy lại y nguyên lệnh này để giải nén (khoảng 1 phút).")
        raise SystemExit(2)
    print("  → giải nén (chỉ lấy file int8 + tokens, bỏ bản fp32 cho nhẹ máy, ~1 phút)…", flush=True)
    os.makedirs(d, exist_ok=True)
    if shutil.which("tar"):
        # --overwrite: ghi đè bằng truncate (không unlink) - cần cho môi trường cấm xoá file
        p = subprocess.run(["tar", "-xjf", tar_path, "-C", d, "--strip-components=1", "--overwrite",
                            "--wildcards", "*int8*", "*tokens.txt"], capture_output=True, text=True)
        if p.returncode != 0:
            print((p.stderr or "")[-800:])
            print("\n⏳ Giải nén chưa xong hoặc bị ngắt - chạy lại y nguyên lệnh này.")
            raise SystemExit(2)
    else:
        with tarfile.open(tar_path, "r:bz2") as t:
            for m in t.getmembers():
                base = os.path.basename(m.name)
                if m.isfile() and (base.endswith("-tokens.txt") or ".int8." in base):
                    m.name = base
                    t.extract(m, d)
                    print(f"    {base}", flush=True)
    can = [f"{model}-encoder.int8.onnx", f"{model}-decoder.int8.onnx", f"{model}-tokens.txt"]
    thieu = [c for c in can if not os.path.isfile(os.path.join(d, c)) or os.path.getsize(os.path.join(d, c)) < 1000]
    if thieu:
        raise SystemExit(f"! Giải nén xong nhưng thiếu {thieu} - xoá thư mục {d} rồi chạy lại")
    for c in can:
        print(f"    {c}: {os.path.getsize(os.path.join(d, c)) / 1e6:.0f} MB", flush=True)
    open(marker, "w").write(time.strftime("%Y-%m-%d %H:%M"))
    try:
        os.remove(tar_path)
    except OSError:
        open(tar_path, "w").close()   # môi trường không cho xoá: ghi rỗng để không tốn chỗ
    ok(f"whisper-{model} sẵn sàng tại tools/models/")
    return {"vad": True, "whisper": model}


# Model mốc lời cho Bàn dựng (tools/moc-tu.py): tên thư mục đích, tệp tar, cỡ, các tệp cần giữ
MO_HINH_LOI = [
    {"dir": "sherpa-onnx-zipformer-vi-int8-2025-04-20", "tar": "sherpa-onnx-zipformer-vi-int8-2025-04-20.tar.bz2",
     "bytes": 60181038, "giu": ["encoder-epoch-12-avg-8.int8.onnx", "decoder-epoch-12-avg-8.onnx",
                                "joiner-epoch-12-avg-8.int8.onnx", "tokens.txt"],
     "mo_ta": "zipformer tiếng Việt (VietASR, Apache 2.0) - chép nguyên văn, giữ từ đệm"},
    {"dir": "sherpa-onnx-omnilingual-asr-300M-ctc-int8-2025-11-12",
     "tar": "sherpa-onnx-omnilingual-asr-1600-languages-300M-ctc-int8-2025-11-12.tar.bz2",
     "bytes": 292571207, "giu": ["model.int8.onnx", "tokens.txt", "LICENSE"],
     "mo_ta": "omnilingual-asr 300M CTC (Meta, Apache 2.0) - căn mốc từng âm tiết"},
]


def b3b_mo_hinh_loi(ngan_sach):
    """Hai model cho Bàn dựng; cùng cách tải nối tiếp và giải nén theo lượt như bước 3."""
    buoc("3b", "Model mốc lời cho Bàn dựng và Dựng bằng lời")
    xong = True
    for m in MO_HINH_LOI:
        d = os.path.join(MODELS, m["dir"])
        marker = os.path.join(d, ".hoan-tat")
        if os.path.isfile(marker):
            ok(f"{m['dir']} đã có")
            continue
        tar_path = os.path.join(MODELS, m["tar"])
        t0 = time.time()
        co = os.path.getsize(tar_path) if os.path.isfile(tar_path) else 0
        if co < m["bytes"]:
            print(f"  → tải {m['tar']} ({m['bytes'] / 1e6:.0f} MB) - {m['mo_ta']}", flush=True)
            if not _tai_tiep(MODEL_URL + m["tar"], tar_path, m["bytes"], ngan_sach):
                co = os.path.getsize(tar_path) if os.path.isfile(tar_path) else 0
                print(f"\n⏳ Đã tải {co / 1e6:.0f}/{m['bytes'] / 1e6:.0f} MB. CHƯA XONG - chạy lại y nguyên lệnh này để tải tiếp.")
                raise SystemExit(2)
        if ngan_sach - (time.time() - t0) < min(90, ngan_sach * 0.6):
            print("\n⏳ Đã tải xong, CHƯA giải nén - chạy lại y nguyên lệnh này để giải nén.")
            raise SystemExit(2)
        print(f"  → giải nén {m['dir']}…", flush=True)
        os.makedirs(d, exist_ok=True)
        with tarfile.open(tar_path, "r:bz2") as t:
            for mem in t.getmembers():
                base = os.path.basename(mem.name)
                if mem.isfile() and base in m["giu"]:
                    mem.name = base
                    t.extract(mem, d)
        thieu = [g for g in m["giu"] if not os.path.isfile(os.path.join(d, g))]
        if thieu:
            canh_bao(f"{m['dir']}: thiếu {thieu} sau khi giải nén - xoá thư mục đó rồi chạy lại")
            xong = False
            continue
        open(marker, "w").write(time.strftime("%Y-%m-%d %H:%M"))
        try:
            os.remove(tar_path)
        except OSError:
            open(tar_path, "w").close()
        ok(f"{m['dir']} sẵn sàng")
    return xong


# ------------------------------------------------------------------ bước 4
def b4_bo_cuc():
    buoc(4, "Khung và mask bố cục bài giảng có slide (do-hoa-chung/bo-cuc)")
    out = os.path.join(ROOT, "do-hoa-chung", "bo-cuc")
    if os.path.isfile(os.path.join(out, "bo-cuc.json")) and len(os.listdir(out)) >= 12:
        ok("đã có 12 file")
        return True
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "bo-cuc-slide.py"), "--out", out], text=True)
    if p.returncode != 0:
        canh_bao("chưa sinh được bố cục (thiếu Pillow?) - bài giảng có slide sẽ chưa dựng được, các việc khác vẫn chạy")
        return False
    return True


# ------------------------------------------------------------------ bước 5
def b5_thu_muc():
    buoc(5, "Thư mục thư viện và dự án")
    for n in NHOM_NHAC:
        os.makedirs(os.path.join(ROOT, "nhac-nen", n), exist_ok=True)
    for n in NHOM_SFX:
        os.makedirs(os.path.join(ROOT, "hieu-ung", n), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "brand", "logo"), exist_ok=True)
    ok("nhac-nen/<nhóm>, hieu-ung/<nhóm>, brand/logo/")
    sys.path.insert(0, TOOLS)
    import cau_hinh as CH
    if os.path.isdir(os.path.join(ROOT, "du-an")):
        canh_bao("còn thư mục du-an/ kiểu cũ trong repo: nhờ Claude dời từng dự án sang thư mục Du an cạnh repo (xem HUONG-DAN.md mục Cập nhật xưởng)")
    else:
        for d in (CH.du_an(), CH.thanh_pham(), CH.tam(tao=False)):
            os.makedirs(d, exist_ok=True)
        ok(f"dự án: {CH.du_an()}; thành phẩm: {CH.thanh_pham()} (nằm cạnh repo, không lên git)")
    nhac = [f for n in NHOM_NHAC for f in os.listdir(os.path.join(ROOT, "nhac-nen", n))
            if f.lower().endswith((".mp3", ".wav", ".m4a", ".flac"))]
    if nhac:
        ok(f"đã có {len(nhac)} file nhạc")
    else:
        canh_bao("chưa có nhạc - bước thiết lập phong cách sẽ tải theo mẫu bạn chọn (tools/tai-chat-lieu.py)")
    return True


# ------------------------------------------------------------------ bước 6
def b6_dung_thu(kt):
    buoc(6, "Dựng thử một dự án tổng hợp nhỏ qua cổng nghiệm thu")
    p = subprocess.run([sys.executable, os.path.join(TOOLS, "kiem-tra-xuong.py")] + (["--co-slide"] if kt else []), text=True)
    if p.returncode != 0:
        raise SystemExit("! Dựng thử KHÔNG ĐẠT - đọc chẩn đoán ở trên; xưởng chưa an toàn để dùng")
    return True


# ------------------------------------------------------------------ dựng xưởng từ bản thiết kế
TEN_BAN_MAU = "xuong-phim-claude"
REPO_BAN_MAU = "https://github.com/wincreator3012/xuong-phim-claude"
DUOI_CHU = (".md", ".py", ".mjs", ".js", ".ts", ".tsx", ".json", ".sh", ".command", ".html", ".css", ".txt")
BO_QUA_CA_NHAN_HOA = {"LICENSE", os.path.join("studio", "package.json"), os.path.join("studio", "package-lock.json"),
                      os.path.join("tools", "cai-dat.py")}


def _khoi_ban_mau(text):
    import re
    return re.sub(r"[ \t]*<!-- BAN-MAU -->.*?<!-- /BAN-MAU -->[ \t]*\n*", "", text, flags=re.S)


def dung_xuong(args, tt):
    import re
    ten = (args.ten_xuong or os.path.basename(ROOT)).strip()
    tien_to = (args.tien_to or "").strip().lower()
    if not re.match(r"^[a-z0-9]{2,6}$", tien_to):
        raise SystemExit("! --tien-to cần 2-6 chữ thường hoặc số, không dấu (vd chữ cái đầu họ tên: tma)")
    if os.path.isdir(os.path.join(ROOT, ".git")):
        try:
            remote = subprocess.run(["git", "remote", "-v"], cwd=ROOT, capture_output=True, text=True).stdout
        except OSError:
            remote = ""
        if TEN_BAN_MAU in remote:
            canh_bao("thư mục này là bản clone còn trỏ về repo bản thiết kế. Xưởng riêng không push, không pull về đó; "
                     "muốn giữ git cho riêng mình thì: git remote remove origin")
    print(f"DỰNG XƯỞNG TỪ BẢN THIẾT KẾ - cá nhân hoá: {ROOT}")
    so_tep = 0
    for dp, dn, fn in os.walk(ROOT):
        rel_dp = os.path.relpath(dp, ROOT)
        dn[:] = [d for d in dn if d not in (".git", "node_modules", "pylib", "models", "__pycache__")]
        for f in fn:
            rel = os.path.normpath(os.path.join(rel_dp, f))
            if rel in BO_QUA_CA_NHAN_HOA or not f.endswith(DUOI_CHU) and f not in ("CLAUDE.md", "AGENTS.md"):
                continue
            p = os.path.join(dp, f)
            try:
                goc = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            moi = _khoi_ban_mau(goc) if f.endswith(".md") else goc
            # tên bản thiết kế thành tên xưởng; giữ nguyên khi là địa chỉ GitHub ("wincreator3012/xuong-phim-claude")
            # hay khi nói về chính bản thiết kế ("bản thiết kế xuong-phim-claude")
            moi = moi.replace("repo " + TEN_BAN_MAU, "xưởng " + ten)
            moi = re.sub(r"(?<![\w.-])(?<!wincreator3012/)(?<!bản thiết kế )" + re.escape(TEN_BAN_MAU) + r"(?![\w-])", lambda m: ten, moi)
            if moi != goc:
                with open(p, "w", encoding="utf-8") as g:
                    g.write(moi)
                so_tep += 1
    ok(f"tài liệu, skill, công cụ mang tên xưởng '{ten}' ({so_tep} tệp); bỏ khối chỉ dành cho bản thiết kế")
    cfg_p = os.path.join(ROOT, "cau-hinh.json")
    cfg = {}
    if os.path.isfile(cfg_p):
        cfg = json.load(open(cfg_p, encoding="utf-8"))
    elif os.path.isfile(os.path.join(ROOT, "cau-hinh.mau.json")):
        cfg = json.load(open(os.path.join(ROOT, "cau-hinh.mau.json"), encoding="utf-8"))
    cfg["tienToSkill"] = tien_to
    with open(cfg_p, "w", encoding="utf-8") as g:
        json.dump(cfg, g, ensure_ascii=False, indent=2)
        g.write("\n")
    ok(f"cau-hinh.json: tiền tố skill '{tien_to}' (skill trong tài khoản sẽ tên {tien_to}-phim-...)")
    readme = os.path.join(ROOT, "README.md")
    if not os.path.isfile(readme):
        with open(readme, "w", encoding="utf-8") as g:
            g.write(f"# {ten}\n\nXưởng dựng phim cùng AI của riêng tôi. AI đọc `CLAUDE.md` ở đầu mỗi phiên; cách dùng ở `HUONG-DAN.md`.\n\n"
                    f"Dựng từ bản thiết kế [xuong-phim-claude]({REPO_BAN_MAU}) của Lương Dũng Nhân "
                    f"(commit {args.ban_mau or 'main'}, ngày {time.strftime('%Y-%m-%d')}), giấy phép MIT (xem `LICENSE`).\n"
                    "Xưởng này không phải bản clone: không push, không pull về repo bản thiết kế. Muốn học thêm từ bản mới, "
                    "nói với AI \"xem bản thiết kế có gì mới\" (HUONG-DAN.md mục Cập nhật xưởng).\n")
        ok("README.md của xưởng (ghi công bản thiết kế)")
    sys.path.insert(0, TOOLS)
    import cau_hinh as CH
    for d in (CH.du_an(), CH.thanh_pham(), CH.tam(tao=False)):
        os.makedirs(d, exist_ok=True)
    ok(f"dự án: {CH.du_an()}; thành phẩm: {CH.thanh_pham()}")
    for f in ("Go bang tren Mac.command", "Mo ban dung.command"):
        p = os.path.join(ROOT, f)
        if os.path.isfile(p):
            os.chmod(p, 0o755)
    tt["ban_mau"] = {"repo": REPO_BAN_MAU, "commit": args.ban_mau or "main", "ngay": time.strftime("%Y-%m-%d")}
    tt["ten_xuong"] = ten
    tt["tien_to"] = tien_to
    ghi_trang_thai(tt)
    print("\n✓ ĐÃ CÁ NHÂN HOÁ. Bước kế tiếp: python3 tools/cai-dat.py (cài môi trường), rồi skill phim-thiet-lap.")


# ------------------------------------------------------------------ main
def in_trang_thai(tt):
    print("\nTRẠNG THÁI CÀI ĐẶT")
    print(f"  ffmpeg      : {tt.get('cong_cu', {}).get('ffmpeg') or 'chưa kiểm'}")
    print(f"  node        : {tt.get('cong_cu', {}).get('node') or 'không có (render ở đám mây)'}")
    tv = tt.get("thu_vien", {})
    print(f"  python libs : " + (", ".join(f"{k}{'' if v else ' (THIẾU)'}" for k, v in tv.items()) or "chưa cài"))
    md = tt.get("model", {})
    print(f"  model       : " + (f"whisper-{md.get('whisper')} + VAD" if md.get("whisper") else "chưa có"))
    print(f"  mốc lời     : {'có (Bàn dựng, Dựng bằng lời)' if tt.get('mo_hinh_loi') else 'chưa'}")
    print(f"  bố cục slide: {'có' if tt.get('bo_cuc') else 'chưa'}")
    print(f"  dựng thử    : {'ĐẠT ' + str(tt.get('dung_thu_luc', '')) if tt.get('dung_thu') else 'chưa'}")
    print(f"  giới thiệu  : {'đã giới thiệu xưởng cho người dùng' if tt.get('da_gioi_thieu') else 'CHƯA (sau khi thiết lập xong, Claude giới thiệu xưởng: skills/phim-thiet-lap/references/gioi-thieu-xuong.md)'}")
    bm = tt.get("ban_mau")
    print(f"  bản thiết kế: " + (f"{bm.get('repo')} @ {bm.get('commit')} ({bm.get('ngay')}), xưởng '{tt.get('ten_xuong')}', tiền tố skill '{tt.get('tien_to')}'" if bm else "chưa ghi (xưởng dựng trước khi có DUNG-XUONG.md, hoặc chưa chạy --dung-xuong)"))
    print(f"  skill tài khoản: xem python3 tools/dong-goi-skill.py (skill nào cần lưu, lưu lại)")
    print(f"  cập nhật    : {tt.get('cap_nhat', '-')}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="turbo", choices=["turbo", "small", "khong"])
    ap.add_argument("--khong-thu", action="store_true", help="bỏ bước dựng thử")
    ap.add_argument("--khong-loi", action="store_true", help="bỏ hai model mốc lời của Bàn dựng")
    ap.add_argument("--trang-thai", action="store_true", help="chỉ in trạng thái")
    ap.add_argument("--danh-dau", choices=["gioi-thieu"], help="ghi dấu một mốc đã xong rồi thoát (không cài gì)")
    ap.add_argument("--thoi-gian", type=int, default=150, help="ngân sách giây cho bước tải model mỗi lần chạy")
    ap.add_argument("--dung-xuong", action="store_true", help="cá nhân hoá xưởng vừa dựng từ bản thiết kế rồi thoát")
    ap.add_argument("--ten-xuong", help="tên thư mục xưởng của người dùng (mặc định: tên thư mục hiện tại)")
    ap.add_argument("--tien-to", help="tiền tố skill trong tài khoản, 2-6 chữ thường (vd tma)")
    ap.add_argument("--ban-mau", help="mã commit của bản thiết kế đã dùng để dựng")
    args = ap.parse_args()

    os.chdir(ROOT)
    tt = doc_trang_thai()
    if args.danh_dau == "gioi-thieu":
        tt["da_gioi_thieu"] = True
        ghi_trang_thai(tt)
        print("✓ Đã ghi dấu: xưởng đã được giới thiệu cho người dùng.")
        return
    if args.trang_thai:
        in_trang_thai(tt)
        return
    if args.dung_xuong:
        dung_xuong(args, tt)
        return
    print(f"XƯỞNG PHIM CLAUDE - cài đặt tại: {ROOT}")

    tt["cong_cu"] = b1_cong_cu()
    ghi_trang_thai(tt)
    tt["thu_vien"] = b2_thu_vien_python()
    ghi_trang_thai(tt)
    tt["model"] = b3_model(args.model, args.thoi_gian)   # có thể SystemExit(2) = chạy lại
    ghi_trang_thai(tt)
    if not args.khong_loi:
        tt["mo_hinh_loi"] = b3b_mo_hinh_loi(args.thoi_gian)   # có thể SystemExit(2) = chạy lại
        ghi_trang_thai(tt)
    tt["bo_cuc"] = b4_bo_cuc()
    ghi_trang_thai(tt)
    b5_thu_muc()
    if not args.khong_thu:
        b6_dung_thu(tt["bo_cuc"])
        tt["dung_thu"] = True
        tt["dung_thu_luc"] = time.strftime("%Y-%m-%d %H:%M")
    ghi_trang_thai(tt)

    in_trang_thai(tt)
    print("\n✓ CÀI XONG. Bước kế tiếp: nói với Claude \"bắt đầu thiết lập phong cách\" (skill phim-thiet-lap)")
    print("  để điền phong-cach/PHONG-CACH.md, brand/brand.json, tải nhạc theo mẫu bạn chọn, rồi lưu skill vào tài khoản.")


if __name__ == "__main__":
    main()
