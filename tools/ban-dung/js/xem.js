// Bộ xem trước của Bàn dựng: phát bố cục của MoHinh bằng các thẻ <video> gốc, không dựng lại gì.
//
// Cách làm (gọn mà mượt): mỗi file nguồn có MỘT thẻ <video> dùng chung. Hai đoạn liền nhau trong cùng
// một file (rất hay gặp: đoạn bị tách chỉ để gắn overlay) phát liền một mạch, không tua, không giật.
// Thẻ mang tiếng là đồng hồ chủ; hình (B-roll, góc máy multicam) bám theo đồng hồ đó.
// Xem trước là GẦN ĐÚNG: bố cục slide, đơn màu, chuẩn hoá -14 LUFS, nhạc giảm khi có lời chỉ có
// ở bản dựng thật (tools/assemble.py).

import { clamp, dbSangHeSo, timTruoc } from "./tien-ich.js";

const LECH_TUA = 0.12;       // giây: hình lệch đồng hồ quá mức này thì tua lại
const LECH_OVERLAY = 0.15;

export class BoXem {
  constructor(san, moHinh, urlMedia) {
    this.san = san;               // khung sân khấu
    this.mh = moHinh;
    this.url = urlMedia;
    this.kho = new Map();         // src -> <video>
    this.khoOv = new Map();       // "ov:k" -> <video> (overlay có thể dùng cùng file ở hai chỗ)
    this.T = 0;
    this.dangPhat = false;
    this.toc = 1;
    this.span = null;
    this.nghe = new Set();
    this.lopDen = san.querySelector(".lop-den");
    this.nhan = san.querySelector(".nhan-san");
    this.nhacEl = null;
    this.ctx = null;
    this.gain = null;
    this._nhinTam = null;
    this._raf = this._raf.bind(this);
    requestAnimationFrame(this._raf);
  }

  // ---------- phần tử ----------
  _video(src, ov = false, khoa = null) {
    const kho = ov ? this.khoOv : this.kho;
    const k = khoa || src;
    let v = kho.get(k);
    if (!v) {
      v = document.createElement("video");
      v.preload = "auto";
      v.playsInline = true;
      v.crossOrigin = "anonymous";
      v.src = this.url(src);
      v.className = ov ? "v-ov" : "v-nen";
      v.style.visibility = "hidden";
      v.muted = true;
      this.san.insertBefore(v, this.lopDen);
      kho.set(k, v);
    }
    return v;
  }

  /** Đo thời lượng các file (trình duyệt đọc phần đầu file). */
  async doThoiLuong(srcs) {
    const mot = (src) => new Promise((ok) => {
      const v = document.createElement("video");
      v.preload = "metadata";
      v.muted = true;
      let xong = false;
      const tra = (d) => { if (!xong) { xong = true; v.removeAttribute("src"); v.load(); ok(d); } };
      v.onloadedmetadata = () => {
        if (isFinite(v.duration) && v.duration > 0) return tra(v.duration);
        // WebM ghi bằng MediaRecorder không có thời lượng ở đầu file: tua thật xa để trình duyệt tự tính
        v.ondurationchange = () => { if (isFinite(v.duration)) tra(v.duration); };
        v.currentTime = 1e7;
      };
      v.onerror = () => tra(NaN);
      setTimeout(() => tra(NaN), 12000);
      v.src = this.url(src);
    });
    const kq = {};
    const ds = [...new Set(srcs)];
    for (let i = 0; i < ds.length; i += 6) {
      const lo = ds.slice(i, i + 6);
      const d = await Promise.all(lo.map(mot));
      lo.forEach((s, j) => (kq[s] = d[j]));
    }
    return kq;
  }

  // ---------- điều khiển ----------
  phat() {
    if (this.dangPhat) return;
    const tong = this.mh.boCuc().tong;
    if (this.T >= tong - 0.05) this.T = 0;
    this.dangPhat = true;
    this._moAmThanh();
    this._vaoSpan(this._spanTai(this.T), true);
    this._baoTin();
  }
  dung() {
    if (!this.dangPhat) return;
    this.dangPhat = false;
    for (const v of this.kho.values()) v.pause();
    for (const v of this.khoOv.values()) v.pause();
    if (this.nhacEl) this.nhacEl.pause();
    this._baoTin();
  }
  batTat() { this.dangPhat ? this.dung() : this.phat(); }
  datToc(r) {
    this.toc = r;
    for (const v of this.kho.values()) v.playbackRate = r;
    for (const v of this.khoOv.values()) v.playbackRate = r;
    if (this.nhacEl) this.nhacEl.playbackRate = r;
  }
  tua(T) {
    const tong = this.mh.boCuc().tong;
    this.T = clamp(T, 0, Math.max(0, tong - 1 / this.mh.fps / 2));
    this._nhinTam = null;
    this._vaoSpan(this._spanTai(this.T), this.dangPhat, true);
    this._capNhatPhu(true);
    this._baoTin();
  }
  /** Bố cục vừa đổi (bạn sửa): giữ nguyên mốc, đồng bộ lại. */
  boCucDoi() {
    this.span = null;
    this.tua(this.T);
  }
  /** Xem tạm một khung nguồn (khi đang kéo tỉa), không đổi mốc đầu đọc. */
  nhinKhung(src, t) {
    const v = this._video(src);
    this._nhinTam = v;
    for (const x of this.kho.values()) x.style.visibility = x === v ? "visible" : "hidden";
    for (const x of this.khoOv.values()) x.style.visibility = "hidden";
    this.lopDen.style.opacity = 0;
    if (Math.abs(v.currentTime - t) > 0.01) v.currentTime = t;
  }
  thoiNhin() {
    if (!this._nhinTam) return;
    this._nhinTam = null;
    this.tua(this.T);
  }

