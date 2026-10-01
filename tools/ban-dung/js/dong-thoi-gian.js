// Dòng thời gian của Bàn dựng: sáu kênh, kéo tỉa, kéo dời, đổi thứ tự, tua, thu phóng.

import { clamp, dongHo, el, r3, tenFile, timTruoc, veKhung } from "./tien-ich.js";
import { DOAN_NGAN_NHAT, THE_NGAN_NHAT, dsOverlay, laInsert } from "./mo-hinh.js";

export const KENH = [
  { k: "chuong", ten: "Chương", cao: 22 },
  { k: "overlay", ten: "Đồ họa nổi", cao: 30 },
  { k: "broll", ten: "B-roll", cao: 30 },
  { k: "hinh", ten: "Hình chính", cao: 58 },
  { k: "tieng", ten: "Tiếng lời", cao: 46 },
  { k: "nhac", ten: "Nhạc nền", cao: 28 },
];
const CAO_THUOC = 26;
const MEP = 7;          // điểm ảnh: vùng bắt mép để tỉa
const HUT_PX = 7;       // điểm ảnh: khoảng hút nam châm

export class DongThoiGian {
  constructor(goc, mh, xem, ui) {
    this.goc = goc;
    this.mh = mh;
    this.xem = xem;
    this.ui = ui;             // {chon(sel), layChon(), bao(chu)}
    this.pps = 40;            // điểm ảnh mỗi giây
    this._dung();
    this._chu = new Map();
    this._nangLuong = {};     // src -> Uint8Array
  }

  // ---------- dựng khung ----------
  _dung() {
    const trai = el("div", { class: "tl-trai" }, [el("div", { class: "o-thuoc", style: { height: CAO_THUOC + "px" } })]);
    this.cuon = el("div", { class: "tl-cuon" });
    this.noi = el("div", { class: "tl-noi" });
    this.cThuoc = el("canvas", { class: "c-thuoc", height: CAO_THUOC });
    this.noi.append(this.cThuoc);
    this.hang = {};
    for (const k of KENH) {
      trai.append(el("div", { class: "nhan-kenh", style: { height: k.cao + "px" } }, k.ten));
      const h = el("div", { class: `hang hang-${k.k}`, "data-k": k.k, style: { height: k.cao + "px" } });
      this.hang[k.k] = h;
      this.noi.append(h);
    }
    this.cSong = el("canvas", { class: "c-song", height: KENH.find((x) => x.k === "tieng").cao });
    this.hang.tieng.append(this.cSong);
    this.dauDoc = el("div", { class: "dau-doc" }, [el("div", { class: "dau-doc-mu" })]);
    this.vachChen = el("div", { class: "vach-chen" });
    this.goiY = el("div", { class: "goi-y-keo" });
    this.noi.append(this.dauDoc, this.vachChen, this.goiY);
    this.cuon.append(this.noi);
    this.goc.append(trai, this.cuon);
    this.cuon.addEventListener("scroll", () => this._veCanvas());
    this.cuon.addEventListener("wheel", (e) => this._banXe(e), { passive: false });
    this.noi.addEventListener("pointerdown", (e) => this._nhan(e));
    this.noi.addEventListener("pointermove", (e) => this._tro(e));
    this.noi.addEventListener("dblclick", (e) => {
      const T = this._Tcua(e);
      this.xem.tua(T);
    });
    new ResizeObserver(() => this._veCanvas()).observe(this.cuon);
  }

  datNangLuong(src, bytes) { this._nangLuong[src] = bytes; this._veCanvas(); }

