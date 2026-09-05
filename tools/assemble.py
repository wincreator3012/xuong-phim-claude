#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ghép dựng video hoàn chỉnh từ timeline.json - chạy bằng ffmpeg trong VM cục bộ.

Cách dùng (từ thư mục gốc "xuong-phim-claude"):
    python3 tools/assemble.py --project "du-an/ten-du-an" [--timeline timeline.json]
                              [--preview] [--out ten-file.mp4]

Thiết kế: mỗi đoạn được cắt + chuẩn hóa MỘT lần (encode đồng nhất), sau đó ghép
bằng concat -c copy (không encode lại), cuối cùng chỉ xử lý audio (nhạc nền +
chuẩn hóa âm lượng) với video copy → toàn bộ video chỉ encode đúng một lần.

timeline.json:
{
  "aspect": "ngang" | "doc",
  "fps": 30,
  "fadeColor": "black",
  "intro": "do-hoa/ngang/intro.mp4",
  "outro": "do-hoa/ngang/outro.mp4",
  "segments": [
    {"type": "video", "src": "nguon/a.mp4", "in": 12.5, "out": 95.0,
     "snap": true,                    // hút điểm cắt về khoảng lặng gần nhất
     "fadeIn": 0, "fadeOut": 0,       // giây; 0 = cắt thẳng
     "cropFocus": 0.5,                // khung dọc: tâm crop ngang (0=trái, 1=phải)
     "chapter": "Tên chương",        // tùy chọn, để tạo chapters.txt
     "overlay": {"src": "do-hoa/ngang/lt.webm", "at": 1.0},  // bảng tên alpha
     "broll": [{"src": "nguon/broll.mp4", "at": 30.0, "duration": 6.0, "from": 0}]
    },                                 // "at" theo thời gian TRONG FILE NGUỒN
    {"type": "insert", "src": "do-hoa/ngang/info-01.mp4"}
  ],
  "music": {"src": "nhac-nen/x.mp3", "mode": "full",   // "full" | "bookends"
            "gainDb": -22, "duck": true, "fadeIn": 2, "fadeOut": 4},
  "colorGrade": {"contrast": 1.04, "saturation": 1.08, "brightness": 0.01}
                                    // tùy chọn, áp cho CẢNH QUAY THẬT (cut_part)
                                    // qua bộ lọc eq của ffmpeg, KHÔNG áp cho đồ họa
                                    // insert (intro/outro/title đã đúng màu sẵn).
                                    // Bỏ trống = không chỉnh gì (mặc định cũ).
}

Đơn màu theo TỪNG FILE NGUỒN (skill phim-mau-sac): nếu dự án có mau-sac.json
  {"<tên file nguồn>": {"vf": "<chuỗi filter ffmpeg>", "note": "<lý do>"}}
thì chuỗi vf đó được chèn TRƯỚC bước chuẩn hóa cho mọi đoạn cắt từ file ấy
(tonemap HDR, cân trắng, khớp góc máy...). Áp cho cả B-roll theo file hình.
Độc lập và cộng dồn được với colorGrade toàn cục. Cache part tự vô hiệu khi đơn đổi.

Bài giảng có SLIDE (skill phim-bai-giang-slide):
  "theme": "light"|"dark" ở cấp cao nhất; mỗi segment thêm
  "layout": "mat"|"slide"|"ca-hai"|"chia-doi"|"mat-chinh", "slide": "slide/slide-03.png",
  "slideZoom": [x, y, w, h] (tỉ lệ 0-1, tùy chọn). Toạ độ/khung/mask: do-hoa-chung/bo-cuc/.
MULTICAM (skill phim-multicam): segment thêm "audioSrc": "nguon/tieng-chu.wav", "audioIn": <giây>
  → hình từ src [in, out], tiếng từ audioSrc bắt đầu tại audioIn (trục tiếng chủ); đặt snap:false.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys

FPS_DEFAULT = 30
SIZES = {"ngang": (1920, 1080), "doc": (1080, 1920)}
PREVIEW_SIZES = {"ngang": (854, 480), "doc": (480, 854)}

# --- Chống lệch hình-tiếng (bản vá 2026-09-05) --------------------------------
# Đổi TOOL_VERSION mỗi khi sửa logic encode → mọi cache .sig cũ tự vô hiệu.
TOOL_VERSION = "2026-09-05.antidrift-1"
AV_TOL = 0.06       # hình và tiếng lệch nhau quá 2 khung hình (30fps) là LỖI
DUR_TOL = 0.15      # part dài/ngắn hơn dự kiến quá mức này là LỖI


def stream_durations(path):
    """Thời lượng THEO TỪNG STREAM (giây): (video, audio); None nếu thiếu stream."""
    p = sh(["ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", path])
    info = json.loads(p.stdout)
    fmt_d = float(info.get("format", {}).get("duration") or 0)
    v = a = None
    for s in info.get("streams", []):
        d = s.get("duration")
        if d is None and s.get("tags", {}).get("DURATION"):
            # mkv/webm ghi thời lượng trong tag dạng HH:MM:SS.mmm
            h, m, sec = s["tags"]["DURATION"].split(":")
            d = int(h) * 3600 + int(m) * 60 + float(sec)
        d = float(d) if d is not None else fmt_d
        if s.get("codec_type") == "video" and v is None:
            v = d
        elif s.get("codec_type") == "audio" and a is None:
            a = d
    return v, a


def file_stamp(path):
    """Dấu vân tay rẻ tiền của file nguồn (kích cỡ + mtime) để đưa vào chữ ký cache."""
    try:
        st = os.stat(path)
        return [st.st_size, int(st.st_mtime)]
    except OSError:
        return None


