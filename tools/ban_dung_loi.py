# -*- coding: utf-8 -*-
"""Quy tắc đặt điểm cắt cho Dựng bằng lời (dùng chung cho tools/ban-dung.py, bộ kiểm và phòng nghe thử).
Thuần Python, không cần numpy: chạy được bằng python3 có sẵn trên Mac lẫn trong VM.

Đầu vào: danh sách âm tiết `tu` của tools/moc-tu.py ({w, s, e, c, k}, giây trong file nguồn) và năng lượng
tiếng `nl` (bytes, 100 khung mỗi giây, byte = dB + 100). Đầu ra: mốc giây trong file nguồn để ghi vào
`in`/`out` của đoạn trong timeline.json, kèm cờ `gat` khi không có khe sạch.

Nguyên tắc (claude/ban-dung-dac-ta.md, BAI-HOC chủ đề "Dựng bằng lời"):
  - chỉ cắt trong khe giữa hai âm tiết, không bao giờ giữa một âm tiết (Berthouzoz và cộng sự, 2012);
  - mốc CTC cho biết âm tiết nào ở đâu; năng lượng tiếng cho biết tiếng thật sự bắt đầu, tắt ở đâu;
  - vào lời: giữ lề LE_VAO trước tiếng bắt đầu; ra lời: giữ lề LE_RA sau tiếng tắt (tiếng nói tắt dần
    chậm hơn lúc khởi), nhưng luôn cách âm tiết bị bỏ ít nhất CACH_BO;
  - không có dải lặng: cắt ở đáy thung năng lượng nếu thung đủ sâu (khe hẹp), không thì gắn cờ gat để
    người dùng quyết; Bàn dựng không tự cắt chỗ gat.
"""

import math

HZ = 100
LE_VAO = 0.12       # giây giữ trước tiếng của âm tiết đầu được giữ (bằng lề của snap_point trong assemble.py)
LE_RA = 0.20        # giây giữ sau tiếng của âm tiết cuối được giữ (auto-editor --margin mặc định 0,2)
CACH_BO = 0.03      # không đặt điểm cắt gần âm tiết bị bỏ hơn mức này
THAN_TOI_THIEU = 0.06  # giây: âm tiết phải có thân tiếng riêng ít nhất chừng này giữa hai khe
DO_SAU = 10.0       # dB: thung năng lượng sâu tới mức này giữa hai âm tiết vẫn cắt được (khe hẹp)


