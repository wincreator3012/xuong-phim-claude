// Mô hình dữ liệu của Bàn dựng: giữ timeline.json gốc (mọi trường lạ được giữ nguyên), tính bố cục
// dòng thời gian ĐÚNG như tools/assemble.py dựng, và các thao tác sửa có hoàn tác.
//
// Quy ước của assemble.py mà file này bám theo (đọc kỹ trước khi sửa):
//   - segments nối liền nhau, không có khoảng trống (dòng thời gian kiểu nam châm);
//   - "in"/"out" là giây trong file nguồn; "snap" mặc định BẬT: điểm cắt hút về khoảng lặng gần nhất
//     (transcript/<nguồn>.silences.json, dung sai 1 s, lề 0,12 s);
//   - overlay.at tính TƯƠNG ĐỐI từ đầu đoạn, chỉ phủ lên quãng trước B-roll đầu tiên; overlay.duration (tuỳ
//     chọn) đổi thời lượng thẻ: dài hơn file thì giữ khung tại "giu" (mặc định giữa file), ngắn hơn thì bỏ
//     một quãng từ "giu", đúng như Assembler._keo_overlay();
//   - volumeDb của đoạn: tăng/giảm tiếng riêng đoạn đó;
//   - broll.at tính theo mốc TRONG FILE NGUỒN, hình lấy từ broll.src tại "from", tiếng vẫn của đoạn;
//   - intro/outro ở cấp cao nhất đứng đầu/cuối; insert có role "intro"/"outro" đánh dấu chỗ nhạc bookends;
//   - fadeIn/fadeOut mờ cả hình lẫn tiếng ở đầu/cuối đoạn; fadeOutAudio chỉ mờ tiếng cuối đoạn;
//   - multicam: hình từ src, tiếng từ audioSrc bắt đầu tại audioIn.

import { clamp, r3, sao } from "./tien-ich.js";

export const DOAN_NGAN_NHAT = 0.3;

/** Bản sao đúng snap_point() của assemble.py. */
export function hutKhoangLang(t, sil, mode, tol = 1.0, le = 0.12) {
  let best = null, bestD = tol;
  for (const s of sil || []) {
    const neo = mode === "in" ? s.end : s.start;
    const d = Math.abs(neo - t);
    if (d < bestD || (s.start - 0.01 <= t && t <= s.end + 0.01 && mode === "in")) {
      if (s.start - tol <= t && t <= s.end + tol) { best = s; bestD = Math.min(d, bestD); }
    }
  }
  if (!best) return t;
  return mode === "in" ? Math.max(0, best.end - le) : best.start + le;
}

export function laInsert(seg) {
  return (seg.type || "video") === "insert";
}

export function dsOverlay(seg) {
  const o = seg.overlay;
  return o ? (Array.isArray(o) ? o : [o]) : [];
}

/** Thông số thời lượng thẻ, bản sao Assembler._keo_overlay(): {N, D, H, X} - X > 0 giữ thêm, X < 0 bớt. */
export function thongSoThe(o, N, fps = 30) {
  if (o.duration === undefined || o.duration === null || Math.abs(+o.duration - N) < 0.5 / fps)
    return { N, D: N, H: N / 2, X: 0 };
  let H = o.giu !== undefined ? +o.giu : N / 2;
  H = Math.min(Math.max(H, 0.1), Math.max(0.1, N - 0.1));
  let X = +o.duration - N;
  if (X < 0) X = -Math.min(-X, Math.max(0, N - H - 0.2));
  return { N, D: N + X, H, X };
}
export const THE_NGAN_NHAT = 0.3;

export class MoHinh {
  constructor(tl, thongTin) {
    this.tl = tl;
    this.p = thongTin.p;
    this.duAn = thongTin.duAn;
    this.phienBan = thongTin.phienBan;
    this.daLuu = JSON.stringify(tl);
    this.lich = [];
    this.lai = [];
    this.thoiLuong = {};   // src -> giây (đo bằng trình duyệt)
    this.phu = {};         // src -> {silences, cau, tu, nangLuong}
    this.nghe = new Set();
    this._tam = null;      // ảnh chụp trước khi kéo
    this._bc = null;
  }

  get fps() { return +this.tl.fps || 30; }
  get doc() { return this.tl.aspect === "doc"; }
  get thayDoi() { return JSON.stringify(this.tl) !== this.daLuu; }

  baoTin(ly) { this._bc = null; for (const f of this.nghe) f(ly); }