def check_av(path, expected=None, label="", raise_on_fail=True, dur_tol=DUR_TOL):
    """BẤT BIẾN của xưởng: mọi file video trung gian và thành phẩm phải có
    hình = tiếng (≤ AV_TOL) và, nếu biết trước, = thời lượng dự kiến (≤ dur_tol).
    Sai → ném lỗi với chẩn đoán (hoặc trả False nếu raise_on_fail=False)."""
    label = label or os.path.basename(path)
    try:
        v, a = stream_durations(path)
    except Exception as e:  # noqa: BLE001
        if raise_on_fail:
            raise RuntimeError(f"[NGHIỆM THU] {label}: không đọc được file ({e})")
        return False
    problems = []
    if v is None:
        problems.append("thiếu stream HÌNH")
    if a is None:
        problems.append("thiếu stream TIẾNG")
    if v is not None and a is not None and abs(v - a) > AV_TOL:
        problems.append(f"HÌNH {v:.3f}s ≠ TIẾNG {a:.3f}s (lệch {v - a:+.3f}s)")
    if expected is not None and v is not None and abs(v - expected) > dur_tol:
        problems.append(f"hình {v:.3f}s ≠ dự kiến {expected:.3f}s (lệch {v - expected:+.3f}s)")
    if not problems:
        return True
    msg = (f"[NGHIỆM THU] {label} KHÔNG ĐẠT: " + "; ".join(problems) +
           "\n  → Đây đúng là lớp lỗi 'lệch hình-tiếng ngầm' (xem docs/BAI-HOC.md)."
           "\n  → Không được đi tiếp/che bằng encode lại. Kiểm lại lệnh ffmpeg của part này"
           " (cờ -t phía output, apad), nguồn có bị cắt cụt không, overlay/B-roll có dài quá đoạn không.")
    if raise_on_fail:
        raise RuntimeError(msg)
    print("  ! " + msg.replace("\n", "\n  "), flush=True)
    return False
# -------------------------------------------------------------------------------


def sh(cmd, quiet=True):
    p = subprocess.run(cmd, capture_output=quiet, text=True)
    if p.returncode != 0:
        err = (p.stderr or "")[-3000:] if quiet else ""
        raise RuntimeError(f"Lệnh lỗi ({p.returncode}): {' '.join(shlex.quote(c) for c in cmd)}\n{err}")
    return p


def probe_duration(path):
    p = sh(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path])
    return float(json.loads(p.stdout)["format"]["duration"])


