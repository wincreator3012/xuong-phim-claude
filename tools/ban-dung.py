#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BÀN DỰNG: máy chủ nhỏ để bạn tự tay tinh chỉnh timeline.json của một clip gần xong, xem trước ngay
trên Chrome. Chỉ dùng thư viện chuẩn của Python (3.8 trở lên): chạy được bằng python3 có sẵn trên Mac,
không cần cài gì. Bạn mở bằng cách bấm đúp "Mo ban dung.command" ở gốc xưởng.

    python3 tools/ban-dung.py [--cong 8765] [--mo]      # --mo: tự mở Chrome

Nguyên tắc (claude/ban-dung-dac-ta.md):
  - timeline.json là nguồn sự thật duy nhất; Bàn dựng chỉ đọc và ghi đúng file đó, bản dựng thật vẫn do
    tools/assemble.py làm và tools/nghiem-thu.py kiểm. Bàn dựng không bao giờ tự nói "xong".
  - Chỉ nghe trên 127.0.0.1 (máy khác trong mạng không vào được).
  - Ghi có khoá lạc quan: file đã đổi từ lúc mở (Claude vừa sửa, hoặc máy kia đồng bộ qua iCloud) thì
    từ chối ghi, trang hỏi bạn nạp bản mới hay ghi đè. Mọi lần ghi đều chép bản cũ vào
    <dự án>/ke-hoach-dung/_phien-ban/ và thêm một dòng vào <dự án>/ke-hoach-dung/_ban-dung/nhat-ky.jsonl.
  - Media phục vụ theo từng khúc byte (HTTP 206) để Chrome và Safari tua được file lớn.