  // ---------- lịch sử ----------
  sua(moTa, fn) {
    const truoc = JSON.stringify(this.tl);
    fn(this.tl);
    if (JSON.stringify(this.tl) === truoc) return false;
    this.lich.push({ tl: truoc, moTa });
    if (this.lich.length > 300) this.lich.shift();
    this.lai = [];
    this.baoTin(moTa);
    return true;
  }
  /** Bắt đầu một thao tác kéo: mọi thay đổi tạm cho tới ketThucKeo() là một bước hoàn tác. */
  batDauKeo() { this._tam = JSON.stringify(this.tl); }
  keo(fn) {
    if (this._tam === null) return;
    this.tl = JSON.parse(this._tam);
    this._bc = null;
    fn(this.tl);
    this.baoTin("keo");
  }
  ketThucKeo(moTa) {
    if (this._tam === null) return;
    const truoc = this._tam;
    this._tam = null;
    if (JSON.stringify(this.tl) !== truoc) {
      this.lich.push({ tl: truoc, moTa });
      this.lai = [];
    }
    this.baoTin(moTa);
  }
  huyKeo() {
    if (this._tam === null) return;
    this.tl = JSON.parse(this._tam);
    this._tam = null;
    this.baoTin("huy");
  }
  hoanTac() {
    const x = this.lich.pop();
    if (!x) return null;
    this.lai.push({ tl: JSON.stringify(this.tl), moTa: x.moTa });
    this.tl = JSON.parse(x.tl);
    this.baoTin("hoan-tac");
    return x.moTa;
  }
  lamLai() {
    const x = this.lai.pop();
    if (!x) return null;
    this.lich.push({ tl: JSON.stringify(this.tl), moTa: x.moTa });
    this.tl = JSON.parse(x.tl);
    this.baoTin("lam-lai");
    return x.moTa;
  }
  daGhi(phienBan, tlDaGhi) {
    this.phienBan = phienBan;
    if (tlDaGhi) this.tl._chinhTay = tlDaGhi._chinhTay;
    this.daLuu = JSON.stringify(this.tl);
    this.baoTin("da-luu");
  }

  // ---------- đo ----------
  dur(src) {
    const d = this.thoiLuong[src];
    return isFinite(d) && d > 0 ? d : 5;
  }
  /** Điểm vào/ra thật sự assemble sẽ dùng (đã tính hút khoảng lặng). */
  inOut(seg) {
    const a0 = +seg.in || 0;
    const b0 = seg.out !== undefined && seg.out !== null ? +seg.out : this.dur(seg.src);
    if (seg.snap === false) return { a: a0, b: b0, daHut: false };
    const sil = (this.phu[seg.src] || {}).silences;
    if (!sil || !sil.length) return { a: a0, b: b0, daHut: false };
    const a = hutKhoangLang(a0, sil, "in"), b = hutKhoangLang(b0, sil, "out");
    return { a, b, daHut: Math.abs(a - a0) > 1e-3 || Math.abs(b - b0) > 1e-3 };
  }