  // ---------- toạ độ ----------
  _x(T) { return T * this.pps; }
  _Tcua(e) {
    const r = this.noi.getBoundingClientRect();
    return Math.max(0, (e.clientX - r.left) / this.pps);
  }
  vuaKhung() {
    const tong = this.mh.boCuc().tong || 10;
    this.pps = clamp((this.cuon.clientWidth - 40) / tong, 0.3, 400);
    this.ve();
  }
  phong(heSo, Tneo) {
    const truoc = this.pps;
    const T = Tneo !== undefined ? Tneo : this.xem.T;
    const xView = this._x(T) - this.cuon.scrollLeft;
    this.pps = clamp(this.pps * heSo, 0.3, 400);
    if (this.pps === truoc) return;
    this.ve();
    this.cuon.scrollLeft = this._x(T) - xView;
  }
  _banXe(e) {
    if (e.ctrlKey || e.metaKey) {
      e.preventDefault();
      this.phong(Math.exp(-e.deltaY * 0.01), this._Tcua(e));
    } else if (Math.abs(e.deltaY) > Math.abs(e.deltaX) && !e.shiftKey) {
      // con lăn dọc cuộn ngang, như phần mềm dựng
      e.preventDefault();
      this.cuon.scrollLeft += e.deltaY;
    }
  }

  // ---------- chữ trong khối ----------
  chuCua(it) {
    const seg = it.seg;
    if (!seg || it.loai !== "doan") return "";
    const khoa = `${seg.audioSrc || seg.src}|${seg.audioIn}|${it.a}|${it.b}`;
    if (this._chu.has(khoa)) return this._chu.get(khoa);
    const nguon = seg.audioSrc || seg.src;
    const lech = seg.audioSrc ? (seg.audioIn !== undefined ? +seg.audioIn : it.a) - it.a : 0;
    const p = this.mh.phu[nguon] || {};
    const a = it.a + lech, b = it.b + lech;
    let chu = "";
    if (p.tu && p.tu.length) {
      const j = Math.max(0, timTruoc(p.tu, a - 0.05, (w) => w.s));
      const ds = [];
      for (let q = j; q < p.tu.length && p.tu[q].s < b; q++) if (p.tu[q].e > a + 0.02) ds.push(p.tu[q].h || p.tu[q].w);
      chu = ds.join(" ");
    } else if (p.cau && p.cau.length) {
      chu = p.cau.filter((c) => c.e > a && c.s < b).map((c) => c.t).join(" ");
    }
    this._chu.set(khoa, chu);
    return chu;
  }

