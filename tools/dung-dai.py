#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""DỰNG PHIM DÀI THEO GIAI ĐOẠN (phim 30 phút trở lên, hoặc máy có giới hạn thời gian mỗi lệnh).

Vì sao có công cụ này: `assemble.py` chạy trọn một lượt, nhưng (1) máy làm việc có giới hạn khoảng 120 giây
mỗi lệnh và tiến trình nền không sống sót qua lệnh, (2) đoạn dọn dẹp cuối `assemble.py run()` làm rỗng toàn bộ
cache part/body/mix, nên một lần chạy trọn lỡ dở là mất hàng trăm part đã encode. `dung-dai.py` dùng chính các
lớp của `assemble.py` nhưng chia việc thành bước nhỏ, mỗi bước tự dừng êm trước giới hạn, chạy lại được, và
KHÔNG BAO GIỜ dọn cache.

Dùng (từ gốc xưởng; luôn truyền đường dẫn dự án tuyệt đối hoặc "../Du an/<YYYY-MM tên>"):

  python3 tools/dung-dai.py song-song  "<dự án>" <tên-ra> [--nhap] [--cong 4] [--ngan-sach 100]
        Encode các part CÒN THIẾU song song bằng nhiều tiến trình; dừng êm sau --ngan-sach giây.
        In "CON-LAI n" (chạy lại y nguyên) hoặc "XONG-SONG-SONG".
  python3 tools/dung-dai.py ghep       "<dự án>" <tên-ra> [--nhap]     # nối part đã encode thành body (cache)
  python3 tools/dung-dai.py tron       "<dự án>" <tên-ra> [--nhap]     # trộn nhạc + đo âm lượng, DỪNG trước khâu mux
  python3 tools/dung-dai.py mux-a      "<dự án>" <tên-ra> [--nhap]     # chuẩn hoá âm lượng hai nửa song song
  python3 tools/dung-dai.py mux-b      "<dự án>" <tên-ra> [--nhap]     # ghép AAC + copy hình ra xuat-nhap/, rồi chạy meta
  python3 tools/dung-dai.py meta       "<dự án>" <tên-ra> [--nhap]     # chương, map, nghiệm thu máy

Thứ tự trọn vẹn: song-song (lặp đến XONG) → ghep → tron → mux-a → mux-b. Phim ngắn dưới 10 phút chỉ cần
`python3 tools/assemble.py` như thường.

Những cái bẫy đã trả giá (phim live 64 phút, 2026-10-09):
  - Chữ ký (.sig) của part chứa đường dẫn nguồn: truyền đường dẫn dự án KHÁC kiểu (tương đối rồi tuyệt đối) là
    mất cache và phải encode lại hết. Công cụ này luôn đổi sang đường dẫn tuyệt đối.
  - Ổ tạm của máy làm việc có thể chỉ vài GB: mux-a ghi PCM thô vào thư mục tạm ngoài thư mục gắn
    (~/.dung-dai-tam), mux-b đọc qua pipe và ghi thẳng vào xuat-nhap/ (còn nhiều chỗ trống).
  - Nháp 480p (--nhap) và final (mặc định) có cache part riêng theo chữ ký; chuyển từ nháp sang final phải
    encode lại toàn bộ part, hãy tính thời gian (khoảng 25-30 phút cho phim 64 phút trên 4 lõi).
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time

XUONG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAM = os.path.expanduser("~/.dung-dai-tam")


def nap_assemble():
    spec = importlib.util.spec_from_file_location("assemble", os.path.join(XUONG, "tools", "assemble.py"))
    m = importlib.util.module_from_spec(spec)
    sys.modules["assemble"] = m
    spec.loader.exec_module(m)
    return m


M = nap_assemble()


def mo_du_an(du_an, ten, nhap):
    proj = os.path.abspath(du_an if os.path.isabs(du_an) else os.path.join(XUONG, du_an))
    if not os.path.isdir(proj):
        proj = os.path.abspath(du_an)
    tl = json.load(open(os.path.join(proj, "timeline.json"), encoding="utf-8"))
    return proj, tl, M.Assembler(proj, tl, bool(nhap), ten)