  /** Bố cục toàn bộ thành phẩm theo thời gian xuất. Được nhớ đệm tới lần sửa kế. */
  boCuc() {
    if (this._bc) return this._bc;
    const tl = this.tl;
    const items = [], overlays = [], brolls = [], spans = [], chuong = [], vaiTro = {};
    let t = 0;
    const themInsert = (loai, i, src, seg) => {
      const d = this.dur(src);
      const it = { loai, i, src, t0: t, t1: t + d, seg };
      items.push(it);
      spans.push({ t0: t, t1: t + d, hinh: { src, tu: 0 }, tieng: null, it, chen: true });
      t += d;
      return it;
    };
    if (tl.intro) vaiTro.intro = themInsert("intro", -1, tl.intro, null);
    (tl.segments || []).forEach((seg, i) => {
      if (seg.chapter) chuong.push({ t, ten: seg.chapter, i });
      if (laInsert(seg)) {
        const it = themInsert("insert", i, seg.src, seg);
        if ((seg.role === "intro" || seg.role === "outro") && !vaiTro[seg.role]) vaiTro[seg.role] = it;
        return;
      }
      const { a, b, daHut } = this.inOut(seg);
      const d = Math.max(0, b - a);
      const it = { loai: "doan", i, src: seg.src, t0: t, t1: t + d, a, b, daHut, seg };
      items.push(it);
      const tiengCua = (x) => seg.audioSrc
        ? { src: seg.audioSrc, tu: (seg.audioIn !== undefined ? +seg.audioIn : a) + (x - a) }
        : { src: seg.src, tu: x };
      const bl = (seg.broll || []).map((x, k) => ({ x, k })).sort((p, q) => +p.x.at - +q.x.at);
      let cur = a, firstEnd = b;
      const doanCon = [];
      for (const { x, k } of bl) {
        const bat = Math.max(a, +x.at), bend = Math.min(b, bat + +x.duration);
        if (bat > cur) doanCon.push({ loai: "chinh", x0: cur, x1: bat });
        if (bend > bat) doanCon.push({ loai: "broll", x0: bat, x1: bend, b: x, k });
        brolls.push({ i, k, src: x.src, t0: t + (bat - a), t1: t + (Math.max(bat, bend) - a), b: x, it });
        cur = Math.max(cur, bend);
      }
      if (cur < b) doanCon.push({ loai: "chinh", x0: cur, x1: b });
      if (doanCon.length && doanCon[0].loai === "broll") firstEnd = a;
      else if (doanCon.length > 1) firstEnd = doanCon[0].x1;
      doanCon.forEach((c, j) => {
        const s = {
          t0: t + (c.x0 - a), t1: t + (c.x1 - a), it, i,
          dau: j === 0, cuoi: j === doanCon.length - 1,
        };
        if (c.loai === "broll") {
          s.hinh = { src: c.b.src, tu: +c.b.from || 0 };
          s.tieng = tiengCua(c.x0);
          s.broll = true;
        } else {
          s.hinh = { src: seg.src, tu: c.x0 };
          s.tieng = seg.audioSrc ? tiengCua(c.x0) : null;
        }
        spans.push(s);
      });
      dsOverlay(seg).forEach((o, k) => {
        const t0 = t + (+o.at || 0);
        const het = t + (firstEnd - a);
        const ts = thongSoThe(o, this.dur(o.src), this.fps);
        overlays.push({ i, k, src: o.src, t0, t1: Math.max(t0, Math.min(t0 + ts.D, het)),
                        tuNhien: t0 + ts.D, ts, o, it });
      });
      t += d;
    });
    if (tl.outro) vaiTro.outro = themInsert("outro", -1, tl.outro, null);
    const tong = t;
    // Nhạc: đúng công thức finalize của assemble.py
    const nhac = [];
    const m = tl.music;
    if (m && m.src) {
      const g = m.gainDb !== undefined ? +m.gainDb : -22;
      if ((m.mode || "full") === "bookends") {
        if (vaiTro.intro) {
          const st = vaiTro.intro.t0, d = vaiTro.intro.t1 - vaiTro.intro.t0;
          nhac.push({ t0: st, t1: Math.min(tong, st + d + 1.5), fi: 0.8, foSt: Math.max(0, d - 0.3), foD: 1.8, g, tu: 0 });
        }
        if (vaiTro.outro) {
          const st = vaiTro.outro.t0, d = vaiTro.outro.t1 - vaiTro.outro.t0, s2 = Math.max(0, st - 1);
          nhac.push({ t0: s2, t1: Math.min(tong, s2 + d + 1), fi: 1.5, foSt: Math.max(0, d - 2.5), foD: 2.5, g, tu: 0 });
        }
      } else {
        const fi = m.fadeIn !== undefined ? +m.fadeIn : 2, fo = m.fadeOut !== undefined ? +m.fadeOut : 4;
        nhac.push({ t0: 0, t1: tong, fi, foSt: Math.max(0, tong - fo), foD: fo, g, tu: 0, lap: true });
      }
    }
    this._bc = { items, overlays, brolls, spans, chuong, nhac, tong, vaiTro };
    return this._bc;
  }

  /** Mục dòng thời gian đang chứa mốc xuất T. */
  mucTai(T) {
    const { items } = this.boCuc();
    for (const it of items) if (T >= it.t0 && T < it.t1) return it;
    return items.length && T >= items[items.length - 1].t1 ? items[items.length - 1] : null;
  }

  // ---------- thao tác ----------
  /** Ghi cứng điểm hút khoảng lặng rồi tắt snap, để chỉnh tay không bị hút lệch đi. */
  _ghiCungHut(seg) {
    if (seg.snap === false) return;
    const { a, b } = this.inOut(seg);
    seg.in = r3(a);
    seg.out = r3(b);
    seg.snap = false;
  }