"""
import argparse
import datetime
import glob
import hashlib
import json
import mimetypes
import os
import re
import shutil
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOOLS = os.path.dirname(os.path.abspath(__file__))
GOC = os.path.dirname(TOOLS)                       # gốc xưởng
sys.path.insert(0, TOOLS)
import cau_hinh as CH  # noqa: E402
DU_AN = CH.du_an()                                 # hồ sơ dự án, NGOÀI repo (cau-hinh.json > thuMucDuAn)
APP = os.path.join(TOOLS, "ban-dung")              # trang tĩnh
sys.path.insert(0, TOOLS)

LOAI = {
    ".mp4": "video/mp4", ".m4v": "video/mp4", ".mov": "video/quicktime", ".webm": "video/webm",
    ".m4a": "audio/mp4", ".mp3": "audio/mpeg", ".wav": "audio/wav", ".aac": "audio/aac",
    ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml",
    ".json": "application/json; charset=utf-8", ".bin": "application/octet-stream",
    ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8",
    ".html": "text/html; charset=utf-8", ".woff2": "font/woff2",
}
KHOI = 1 << 20
KHOA_GHI = threading.Lock()


def loai_cua(path):
    return LOAI.get(os.path.splitext(path)[1].lower()) or mimetypes.guess_type(path)[0] or "application/octet-stream"


def trong(goc, path):
    """path (tuyệt đối) có nằm trong goc không - chặn ../ thoát ra ngoài xưởng."""
    goc = os.path.realpath(goc)
    p = os.path.realpath(path)
    return p == goc or p.startswith(goc + os.sep)


def phien_ban(path):
    """Dấu phiên bản của file: băm nội dung (mtime của iCloud không đủ tin)."""
    with open(path, "rb") as fh:
        return hashlib.sha1(fh.read()).hexdigest()[:16]


def thu_muc_du_an(tl_path):
    """Thư mục dự án mà đường dẫn trong timeline tính theo (giống --project của assemble.py):
    <Du an>/<x>/timeline*.json, <Du an>/<x>/ke-hoach-dung/timeline*.json, <Du an>/<x>/clip-ngan/<slug>/timeline*.json."""
    d = os.path.dirname(tl_path)
    if os.path.basename(d) == "ke-hoach-dung":
        return os.path.dirname(d)
    if os.path.basename(os.path.dirname(d)) == "clip-ngan":
        return os.path.dirname(os.path.dirname(d))
    return d


def giai_media(du_an, p):
    """Giống Assembler.resolve: tìm trong dự án trước, rồi tới gốc xưởng (nhac-nen/, brand/...)."""
    if os.path.isabs(p):
        return p
    c1 = os.path.join(du_an, p)
    if os.path.exists(c1):
        return c1
    c2 = os.path.join(GOC, p)
    return c2 if os.path.exists(c2) else c1


def thut_le(raw):
    """Số dấu cách thụt lề của file JSON gốc, để ghi lại cùng kiểu (file của xưởng dùng 1 hoặc 2)."""
    m = re.search(r"\n( +)\S", raw)
    return len(m.group(1)) if m else 2


def danh_sach():
    ra = []
    mau = [os.path.join(DU_AN, "*", "timeline*.json"),
           os.path.join(DU_AN, "*", "ke-hoach-dung", "timeline*.json"),
           os.path.join(DU_AN, "*", "clip-ngan", "*", "timeline*.json")]
    for f in sorted(set(sum((glob.glob(m) for m in mau), []))):
        rel = os.path.relpath(f, GOC)
        da = os.path.relpath(thu_muc_du_an(f), GOC)
        try:
            tl = json.load(open(f, encoding="utf-8"))
            n = len(tl.get("segments", []))
        except (OSError, ValueError):
            continue
        ten_da = os.path.basename(da)
        ra.append({"p": rel, "duAn": da, "tenDuAn": ten_da, "file": os.path.relpath(f, thu_muc_du_an(f)), "doan": n,
                   "khung": tl.get("aspect", "ngang"),
                   "luc": int(os.path.getmtime(f)), "phu": ten_da.startswith("_"),
                   "chinhTay": bool(tl.get("_chinhTay"))})
    ra.sort(key=lambda x: (x["phu"], -x["luc"]))
    return ra


def tom_tat_doi(cu, moi):
    """Mô tả ngắn các thay đổi giữa hai timeline, để Claude đọc nhật ký và học góp ý của bạn."""
    doi = []
    for k in ("intro", "outro"):
        if cu.get(k) != moi.get(k):
            doi.append(f"{k}: {cu.get(k)} -> {moi.get(k)}")
    if cu.get("music") != moi.get("music"):
        a, b = cu.get("music") or {}, moi.get("music") or {}
        for k in sorted(set(a) | set(b)):
            if a.get(k) != b.get(k):
                doi.append(f"nhạc.{k}: {a.get(k)} -> {b.get(k)}")
    sa, sb = cu.get("segments", []), moi.get("segments", [])
    khoa = lambda s: json.dumps(s, sort_keys=True, ensure_ascii=False)  # noqa: E731
    if len(sa) == len(sb) and sa != sb and sorted(map(khoa, sa)) == sorted(map(khoa, sb)):
        vi_tri = {khoa(s): i + 1 for i, s in enumerate(sa)}
        doi.append("đổi thứ tự đoạn: " + ", ".join(str(vi_tri.get(khoa(s), "?")) for s in sb))
        return doi
    if len(sa) != len(sb):
        doi.append(f"số đoạn: {len(sa)} -> {len(sb)}")
    for i in range(min(len(sa), len(sb))):
        x, y = sa[i], sb[i]
        if x == y:
            continue
        for k in sorted(set(x) | set(y)):
            if k == "_id" or x.get(k) == y.get(k):
                continue
            if k in ("overlay", "broll"):
                doi.append(f"đoạn {i + 1}.{k}: {json.dumps(x.get(k), ensure_ascii=False)} -> "
                           f"{json.dumps(y.get(k), ensure_ascii=False)}")
            else:
                doi.append(f"đoạn {i + 1}.{k}: {x.get(k)} -> {y.get(k)}")
    return doi[:200]


def ghi_timeline(tl_path, tl_moi, phien_cu, ghi_de):
    with KHOA_GHI:
        raw = open(tl_path, encoding="utf-8").read()
        hien = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]
        if hien != phien_cu and not ghi_de:
            return 409, {"loi": "xung-dot", "phienBan": hien}
        du_an = thu_muc_du_an(tl_path)
        khd = os.path.join(du_an, "ke-hoach-dung")
        luc = datetime.datetime.now()
        dau = luc.strftime("%Y%m%d-%H%M%S")
        # tên bản cất: đường dẫn timeline tính từ dự án (clip-ngan/<slug>/timeline -> clip-ngan__<slug>__timeline)
        ten = os.path.splitext(os.path.relpath(tl_path, du_an))[0].replace(os.sep, "__")
        pb = os.path.join(khd, "_phien-ban")
        os.makedirs(pb, exist_ok=True)
        shutil.copy2(tl_path, os.path.join(pb, f"{ten}.{dau}.json"))
        try:
            cu = json.loads(raw)
        except ValueError:
            cu = {}
        dem = int((cu.get("_chinhTay") or {}).get("soLan", 0)) + 1
        tl_moi["_chinhTay"] = {"luc": luc.isoformat(timespec="seconds"), "soLan": dem,
                               "boi": "Bàn dựng",
                               "ghiChu": "Timeline đã được bạn chỉnh tay: là nguồn sự thật, không sinh lại "
                                         "từ plan của dự án; Claude sửa thẳng file này và giữ các chỉnh tay."}
        out = json.dumps(tl_moi, ensure_ascii=False, indent=thut_le(raw)) + "\n"
        tmp = tl_path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(out)
        os.replace(tmp, tl_path)
        nk = os.path.join(khd, "_ban-dung")
        os.makedirs(nk, exist_ok=True)
        with open(os.path.join(nk, "nhat-ky.jsonl"), "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"luc": luc.isoformat(timespec="seconds"),
                                 "file": os.path.relpath(tl_path, du_an),
                                 "banCu": os.path.relpath(os.path.join(pb, f"{ten}.{dau}.json"), du_an),
                                 "thayDoi": tom_tat_doi(cu, tl_moi)}, ensure_ascii=False) + "\n")
        return 200, {"phienBan": hashlib.sha1(out.encode("utf-8")).hexdigest()[:16],
                     "banCu": os.path.relpath(os.path.join(pb, f"{ten}.{dau}.json"), GOC),
                     "chinhTay": tl_moi["_chinhTay"]}


_DEP = {}


def lam_dep(tu, cau, khoa):
    """Lớp chữ để dựng là chữ nguyên văn viết thường của zipformer. Chữ nào khớp với bản gỡ băng large-v3
    (so dãy âm tiết) thì mượn cách viết của large-v3 (hoa, dấu câu) để dễ đọc; từ đệm, chữ large-v3 bỏ
    sót vẫn hiện nguyên văn. Chỉ đổi cách HIỂN THỊ (trường "h"), mốc thời gian không đổi."""
    import difflib
    import unicodedata
    if khoa in _DEP:
        hien = _DEP[khoa]
    else:
        toks = []
        for c in cau:
            for t in (c.get("t") or "").split():
                n = unicodedata.normalize("NFC", re.sub(r"[^\w]", "", t.lower()))
                if n:
                    toks.append((n, t))
        sm = difflib.SequenceMatcher(None, [w["w"] for w in tu], [n for n, _ in toks], autojunk=False)
        hien = {}
        for b in sm.get_matching_blocks():
            for k in range(b.size):
                hien[b.a + k] = toks[b.b + k][1]
        _DEP[khoa] = hien
    for j, h in hien.items():
        if j < len(tu):
            tu[j]["h"] = h


def phu_tro(du_an, src):
    """Dữ liệu đi kèm một file nguồn: khoảng lặng, bản gỡ băng (câu), mốc âm tiết, năng lượng."""
    base = os.path.splitext(os.path.basename(src))[0]
    td = os.path.join(du_an, "transcript")
    ra = {"src": src}

    def doc(ten):
        f = os.path.join(td, ten)
        if os.path.isfile(f):
            try:
                return json.load(open(f, encoding="utf-8"))
            except ValueError:
                return None
        return None
    ra["silences"] = doc(f"{base}.silences.json") or []
    ra["cau"] = [{"s": c.get("start"), "e": c.get("end"), "t": c.get("text", "")}
                 for c in (doc(f"{base}.transcript.json") or [])]
    tu = doc(f"{base}.tu.json")
    if tu:
        ra["tu"] = [{"w": w["w"], "s": w["s"], "e": w["e"], "c": w.get("c", 1), "k": w.get("k", 0)} for w in tu["tu"]]
        if ra["cau"]:
            try:
                f_tu = os.path.join(td, f"{base}.tu.json")
                f_cau = os.path.join(td, f"{base}.transcript.json")
                lam_dep(ra["tu"], ra["cau"], (f_tu, os.path.getmtime(f_tu), os.path.getmtime(f_cau)))
            except Exception:  # noqa: BLE001 - làm đẹp chữ hỏng thì vẫn hiện chữ nguyên văn
                pass
        nl = tu.get("nangLuong", {})
        ra["nangLuong"] = {"url": os.path.relpath(os.path.join(td, nl.get("file", "")), du_an),
                           "hz": nl.get("hz", 100), "san": nl.get("san", -60)}
    elif os.path.isfile(os.path.join(td, f"{base}.nang-luong.bin")):
        ra["nangLuong"] = {"url": os.path.relpath(os.path.join(td, f"{base}.nang-luong.bin"), du_an),
                           "hz": 100, "san": -60}
    return ra


class XuLy(BaseHTTPRequestHandler):
    server_version = "BanDung/1"

    def log_message(self, fmt, *args):
        if getattr(self.server, "noi_nhieu", False):
            sys.stderr.write("  " + fmt % args + "\n")

    # ---- tiện ích ----
    def _json(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(b)

    def _loi(self, code, msg):
        self._json(code, {"loi": msg})

    def _tham_so(self):
        u = urllib.parse.urlparse(self.path)
        return u.path, {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}

    def _tl_path(self, q):
        p = q.get("p", "")
        f = os.path.join(GOC, p)
        if not p.endswith(".json") or not os.path.basename(p).startswith("timeline") or not trong(
                DU_AN, f) or not os.path.isfile(f):
            return None
        return f

    def _gui_file(self, f, dau_trang=False):
        try:
            size = os.path.getsize(f)
        except OSError:
            return self._loi(404, "không thấy file")
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        code = 200
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m:
                if m.group(1):
                    start = int(m.group(1))
                    if m.group(2):
                        end = min(int(m.group(2)), size - 1)
                elif m.group(2):
                    start = max(0, size - int(m.group(2)))
                if start > end or start >= size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.end_headers()
                    return
                code = 206
        self.send_response(code)
        self.send_header("Content-Type", loai_cua(f))
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        self.send_header("Cache-Control", "no-cache" if dau_trang else "private, max-age=3600")
        self.end_headers()
        if self.command == "HEAD":
            return
        try:
            with open(f, "rb") as fh:
                fh.seek(start)
                con = end - start + 1
                while con > 0:
                    b = fh.read(min(KHOI, con))
                    if not b:
                        break
                    self.wfile.write(b)
                    con -= len(b)
        except (BrokenPipeError, ConnectionResetError):
            pass

    # ---- định tuyến ----
    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path, q = self._tham_so()
        try:
            if path == "/" or path == "/index.html":
                return self._gui_file(os.path.join(APP, "index.html"), True)
            if path.startswith("/app/"):
                f = os.path.join(APP, urllib.parse.unquote(path[5:]))
                return self._gui_file(f, True) if trong(APP, f) else self._loi(403, "ngoài thư mục")
            if path.startswith("/m/"):
                # /m/<dự án tương đối gốc>::<đường dẫn media tương đối dự án>
                rest = urllib.parse.unquote(path[3:])
                if "::" not in rest:
                    return self._loi(400, "thiếu ::")
                da, p = rest.split("::", 1)
                du_an = os.path.join(GOC, da)
                f = giai_media(du_an, p)
                if not (trong(GOC, f) or trong(DU_AN, f)):
                    return self._loi(403, "ngoài xưởng")
                return self._gui_file(f)
            if path == "/api/danh-sach":
                return self._json(200, {"goc": os.path.basename(GOC), "ds": danh_sach()})
            if path == "/api/timeline":
                f = self._tl_path(q)
                if not f:
                    return self._loi(404, "không thấy timeline")
                raw = open(f, encoding="utf-8").read()
                return self._json(200, {"tl": json.loads(raw), "phienBan": hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16],
                                        "duAn": os.path.relpath(thu_muc_du_an(f), GOC), "p": q["p"]})
            if path == "/api/phu-tro":
                du_an = os.path.join(GOC, q.get("duAn", ""))
                if not trong(DU_AN, du_an):
                    return self._loi(403, "ngoài Du an")
                return self._json(200, phu_tro(du_an, q.get("src", "")))
            if path == "/api/ping":
                return self._json(200, {"ok": True})
            return self._loi(404, "không có đường này")
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:  # noqa: BLE001 - báo lỗi cho trang thay vì treo
            try:
                self._loi(500, f"{type(e).__name__}: {e}")
            except Exception:  # noqa: BLE001
                pass

    def do_POST(self):
        path, q = self._tham_so()
        try:
            n = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(n).decode("utf-8") or "{}")
            if path == "/api/timeline":
                f = self._tl_path(q)
                if not f:
                    return self._loi(404, "không thấy timeline")
                tl = body.get("tl")
                if not isinstance(tl, dict) or not isinstance(tl.get("segments"), list):
                    return self._loi(400, "timeline không hợp lệ")
                code, kq = ghi_timeline(f, tl, body.get("phienBanCu"), bool(body.get("ghiDe")))
                return self._json(code, kq)
            if path == "/api/cat":
                import ban_dung_loi as L
                du_an = os.path.join(GOC, q.get("duAn", ""))
                base = os.path.splitext(os.path.basename(body["src"]))[0]
                loi, _ = L.doc(du_an, base)
                ra = {}
                if body.get("vao") is not None:
                    ra["vao"] = loi.diem_vao(int(body["vao"]))
                if body.get("ra") is not None:
                    ra["ra"] = loi.diem_ra(int(body["ra"]))
                if body.get("khe"):
                    ra["khe"] = {str(i): loi.khe(int(i)) for i in body["khe"]}
                return self._json(200, ra)
            return self._loi(404, "không có đường này")
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as e:  # noqa: BLE001
            try:
                self._loi(500, f"{type(e).__name__}: {e}")
            except Exception:  # noqa: BLE001
                pass


def mo_trinh_duyet(url):
    if sys.platform == "darwin":
        for app in ("Google Chrome", "Chromium"):
            if subprocess.run(["open", "-a", app, url], capture_output=True).returncode == 0:
                return
        subprocess.run(["open", url])
    else:
        webbrowser.open(url)


def main():
    ap = argparse.ArgumentParser(description="Bàn dựng: tinh chỉnh timeline.json bằng tay")
    ap.add_argument("--cong", type=int, default=8765)
    ap.add_argument("--mo", action="store_true", help="tự mở Chrome")
    ap.add_argument("--noi-nhieu", action="store_true", help="in từng yêu cầu")
    args = ap.parse_args()
    srv = None
    for cong in range(args.cong, args.cong + 20):
        try:
            srv = ThreadingHTTPServer(("127.0.0.1", cong), XuLy)
            break
        except OSError:
            continue
    if srv is None:
        sys.exit("Không mở được cổng nào từ %d" % args.cong)
    srv.daemon_threads = True
    srv.noi_nhieu = args.noi_nhieu
    url = f"http://127.0.0.1:{srv.server_address[1]}/"
    print(f"Bàn dựng đang chạy: {url}")
    print("Giữ cửa sổ này mở trong lúc chỉnh. Xong thì đóng cửa sổ (hoặc bấm Ctrl+C).")
    if args.mo:
        threading.Timer(0.6, mo_trinh_duyet, args=(url,)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nĐã tắt Bàn dựng.")


if __name__ == "__main__":
    main()