  // ---------- lõi ----------
  _spanTai(T) {
    const sp = this.mh.boCuc().spans;
    const j = timTruoc(sp, T + 1e-6, (s) => s.t0);
    return sp[Math.max(0, j)] || null;
  }

  _vaoSpan(s, phat, ep = false) {
    if (!s) return;
    const truoc = this.span;
    this.span = s;
    const vh = this._video(s.hinh.src);
    const vt = s.tieng ? this._video(s.tieng.src) : vh;
    const tuHinh = s.hinh.tu + (this.T - s.t0);
    const tuTieng = s.tieng ? s.tieng.tu + (this.T - s.t0) : tuHinh;
    // âm: chỉ thẻ mang tiếng được mở tiếng
    for (const v of this.kho.values()) {
      const dung = v === vh || v === vt;
      v.style.visibility = v === vh ? "visible" : "hidden";
      v.muted = v !== vt;
      if (!dung && !v.paused) v.pause();
    }
    const lienMach = !ep && truoc && phat && !truoc.chen && !s.chen &&
      Math.abs(vt.currentTime - tuTieng) < 0.08;
    if (!lienMach && Math.abs(vt.currentTime - tuTieng) > 0.005) vt.currentTime = tuTieng;
    if (vh !== vt && Math.abs(vh.currentTime - tuHinh) > (phat ? LECH_TUA : 0.005)) vh.currentTime = tuHinh;
    for (const v of new Set([vh, vt])) {
      v.playbackRate = this.toc;
      if (phat) { if (v.paused) v.play().catch(() => {}); } else if (!v.paused) v.pause();
    }
    this._ganNhan(s);
  }

  _ganNhan(s) {
    const seg = s.it && s.it.seg;
    const ds = [];
    if (seg && seg.layout && seg.layout !== "mat" && !s.broll) ds.push(`Bố cục "${seg.layout}": slide chỉ hiện ở bản dựng thật`);
    if (this.mh.tl.colorGrade) ds.push("Chỉnh màu chỉ có ở bản dựng thật");
    this.nhan.textContent = ds.join(" · ");
    this.nhan.style.display = ds.length ? "block" : "none";
    // khung dọc: cắt theo cropFocus
    const vh = this._video(s.hinh.src);
    vh.style.objectPosition = this.mh.doc && seg ? `${(seg.cropFocus !== undefined ? +seg.cropFocus : 0.5) * 100}% 50%` : "50% 50%";
  }

  _moAmThanh() {
    const m = this.mh.tl.music;
    if (!m || !m.src) return;
    try {
      if (!this.ctx) this.ctx = new (window.AudioContext || window.webkitAudioContext)();
      if (this.ctx.state === "suspended") this.ctx.resume();
      if (!this.nhacEl || this.nhacEl.dataset.src !== m.src) {
        if (this.nhacEl) this.nhacEl.pause();
        const a = new Audio();
        a.crossOrigin = "anonymous";
        a.preload = "auto";
        a.src = this.url(m.src);
        a.dataset.src = m.src;
        const nguon = this.ctx.createMediaElementSource(a);
        this.gain = this.ctx.createGain();
        this.gain.gain.value = 0;
        nguon.connect(this.gain).connect(this.ctx.destination);
        this.nhacEl = a;
      }
    } catch (e) {
      console.warn("không mở được nhạc", e);
    }
  }

  /** Đường bao nhạc tại T (hệ số biên độ) và vị trí trong file nhạc. */
  _nhacTai(T) {
    for (const p of this.mh.boCuc().nhac) {
      if (T < p.t0 || T >= p.t1) continue;
      const x = T - p.t0;
      let he = dbSangHeSo(p.g);
      if (p.fi > 0 && x < p.fi) he *= x / p.fi;
      if (p.foD > 0 && x > p.foSt) he *= clamp(1 - (x - p.foSt) / p.foD, 0, 1);
      return { he, vt: p.tu + x, lap: p.lap };
    }
    return null;
  }