  // ---------- vẽ ----------
  ve() {
    const bc = this.mh.boCuc();
    const chon = this.ui.layChon();
    const rong = Math.max(this.cuon.clientWidth, this._x(bc.tong) + 240);
    this.noi.style.width = rong + "px";
    for (const k of Object.keys(this.hang)) {
      for (const c of [...this.hang[k].children]) if (c !== this.cSong) c.remove();
    }
    const giong = (sel, loai, i, k) => sel && sel.loai === loai && sel.i === i && (k === undefined || sel.k === k);
    // hình chính
    bc.items.forEach((it) => {
      const w = Math.max(1, this._x(it.t1 - it.t0));
      const loai = it.loai === "doan" ? "doan" : it.loai;
      const sel = it.loai === "doan" || it.loai === "insert" ? giong(chon, "doan", it.i) : chon && chon.loai === it.loai;
      const nhan = it.loai === "doan" ? (this.chuCua(it) || tenFile(it.src)) : `${it.loai === "insert" ? "Chèn" : it.loai === "intro" ? "Intro" : "Outro"}: ${tenFile(it.src)}`;
      const k = el("div", {
        class: `khoi k-${loai}${sel ? " chon" : ""}${it.daHut ? " da-hut" : ""}`,
        "data-loai": it.loai === "insert" ? "doan" : it.loai, "data-i": it.i,
        style: { left: this._x(it.t0) + "px", width: w + "px" },
        title: `${it.loai === "doan" ? `Đoạn ${it.i + 1}: ${tenFile(it.src)} [${dongHo(it.a)} → ${dongHo(it.b)}]` : tenFile(it.src)}\n${dongHo(it.t1 - it.t0)}`,
      }, [el("span", { class: "nhan-khoi" }, nhan)]);
      const seg = it.seg;
      if (seg && it.loai === "doan") {
        if (+seg.fadeIn > 0) k.append(el("i", { class: "mo mo-vao", style: { width: this._x(+seg.fadeIn) + "px" } }));
        if (+seg.fadeOut > 0) k.append(el("i", { class: "mo mo-ra", style: { width: this._x(+seg.fadeOut) + "px" } }));
        if (seg.audioSrc) k.append(el("b", { class: "dau-goc" }, tenFile(seg.src).replace(/\.[^.]+$/, "")));
      }
      this.hang.hinh.append(k);
    });
    // chương
    bc.chuong.forEach((c) => {
      this.hang.chuong.append(el("div", { class: "moc-chuong", "data-loai": "doan", "data-i": c.i, style: { left: this._x(c.t) + "px" }, title: c.ten }, c.ten));
    });
    // overlay
    bc.overlays.forEach((o) => {
      const sel = giong(chon, "overlay", o.i, o.k);
      const w = Math.max(4, this._x(o.t1 - o.t0));
      const khoi = el("div", {
        class: `khoi k-overlay${sel ? " chon" : ""}`, "data-loai": "overlay", "data-i": o.i, "data-k": o.k,
        style: { left: this._x(o.t0) + "px", width: w + "px" },
        title: `${tenFile(o.src)}\nhiện lúc ${dongHo(o.t0)} (cách đầu đoạn ${(+o.o.at || 0).toFixed(2)} s), trong ${o.ts.D.toFixed(2)} s` +
          (o.ts.X ? `\nfile dài ${o.ts.N.toFixed(2)} s: ${o.ts.X > 0 ? "giữ khung giữa thêm" : "bỏ bớt quãng giữa"} ${Math.abs(o.ts.X).toFixed(2)} s` : "") +
          "\nkéo mép phải để đổi thời lượng",
      }, [el("span", { class: "nhan-khoi" }, tenFile(o.src).replace(/\.webm$/, ""))]);
      if (o.tuNhien > o.t1 + 0.05) khoi.classList.add("bi-cat");
      if (o.ts.X > 0) khoi.append(el("i", { class: "vung-giu", style: { left: this._x(o.ts.H) + "px", width: this._x(o.ts.X) + "px" } }));
      if (o.ts.X < 0) khoi.append(el("i", { class: "vach-bot", style: { left: this._x(o.ts.H) + "px" } }));
      this.hang.overlay.append(khoi);
    });
    // b-roll
    bc.brolls.forEach((b) => {
      const sel = giong(chon, "broll", b.i, b.k);
      this.hang.broll.append(el("div", {
        class: `khoi k-broll${sel ? " chon" : ""}`, "data-loai": "broll", "data-i": b.i, "data-k": b.k,
        style: { left: this._x(b.t0) + "px", width: Math.max(4, this._x(b.t1 - b.t0)) + "px" },
        title: `${tenFile(b.src)}\n${dongHo(b.t0)} → ${dongHo(b.t1)}`,
      }, [el("span", { class: "nhan-khoi" }, tenFile(b.src))]));
    });
    // nhạc
    const m = this.mh.tl.music;
    bc.nhac.forEach((p) => {
      const w = Math.max(4, this._x(p.t1 - p.t0));
      const khoi = el("div", {
        class: `khoi k-nhac${chon && chon.loai === "nhac" ? " chon" : ""}`, "data-loai": "nhac",
        style: { left: this._x(p.t0) + "px", width: w + "px" },
        title: `${tenFile(m.src)}\n${p.g} dB`,
      }, [el("span", { class: "nhan-khoi" }, `${tenFile(m.src)} · ${p.g} dB`)]);
      if (p.fi > 0) khoi.append(el("i", { class: "mo mo-vao", style: { width: this._x(p.fi) + "px" } }));
      if (p.foD > 0) khoi.append(el("i", { class: "mo mo-ra", style: { width: this._x(Math.min(p.foD, p.t1 - p.t0)) + "px" } }));
      this.hang.nhac.append(khoi);
    });
    if (!bc.nhac.length) this.hang.nhac.append(el("div", { class: "trong-kenh" }, m && m.src ? "nhạc không có chỗ nào để phát" : "chưa có nhạc nền"));
    // khối trong suốt trên kênh tiếng để chọn đoạn
    bc.items.forEach((it) => {
      if (it.loai !== "doan") return;
      this.hang.tieng.append(el("div", {
        class: `khoi k-tieng${giong(chon, "doan", it.i) ? " chon" : ""}`, "data-loai": "doan", "data-i": it.i,
        style: { left: this._x(it.t0) + "px", width: Math.max(1, this._x(it.t1 - it.t0)) + "px" },
      }));
    });
    this.datDauDoc(this.xem.T);
    this._veCanvas();
  }