# ----------------------------------------------------------------- song song
_JOBS = []
_WA = None
_HAN = 0.0
_ARGS = None


def _ghi_job(self, *args, **kw):
    idx = len(self.parts)
    _JOBS.append((idx, args, kw))
    dur = self._exact(args[2] - args[1])[2]
    self.parts.append("x")
    return dur


def _ghi_chen(self, src, *a, **k):
    self.parts.append("x")
    return M.probe_duration(src)


def _lam(job):
    idx, args, kw = job
    if time.time() > _HAN:
        return idx, "skip", 0.0
    _WA.parts = ["x"] * idx
    t0 = time.time()
    try:
        _CUT_GOC(_WA, *args, **kw)
        return idx, "ok", time.time() - t0
    except BaseException as e:  # noqa: BLE001
        return idx, "LỖI %s" % e, time.time() - t0


_CUT_GOC = M.Assembler.cut_part
_CHEN_GOC = M.Assembler.insert_part


def _khoi(proj, tl, nhap, ten, han):
    global _WA, _HAN
    _WA = M.Assembler(proj, tl, bool(nhap), ten)
    _HAN = han
    sys.stdout = open(os.devnull, "w")


def song_song(a):
    from multiprocessing import Pool
    proj, tl, asm = mo_du_an(a.du_an, a.ten, a.nhap)
    asm.validate_timeline()
    M.Assembler.cut_part = _ghi_job
    M.Assembler.insert_part = _ghi_chen
    asm.build_parts()
    M.Assembler.cut_part = _CUT_GOC
    M.Assembler.insert_part = _CHEN_GOC
    viec = sorted(_JOBS, key=lambda j: -(j[1][2] - j[1][1]))
    han = time.time() + a.ngan_sach
    print("tổng %d part, %d tiến trình, ngân sách %.0f s" % (len(viec), a.cong, a.ngan_sach), flush=True)
    t0 = time.time()
    xong = bo_qua = 0
    with Pool(a.cong, initializer=_khoi, initargs=(proj, tl, a.nhap, a.ten, han)) as p:
        for idx, st, dt in p.imap_unordered(_lam, viec):
            xong += 1
            if st == "skip":
                bo_qua += 1
                continue
            print("[%d/%d] part-%03d %s (%.0fs) | tổng %.0fs" % (xong, len(viec), idx, st, dt, time.time() - t0), flush=True)
    print("XONG-SONG-SONG" if not bo_qua else "CON-LAI %d" % bo_qua, flush=True)
    return 0 if not bo_qua else 3


# ----------------------------------------------------------------- ghép, trộn
def ghep(a):
    proj, tl, asm = mo_du_an(a.du_an, a.ten, a.nhap)
    asm.validate_timeline()
    body = asm.concat(asm.build_parts())
    print("GHEP-OK", M.probe_duration(body))
    return 0


def tron(a):
    proj, tl, asm = mo_du_an(a.du_an, a.ten, a.nhap)
    asm.validate_timeline()
    body = asm.concat(asm.build_parts())
    goc = M.sh

    def sh_dung(cmd, *x, **k):
        if "+faststart" in cmd:  # tới khâu mux cuối thì dừng
            print("TRON-OK (dừng trước mux)")
            sys.exit(0)
        return goc(cmd, *x, **k)

    M.sh = sh_dung
    asm.finalize(body)
    return 0


def _lenh_loudnorm(tam):
    ln = open(os.path.join(tam, "mix.wav.ln"), encoding="utf-8").read().split("\n", 1)[1]
    m = json.loads("{" + ln.rsplit("{", 1)[1])
    return ("loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:measured_I=%s:measured_TP=%s:measured_LRA=%s:"
            "measured_thresh=%s:offset=%s" % (m["input_i"], m["input_tp"], m["input_lra"], m["input_thresh"], m["target_offset"]))