def san(nl):
    """Sàn ồn (dB): phân vị 10 của năng lượng."""
    if not nl:
        return -60.0
    xs = sorted(nl[::7]) or [40]
    return xs[len(xs) // 10] - 100.0


class Loi:
    def __init__(self, tu, nl, san_on=None):
        self.tu = tu
        self.nl = nl
        self.san = san(nl) if san_on is None else san_on
        self.lang = self.san + 10      # dưới mức này: lặng
        self._cache = {}

    def db(self, t):
        i = int(round(t * HZ))
        if i < 0 or i >= len(self.nl):
            return self.san
        return self.nl[i] - 100.0

    def _e(self, i):
        return (self.nl[i] - 100.0) if 0 <= i < len(self.nl) else self.san

    def khe(self, i):
        """Khe giữa âm tiết i và i+1 (i = -1: trước âm tiết đầu; i = len-1: sau âm tiết cuối).
        Trả {loai, g0, g1, m} theo giây:
          loai "lang": có dải lặng thật [g0, g1) (dưới sàn ồn + 10 dB);
          loai "hep":  không lặng nhưng có thung năng lượng sâu từ DO_SAU dB trở lên tại m;
          loai "gat":  hai âm tiết dính liền, m là điểm năng lượng thấp nhất (cắt sẽ nghe gượng).
        Vùng tìm: từ mốc cuối CTC của âm tiết trái trừ 0,06 s (nhưng không sớm hơn đầu âm tiết trái
        cộng 0,08 s, làm tròn lên khung kế: sát đầu chữ là chỗ tiếng mới nhú, năng lượng còn thấp, dễ bị
        nhận nhầm là khe; ví dụ "hôm" trong "thì ờ hôm nay", Pha 2) tới đầu âm tiết phải cộng 0,06 s. Nguyên âm kéo dài như "ờ..." có đỉnh CTC nằm bất kỳ
        đâu trong nguyên âm nên mốc cuối CTC chỉ là cận dưới của chỗ tiếng tắt, không phải chỗ tắt."""
        if i in self._cache:
            return self._cache[i]
        r = dict(self._khe_tho(i))
        # Âm tiết dính: khe trái và khe phải của một âm tiết gần như trùng nhau (âm tiết không có thân tiếng
        # riêng giữa hai khe, thường là từ đệm "á", "ờ" kéo liền với chữ trước). Khi đó khe này không tách
        # được hai âm tiết, coi là gat để người dùng bỏ cả cụm.
        if r["loai"] != "gat":
            for trai, phai in ((i - 1, i), (i, i + 1)):
                if trai < -1 or phai > len(self.tu) - 1 or trai == i and phai == i:
                    continue
                kt, kp = (self._khe_tho(trai), r) if phai == i else (r, self._khe_tho(phai))
                if kt["loai"] != "gat" and kp["loai"] != "gat" and kp["g0"] - kt["g1"] < THAN_TOI_THIEU:
                    r.update(loai="gat", dinh=True)
                    break
        self._cache[i] = r
        return r

    def _khe_tho(self, i):
        if ("tho", i) in self._cache:
            return self._cache[("tho", i)]
        tu, n = self.tu, len(self.nl)
        if i < 0:
            a, b = max(0, int((tu[0]["s"] - 2.0) * HZ)), int((tu[0]["s"] + 0.06) * HZ)
        elif i >= len(tu) - 1:
            a, b = int((tu[-1]["s"] + 0.04) * HZ), min(n - 1, int((tu[-1]["e"] + 2.0) * HZ))
        else:
            # đầu vùng: không sớm hơn mốc cuối CTC của âm tiết trái trừ 0,06 s. Chữ nhiều âm (tên nước ngoài
            # như "vitoling") có khe lặng bên trong (âm tắc /t/); tìm từ đầu chữ sẽ cắt lẹm giữa chữ.
            a = math.ceil(max(tu[i]["s"] + 0.08, tu[i]["e"] - 0.06) * HZ)
            b = int((tu[i + 1]["s"] + 0.06) * HZ)
            if b - a < 2:
                a, b = a - 2, b + 2
        a, b = max(0, a), min(n - 1, max(a + 1, b))
        m = min(range(a, b + 1), key=lambda k: (self._e(k), -k))
        if self._e(m) < self.lang:
            g0 = m
            while g0 - 1 >= a and self._e(g0 - 1) < self.lang:
                g0 -= 1
            g1 = m
            while g1 + 1 <= b and self._e(g1 + 1) < self.lang:
                g1 += 1
            r = {"loai": "lang", "g0": g0 / HZ, "g1": (g1 + 1) / HZ, "m": m / HZ}
        else:
            trai = max(self._e(k) for k in range(max(0, m - 30), m + 1))
            phai = max(self._e(k) for k in range(m, min(n, m + 31)))
            sau = min(trai, phai) - self._e(m)
            r = {"loai": "hep" if sau >= DO_SAU else "gat", "g0": m / HZ, "g1": m / HZ, "m": m / HZ,
                 "sau": round(sau, 1)}
        self._cache[("tho", i)] = r
        return r

    def diem_vao(self, j):
        """Điểm vào khi giữ âm tiết j làm âm tiết đầu (bỏ mọi thứ trước nó)."""
        k = self.khe(j - 1)
        if k["loai"] == "lang":
            t = max(k["g1"] - LE_VAO, k["g0"] + CACH_BO if j > 0 else 0.0)
            return {"t": round(min(t, k["g1"]), 3), "loai": "lang", "gat": False}
        return {"t": round(k["m"], 3), "loai": k["loai"], "gat": k["loai"] == "gat"}

    def diem_ra(self, i):
        """Điểm ra khi giữ âm tiết i làm âm tiết cuối (bỏ mọi thứ sau nó)."""
        k = self.khe(i)
        if k["loai"] == "lang":
            cuoi = i >= len(self.tu) - 1
            t = min(k["g0"] + LE_RA, k["g1"] - CACH_BO if not cuoi else k["g0"] + LE_RA)
            return {"t": round(max(t, k["g0"]), 3), "loai": "lang", "gat": False}
        return {"t": round(k["m"], 3), "loai": k["loai"], "gat": k["loai"] == "gat"}


def doc(du_an_dir, base):
    """Đọc <base>.tu.json và <base>.nang-luong.bin trong transcript/ của dự án."""
    import json
    import os
    td = os.path.join(du_an_dir, "transcript")
    d = json.load(open(os.path.join(td, f"{base}.tu.json"), encoding="utf-8"))
    nl = open(os.path.join(td, d["nangLuong"]["file"]), "rb").read()
    return Loi(d["tu"], nl, d["nangLuong"].get("san")), d
