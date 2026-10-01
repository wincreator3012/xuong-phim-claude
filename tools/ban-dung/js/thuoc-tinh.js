// Bảng thuộc tính: chỉnh số liệu của mục đang chọn. Mọi ô số ghi khi bấm Enter hoặc rời ô.

import { dongHo, el, r3, tenFile } from "./tien-ich.js";
import { dsOverlay, laInsert } from "./mo-hinh.js";

const BO_CUC = ["mat", "slide", "ca-hai", "chia-doi", "mat-chinh"];

export class BangThuocTinh {
  constructor(goc, mh, xem, ui) {
    this.goc = goc;
    this.mh = mh;
    this.xem = xem;
    this.ui = ui;   // {layChon, chon, lenh(ten), bao}
  }

  _so(nhan, gia, { buoc = 0.01, min, max, donVi = "s", ghi, chiDoc = false, goiY } = {}) {
    const o = el("input", { type: "number", step: buoc, value: gia === undefined || gia === null ? "" : r3(+gia),
      min, max, readonly: chiDoc, class: chiDoc ? "chi-doc" : "" });
    if (!chiDoc) {
      o.addEventListener("change", () => {
        const v = o.value === "" ? null : +o.value;
        if (v !== null && !isFinite(v)) return;
        ghi(v);
      });
      o.addEventListener("keydown", (e) => { if (e.key === "Enter") o.blur(); e.stopPropagation(); });
    }
    return el("label", { class: "truong" }, [el("span", {}, nhan), el("span", { class: "o-nhap" }, [o, el("em", {}, donVi)]),
      goiY ? el("small", {}, goiY) : null]);
  }
  _chu(nhan, gia, ghi, goiY) {
    const o = el("input", { type: "text", value: gia || "" });
    o.addEventListener("change", () => ghi(o.value.trim()));
    o.addEventListener("keydown", (e) => { if (e.key === "Enter") o.blur(); e.stopPropagation(); });
    return el("label", { class: "truong" }, [el("span", {}, nhan), o, goiY ? el("small", {}, goiY) : null]);
  }
  _chon(nhan, gia, ds, ghi, goiY) {
    const o = el("select", {}, ds.map(([v, t]) => el("option", { value: v, selected: v === gia }, t)));
    o.addEventListener("change", () => ghi(o.value));
    return el("label", { class: "truong" }, [el("span", {}, nhan), o, goiY ? el("small", {}, goiY) : null]);
  }
  _bat(nhan, gia, ghi, goiY) {
    const o = el("input", { type: "checkbox", checked: !!gia });
    o.addEventListener("change", () => ghi(o.checked));
    return el("label", { class: "truong truong-bat" }, [o, el("span", {}, nhan), goiY ? el("small", {}, goiY) : null]);
  }
  _nut(chu, fn, phu = "") {
    return el("button", { class: `nut ${phu}`, onclick: fn }, chu);
  }
  _datHoacXoa(obj, k, v) {
    if (v === null || v === "" || v === 0 || v === false) delete obj[k]; else obj[k] = v;
  }