  tiaVao(tl, i, aMoi) {
    const seg = tl.segments[i];
    this._ghiCungHut(seg);
    const b = +seg.out, a = +seg.in || 0;
    aMoi = r3(clamp(aMoi, 0, b - DOAN_NGAN_NHAT));
    const delta = aMoi - a;
    if (!delta) return;
    seg.in = aMoi;
    // overlay neo theo lời: thẻ vẫn hiện đúng câu nói
    const ov = dsOverlay(seg);
    if (ov.length) {
      const giu = [];
      for (const o of ov) {
        const at = r3((+o.at || 0) - delta);
        if (at + 0.2 > 0) giu.push(Object.assign(o, { at: Math.max(0, at) }));
      }
      seg.overlay = giu;
      if (!giu.length) delete seg.overlay;
    }
    if (seg.audioSrc && seg.audioIn !== undefined) seg.audioIn = r3(+seg.audioIn + delta);
    this._kepBroll(seg);
  }

  tiaRa(tl, i, bMoi) {
    const seg = tl.segments[i];
    this._ghiCungHut(seg);
    const a = +seg.in || 0;
    seg.out = r3(clamp(bMoi, a + DOAN_NGAN_NHAT, Math.max(a + DOAN_NGAN_NHAT, this.dur(seg.src))));
    this._kepBroll(seg);
  }

  /** B-roll ra ngoài đoạn sau khi tỉa: kẹp lại cho vừa, còn quá ngắn thì bỏ. */
  _kepBroll(seg) {
    if (!seg.broll) return;
    const a = +seg.in || 0, b = +seg.out;
    const giu = [];
    for (const x of seg.broll) {
      let at = +x.at, d = +x.duration, from = +x.from || 0;
      if (at < a) { from += a - at; d -= a - at; at = a; }
      if (at + d > b) d = b - at;
      if (d >= 0.2) giu.push(Object.assign(x, { at: r3(at), duration: r3(d), from: r3(from) }));
    }
    if (giu.length) seg.broll = giu; else delete seg.broll;
  }

  /** Tách đoạn i tại mốc nguồn x. Trả chỉ số đoạn sau. */
  tach(tl, i, x) {
    const seg = tl.segments[i];
    this._ghiCungHut(seg);
    const a = +seg.in || 0, b = +seg.out;
    x = r3(x);
    if (x - a < DOAN_NGAN_NHAT || b - x < DOAN_NGAN_NHAT) return -1;
    const s1 = sao(seg), s2 = sao(seg);
    s1.out = x;
    s2.in = x;
    delete s2.chapter;
    delete s2.fadeIn;
    delete s1.fadeOut;
    delete s1.fadeOutAudio;
    if (seg.audioSrc && seg.audioIn !== undefined) s2.audioIn = r3(+seg.audioIn + (x - a));
    const ov = dsOverlay(seg);
    const o1 = ov.filter((o) => a + (+o.at || 0) < x);
    const o2 = ov.filter((o) => a + (+o.at || 0) >= x).map((o) => Object.assign(sao(o), { at: r3(a + (+o.at || 0) - x) }));
    if (o1.length) s1.overlay = sao(o1); else delete s1.overlay;
    if (o2.length) s2.overlay = o2; else delete s2.overlay;
    const b1 = [], b2 = [];
    for (const r of seg.broll || []) {
      const at = +r.at, d = +r.duration, from = +r.from || 0;
      if (at + d <= x) b1.push(sao(r));
      else if (at >= x) b2.push(sao(r));
      else {
        b1.push(Object.assign(sao(r), { duration: r3(x - at) }));
        b2.push(Object.assign(sao(r), { at: x, duration: r3(at + d - x), from: r3(from + (x - at)) }));
      }
    }
    if (b1.length) s1.broll = b1.filter((r) => r.duration >= 0.2); else delete s1.broll;
    if (b2.length) s2.broll = b2.filter((r) => r.duration >= 0.2); else delete s2.broll;
    for (const s of [s1, s2]) if (s.broll && !s.broll.length) delete s.broll;
    tl.segments.splice(i, 1, s1, s2);
    return i + 1;
  }