def mux_a(a):
    proj, tl, asm = mo_du_an(a.du_an, a.ten, a.nhap)
    tam = asm.tmp
    os.makedirs(TAM, exist_ok=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                       os.path.join(tam, "body.mp4")]).decode().strip())
    nua = round(d / 2, 2)
    json.dump({"dur": d, "nua": nua}, open(os.path.join(TAM, "mux.json"), "w"))
    ln = _lenh_loudnorm(tam)
    mix = os.path.join(tam, "mix.wav")
    ps = [
        subprocess.Popen(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", mix, "-t", str(nua), "-af", ln,
                          "-f", "s16le", "-ar", "48000", "-ac", "2", os.path.join(TAM, "a1.raw")]),
        subprocess.Popen(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-ss", str(nua), "-i", mix, "-af", ln,
                          "-f", "s16le", "-ar", "48000", "-ac", "2", os.path.join(TAM, "a2.raw")]),
    ]
    rc = [p.wait() for p in ps]
    print("MUX-A-OK" if rc == [0, 0] else "MUX-A-LOI %s" % rc)
    return 0 if rc == [0, 0] else 1


def mux_b(a):
    proj, tl, asm = mo_du_an(a.du_an, a.ten, a.nhap)
    tam = asm.tmp
    d = json.load(open(os.path.join(TAM, "mux.json")))["dur"]
    a1, a2 = os.path.join(TAM, "a1.raw"), os.path.join(TAM, "a2.raw")
    cat = subprocess.Popen(["cat", a1, a2], stdout=subprocess.PIPE)
    os.makedirs(os.path.dirname(asm.out_file), exist_ok=True)
    rc = subprocess.call(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y", "-i", os.path.join(tam, "body_v.mp4"),
                          "-f", "s16le", "-ar", "48000", "-ac", "2", "-i", "pipe:0", "-map", "0:v", "-c:v", "copy", "-map", "1:a",
                          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", "-t", "%.3f" % d, asm.out_file],
                         stdin=cat.stdout)
    cat.wait()
    if rc != 0:
        print("MUX-B-LOI")
        return 1
    print("MUX-B-OK", asm.out_file, "%.0f MB" % (os.path.getsize(asm.out_file) / 1e6))
    return meta(a)


def meta(a):
    proj, tl, asm = mo_du_an(a.du_an, a.ten, a.nhap)
    asm.validate_timeline()
    asm.concat(asm.build_parts())  # để có sum_parts và time_map; part, body đã cache nên nhanh
    asm.write_chapters()
    asm.write_time_map()
    fv, fa = M.stream_durations(asm.out_file)
    M.check_av(asm.out_file, getattr(asm, "sum_parts", None), label="THÀNH PHẨM", dur_tol=0.1 + 0.01 * len(asm.parts))
    json.dump({"file": os.path.basename(asm.out_file), "tool_version": M.TOOL_VERSION + "+" + M.CONCAT_REV, "parts": len(asm.parts),
               "hinh": round(fv or 0, 3), "tieng": round(fa or 0, 3), "tong_part": round(getattr(asm, "sum_parts", 0) or 0, 3),
               "ket_luan": "ĐẠT: hình = tiếng = tổng part"},
              open(os.path.splitext(asm.out_file)[0] + ".nghiem-thu.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("META-OK", fv, fa, getattr(asm, "sum_parts", None))
    print("Tiếp: python3 tools/nghiem-thu.py (video, transcript) rồi gói đăng tải.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lenh", choices=["song-song", "ghep", "tron", "mux-a", "mux-b", "meta"])
    ap.add_argument("du_an")
    ap.add_argument("ten")
    ap.add_argument("--nhap", action="store_true", help="bản nháp 480p (mặc định: final)")
    ap.add_argument("--cong", type=int, default=4, help="số tiến trình song song")
    ap.add_argument("--ngan-sach", type=float, default=100.0, help="giây, sau mốc này không bắt đầu part mới")
    a = ap.parse_args()
    sys.exit({"song-song": song_song, "ghep": ghep, "tron": tron, "mux-a": mux_a, "mux-b": mux_b, "meta": meta}[a.lenh](a))


if __name__ == "__main__":
    main()
