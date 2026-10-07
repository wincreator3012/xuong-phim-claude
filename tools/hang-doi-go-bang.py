#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hàng đợi gỡ băng: Claude xếp việc trong VM, máy Mac chạy large-v3 ngoài VM.

Vì sao: VM Cowork chỉ có khoảng 3-4 GB RAM nên whisper large-v3 không chạy được
trong đó (chết lặng vì hết bộ nhớ). Máy Mac thật đủ RAM, nên ưu tiên gỡ băng trên
Mac; VM (turbo) chỉ là đường dự phòng.

Cách dùng (từ thư mục gốc "xuong-phim-claude"):

  Trong VM (Claude chạy qua device_bash):
    python3 tools/hang-doi-go-bang.py them "../Du an/x/nguon/a.mp4" [--out-dir "../Du an/x/transcript"] [--model auto]
    python3 tools/hang-doi-go-bang.py trang-thai          # việc nào chờ, xong, lỗi
    python3 tools/hang-doi-go-bang.py don                 # cất việc đã xong vào <Du an>/_tam/go-bang/xong/
  Trên Mac (người dùng bấm đúp "Go bang tren Mac.command", script đó gọi):
    python3 tools/hang-doi-go-bang.py chay                # chạy lần lượt mọi việc đang chờ

Mỗi việc là một file <Du an>/_tam/go-bang/viec/<id>.json (cau-hinh.json > thuMucTam); kết quả ghi vào
<Du an>/_tam/go-bang/viec/<id>.ket-qua.json (trạng thái, model đã dùng, máy, số giây, dòng
cuối của log) và log đầy đủ ở <Du an>/_tam/go-bang/log/<id>.log. Việc đã có ket-qua với
trạng thái "xong" thì không chạy lại; trạng thái "loi" thì lần bấm sau chạy lại.
Mọi đường dẫn trong việc là đường dẫn TƯƠNG ĐỐI so với thư mục gốc xưởng, nên cùng
một việc chạy được ở cả VM lẫn Mac (thư mục có thể đồng bộ qua đám mây, gốc khác nhau).
"""
import argparse
import datetime as dt
import glob
import json
import os
import platform
import re
import subprocess
import sys
import time

TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS_DIR)
sys.path.insert(0, TOOLS_DIR)
import cau_hinh as CH  # noqa: E402
QDIR = CH.tam("go-bang", "viec")      # hàng đợi là việc tạm, NGOÀI repo
LOGDIR = CH.tam("go-bang", "log")




def rel(p):
    ap = os.path.abspath(p)
    if not CH.cho_phep(ap):
        sys.exit(f"Đường dẫn phải nằm trong thư mục xưởng hoặc thư mục Du an: {p}")
    return os.path.relpath(ap, ROOT)


def slug(s):
    s = re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-")
    return s[:60] or "viec"


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def jobs():
    out = []
    for p in sorted(glob.glob(os.path.join(QDIR, "*.json"))):
        if p.endswith(".ket-qua.json") or p.endswith(".tmp"):
            continue
        jid = os.path.basename(p)[:-5]
        kq = os.path.join(QDIR, jid + ".ket-qua.json")
        out.append((jid, p, kq if os.path.isfile(kq) else None))
    return out


def cmd_them(a):
    os.makedirs(QDIR, exist_ok=True)
    src = rel(a.input)
    if not os.path.isfile(os.path.join(ROOT, src)):
        sys.exit(f"Không thấy file nguồn: {src}")
    out_dir = rel(a.out_dir) if a.out_dir else os.path.join(os.path.dirname(os.path.dirname(src)), "transcript")
    jid = dt.datetime.now().strftime("%Y%m%d-%H%M%S") + "-" + slug(os.path.splitext(os.path.basename(src))[0])
    job = {"input": src, "out_dir": out_dir, "model": a.model, "lang": a.lang,
           "tao_luc": dt.datetime.now().isoformat(timespec="seconds")}
    save(os.path.join(QDIR, jid + ".json"), job)
    print(f"✓ Đã xếp việc {jid}: {src} → {out_dir} (model {a.model})")
    print('  Nhờ người dùng mở Finder, vào thư mục xưởng, bấm đúp "Go bang tren Mac.command".')


def cmd_trang_thai(a):
    js = jobs()
    if not js:
        print("Hàng đợi trống.")
        return
    cho = 0
    for jid, p, kq in js:
        job = load(p)
        if kq:
            r = load(kq)
            print(f"[{r.get('trang_thai', '?'):>5}] {jid}  model={r.get('model', '?')}  may={r.get('may', '?')}  "
                  f"{r.get('giay', 0):.0f}s  {r.get('ghi_chu', '')}")
            if r.get("trang_thai") != "xong":
                cho += 1
        else:
            cho += 1
            print(f"[  chờ] {jid}  {job.get('input', job.get('loai'))}")
    print(f"Còn {cho} việc chưa xong.")


def cmd_chay(a):
    js = [(j, p, k) for j, p, k in jobs() if not (k and load(k).get("trang_thai") == "xong")]
    if not js:
        print("Không có việc nào đang chờ gỡ băng.")
        return 0
    os.makedirs(LOGDIR, exist_ok=True)
    loi = 0
    may = f"{platform.system()} {platform.machine()}"
    for n, (jid, p, _) in enumerate(js, 1):
        job = load(p)
        print(f"\n=== Việc {n}/{len(js)}: {job.get('input', job.get('loai'))} ===", flush=True)
        if job.get("loai") == "proxy":
            # việc loại "proxy": tạo proxy 1080p cho multicam trên Mac (giải mã 4K nhanh hơn VM nhiều lần)
            cmd = [sys.executable, os.path.join(TOOLS_DIR, "proxy-mac.py"), p]
        else:
            cmd = [sys.executable, os.path.join(TOOLS_DIR, "transcribe.py"), os.path.join(ROOT, job["input"]),
                   "--out-dir", os.path.join(ROOT, job["out_dir"]), "--model", job.get("model", "auto"),
                   "--lang", job.get("lang", "vi")]
        t0 = time.time()
        model, last = job.get("model", "auto"), ""
        with open(os.path.join(LOGDIR, jid + ".log"), "w", encoding="utf-8") as log:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, cwd=ROOT)
            for line in proc.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                log.write(line)
                m = re.search(r"model tự chọn: whisper-(\S+)", line) or re.search(r"Nhận dạng bằng whisper-(\S+)", line)
                if m:
                    model = m.group(1)
                if line.strip():
                    last = line.strip()
            rc = proc.wait()
        giay = time.time() - t0
        tt = "xong" if rc == 0 else "loi"
        loi += rc != 0
        save(os.path.join(QDIR, jid + ".ket-qua.json"),
             {"trang_thai": tt, "model": model, "may": may, "giay": round(giay, 1),
              "xong_luc": dt.datetime.now().isoformat(timespec="seconds"),
              "ghi_chu": last[:200], "ma_thoat": rc})
        print(f"--- {tt.upper()} sau {giay:.0f} giây (model {model})", flush=True)
    return 1 if loi else 0


def cmd_don(a):
    import shutil
    dst = CH.tam("go-bang", "xong")
    os.makedirs(dst, exist_ok=True)
    n = 0
    for jid, p, kq in jobs():
        if kq and load(kq).get("trang_thai") == "xong":
            for f in (p, kq):
                shutil.move(f, os.path.join(dst, os.path.basename(f)))
            n += 1
    print(f"Đã cất {n} việc xong vào {dst}.")


def main():
    ap = argparse.ArgumentParser(description="Hàng đợi gỡ băng VM → Mac")
    sub = ap.add_subparsers(dest="lenh", required=True)
    t = sub.add_parser("them")
    t.add_argument("input")
    t.add_argument("--out-dir", default=None)
    t.add_argument("--model", default="auto")
    t.add_argument("--lang", default="vi")
    sub.add_parser("trang-thai")
    sub.add_parser("chay")
    sub.add_parser("don")
    a = ap.parse_args()
    if a.lenh == "them":
        cmd_them(a)
    elif a.lenh == "trang-thai":
        cmd_trang_thai(a)
    elif a.lenh == "don":
        cmd_don(a)
    else:
        sys.exit(cmd_chay(a))


if __name__ == "__main__":
    main()