  /** Gộp đoạn i với đoạn i+1 khi chúng liền nhau trong cùng file nguồn. */
  coTheNoi(tl, i) {
    const s1 = tl.segments[i], s2 = tl.segments[i + 1];
    if (!s1 || !s2 || laInsert(s1) || laInsert(s2) || s1.src !== s2.src) return false;
    if ((s1.audioSrc || null) !== (s2.audioSrc || null)) return false;
    const p = this.inOut(s1), q = this.inOut(s2);
    return Math.abs(p.b - q.a) < 0.02;
  }
  noi(tl, i) {
    if (!this.coTheNoi(tl, i)) return false;
    const s1 = tl.segments[i], s2 = tl.segments[i + 1];
    this._ghiCungHut(s1);
    this._ghiCungHut(s2);
    const lech = +s2.in - (+s1.in || 0);
    const ov = dsOverlay(s1).concat(dsOverlay(s2).map((o) => Object.assign(o, { at: r3((+o.at || 0) + lech) })));
    s1.out = s2.out;
    if (ov.length) s1.overlay = ov;
    const br = (s1.broll || []).concat(s2.broll || []);
    if (br.length) s1.broll = br;
    if (s2.fadeOut) s1.fadeOut = s2.fadeOut; else delete s1.fadeOut;
    if (s2.fadeOutAudio) s1.fadeOutAudio = s2.fadeOutAudio; else delete s1.fadeOutAudio;
    tl.segments.splice(i + 1, 1);
    return true;
  }

  /** Nối lại đoạn i với đoạn i+1 khi giữa chúng là một quãng đã cắt bỏ trong cùng file (dựng bằng lời). */
  coTheNoiQuaKhoang(tl, i) {
    const s1 = tl.segments[i], s2 = tl.segments[i + 1];
    if (!s1 || !s2 || laInsert(s1) || laInsert(s2) || s1.src !== s2.src) return false;
    if ((s1.audioSrc || null) !== (s2.audioSrc || null)) return false;
    const p = this.inOut(s1), q = this.inOut(s2);
    if (q.a < p.b - 0.02 || q.a - p.b > 30) return false;
    if (s1.audioSrc) {
      const l1 = (s1.audioIn !== undefined ? +s1.audioIn : p.a) - p.a, l2 = (s2.audioIn !== undefined ? +s2.audioIn : q.a) - q.a;
      if (Math.abs(l1 - l2) > 0.02) return false;
    }
    return true;
  }
  noiQuaKhoang(tl, i) {
    if (!this.coTheNoiQuaKhoang(tl, i)) return false;
    const s1 = tl.segments[i], s2 = tl.segments[i + 1];
    this._ghiCungHut(s1);
    this._ghiCungHut(s2);
    const lech = +s2.in - (+s1.in || 0);
    const ov = dsOverlay(s1).concat(dsOverlay(s2).map((o) => Object.assign(o, { at: r3((+o.at || 0) + lech) })));
    s1.out = s2.out;
    if (ov.length) s1.overlay = ov;
    const br = (s1.broll || []).concat(s2.broll || []);
    if (br.length) s1.broll = br;
    if (s2.fadeOut) s1.fadeOut = s2.fadeOut; else delete s1.fadeOut;
    if (s2.fadeOutAudio) s1.fadeOutAudio = s2.fadeOutAudio; else delete s1.fadeOutAudio;
    tl.segments.splice(i + 1, 1);
    return true;
  }

  doiCho(tl, tu, toi) {
    if (tu === toi || tu + 1 === toi) return;
    const [s] = tl.segments.splice(tu, 1);
    tl.segments.splice(toi > tu ? toi - 1 : toi, 0, s);
  }

  /** Dời overlay (i, k) tới mốc xuất T; tự đổi sang đoạn chứa T nếu cần. Trả {i, k} mới. */
  datOverlay(tl, i, k, T) {
    const seg = tl.segments[i];
    const ov = dsOverlay(seg);
    const o = ov[k];
    if (!o) return { i, k };
    const items = this.boCuc().items.filter((it) => it.loai === "doan");
    let dich = items.find((it) => T >= it.t0 && T < it.t1) || items.find((it) => it.i === i);
    let at = r3(clamp(T - dich.t0, 0, Math.max(0, dich.t1 - dich.t0 - 0.1)));
    if (dich.i === i) {
      o.at = at;
      seg.overlay = ov;
      return { i, k };
    }
    ov.splice(k, 1);
    if (ov.length) seg.overlay = ov; else delete seg.overlay;
    const sd = tl.segments[dich.i];
    const ov2 = dsOverlay(sd);
    ov2.push(Object.assign(o, { at }));
    sd.overlay = ov2;
    return { i: dich.i, k: ov2.length - 1 };
  }