  _capNhatPhu(ep) {
    const bc = this.mh.boCuc();
    const T = this.T;
    // overlay
    const dangCo = new Set();
    bc.overlays.forEach((o) => {
      if (T < o.t0 || T >= o.t1) return;
      const khoa = `${o.i}:${o.k}:${o.src}`;
      dangCo.add(khoa);
      const v = this._video(o.src, true, khoa);
      v.style.visibility = "visible";
      // thời lượng thẻ đã đổi: giữ khung tại H thêm X giây, hoặc bỏ quãng [H, H-X] (X âm)
      const tau = T - o.t0, ts = o.ts || { H: 0, X: 0 };
      let can = tau, giu = false;
      if (ts.X > 0 && tau >= ts.H) { if (tau < ts.H + ts.X) { can = ts.H; giu = true; } else can = tau - ts.X; }
      else if (ts.X < 0 && tau >= ts.H) can = tau - ts.X;
      if (ep || !this.dangPhat || giu || Math.abs(v.currentTime - can) > LECH_OVERLAY) {
        if (Math.abs(v.currentTime - can) > 0.02 || ep) v.currentTime = can;
      }
      v.playbackRate = this.toc;
      if (this.dangPhat && !giu) { if (v.paused) v.play().catch(() => {}); } else if (!v.paused) v.pause();
    });
    for (const [k, v] of this.khoOv) if (!dangCo.has(k)) { v.style.visibility = "hidden"; if (!v.paused) v.pause(); }
    // mờ đen và mờ tiếng
    let den = 0, am = 1;
    const s = this.span;
    if (s && s.it) {
      const seg = s.it.seg;
      if (seg) {
        const fi = +seg.fadeIn || 0, fo = +seg.fadeOut || 0, foa = +seg.fadeOutAudio || 0;
        const x = T - s.it.t0, con = s.it.t1 - T;
        if (fi > 0 && x < fi) { den = Math.max(den, 1 - x / fi); am = Math.min(am, x / fi); }
        if (fo > 0 && con < fo) { den = Math.max(den, 1 - con / fo); am = Math.min(am, con / fo); }
        else if (foa > 0 && con < foa) am = Math.min(am, con / foa);
      }
      const vt = s.tieng ? this._video(s.tieng.src) : this._video(s.hinh.src);
      const vdb = seg && seg.volumeDb ? Math.min(1, dbSangHeSo(+seg.volumeDb)) : 1;
      vt.volume = clamp(am * vdb, 0, 1);
    }
    this.lopDen.style.opacity = den;
    this.lopDen.style.background = this.mh.tl.fadeColor || "black";
    // nhạc
    if (this.nhacEl && this.gain) {
      const n = this._nhacTai(T);
      if (!n) {
        this.gain.gain.value = 0;
        if (!this.nhacEl.paused) this.nhacEl.pause();
      } else {
        this.gain.gain.value = n.he;
        const d = this.nhacEl.duration;
        const vt = n.lap && isFinite(d) && d > 0 ? n.vt % d : n.vt;
        if (ep || Math.abs(this.nhacEl.currentTime - vt) > 0.25) this.nhacEl.currentTime = vt;
        this.nhacEl.playbackRate = this.toc;
        if (this.dangPhat) { if (this.nhacEl.paused) this.nhacEl.play().catch(() => {}); }
        else if (!this.nhacEl.paused) this.nhacEl.pause();
      }
    }
  }

  _raf() {
    requestAnimationFrame(this._raf);
    if (!this.dangPhat || this._nhinTam) return;
    const s = this.span;
    if (!s) return;
    const vh = this._video(s.hinh.src);
    const vt = s.tieng ? this._video(s.tieng.src) : vh;
    const tu = s.tieng ? s.tieng.tu : s.hinh.tu;
    if (!vt.seeking && vt.readyState >= 2) this.T = s.t0 + (vt.currentTime - tu);
    const tong = this.mh.boCuc().tong;
    if (this.T >= s.t1 - 0.004) {
      const sp = this.mh.boCuc().spans;
      const j = sp.indexOf(s);
      const ke = sp[j + 1];
      if (!ke || this.T >= tong - 0.004) { this.T = tong; this.dung(); return; }
      this.T = ke.t0;
      this._vaoSpan(ke, true);
    } else if (vh !== vt) {
      const can = s.hinh.tu + (this.T - s.t0);
      if (!vh.seeking && Math.abs(vh.currentTime - can) > LECH_TUA) vh.currentTime = can;
    }
    this._capNhatPhu(false);
    this._baoTin();
  }

  _baoTin() { for (const f of this.nghe) f(this.T, this.dangPhat); }
}