  ve() {
    // không vẽ lại khi bạn đang gõ dở trong một ô
    if (this.goc.contains(document.activeElement) && document.activeElement.tagName === "INPUT" &&
        document.activeElement.type !== "checkbox") return;
    const sel = this.ui.layChon();
    this.goc.innerHTML = "";
    const mh = this.mh, tl = mh.tl, bc = mh.boCuc();
    const tieuDe = (t, phu) => this.goc.append(el("div", { class: "tt-dau" }, [el("h3", {}, t), phu ? el("p", {}, phu) : null]));
    const nhom = (...con) => this.goc.append(el("div", { class: "tt-nhom" }, con));

    if (!sel) {
      tieuDe("Tổng quan", mh.p);
      const kq = mh.kiem();
      nhom(el("div", { class: "tt-so" }, [
        el("div", {}, [el("b", {}, dongHo(bc.tong, false)), el("span", {}, "thời lượng")]),
        el("div", {}, [el("b", {}, String((tl.segments || []).length)), el("span", {}, "đoạn")]),
        el("div", {}, [el("b", {}, String(bc.overlays.length)), el("span", {}, "đồ họa nổi")]),
      ]));
      if (kq.loi.length || kq.canh.length) {
        nhom(el("h4", {}, "Cần xem"), ...kq.loi.map((x) => el("button", { class: "dong-kiem loi", onclick: () => x.chon && this.ui.chon(x.chon) }, x.chu)),
          ...kq.canh.map((x) => el("button", { class: "dong-kiem canh", onclick: () => x.chon && this.ui.chon(x.chon) }, x.chu)));
      } else {
        nhom(el("p", { class: "nhat" }, "Không thấy lỗi nào trong timeline."));
      }
      nhom(el("p", { class: "nhat" }, "Bấm vào một khối trên dòng thời gian để chỉnh. Kéo mép khối hình chính để tỉa, kéo thân khối để đổi thứ tự. Bấm ? để xem phím tắt."));
      if (tl._chinhTay) nhom(el("p", { class: "nhat" }, `Đã chỉnh tay ${tl._chinhTay.soLan} lần, lần cuối ${tl._chinhTay.luc.replace("T", " ")}.`));
      return;
    }

    if (sel.loai === "doan") {
      const seg = tl.segments[sel.i];
      if (!seg) return this.ui.chon(null);
      const it = bc.items.find((x) => x.i === sel.i);
      if (laInsert(seg)) {
        tieuDe(`Đoạn ${sel.i + 1}: đồ họa chèn`, tenFile(seg.src));
        nhom(this._so("Thời lượng", it.t1 - it.t0, { chiDoc: true }),
          this._chon("Vai trò", seg.role || "", [["", "đồ họa thường"], ["intro", "intro (nhạc bookends bám vào)"], ["outro", "outro (nhạc bookends bám vào)"]],
            (v) => mh.sua("Đổi vai trò đồ họa", (t) => this._datHoacXoa(t.segments[sel.i], "role", v))),
          this._chu("Chương bắt đầu ở đây", seg.chapter, (v) => mh.sua("Đổi chương", (t) => this._datHoacXoa(t.segments[sel.i], "chapter", v))));
        nhom(el("div", { class: "hang-nut" }, [this._nut("Tới đầu đoạn", () => this.xem.tua(it.t0)), this._nut("Xoá đoạn", () => this.ui.lenh("xoa"), "nguy")]));
        return;
      }
      const { a, b, daHut } = mh.inOut(seg);
      tieuDe(`Đoạn ${sel.i + 1}`, tenFile(seg.src) + (seg.label ? ` · ${seg.label}` : ""));
      nhom(
        this._so("Vào (giây trong file nguồn)", daHut ? a : seg.in, { buoc: 1 / mh.fps, ghi: (v) => mh.sua(`Đặt điểm vào đoạn ${sel.i + 1}`, (t) => mh.tiaVao(t, sel.i, v ?? 0)) }),
        this._so("Ra (giây trong file nguồn)", daHut ? b : seg.out, { buoc: 1 / mh.fps, ghi: (v) => v !== null && mh.sua(`Đặt điểm ra đoạn ${sel.i + 1}`, (t) => mh.tiaRa(t, sel.i, v)) }),
        this._so("Thời lượng", b - a, { chiDoc: true }),
        this._bat("Hút điểm cắt về khoảng lặng gần nhất", seg.snap !== false,
          (v) => mh.sua("Đổi hút khoảng lặng", (t) => { t.segments[sel.i].snap = !!v; }),
          daHut ? `Đang hút: ${seg.in} → ${r3(a)}, ${seg.out} → ${r3(b)}. Kéo tỉa tay sẽ tự tắt hút để giữ đúng chỗ bạn chọn.` :
            "Kéo tỉa tay sẽ tự tắt hút để giữ đúng chỗ bạn chọn."),
      );
      nhom(
        this._so("Mờ vào (hình và tiếng)", seg.fadeIn || 0, { buoc: 0.1, min: 0, ghi: (v) => mh.sua("Đổi mờ vào", (t) => this._datHoacXoa(t.segments[sel.i], "fadeIn", v && r3(v))) }),
        this._so("Mờ ra (hình và tiếng)", seg.fadeOut || 0, { buoc: 0.1, min: 0, ghi: (v) => mh.sua("Đổi mờ ra", (t) => this._datHoacXoa(t.segments[sel.i], "fadeOut", v && r3(v))) }),
        this._so("Tăng/giảm tiếng riêng đoạn này", seg.volumeDb || 0, { buoc: 1, donVi: "dB", goiY: "Âm để nhỏ đi (tiếng nền cảnh thật thường khởi đầu ở -12). Xem trước chỉ nghe được phần giảm.",
          ghi: (v) => mh.sua("Đổi tiếng riêng đoạn", (t) => this._datHoacXoa(t.segments[sel.i], "volumeDb", v && Math.round(v * 10) / 10)) }),
        this._so("Chỉ mờ tiếng cuối đoạn", seg.fadeOutAudio || 0, { buoc: 0.1, min: 0, goiY: "Hình vẫn cắt thẳng; dùng khi lời cần tắt êm trước đồ họa chèn.",
          ghi: (v) => mh.sua("Đổi mờ tiếng cuối", (t) => this._datHoacXoa(t.segments[sel.i], "fadeOutAudio", v && r3(v))) }),
      );
      const truongPhu = [this._chu("Chương bắt đầu ở đây", seg.chapter, (v) => mh.sua("Đổi chương", (t) => this._datHoacXoa(t.segments[sel.i], "chapter", v)), "Để trống nếu không mở chương mới.")];
      if (seg.layout || tl.theme) truongPhu.push(this._chon("Bố cục", seg.layout || "mat", BO_CUC.map((x) => [x, x]),
        (v) => mh.sua("Đổi bố cục", (t) => { if (v === "mat") delete t.segments[sel.i].layout; else t.segments[sel.i].layout = v; })));
      if (mh.doc) truongPhu.push(this._so("Tâm khung dọc (0 trái, 1 phải)", seg.cropFocus ?? 0.5, { buoc: 0.01, min: 0, max: 1, donVi: "",
        ghi: (v) => mh.sua("Đổi tâm khung dọc", (t) => { t.segments[sel.i].cropFocus = r3(Math.min(1, Math.max(0, v ?? 0.5))); }) }));
      if (seg.audioSrc) truongPhu.push(el("p", { class: "nhat" }, `Tiếng lấy từ ${tenFile(seg.audioSrc)} tại ${r3(+seg.audioIn || 0)} s (multicam). Tỉa đầu đoạn tự dời mốc tiếng theo.`));
      nhom(...truongPhu);
      nhom(el("div", { class: "hang-nut" }, [
        this._nut("Tới đầu đoạn", () => this.xem.tua(it.t0)),
        this._nut("Tách tại đầu đọc", () => this.ui.lenh("tach")),
        mh.coTheNoi(tl, sel.i) ? this._nut("Nối với đoạn sau", () => this.ui.lenh("noi")) : null,
        this._nut("Xoá đoạn", () => this.ui.lenh("xoa"), "nguy"),
      ]));
      const ov = dsOverlay(seg), br = seg.broll || [];
      if (ov.length || br.length) {
        nhom(el("h4", {}, "Gắn trên đoạn này"),
          ...ov.map((o, k) => el("button", { class: "dong-kiem", onclick: () => this.ui.chon({ loai: "overlay", i: sel.i, k }) }, `Đồ họa nổi: ${tenFile(o.src)} lúc +${r3(+o.at || 0)} s`)),
          ...br.map((x, k) => el("button", { class: "dong-kiem", onclick: () => this.ui.chon({ loai: "broll", i: sel.i, k }) }, `B-roll: ${tenFile(x.src)}`)));
      }
      return;
    }

    if (sel.loai === "intro" || sel.loai === "outro") {
      const it = bc.items.find((x) => x.loai === sel.loai);
      if (!it) return this.ui.chon(null);
      tieuDe(sel.loai === "intro" ? "Intro" : "Outro", tenFile(tl[sel.loai]));
      nhom(this._so("Thời lượng", it.t1 - it.t0, { chiDoc: true }),
        el("div", { class: "hang-nut" }, [this._nut("Tới đầu", () => this.xem.tua(it.t0)), this._nut(`Bỏ ${sel.loai}`, () => this.ui.lenh("xoa"), "nguy")]));
      return;
    }

    if (sel.loai === "overlay") {
      const seg = tl.segments[sel.i];
      const o = seg && dsOverlay(seg)[sel.k];
      if (!o) return this.ui.chon(null);
      const x = bc.overlays.find((q) => q.i === sel.i && q.k === sel.k);
      tieuDe("Đồ họa nổi", tenFile(o.src));
      nhom(this._so("Hiện sau đầu đoạn", +o.at || 0, { buoc: 1 / mh.fps, min: 0,
          ghi: (v) => mh.sua("Dời đồ họa nổi", (t) => { dsOverlay(t.segments[sel.i])[sel.k].at = r3(Math.max(0, v ?? 0)); t.segments[sel.i].overlay = dsOverlay(t.segments[sel.i]); }),
          goiY: `Trên thành phẩm: ${x ? dongHo(x.t0) : "?"}. Kéo khối sang đoạn khác để chuyển thẻ sang đoạn đó.` }),
        this._so("Hiện trong", x ? x.ts.D : mh.dur(o.src), { buoc: 1 / mh.fps, min: 0.3,
          ghi: (v) => v !== null && mh.sua("Đổi thời lượng đồ họa nổi", (t) => mh.datThoiLuongThe(t, sel.i, sel.k, v)),
          goiY: `File dài ${r3(mh.dur(o.src))} s. Dài hơn: giữ khung giữa thẻ; ngắn hơn: bỏ bớt quãng giữa. Hoạt cảnh vào và ra giữ nguyên. Cũng kéo được mép phải khối trên dòng thời gian.` }),
        o.duration !== undefined ? el("div", { class: "hang-nut" }, [this._nut("Về độ dài gốc của file", () => mh.sua("Bỏ đổi thời lượng thẻ", (t) => { delete dsOverlay(t.segments[sel.i])[sel.k].duration; t.segments[sel.i].overlay = dsOverlay(t.segments[sel.i]); }))]) : null,
        x && x.tuNhien > x.t1 + 0.05 ? el("p", { class: "canh" }, `Thẻ bị cắt cụt ${r3(x.tuNhien - x.t1)} s vì đoạn hết hoặc B-roll bắt đầu.`) : null,
        el("div", { class: "hang-nut" }, [this._nut("Tới lúc hiện", () => this.xem.tua(x ? x.t0 : 0)), this._nut("Xoá thẻ", () => this.ui.lenh("xoa"), "nguy")]));
      return;
    }

    if (sel.loai === "broll") {
      const seg = tl.segments[sel.i];
      const x = seg && (seg.broll || [])[sel.k];
      if (!x) return this.ui.chon(null);
      const b = bc.brolls.find((q) => q.i === sel.i && q.k === sel.k);
      tieuDe("B-roll", tenFile(x.src));
      nhom(
        this._so("Bắt đầu (mốc trong file nguồn của đoạn)", x.at, { buoc: 1 / mh.fps, ghi: (v) => mh.sua("Dời B-roll", (t) => mh.datBroll(t, sel.i, sel.k, { at: v })) }),
        this._so("Dài", x.duration, { buoc: 1 / mh.fps, min: 0.2, ghi: (v) => mh.sua("Đổi độ dài B-roll", (t) => mh.datBroll(t, sel.i, sel.k, { duration: v })) }),
        this._so("Lấy hình từ giây", x.from || 0, { buoc: 1 / mh.fps, min: 0, goiY: "Giây trong file B-roll.", ghi: (v) => mh.sua("Đổi điểm lấy B-roll", (t) => mh.datBroll(t, sel.i, sel.k, { from: v ?? 0 })) }),
        el("div", { class: "hang-nut" }, [this._nut("Tới đầu B-roll", () => this.xem.tua(b ? b.t0 : 0)), this._nut("Xoá B-roll", () => this.ui.lenh("xoa"), "nguy")]));
      return;
    }

    if (sel.loai === "nhac") {
      const m = tl.music;
      if (!m) return this.ui.chon(null);
      const full = (m.mode || "full") === "full";
      tieuDe("Nhạc nền", tenFile(m.src));
      const thanh = el("input", { type: "range", min: -40, max: 0, step: 0.5, value: m.gainDb ?? -22 });
      const so = el("b", {}, `${m.gainDb ?? -22} dB`);
      thanh.addEventListener("input", () => { so.textContent = `${thanh.value} dB`; });
      thanh.addEventListener("change", () => mh.sua("Đổi âm lượng nhạc", (t) => { t.music.gainDb = +thanh.value; }));
      nhom(el("label", { class: "truong" }, [el("span", {}, "Âm lượng"), el("span", { class: "o-thanh" }, [thanh, so]),
        el("small", {}, "Mức gốc lấy theo thu-vien/AM-THANH.md; chỉnh ít một, nghe lại cùng lời nói.")]),
        this._chon("Kiểu", m.mode || "full", [["full", "suốt clip"], ["bookends", "chỉ dưới intro và outro"]],
          (v) => mh.sua("Đổi kiểu nhạc", (t) => { t.music.mode = v; })),
        full ? this._so("Mờ vào", m.fadeIn ?? 2, { buoc: 0.5, min: 0, ghi: (v) => mh.sua("Đổi mờ vào nhạc", (t) => { t.music.fadeIn = v ?? 0; }) }) : null,
        full ? this._so("Mờ ra", m.fadeOut ?? 4, { buoc: 0.5, min: 0, ghi: (v) => mh.sua("Đổi mờ ra nhạc", (t) => { t.music.fadeOut = v ?? 0; }) }) : null,
        full ? this._bat("Nhạc nhỏ đi khi có lời", m.duck !== false, (v) => mh.sua("Đổi giảm nhạc khi có lời", (t) => { t.music.duck = !!v; }),
          "Chỉ nghe được ở bản dựng thật; xem trước phát nhạc đều mức.") : el("p", { class: "nhat" }, "Kiểu bookends: độ mờ cố định theo assemble.py."),
        el("div", { class: "hang-nut" }, [this._nut("Bỏ nhạc", () => this.ui.lenh("xoa"), "nguy")]));
    }
  }
}