  /** Đổi thời lượng thẻ (giây hiện trên hình); bằng độ dài file thì bỏ trường duration. */
  datThoiLuongThe(tl, i, k, D, atMoi) {
    const seg = tl.segments[i];
    const ov = dsOverlay(seg);
    const o = ov[k];
    if (!o) return;
    const N = this.dur(o.src);
    if (atMoi !== undefined) o.at = r3(Math.max(0, atMoi));
    D = r3(Math.max(THE_NGAN_NHAT, D));
    if (Math.abs(D - N) < 0.5 / this.fps) delete o.duration; else o.duration = D;
    seg.overlay = ov;
  }

  xoaOverlay(tl, i, k) {
    const seg = tl.segments[i];
    const ov = dsOverlay(seg);
    ov.splice(k, 1);
    if (ov.length) seg.overlay = ov; else delete seg.overlay;
  }

  datBroll(tl, i, k, { at, duration, from }) {
    const seg = tl.segments[i];
    const x = seg.broll[k];
    const { a, b } = this.inOut(seg);
    let nAt = at !== undefined ? +at : +x.at, nD = duration !== undefined ? +duration : +x.duration;
    const nFrom = from !== undefined ? +from : +x.from || 0;
    nD = clamp(nD, 0.2, b - a);
    nAt = clamp(nAt, a, b - nD);
    x.at = r3(nAt);
    x.duration = r3(nD);
    x.from = r3(Math.max(0, nFrom));
  }

  xoaBroll(tl, i, k) {
    const seg = tl.segments[i];
    seg.broll.splice(k, 1);
    if (!seg.broll.length) delete seg.broll;
  }

  // ---------- kiểm ----------
  /** Lỗi chặn lưu và cảnh báo, theo đúng các kiểm của assemble.py --kiem-tra (phần không cần ffprobe). */
  kiem() {
    const loi = [], canh = [];
    const tl = this.tl;
    const bc = this.boCuc();
    if (!(tl.segments || []).length) loi.push({ chu: "timeline không có đoạn nào" });
    (tl.segments || []).forEach((seg, i) => {
      const ten = `Đoạn ${i + 1}`;
      if (laInsert(seg)) return;
      const { a, b } = this.inOut(seg);
      if (!(b > a)) loi.push({ chu: `${ten}: điểm ra không sau điểm vào`, chon: { loai: "doan", i } });
      else if (b - a < 0.5) canh.push({ chu: `${ten}: chỉ dài ${(b - a).toFixed(2)} s`, chon: { loai: "doan", i } });
      if (a < 0) loi.push({ chu: `${ten}: điểm vào âm`, chon: { loai: "doan", i } });
      if (this.thoiLuong[seg.src] && b > this.thoiLuong[seg.src] + 0.05)
        loi.push({ chu: `${ten}: điểm ra vượt quá độ dài file nguồn`, chon: { loai: "doan", i } });
      dsOverlay(seg).forEach((o, k) => {
        if (o.duration !== undefined && +o.duration < THE_NGAN_NHAT) loi.push({ chu: `${ten}: overlay ${k + 1} ngắn hơn 0,3 s`, chon: { loai: "overlay", i, k } });
        if ((+o.at || 0) >= b - a) loi.push({ chu: `${ten}: overlay ${k + 1} bắt đầu sau khi đoạn đã hết`, chon: { loai: "overlay", i, k } });
      });
      (seg.broll || []).forEach((x, k) => {
        if (!(a <= +x.at && +x.at < b)) loi.push({ chu: `${ten}: B-roll ${k + 1} nằm ngoài đoạn`, chon: { loai: "broll", i, k } });
        else if (+x.at + +x.duration > b + 0.05) canh.push({ chu: `${ten}: B-roll ${k + 1} dài quá đuôi đoạn`, chon: { loai: "broll", i, k } });
      });
    });
    for (const o of bc.overlays) {
      if (o.tuNhien > o.t1 + 0.05)
        canh.push({ chu: `Đoạn ${o.i + 1}: overlay ${o.k + 1} bị cắt cụt (đoạn hết hoặc B-roll đến trước khi thẻ chạy xong)`, chon: { loai: "overlay", i: o.i, k: o.k } });
    }
    const m = tl.music;
    if (m && m.src && (m.mode || "full") === "bookends" && !bc.vaiTro.intro && !bc.vaiTro.outro)
      loi.push({ chu: "Nhạc kiểu bookends nhưng không có intro/outro nào", chon: { loai: "nhac" } });
    return { loi, canh };
  }

  /** Bản timeline sạch để ghi. */
  banGhi() {
    return JSON.parse(JSON.stringify(this.tl));
  }
}