def has_audio(path):
    p = sh(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", path])
    return any(s.get("codec_type") == "audio" for s in json.loads(p.stdout).get("streams", []))


def video_codec(path):
    p = sh(["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", path])
    for s in json.loads(p.stdout).get("streams", []):
        if s.get("codec_type") == "video":
            return s.get("codec_name")
    return None


def load_silences(project, src):
    base = os.path.splitext(os.path.basename(src))[0]
    f = os.path.join(project, "transcript", f"{base}.silences.json")
    if os.path.isfile(f):
        with open(f, encoding="utf-8") as fh:
            return json.load(fh)
    return []


def snap_point(t, silences, mode, tolerance=1.0, margin=0.12):
    """Hút điểm cắt về khoảng lặng gần nhất.
    mode="in": điểm vào → cuối khoảng lặng - margin (vào ngay trước khi nói)
    mode="out": điểm ra → đầu khoảng lặng + margin (ra ngay sau khi dứt lời)
    """
    best, best_d = None, tolerance
    for s in silences:
        anchor = s["end"] if mode == "in" else s["start"]
        d = abs(anchor - t)
        if d < best_d or (s["start"] - 0.01 <= t <= s["end"] + 0.01 and mode == "in"):
            if s["start"] - tolerance <= t <= s["end"] + tolerance:
                best, best_d = s, min(d, best_d)
    if best is None:
        return t
    return max(0.0, best["end"] - margin) if mode == "in" else best["start"] + margin


class Assembler:
    def __init__(self, project, timeline, preview, out_name):
        self.project = project
        self.tl = timeline
        self.preview = preview
        self.aspect = timeline.get("aspect", "ngang")
        self.fps = timeline.get("fps", FPS_DEFAULT)
        self.w, self.h = (PREVIEW_SIZES if preview else SIZES)[self.aspect]
        self.fade_color = timeline.get("fadeColor", "black")
        self.color_grade = timeline.get("colorGrade")
        # Đơn màu theo TỪNG FILE NGUỒN (skill phim-mau-sac): <dự án>/mau-sac.json
        # {"<tên file>": {"vf": "<chuỗi filter>", "note": "..."}} - key bắt đầu "_" bị bỏ qua
        self.mau_sac = {}
        ms_path = os.path.join(project, "mau-sac.json")
        if os.path.isfile(ms_path):
            with open(ms_path, encoding="utf-8") as f:
                self.mau_sac = {k: v for k, v in json.load(f).items()
                                if not k.startswith("_")}
            print(f"  Đơn màu: {len(self.mau_sac)} nguồn từ mau-sac.json", flush=True)
        self.tmp = os.path.join(project, ".tam")
        os.makedirs(self.tmp, exist_ok=True)
        self.out_dir = os.path.join(project, "xuat-nhap")
        os.makedirs(self.out_dir, exist_ok=True)
        name = out_name or f"{os.path.basename(os.path.normpath(project))}-{self.aspect}"
        if name.endswith(".mp4"):
            name = name[:-4]
        if preview:
            name += "-nhap"
        self.out_file = os.path.join(self.out_dir, name if name.endswith(".mp4") else name + ".mp4")
        self.parts = []
        self.chapters = []

    def resolve(self, p):
        """Đường dẫn tương đối: tìm trong thư mục dự án trước, rồi tới thư mục gốc
        (để dùng chung nhac-nen/, brand/ ở cấp gốc)."""
        if os.path.isabs(p):
            return p
        cand1 = os.path.join(self.project, p)
        if os.path.exists(cand1):
            return cand1
        root = os.path.dirname(os.path.dirname(os.path.normpath(self.project)))
        cand2 = os.path.join(root, p)
        return cand2 if os.path.exists(cand2) else cand1

    # ---------- encode 1 phần ----------
    def enc_args(self):
        if self.preview:
            return ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "28",
                    "-pix_fmt", "yuv420p", "-video_track_timescale", "90000",
                    "-c:a", "aac", "-b:a", "96k", "-ar", "48000", "-ac", "2"]
        return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                "-pix_fmt", "yuv420p", "-profile:v", "high", "-level", "4.1",
                "-video_track_timescale", "90000",
                "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]

    def vf_normalize(self, focus=0.5):
        tar = self.w / self.h
        return (
            f"fps={self.fps},"
            f"crop='min(iw,ih*{tar:.6f})':'min(ih,iw/{tar:.6f})':'(iw-ow)*{focus}':'(ih-oh)*0.5',"
            f"scale={self.w}:{self.h},setsar=1,format=yuv420p"
        )

    def vf_grade(self):
        """Bộ lọc màu tùy chọn (eq) cho cảnh quay thật - xem "colorGrade" trong
        docstring. Không dùng cho insert_part (đồ họa đã đúng màu thiết kế)."""
        g = self.color_grade
        if not g:
            return ""
        parts = []
        for key in ("contrast", "brightness", "saturation", "gamma"):
            if key in g:
                parts.append(f"{key}={g[key]}")
        return f",eq={':'.join(parts)}" if parts else ""

    def vf_mau_sac(self, src):
        """Đơn màu theo từng file nguồn (mau-sac.json). Đặt TRƯỚC chuỗi chuẩn hóa
        để xử lý ở không gian màu gốc (ví dụ tonemap HDR trước khi scale)."""
        if not self.mau_sac or not src:
            return ""
        don = self.mau_sac.get(os.path.basename(src)) or {}
        vf = don.get("vf", "")
        return f"{vf}," if vf else ""

    def af_normalize(self):
        return "aresample=async=1:first_pts=0,aformat=sample_rates=48000:channel_layouts=stereo,apad"

    # ---------- bố cục bài giảng có slide ----------
    LAYOUTS_OK = ("mat", "slide", "ca-hai", "chia-doi", "mat-chinh")

    def bo_cuc(self):
        """Đọc do-hoa-chung/bo-cuc/bo-cuc.json (cache) - toạ độ ô, palette, đường dẫn khung/mask."""
        if getattr(self, "_bo_cuc", None) is None:
            root = os.path.dirname(os.path.dirname(os.path.normpath(self.project)))
            d = os.path.join(root, "do-hoa-chung", "bo-cuc")
            p = os.path.join(d, "bo-cuc.json")
            if not os.path.isfile(p):
                raise RuntimeError(f"Thiếu {p} - chạy: python3 tools/bo-cuc-slide.py")
            with open(p, encoding="utf-8") as f:
                spec = json.load(f)
            spec["_dir"] = d
            self._bo_cuc = spec
        return self._bo_cuc

    def _crop_to(self, ar, focus):
        """Crop nguồn về tỉ lệ ar (w/h) quanh tâm ngang focus, giữ tối đa chiều cao."""
        return (f"crop='min(iw,ih*{ar:.6f})':'min(ih,iw/{ar:.6f})':"
                f"'(iw-ow)*{focus}':'(ih-oh)*0.5'")

    def cut_part(self, src, t_in, t_out, focus=0.5, fade_in=0.0, fade_out=0.0,
                 overlay=None, video_from=None, broll_from=0.0,
                 layout="mat", slide=None, slide_zoom=None,
                 audio_src=None, audio_in=None):
        """Cắt [t_in, t_out] từ src thành một phần chuẩn hóa.
        video_from: nếu đặt → video lấy từ file khác (B-roll), audio vẫn từ src.
        layout/slide: bố cục bài giảng có slide (xem skill phim-bai-giang-slide).
        audio_src/audio_in: MULTICAM - tiếng lấy từ file khác (tiếng chủ) bắt đầu tại audio_in,
        hình vẫn từ src [t_in, t_out]. Bất biến: mọi part ra đều hình = tiếng = dur (check_av)."""
        idx = len(self.parts)
        out = os.path.join(self.tmp, f"part-{idx:03d}.mp4")
        dur = t_out - t_in
        layout = layout or "mat"
        if video_from:
            layout = "mat"  # B-roll thay hình → không ghép slide
        self._map_add("cut", src, t_in, t_out, dur, video_from)
        self.time_map[-1]["layout"] = layout
        if slide:
            self.time_map[-1]["slide"] = slide
        if audio_src:
            # multicam: mốc phụ đề/chapter tính theo TIẾNG CHỦ, không theo file góc
            self.time_map[-1]["audio_src"] = os.path.relpath(self.resolve(audio_src), self.project)
            self.time_map[-1]["audio_in"] = round(float(audio_in or 0.0), 3)
        theme = self.tl.get("theme", "light")
        mau = self.vf_mau_sac(video_from or src)  # B-roll: hình từ video_from → đơn của nó
        a_path = self.resolve(audio_src) if audio_src else None
        sig = self._cache_sig(kind="cut", src=src, t_in=t_in, t_out=t_out, focus=focus,
                               fade_in=fade_in, fade_out=fade_out, overlay=overlay,
                               video_from=video_from, broll_from=broll_from, preview=self.preview,
                               mau=mau, layout=layout, slide=slide, slide_zoom=slide_zoom, theme=theme,
                               audio_src=a_path, audio_in=audio_in)
        if self._cache_hit(out, dur, sig) and check_av(out, dur, label=os.path.basename(out) + " (cache)", raise_on_fail=False):
            print(f"    (dùng lại part-{idx:03d}.mp4 đã encode)", flush=True)
            self.parts.append(out)
            return dur

        af = self.af_normalize()
        fade_v = ""
        if fade_in > 0:
            fade_v += f",fade=t=in:st=0:d={fade_in}:color={self.fade_color}"
            af += f",afade=t=in:st=0:d={fade_in}"
        if fade_out > 0:
            fade_v += f",fade=t=out:st={max(0, dur - fade_out):.3f}:d={fade_out}:color={self.fade_color}"
            af += f",afade=t=out:st={max(0, dur - fade_out):.3f}:d={fade_out}"

        cmd = ["ffmpeg", "-hide_banner", "-y"]
        overlays = (overlay if isinstance(overlay, list) else [overlay]) if overlay else []
        # Đầu vào tiếng: mặc định chính src; multicam → file tiếng chủ tại audio_in
        if a_path:
            a_in_args = ["-ss", f"{float(audio_in or 0.0):.3f}", "-t", f"{dur:.3f}", "-i", a_path]
        else:
            a_in_args = None

        if video_from:
            vf = mau + self.vf_normalize(focus) + self.vf_grade() + fade_v
            cmd += ["-ss", f"{broll_from:.3f}", "-t", f"{dur:.3f}", "-i", video_from]
            cmd += a_in_args if a_in_args else ["-ss", f"{t_in:.3f}", "-t", f"{dur:.3f}", "-i", src]
            cmd += ["-filter_complex", f"[0:v]{vf}[v];[1:a]{af}[a]",
                    "-map", "[v]", "-map", "[a]"]
        elif layout == "mat" and not overlays:
            vf = mau + self.vf_normalize(focus) + self.vf_grade() + fade_v
            cmd += ["-ss", f"{t_in:.3f}", "-t", f"{dur:.3f}", "-i", src]
            if a_in_args:
                cmd += a_in_args + ["-map", "0:v", "-map", "1:a"]
            cmd += ["-vf", vf, "-af", af]
        else:
            cmd += ["-ss", f"{t_in:.3f}", "-t", f"{dur:.3f}", "-i", src]
            a_idx = 0
            n_in = 1
            if a_in_args:
                cmd += a_in_args
                a_idx, n_in = 1, 2
            fc = ""
            if layout == "mat":
                fc += f"[0:v]{mau}{self.vf_normalize(focus)}{self.vf_grade()}[v0];"
            else:
                spec = self.bo_cuc()
                W, H = spec["size"]
                lay = spec["layouts"][layout]
                pal = spec["palette"][theme]
                bg = "0x" + pal["bg"].lstrip("#")
                sd = spec["_dir"]
                if not slide:
                    raise RuntimeError(f"Đoạn layout '{layout}' cần trường 'slide'")
                slide_path = self.resolve(slide)
                cmd += ["-loop", "1", "-framerate", str(self.fps), "-i", slide_path]
                i_slide, n_in = n_in, n_in + 1
                zoom = ""
                if slide_zoom:
                    zx, zy, zw, zh = [float(v) for v in slide_zoom]
                    zoom = f"crop=iw*{zw:.4f}:ih*{zh:.4f}:iw*{zx:.4f}:ih*{zy:.4f},"
                ss = lay["slide"]
                slide_chain = (f"[{i_slide}:v]{zoom}scale={ss['w']}:{ss['h']}:force_original_aspect_ratio=decrease,"
                               f"pad={ss['w']}:{ss['h']}:(ow-iw)/2:(oh-ih)/2:color={bg},setsar=1,format=rgba")

                def mask_for(slot):
                    key = f"mask-{slot['w']}x{slot['h']}-r{slot['r']}.png"
                    return os.path.join(sd, key)

                if layout == "slide":
                    fc += f"{slide_chain},fps={self.fps},format=yuv420p[v0];"
                else:
                    # khung nền + bóng
                    khung = os.path.join(sd, f"{layout}-{theme}-khung.png")
                    if not os.path.isfile(khung):
                        raise RuntimeError(f"Thiếu {khung} - chạy: python3 tools/bo-cuc-slide.py")
                    cmd += ["-loop", "1", "-framerate", str(self.fps), "-i", khung]
                    i_khung, n_in = n_in, n_in + 1
                    # mask slide
                    cmd += ["-loop", "1", "-framerate", str(self.fps), "-i", mask_for(ss)]
                    i_ms, n_in = n_in, n_in + 1
                    fc += f"{slide_chain}[s0];[{i_ms}:v]format=gray[ms];[s0][ms]alphamerge[sa];"
                    fs = lay["face"]
                    face_full = fs["w"] == W and fs["h"] == H
                    if face_full:
                        # mat-chinh: mặt toàn khung làm nền, khung (bóng + viền) rồi thẻ slide lên trên
                        fc += (f"[0:v]{mau}{self.vf_normalize_full(focus, W, H)}{self.vf_grade()}[base];"
                               f"[base][{i_khung}:v]overlay=0:0[t1];"
                               f"[t1][sa]overlay={ss['x']}:{ss['y']}[v0];")
                    else:
                        cmd += ["-loop", "1", "-framerate", str(self.fps), "-i", mask_for(fs)]
                        i_mf, n_in = n_in, n_in + 1
                        ar = fs["w"] / fs["h"]
                        fc += (f"[0:v]{mau}fps={self.fps},{self._crop_to(ar, focus)},"
                               f"scale={fs['w']}:{fs['h']},setsar=1{self.vf_grade()},format=rgba[f0];"
                               f"[{i_mf}:v]format=gray[mf];[f0][mf]alphamerge[fa];"
                               f"[{i_khung}:v][sa]overlay={ss['x']}:{ss['y']}[t1];"
                               f"[t1][fa]overlay={fs['x']}:{fs['y']}:shortest=1[v0];")
            # overlay (pill/caption) chồng lên bố cục
            k = 0
            for ov in overlays:
                ov_src = self.resolve(ov["src"])
                at = float(ov.get("at", 0.5))
                codec = video_codec(ov_src)
                dec = {"vp8": "libvpx", "vp9": "libvpx-vp9"}.get(codec)
                if dec:
                    cmd += ["-c:v", dec]
                cmd += ["-itsoffset", f"{at:.3f}", "-i", ov_src]
                # nền đang ở 1920x1080 (bố cục slide) hoặc kích cỡ xuất (mat) - scale overlay cho khớp
                ovW, ovH = (self.bo_cuc()["size"] if layout != "mat" else (self.w, self.h))
                fc += f"[{n_in}:v]scale={ovW}:{ovH}[ov{k}];"
                fc += f"[v{k}][ov{k}]overlay=0:0:eof_action=pass[v{k + 1}];"
                n_in += 1
                k += 1
            # về kích cỡ xuất (preview thu nhỏ) + fade + format
            tail = ""
            if layout != "mat":
                tail += f"scale={self.w}:{self.h},setsar=1,"
            fc += f"[v{k}]{tail}format=yuv420p{fade_v}[v];[{a_idx}:a]{af}[a]"
            cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"]
        cmd += ["-t", f"{dur:.3f}"] + self.enc_args() + [out]
        sh(cmd)
        check_av(out, dur, label=os.path.basename(out))
        self._cache_save(out, sig)
        self.parts.append(out)
        return dur

    def vf_normalize_full(self, focus, W, H):
        """Chuẩn hóa về khung thật WxH (bố cục slide luôn ghép ở 1920x1080 rồi mới thu về preview)."""
        tar = W / H
        return (f"fps={self.fps},"
                f"crop='min(iw,ih*{tar:.6f})':'min(ih,iw/{tar:.6f})':'(iw-ow)*{focus}':'(ih-oh)*0.5',"
                f"scale={W}:{H},setsar=1,format=yuv420p")

    def _cache_sig(self, **kw):
        import hashlib
        kw["_tool"] = TOOL_VERSION
        # Vân tay mọi file nguồn liên quan (src, video_from, overlay.src…):
        # đổi file (quay lại, render lại đồ họa) là cache tự vô hiệu.
        stamps = {}

        def walk(v):
            if isinstance(v, str) and os.path.isfile(v):
                stamps[os.path.basename(v)] = file_stamp(v)
            elif isinstance(v, dict):
                for kk, vv in v.items():
                    walk(self.resolve(vv) if kk == "src" and isinstance(vv, str) else vv)
            elif isinstance(v, (list, tuple)):
                for vv in v:
                    walk(vv)
        walk(list(kw.values()))
        kw["_files"] = stamps
        s = json.dumps(kw, sort_keys=True, ensure_ascii=False)
        return hashlib.sha1(s.encode("utf-8")).hexdigest()[:16]

    def _cache_hit(self, out, expected_dur, sig, tol=0.6):
        """Cho phép resume: nếu part đã encode xong với đúng tham số ở lần chạy
        trước (bị ngắt do timeout của shell) thì bỏ qua, không encode lại.
        So khớp với thời lượng THỰC TẾ đã ghi lại lúc encode xong (không phải
        con số lý thuyết t_out-t_in, vì ffmpeg seek/fade có thể lệch chút ít)."""
        sig_file = out + ".sig"
        if not (os.path.isfile(out) and os.path.getsize(out) > 0 and os.path.isfile(sig_file)):
            return False
        try:
            with open(sig_file, encoding="utf-8") as f:
                saved = json.loads(f.read())
            if saved.get("sig") != sig:
                return False
            d = probe_duration(out)
        except Exception:
            return False
        return abs(d - saved.get("dur", -999)) < tol

    def _cache_save(self, out, sig):
        try:
            d = probe_duration(out)
            with open(out + ".sig", "w", encoding="utf-8") as f:
                f.write(json.dumps({"sig": sig, "dur": d}))
        except OSError:
            pass

    def insert_part(self, src, fade_in=0.0, fade_out=0.0):
        """Đồ họa chèn (intro/outro/infographic). Thêm audio im lặng nếu thiếu."""
        idx = len(self.parts)
        out = os.path.join(self.tmp, f"part-{idx:03d}.mp4")
        dur = probe_duration(src)
        self._map_add("insert", src, 0.0, dur, dur)
        sig = self._cache_sig(kind="insert", src=src, preview=self.preview)
        if self._cache_hit(out, dur, sig) and check_av(out, dur, label=os.path.basename(out) + " (cache)", raise_on_fail=False):
            print(f"    (dùng lại part-{idx:03d}.mp4 đã encode)", flush=True)
            self.parts.append(out)
            return dur
        vf = self.vf_normalize()
        cmd = ["ffmpeg", "-hide_banner", "-y", "-i", src]
        if has_audio(src):
            cmd += ["-vf", vf, "-af", self.af_normalize()]
        else:
            cmd += ["-f", "lavfi", "-t", f"{dur:.3f}",
                    "-i", "anullsrc=r=48000:cl=stereo",
                    "-vf", vf, "-map", "0:v", "-map", "1:a"]
        cmd += ["-t", f"{dur:.3f}"] + self.enc_args() + [out]
        sh(cmd)
        check_av(out, dur, label=os.path.basename(out))
        self._cache_save(out, sig)
        self.parts.append(out)
        return dur


    # ---------- kiểm timeline TRƯỚC khi encode + bản đồ thời gian ----------
    def validate_timeline(self):
        """Bắt lỗi cấu hình trong 1 giây thay vì sau 40 phút encode. Lỗi (ERR)
        → dừng; cảnh báo (WARN) → in ra cho Claude cân nhắc. Quy ước mốc thời gian:
        segment.in/out và broll.at tính theo FILE NGUỒN (tuyệt đối);
        overlay.at tính TƯƠNG ĐỐI từ đầu đoạn (0 = ngay khi đoạn bắt đầu)."""
        errs, warns = [], []
        rel = self.resolve

        def need(p, what):
            if not p:
                return None
            full = rel(p)
            if not os.path.isfile(full):
                errs.append(f"{what}: không thấy file '{p}' (tìm ở {full})")
                return None
            return full

        need(self.tl.get("intro"), "intro")
        need(self.tl.get("outro"), "outro")
        if self.tl.get("music", {}).get("src"):
            need(self.tl["music"]["src"], "music")
        if self.tl.get("aspect", "ngang") not in SIZES:
            errs.append(f"aspect '{self.tl.get('aspect')}' không hợp lệ (ngang|doc)")

        for i, seg in enumerate(self.tl.get("segments", []), start=1):
            tag = f"đoạn {i}"
            stype = seg.get("type", "video")
            if stype == "insert":
                need(seg.get("src"), f"{tag} (insert)")
                for k in ("in", "out", "overlay", "broll"):
                    if k in seg:
                        warns.append(f"{tag} là insert nhưng có trường '{k}' - sẽ bị bỏ qua")
                continue
            if stype != "video":
                errs.append(f"{tag}: type '{stype}' không hợp lệ (video|insert)")
                continue
            src = need(seg.get("src"), tag)
            if not src:
                continue
            try:
                src_d = probe_duration(src)
            except Exception:
                errs.append(f"{tag}: ffprobe không đọc được {seg['src']}")
                continue
            t_in = float(seg.get("in", 0))
            t_out = float(seg.get("out") or src_d)
            if t_in < 0:
                errs.append(f"{tag}: in={t_in} âm")
            if t_out <= t_in:
                errs.append(f"{tag}: out={t_out} phải lớn hơn in={t_in}")
            if t_out > src_d + 0.05:
                errs.append(f"{tag}: out={t_out:.2f} vượt thời lượng nguồn {src_d:.2f}s")
            if t_out - t_in < 0.5 and t_out > t_in:
                warns.append(f"{tag}: đoạn chỉ {t_out - t_in:.2f}s - cố ý?")
            seg_d = max(0.0, t_out - t_in)

            if seg.get("audioSrc"):
                a_full = need(seg["audioSrc"], f"{tag} audioSrc")
                a_in = float(seg.get("audioIn", 0))
                if a_full:
                    try:
                        a_d = probe_duration(a_full)
                        if a_in < 0 or a_in + (t_out - t_in) > a_d + 0.05:
                            errs.append(f"{tag}: audioIn={a_in} vượt file tiếng ({a_d:.1f}s) cho đoạn dài {t_out - t_in:.1f}s")
                    except Exception:
                        errs.append(f"{tag}: ffprobe không đọc được audioSrc")
                if seg.get("snap", True):
                    warns.append(f"{tag}: có audioSrc mà snap=true - snap dùng khoảng lặng của file GÓC, "
                                 "nên đặt snap:false (multicam-dan.py đã hút điểm cắt theo tiếng chủ)")
            layout = seg.get("layout", "mat")
            if layout not in self.LAYOUTS_OK:
                errs.append(f"{tag}: layout '{layout}' không hợp lệ ({'|'.join(self.LAYOUTS_OK)})")
            elif layout != "mat":
                if not seg.get("slide"):
                    errs.append(f"{tag}: layout '{layout}' cần trường 'slide' (ảnh slide)")
                else:
                    need(seg["slide"], f"{tag} slide")
                if seg.get("broll"):
                    warns.append(f"{tag}: có cả layout '{layout}' và B-roll - quãng B-roll sẽ không ghép slide")
                try:
                    self.bo_cuc()
                except Exception as e:  # noqa: BLE001
                    errs.append(str(e))
            if seg.get("slideZoom") and (len(seg["slideZoom"]) != 4 or
                                         not all(0 <= float(v) <= 1 for v in seg["slideZoom"])):
                errs.append(f"{tag}: slideZoom phải là [x, y, w, h] tỉ lệ 0-1")
            ov = seg.get("overlay")
            overlays = ov if isinstance(ov, list) else ([ov] if ov else [])
            brolls = sorted(seg.get("broll", []), key=lambda b: float(b.get("at", 0)))
            first_span_end = seg_d
            if brolls:
                b0 = float(brolls[0].get("at", 0))
                if t_in <= b0 < t_out:
                    first_span_end = b0 - t_in
            for o in overlays:
                osrc = need(o.get("src"), f"{tag} overlay")
                at = float(o.get("at", 0.5))
                if at < 0:
                    errs.append(f"{tag} overlay: at={at} âm")
                if at >= seg_d and seg_d > 0:
                    errs.append(f"{tag} overlay: at={at} ≥ thời lượng đoạn {seg_d:.2f}s "
                                f"(overlay.at tính TƯƠNG ĐỐI từ đầu đoạn, không phải mốc trong file nguồn)")
                elif at >= first_span_end > 0:
                    warns.append(f"{tag} overlay: at={at} rơi vào quãng B-roll đầu tiên "
                                 f"(overlay chỉ phủ lên phần đầu của đoạn, tới {first_span_end:.2f}s)")
                if osrc:
                    try:
                        od = probe_duration(osrc)
                        if at + od > first_span_end + 0.05:
                            warns.append(f"{tag} overlay: {os.path.basename(osrc)} dài {od:.1f}s, "
                                         f"bắt đầu {at}s → bị cắt tại {first_span_end:.2f}s")
                    except Exception:
                        pass
            prev_end = t_in
            for b in brolls:
                bsrc = need(b.get("src"), f"{tag} B-roll")
                b_at = float(b.get("at", 0))
                b_dur = float(b.get("duration", 0))
                if b_dur <= 0:
                    errs.append(f"{tag} B-roll: duration phải > 0")
                if not (t_in <= b_at < t_out):
                    errs.append(f"{tag} B-roll: at={b_at} nằm ngoài [{t_in:.2f}, {t_out:.2f}] của đoạn "
                                f"(broll.at tính theo mốc TRONG FILE NGUỒN, giống in/out)")
                if b_at + b_dur > t_out + 0.05:
                    warns.append(f"{tag} B-roll: at+duration={b_at + b_dur:.2f} vượt out={t_out:.2f} → bị cắt")
                if b_at < prev_end - 0.001:
                    errs.append(f"{tag} B-roll: chồng lên B-roll trước (at={b_at} < {prev_end:.2f})")
                prev_end = max(prev_end, b_at + b_dur)
                if bsrc:
                    try:
                        bd = probe_duration(bsrc)
                        b_from = float(b.get("from", 0))
                        if b_from + b_dur > bd + 0.05:
                            errs.append(f"{tag} B-roll: from+duration={b_from + b_dur:.2f} vượt "
                                        f"thời lượng file B-roll {bd:.2f}s ({os.path.basename(bsrc)})")
                    except Exception:
                        pass
        for w in warns:
            print(f"  ⚠ {w}", flush=True)
        if errs:
            raise RuntimeError("[KIỂM TIMELINE] " + str(len(errs)) + " lỗi - chưa encode gì:\n  - "
                               + "\n  - ".join(errs))
        print(f"  ✓ timeline hợp lệ ({len(self.tl.get('segments', []))} đoạn"
              + (f", {len(warns)} cảnh báo" if warns else "") + ")", flush=True)

    def _map_add(self, kind, src, t_in, t_out, dur, video_from=None):
        """Ghi một dòng bản đồ nguồn → thành phẩm (mốc ra = tổng dur các part trước)."""
        if not hasattr(self, "time_map"):
            self.time_map = []
        start = sum(m["dur"] for m in self.time_map)
        self.time_map.append({
            "part": len(self.time_map), "kind": kind,
            "src": os.path.relpath(src, self.project) if src else None,
            "in": round(t_in, 3), "out": round(t_out, 3),
            "video_from": os.path.relpath(video_from, self.project) if video_from else None,
            "start": round(start, 3), "end": round(start + dur, 3), "dur": round(dur, 3),
        })

    def write_time_map(self):
        """<thành phẩm>.map.json: dùng để tính lại phụ đề/chapter theo mốc thành phẩm."""
        if not getattr(self, "time_map", None):
            return
        f = os.path.splitext(self.out_file)[0] + ".map.json"
        with open(f, "w", encoding="utf-8") as fh:
            json.dump({"_ghi_chu": "start/end = mốc trong thành phẩm; in/out = mốc trong file nguồn. "
                                   "Phụ đề: giữ câu có in ≤ t < out, mốc mới = start + (t - in).",
                       "fps": self.fps, "parts": self.time_map}, fh, ensure_ascii=False, indent=1)
        print(f"  → bản đồ thời gian: {f}")

    # ---------- toàn bộ timeline ----------
    def build_parts(self):
        t_cursor = 0.0
        rel = self.resolve

        if self.tl.get("intro"):
            print("  + intro", flush=True)
            t_cursor += self.insert_part(rel(self.tl["intro"]))

        for i, seg in enumerate(self.tl.get("segments", [])):
            stype = seg.get("type", "video")
            if seg.get("chapter"):
                self.chapters.append((t_cursor, seg["chapter"]))
            if stype == "insert":
                print(f"  + đồ họa chèn: {seg['src']}", flush=True)
                t_cursor += self.insert_part(rel(seg["src"]))
                continue

            src = rel(seg["src"])
            t_in = float(seg.get("in", 0))
            t_out = float(seg.get("out") or probe_duration(src))
            if seg.get("snap", True):
                sil = load_silences(self.project, src)
                if sil:
                    t_in = snap_point(t_in, sil, "in")
                    t_out = snap_point(t_out, sil, "out")
            focus = float(seg.get("cropFocus", 0.5))
            fade_in = float(seg.get("fadeIn", 0))
            fade_out = float(seg.get("fadeOut", 0))
            brolls = sorted(seg.get("broll", []), key=lambda b: b["at"])

            # Chia đoạn theo các quãng B-roll (hình thay, tiếng giữ)
            spans = []
            cur = t_in
            for b in brolls:
                b_at = max(t_in, float(b["at"]))
                b_end = min(t_out, b_at + float(b["duration"]))
                if b_at > cur:
                    spans.append(("main", cur, b_at, None))
                spans.append(("broll", b_at, b_end, b))
                cur = b_end
            if cur < t_out:
                spans.append(("main", cur, t_out, None))

            print(f"  + đoạn {i + 1}: {os.path.basename(src)} "
                  f"[{t_in:.2f} → {t_out:.2f}]"
                  + (f" ({len(brolls)} B-roll)" if brolls else ""), flush=True)

            for j, (kind, a, b, binfo) in enumerate(spans):
                first, last = j == 0, j == len(spans) - 1
                t_cursor += self.cut_part(
                    src, a, b, focus=focus,
                    fade_in=fade_in if first else 0.0,
                    fade_out=fade_out if last else 0.0,
                    overlay=seg.get("overlay") if first else None,
                    video_from=rel(binfo["src"]) if kind == "broll" else None,
                    broll_from=float(binfo.get("from", 0)) if kind == "broll" else 0.0,
                    layout=seg.get("layout", "mat"), slide=seg.get("slide"),
                    slide_zoom=seg.get("slideZoom"),
                    audio_src=seg.get("audioSrc"), audio_in=seg.get("audioIn"),
                )

        if self.tl.get("outro"):
            print("  + outro", flush=True)
            t_cursor += self.insert_part(rel(self.tl["outro"]))
        return t_cursor

    def concat(self, expected):
        """Ghép các part bằng concat -c copy. TRƯỚC khi ghép: kiểm từng part
        hình = tiếng. SAU khi ghép: body phải = tổng part và hình = tiếng.
        Không còn tự 'encode lại' để che lệch - muốn encode lại phải bật
        --ep-encode-lai một cách có ý thức, và kết quả vẫn bị kiểm."""
        # Kiểm từng part (kể cả part lấy từ cache) - in bảng chẩn đoán nếu có lệch
        rows, bad = [], []
        for p in self.parts:
            v, a = stream_durations(p)
            rows.append((os.path.basename(p), v, a))
            if v is None or a is None or abs(v - a) > AV_TOL:
                bad.append(os.path.basename(p))
        total_parts = sum(r[1] or 0 for r in rows)
        if bad:
            tbl = "\n".join(f"    {n:<16} hình {v if v is None else round(v, 3)!s:>9}  "
                            f"tiếng {a if a is None else round(a, 3)!s:>9}" for n, v, a in rows)
            raise RuntimeError(f"[NGHIỆM THU] {len(bad)} part lệch hình-tiếng: {', '.join(bad)}\n{tbl}"
                               "\n  → Dừng trước khi ghép. Xóa (truncate) các part lỗi + .sig rồi chạy lại;"
                               " nếu vẫn lệch là lệnh encode của nhánh đó thiếu -t/apad.")
        if abs(total_parts - expected) > 0.1 + 0.01 * len(self.parts):
            print(f"  ⚠ tổng part {total_parts:.2f}s khác dự kiến {expected:.2f}s "
                  f"(mỗi part đã đúng hình=tiếng; chênh do seek/snap - chấp nhận)", flush=True)
        self.sum_parts = total_parts

        lst = os.path.join(self.tmp, "concat.txt")
        with open(lst, "w", encoding="utf-8") as f:
            for p in self.parts:
                f.write("file '" + os.path.abspath(p).replace("'", r"'\''") + "'\n")
        body = os.path.join(self.tmp, "body.mp4")
        sh(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0",
            "-i", lst, "-c", "copy", body])
        ok = check_av(body, total_parts, label="body (sau concat copy)",
                      raise_on_fail=False, dur_tol=0.1 + 0.01 * len(self.parts))
        if not ok:
            if not getattr(self, "allow_reencode", False):
                raise RuntimeError("[NGHIỆM THU] concat copy cho body lệch dù từng part đều đạt → "
                                   "các part không đồng nhất tham số (fps/timescale/codec?). "
                                   "Xem lại enc_args; chỉ dùng --ep-encode-lai khi đã hiểu nguyên nhân.")
            print("  ! --ep-encode-lai: encode lại body (chậm, chất lượng giảm một bậc)", flush=True)
            sh(["ffmpeg", "-hide_banner", "-y", "-f", "concat", "-safe", "0",
                "-i", lst, "-vf", f"fps={self.fps}", "-af",
                "aresample=async=1:first_pts=0,aformat=sample_rates=48000:channel_layouts=stereo",
                "-t", f"{total_parts:.3f}"] + self.enc_args() + [body])
            check_av(body, total_parts, label="body (sau encode lại)",
                     dur_tol=0.1 + 0.01 * len(self.parts))
        return body

    def finalize(self, body):
        """Nhạc nền + chuẩn hóa âm lượng hai lượt (-14 LUFS); video copy."""
        music = self.tl.get("music")
        dur = probe_duration(body)
        mix = os.path.join(self.tmp, "mix.wav")
        cmd = ["ffmpeg", "-hide_banner", "-y", "-i", body]

        if music and music.get("src"):
            msrc = self.resolve(music["src"])
            gain = float(music.get("gainDb", -22))
            f_in = float(music.get("fadeIn", 2))
            f_out = float(music.get("fadeOut", 4))
            mode = music.get("mode", "full")
            duck = bool(music.get("duck", True))
            cmd += ["-stream_loop", "-1", "-i", msrc]

            mchain = (f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                      f"atrim=0:{dur:.3f},volume={gain}dB,"
                      f"afade=t=in:st=0:d={f_in},afade=t=out:st={max(0, dur - f_out):.3f}:d={f_out}[mus]")
            if mode == "bookends":
                intro_d = probe_duration(self.parts[0]) if self.tl.get("intro") else 0.0
                outro_d = probe_duration(self.parts[-1]) if self.tl.get("outro") else 0.0
                start2 = max(0.0, dur - outro_d - 1.0)
                mchain = (
                    f"[1:a]aformat=sample_rates=48000:channel_layouts=stereo,asplit=2[m1][m2];"
                    f"[m1]atrim=0:{intro_d + 1.5:.3f},volume={gain}dB,"
                    f"afade=t=in:st=0:d=0.8,afade=t=out:st={max(0.0, intro_d - 0.3):.3f}:d=1.8[i1];"
                    f"[m2]atrim=0:{outro_d + 1.0:.3f},volume={gain}dB,"
                    f"afade=t=in:st=0:d=1.5,afade=t=out:st={max(0.0, outro_d - 2.5):.3f}:d=2.5,"
                    f"adelay={int(start2 * 1000)}|{int(start2 * 1000)}[i2];"
                    f"[i1][i2]amix=inputs=2:duration=longest:normalize=0[mus]"
                )
            if duck and mode == "full":
                fc = (f"{mchain};[0:a]asplit=2[voice][sc];"
                      f"[mus][sc]sidechaincompress=threshold=0.015:ratio=8:attack=150:release=900[duckm];"
                      f"[voice][duckm]amix=inputs=2:duration=first:normalize=0[aout]")
            else:
                fc = f"{mchain};[0:a][mus]amix=inputs=2:duration=first:normalize=0[aout]"
            cmd += ["-filter_complex", fc, "-map", "[aout]"]
        else:
            cmd += ["-map", "0:a"]
        cmd += ["-vn", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", mix]
        sh(cmd)  # lượt 0: trộn nhạc (nếu có) ra wav

        # Lượt 1: đo loudness
        p = subprocess.run(
            ["ffmpeg", "-hide_banner", "-i", mix,
             "-af", "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json", "-f", "null", "-"],
            capture_output=True, text=True,
        )
        try:
            m = json.loads("{" + p.stderr.rsplit("{", 1)[1])
            ln = (f"loudnorm=I=-14:TP=-1.5:LRA=11:linear=true:"
                  f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                  f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
                  f"offset={m['target_offset']}")
        except Exception:
            ln = "loudnorm=I=-14:TP=-1.5:LRA=11"

        # Lượt 2: áp chuẩn hóa, ghép với video (copy, không encode lại)
        sh(["ffmpeg", "-hide_banner", "-y", "-i", body, "-i", mix,
            "-map", "0:v", "-c:v", "copy",
            "-map", "1:a", "-af",
            ln + ",aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-movflags", "+faststart", "-t", f"{dur:.3f}", self.out_file])
        try:
            open(mix, "w").close()
        except OSError:
            pass

    def write_chapters(self):
        if not self.chapters:
            return
        f = os.path.splitext(self.out_file)[0] + ".chapters.txt"
        with open(f, "w", encoding="utf-8") as fh:
            if self.chapters[0][0] > 0.01:
                fh.write("00:00 Mở đầu\n")
            for t, name in self.chapters:
                h, m, s = int(t // 3600), int(t % 3600 // 60), int(t % 60)
                ts = f"{h:d}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"
                fh.write(f"{ts} {name}\n")
        print(f"  → chapters: {f}")

    def run(self):
        print(f"[1/3] Cắt và chuẩn hóa các phần ({self.w}x{self.h} @ {self.fps}fps"
              + (", BẢN NHÁP" if self.preview else "") + ") …", flush=True)
        self.validate_timeline()
        expected = self.build_parts()
        print(f"[2/3] Ghép {len(self.parts)} phần …", flush=True)
        body = self.concat(expected)
        print("[3/3] Nhạc nền + chuẩn hóa âm lượng (-14 LUFS) …", flush=True)
        self.finalize(body)
        self.write_chapters()
        self.write_time_map()
        final_d = probe_duration(self.out_file)
        # Nghiệm thu thành phẩm: hình = tiếng và = tổng các part
        fv, fa = stream_durations(self.out_file)
        check_av(self.out_file, getattr(self, "sum_parts", None), label="THÀNH PHẨM",
                 dur_tol=0.1 + 0.01 * len(self.parts))
        with open(os.path.splitext(self.out_file)[0] + ".nghiem-thu.json", "w", encoding="utf-8") as fh:
            json.dump({"file": os.path.basename(self.out_file), "tool_version": TOOL_VERSION,
                       "parts": len(self.parts), "hinh": round(fv or 0, 3), "tieng": round(fa or 0, 3),
                       "tong_part": round(getattr(self, "sum_parts", 0) or 0, 3),
                       "ket_luan": "ĐẠT: hình = tiếng = tổng part"}, fh, ensure_ascii=False, indent=1)
        print(f"  ✓ NGHIỆM THU: hình {fv:.2f}s = tiếng {fa:.2f}s = tổng {len(self.parts)} part "
              f"({getattr(self, 'sum_parts', 0):.2f}s) → chạy thêm tools/nghiem-thu.py video để soi âm lượng/khung hình")
        size = os.path.getsize(self.out_file) / 1e6
        print(f"✓ Xong: {self.out_file}")
        print(f"  Thời lượng {int(final_d // 60)}m{final_d % 60:04.1f}s | {size:.0f} MB")
        # Dọn file tạm: VM không cho xóa file trên mount → giải phóng bằng truncate
        for p in self.parts + [os.path.join(self.tmp, "body.mp4")]:
            for f in (p, p + ".sig"):
                try:
                    os.remove(f)
                except OSError:
                    try:
                        open(f, "w").close()
                    except OSError:
                        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--project", required=True)
    ap.add_argument("--timeline", default="timeline.json")
    ap.add_argument("--preview", action="store_true", help="bản nháp 480p, encode nhanh")
    ap.add_argument("--out", default=None)
    ap.add_argument("--kiem-tra", action="store_true",
                    help="chỉ kiểm timeline (file, mốc thời gian, overlay/B-roll), không dựng")
    ap.add_argument("--ep-encode-lai", action="store_true",
                    help="cho phép encode lại body khi concat copy lệch (mặc định: DỪNG và báo)")
    args = ap.parse_args()

    tl_path = args.timeline if os.path.isabs(args.timeline) else os.path.join(args.project, args.timeline)
    with open(tl_path, encoding="utf-8") as f:
        timeline = json.load(f)
    asm = Assembler(args.project, timeline, args.preview, args.out)
    asm.allow_reencode = args.ep_encode_lai
    if args.kiem_tra:
        asm.validate_timeline()
        return
    asm.run()


if __name__ == "__main__":
    main()