  datDauDoc(T, theo = false) {
    const x = this._x(T);
    this.dauDoc.style.transform = `translateX(${x}px)`;
    if (theo) {
      const w = this.cuon.clientWidth;
      if (x < this.cuon.scrollLeft || x > this.cuon.scrollLeft + w - 30) this.cuon.scrollLeft = x - w * 0.2;
    }
  }

  _veCanvas() {
    const w = this.cuon.clientWidth;
    const sl = this.cuon.scrollLeft;
    const dpr = window.devicePixelRatio || 1;
    const cs = getComputedStyle(document.documentElement);
    const mauChu = cs.getPropertyValue("--chu-nhat").trim() || "#888";
    const mauVach = cs.getPropertyValue("--vien").trim() || "#ccc";
    const mauSong = cs.getPropertyValue("--song").trim() || "#5a8";
    // thước
    const c = this.cThuoc;
    c.width = w * dpr; c.style.width = w + "px"; c.style.height = CAO_THUOC + "px";
    const g = c.getContext("2d");
    g.setTransform(dpr, 0, 0, dpr, 0, 0);
    g.clearRect(0, 0, w, CAO_THUOC);
    const buoc = [0.1, 0.2, 0.5, 1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 1800].find((s) => s * this.pps >= 80) || 3600;
    const nho = buoc / 5;
    g.font = "11px -apple-system, BlinkMacSystemFont, sans-serif";
    g.fillStyle = mauChu; g.strokeStyle = mauVach; g.lineWidth = 1;
    const T0 = sl / this.pps, T1 = (sl + w) / this.pps;
    g.beginPath();
    for (let t = Math.floor(T0 / nho) * nho; t <= T1; t += nho) {
      const x = Math.round(t * this.pps - sl) + 0.5;
      const lon = Math.abs(t / buoc - Math.round(t / buoc)) < 1e-6;
      g.moveTo(x, CAO_THUOC); g.lineTo(x, lon ? CAO_THUOC - 10 : CAO_THUOC - 4);
      if (lon) g.fillText(dongHo(Math.round(t * 100) / 100, buoc < 1), x + 3, 12);
    }
    g.stroke();
    // dạng sóng
    const cao = this.cSong.height / (this.cSong._dpr || 1) || 46;
    const H = KENH.find((x) => x.k === "tieng").cao;
    const s = this.cSong;
    s.width = w * dpr; s.height = H * dpr; s._dpr = dpr;
    s.style.width = w + "px"; s.style.height = H + "px";
    const q = s.getContext("2d");
    q.setTransform(dpr, 0, 0, dpr, 0, 0);
    q.clearRect(0, 0, w, H);
    const items = this.mh.boCuc().items;
    q.fillStyle = mauSong;
    const giua = H / 2;
    for (let x = 0; x < w; x++) {
      const Ta = (sl + x) / this.pps, Tb = (sl + x + 1) / this.pps;
      const j = timTruoc(items, Ta, (it) => it.t0);
      const it = items[j];
      if (!it || it.loai !== "doan" || Ta >= it.t1) continue;
      const seg = it.seg;
      const nguon = seg.audioSrc || seg.src;
      const nl = this._nangLuong[nguon];
      if (!nl) continue;
      const p = this.mh.phu[nguon] || {};
      const hz = (p.nangLuong && p.nangLuong.hz) || 100;
      const san = (p.nangLuong && p.nangLuong.san) || -60;
      const lech = seg.audioSrc ? (seg.audioIn !== undefined ? +seg.audioIn : it.a) - it.a : 0;
      const sa = it.a + lech + (Ta - it.t0), sb = it.a + lech + (Math.min(Tb, it.t1) - it.t0);
      let mx = 0;
      for (let k = Math.floor(sa * hz); k <= Math.floor(sb * hz) && k < nl.length; k++) if (k >= 0 && nl[k] > mx) mx = nl[k];
      const db = mx - 100;
      const v = clamp((db - san) / (-6 - san), 0, 1);
      const h = Math.max(1, v * (H - 6));
      q.fillRect(x, giua - h / 2, 1, h);
    }
    // vạch ranh giới đoạn
    q.fillStyle = mauVach;
    for (const it of items) {
      const x = Math.round(it.t0 * this.pps - sl);
      if (x >= 0 && x <= w) q.fillRect(x, 0, 1, H);
    }
    void cao;
  }

  // ---------- tương tác ----------
  _tro(e) {
    if (this._keo) return;
    const k = e.target.closest(".khoi");
    let cur = "";
    if (k) {
      const vung = this._vung(k, e);
      const loai = k.dataset.loai;
      if ((loai === "doan" && !k.classList.contains("k-insert") || loai === "broll" || loai === "overlay") && vung !== "giua") cur = "col-resize";
      else if (loai === "overlay" || loai === "broll" || loai === "doan") cur = "grab";
    }
    this.noi.style.cursor = cur;
  }

  _vung(k, e) {
    const r = k.getBoundingClientRect();
    if (r.width < MEP * 3) return "giua";
    if (e.clientX - r.left < MEP) return "trai";
    if (r.right - e.clientX < MEP) return "phai";
    return "giua";
  }

  _hut(T, boQua = null) {
    const ds = [this.xem.T];
    for (const it of this.mh.boCuc().items) { ds.push(it.t0, it.t1); }
    let tot = T, d = HUT_PX / this.pps;
    for (const c of ds) if (c !== boQua && Math.abs(c - T) < d) { d = Math.abs(c - T); tot = c; }
    return tot;
  }

  _goiY(e, chu) {
    if (!chu) { this.goiY.style.display = "none"; return; }
    const r = this.noi.getBoundingClientRect();
    this.goiY.textContent = chu;
    this.goiY.style.display = "block";
    this.goiY.style.transform = `translate(${e.clientX - r.left + 12}px, ${e.clientY - r.top - 34}px)`;
  }

  _nhan(e) {
    if (e.button !== 0) return;
    const T = this._Tcua(e);
    const r = this.noi.getBoundingClientRect();
    // thước: tua
    if (e.clientY - r.top < CAO_THUOC) {
      this.xem.tua(T);
      this._batKeo(e, { kieu: "tua" });
      return;
    }
    const k = e.target.closest(".khoi, .moc-chuong");
    if (!k) { this.ui.chon(null); this.xem.tua(T); this._batKeo(e, { kieu: "tua" }); return; }
    const loai = k.dataset.loai, i = +k.dataset.i, kk = k.dataset.k !== undefined ? +k.dataset.k : undefined;
    const sel = loai === "doan" ? { loai: "doan", i } : loai === "overlay" ? { loai, i, k: kk } :
      loai === "broll" ? { loai, i, k: kk } : { loai };
    const vung = this._vung(k, e);   // đo trước khi chọn: chọn sẽ vẽ lại, khối cũ bị thay
    this.ui.chon(sel);
    const bc = this.mh.boCuc();
    const fps = this.mh.fps;
    if (loai === "doan" && !k.classList.contains("moc-chuong")) {
      const it = bc.items.find((x) => x.i === i && (x.loai === "doan" || x.loai === "insert"));
      const seg = this.mh.tl.segments[i];
      if (it && it.loai === "doan" && vung !== "giua") {
        this._batKeo(e, { kieu: vung === "trai" ? "tia-vao" : "tia-ra", i, a0: it.a, b0: it.b, src: seg.src, T0: T, it });
        return;
      }
      this._batKeo(e, { kieu: "doi-cho", i, T0: T });
      return;
    }
    if (loai === "overlay") {
      const o = bc.overlays.find((x) => x.i === i && x.k === kk);
      if (vung !== "giua") {
        this._batKeo(e, { kieu: vung === "trai" ? "ov-trai" : "ov-phai", i, k: kk, t0: o.t0, at0: +o.o.at || 0, D0: o.ts.D, N: o.ts.N, T0: T });
        return;
      }
      this._batKeo(e, { kieu: "overlay", i, k: kk, t0: o.t0, T0: T });
      return;
    }
    if (loai === "broll") {
      const b = this.mh.tl.segments[i].broll[kk];
      this._batKeo(e, { kieu: vung === "trai" ? "broll-trai" : vung === "phai" ? "broll-phai" : "broll-dich", i, k: kk,
        at0: +b.at, d0: +b.duration, f0: +b.from || 0, T0: T });
      return;
    }
    void fps;
  }

  _batKeo(e, st) {
    this._keo = Object.assign(st, { x0: e.clientX, daKeo: false });
    this.noi.setPointerCapture(e.pointerId);
    const di = (ev) => this._keoDi(ev);
    const tha = (ev) => {
      this.noi.removeEventListener("pointermove", di);
      this.noi.removeEventListener("pointerup", tha);
      this.noi.removeEventListener("pointercancel", tha);
      this._keoTha(ev, ev.type === "pointercancel");
    };
    this.noi.addEventListener("pointermove", di);
    this.noi.addEventListener("pointerup", tha);
    this.noi.addEventListener("pointercancel", tha);
  }

  _keoDi(e) {
    const st = this._keo;
    if (!st) return;
    const dx = e.clientX - st.x0;
    if (!st.daKeo && Math.abs(dx) < 4) return;
    const fps = this.mh.fps;
    if (!st.daKeo) {
      st.daKeo = true;
      if (st.kieu !== "tua" && st.kieu !== "doi-cho") this.mh.batDauKeo();
    }
    const dt = dx / this.pps;
    const T = this._Tcua(e);
    switch (st.kieu) {
      case "tua":
        this.xem.tua(T);
        break;
      case "tia-vao": {
        const a = veKhung(clamp(st.a0 + dt, 0, st.b0 - DOAN_NGAN_NHAT), fps);
        this.mh.keo((tl) => this.mh.tiaVao(tl, st.i, a));
        this.xem.nhinKhung(st.src, a);
        this._goiY(e, `vào ${dongHo(a)}  (${a - st.a0 >= 0 ? "+" : ""}${(a - st.a0).toFixed(2)} s)`);
        break;
      }
      case "tia-ra": {
        let Tra = st.it.t0 + (st.b0 - st.a0) + dt;
        const hut = this._hut(Tra, st.it.t1);
        if (hut === this.xem.T) Tra = hut;
        const b = veKhung(clamp(st.a0 + (Tra - st.it.t0), st.a0 + DOAN_NGAN_NHAT, this.mh.dur(st.src)), fps);
        this.mh.keo((tl) => this.mh.tiaRa(tl, st.i, b));
        this.xem.nhinKhung(st.src, Math.max(st.a0, b - 1 / fps));
        this._goiY(e, `ra ${dongHo(b)}  (${b - st.b0 >= 0 ? "+" : ""}${(b - st.b0).toFixed(2)} s)`);
        break;
      }
      case "doi-cho": {
        const items = this.mh.boCuc().items.filter((x) => x.i >= 0);
        let dich = items.length;
        for (let q = 0; q < items.length; q++) if (T < (items[q].t0 + items[q].t1) / 2) { dich = q; break; }
        const segIdx = dich < items.length ? items[dich].i : this.mh.tl.segments.length;
        st.dich = segIdx;
        const xv = dich < items.length ? items[dich].t0 : items[items.length - 1].t1;
        this.vachChen.style.display = "block";
        this.vachChen.style.transform = `translateX(${this._x(xv)}px)`;
        this._goiY(e, segIdx === st.i || segIdx === st.i + 1 ? "thả để giữ nguyên chỗ" : `đưa đoạn ${st.i + 1} tới đây`);
        break;
      }
      case "overlay": {
        const t0 = this._hut(veKhung(st.t0 + dt, fps), st.t0);
        let moi = null;
        this.mh.keo((tl) => { moi = this.mh.datOverlay(tl, st.i, st.k, t0); });
        if (moi) this.ui.chon({ loai: "overlay", i: moi.i, k: moi.k }, true);
        this._goiY(e, `hiện lúc ${dongHo(t0)}`);
        break;
      }
      case "ov-phai":
      case "ov-trai": {
        let d = veKhung(dt, fps);
        if (st.kieu === "ov-phai") {
          const hut = this._hut(st.t0 + st.D0 + d, st.t0 + st.D0);
          d = veKhung(hut - st.t0 - st.D0, fps);
          const D = Math.max(THE_NGAN_NHAT, st.D0 + d);
          this.mh.keo((tl) => this.mh.datThoiLuongThe(tl, st.i, st.k, D));
          this._goiY(e, `hiện trong ${D.toFixed(2)} s${Math.abs(D - st.N) > 0.02 ? ` (file ${st.N.toFixed(2)} s, ${D > st.N ? "giữ khung giữa thêm" : "bỏ bớt"} ${Math.abs(D - st.N).toFixed(2)} s)` : " (đúng độ dài file)"}`);
        } else {
          d = Math.min(d, st.D0 - THE_NGAN_NHAT);
          d = Math.max(d, -st.at0);
          this.mh.keo((tl) => this.mh.datThoiLuongThe(tl, st.i, st.k, st.D0 - d, st.at0 + d));
          this._goiY(e, `hiện lúc +${(st.at0 + d).toFixed(2)} s, trong ${(st.D0 - d).toFixed(2)} s`);
        }
        break;
      }
      case "broll-dich":
      case "broll-trai":
      case "broll-phai": {
        const d = veKhung(dt, fps);
        const v = st.kieu === "broll-dich" ? { at: st.at0 + d } :
          st.kieu === "broll-trai" ? { at: st.at0 + d, duration: st.d0 - d, from: st.f0 + d } : { duration: st.d0 + d };
        this.mh.keo((tl) => this.mh.datBroll(tl, st.i, st.k, v));
        const b = this.mh.tl.segments[st.i].broll[st.k];
        this._goiY(e, `B-roll ${(+b.duration).toFixed(2)} s, từ ${(+b.from).toFixed(2)} s của file`);
        break;
      }
    }
  }

  _keoTha(e, huy) {
    const st = this._keo;
    this._keo = null;
    this._goiY(e, null);
    this.vachChen.style.display = "none";
    if (!st) return;
    if (!st.daKeo) {
      // bấm (không kéo) vào một khối: chọn và đưa đầu đọc tới chỗ bấm để khung xem theo đúng chỗ đó
      if (st.T0 !== undefined && st.kieu !== "tua") this.xem.tua(st.T0);
      return;
    }
    if (st.kieu === "tua") return;
    if (st.kieu === "doi-cho") {
      if (!huy && st.dich !== undefined && st.dich !== st.i && st.dich !== st.i + 1) {
        this.mh.sua(`Đổi chỗ đoạn ${st.i + 1}`, (tl) => this.mh.doiCho(tl, st.i, st.dich));
        const moi = st.dich > st.i ? st.dich - 1 : st.dich;
        this.ui.chon({ loai: "doan", i: moi });
      }
      return;
    }
    if (huy) { this.mh.huyKeo(); this.xem.thoiNhin(); return; }
    const moTa = { "tia-vao": `Tỉa đầu đoạn ${st.i + 1}`, "tia-ra": `Tỉa cuối đoạn ${st.i + 1}`, overlay: "Dời đồ họa nổi", "ov-phai": "Đổi thời lượng đồ họa nổi", "ov-trai": "Đổi lúc hiện và thời lượng đồ họa nổi",
      "broll-dich": "Dời B-roll", "broll-trai": "Tỉa đầu B-roll", "broll-phai": "Tỉa cuối B-roll" }[st.kieu] || "Kéo";
    this.mh.ketThucKeo(moTa);
    this.xem.thoiNhin();
  }
}

export { r3, laInsert, dsOverlay };
