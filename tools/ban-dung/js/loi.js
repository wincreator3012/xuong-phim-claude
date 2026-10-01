// Khung Lời của Bàn dựng: dựng bằng lời [text-based editing].
//
// Văn bản là chữ NGUYÊN VĂN (tools/moc-tu.py, giữ cả từ đệm), xếp theo đúng thứ tự dòng thời gian, mỗi đoạn
// một khối. Ba loại chữ:
//   giu   - chữ đang có trong clip;
//   ngoai - chữ ngay trước/sau đoạn trong file nguồn, chưa dùng (hiện mờ, khôi phục được để kéo dài đoạn);
//   bo    - chữ đã bị cắt bỏ giữa hai đoạn liền nhau trong cùng file (gạch ngang, khôi phục được).
// Bôi đen chữ bằng chuột rồi bấm "Bỏ" (Delete) hoặc "Khôi phục" (Enter). Điểm cắt do tools/ban_dung_loi.py
// tính trên máy chủ (một nguồn sự thật cho Bàn dựng, bộ kiểm và phòng nghe thử): chỉ cắt trong khe giữa hai
// âm tiết, theo năng lượng tiếng; ranh giới dính liền thì hỏi bạn nới vùng chọn.

import { clamp, el, giay, r3, timTruoc } from "./tien-ich.js";
import { laInsert, dsOverlay } from "./mo-hinh.js";

const TU_DEM = new Set(["à", "ờ", "á", "ạ", "ơ", "ừ", "ừm", "ư", "ơi", "hả", "hử", "ừa"]);
const KHOANG_TOI_DA = 20;      // giây: khoảng bỏ giữa hai đoạn dài hơn thì không hiện hết chữ bị bỏ
const CHU_NGOAI = 8;           // số chữ ngoài đoạn hiện ở mỗi đầu
const LANG_HIEN = 0.5;         // giây: khoảng lặng từ mức này hiện thành dấu

export class KhungLoi {
  constructor(goc, mh, xem, ui) {
    this.goc = goc;
    this.mh = mh;
    this.xem = xem;
    this.ui = ui;             // {chon, layChon, bao, hopThoai, duAn}
    this.span = new Map();    // "i:j" -> span chữ giữ
    this.dang = null;
    this.theo = true;
    this.thanh = el("div", { class: "l-thanh" });
    this.thanh.addEventListener("mousedown", (e) => e.preventDefault());
    document.body.append(this.thanh);
    this.vb = el("div", { class: "l-van-ban" });
    const dau = el("div", { class: "l-dau" }, [
      el("span", { class: "nhat" }, "Bôi đen chữ rồi bấm Delete để bỏ, Enter để khôi phục chữ mờ hoặc gạch."),
    ]);
    this.goc.append(dau, this.vb);
    this.vb.addEventListener("mouseup", () => setTimeout(() => this._capNhatChon(), 0));
    this.vb.addEventListener("keyup", () => this._capNhatChon());
    this.vb.addEventListener("click", (e) => this._bam(e));
    document.addEventListener("selectionchange", () => { if (!this._chonTrong()) this._anThanh(); });
    this.vb.addEventListener("scroll", () => this._anThanh());
  }

  // ---------- dữ liệu ----------
  _nguon(seg) { return seg.audioSrc || seg.src; }
  _lech(it) {
    const seg = it.seg;
    return seg.audioSrc ? (seg.audioIn !== undefined ? +seg.audioIn : it.a) - it.a : 0;
  }
  _tu(nguon) { const p = this.mh.phu[nguon]; return p && p.tu && p.tu.length ? p.tu : null; }
  _giua(w) { return (w.s + w.e) / 2; }
  coDuLieu() {
    return Object.values(this.mh.phu).some((p) => p && p.tu && p.tu.length);
  }

  /** Chỉ số các chữ có điểm giữa nằm trong [A, B] (mốc tiếng). */
  _trong(tu, A, B) {
    const ra = [];
    let j = Math.max(0, timTruoc(tu, A - 1, (w) => w.s));
    for (; j < tu.length && tu[j].s < B + 0.5; j++) {
      const g = this._giua(tu[j]);
      if (g >= A && g <= B) ra.push(j);
    }
    return ra;
  }

  /** Mô hình văn bản: mỗi mục dòng thời gian một khối. */
  _moHinhVanBan() {
    const bc = this.mh.boCuc();
    const khoi = [];
    const items = bc.items;
    // quãng tiếng đang được dùng ở MỌI đoạn: chữ mờ hoặc gạch chỉ hiện khi chưa đoạn nào dùng nó
    // (thứ tự đoạn có thể không theo thứ tự file; khôi phục chữ đã có ở đoạn khác sẽ thành lặp lời)
    const dung = {};
    for (const it of items) {
      if (it.loai !== "doan") continue;
      const ng = this._nguon(it.seg), l = this._lech(it);
      (dung[ng] = dung[ng] || []).push([it.a + l, it.b + l, it.i]);
    }
    const chuaDung = (ng, tu, i) => (j) => {
      const g = this._giua(tu[j]);
      return !(dung[ng] || []).some(([a, b, ii]) => ii !== i && g >= a && g <= b);
    };
    items.forEach((it, n) => {
      if (it.loai !== "doan") { khoi.push({ it, chen: true }); return; }
      const nguon = this._nguon(it.seg);
      const tu = this._tu(nguon);
      if (!tu) { khoi.push({ it, thieu: true }); return; }
      const lech = this._lech(it);
      const A = it.a + lech, B = it.b + lech;
      const giu = this._trong(tu, A, B);
      const truoc = items[n - 1], sau = items[n + 1];
      const cungNguon = (x) => x && x.loai === "doan" && this._nguon(x.seg) === nguon;
      let dau = [], vaiDau = null, cuoi = [];
      if (cungNguon(truoc)) {
        const pB = truoc.b + this._lech(truoc);
        if (Math.abs(pB - A) < 0.05) { /* liền mạch */ }
        else if (pB < A && A - pB <= KHOANG_TOI_DA) { dau = this._trong(tu, pB, A).filter((j) => !giu.includes(j)); vaiDau = "bo"; }
        else { dau = this._trong(tu, A - 30, A).filter((j) => this._giua(tu[j]) < A).slice(-CHU_NGOAI); vaiDau = "ngoai"; }
      } else {
        dau = this._trong(tu, A - 30, A).filter((j) => this._giua(tu[j]) < A).slice(-CHU_NGOAI);
        vaiDau = "ngoai";
      }
      if (cungNguon(sau)) {
        const nA = sau.a + this._lech(sau);
        if (Math.abs(nA - B) < 0.05 || (nA > B && nA - B <= KHOANG_TOI_DA)) { /* khối sau tự hiện */ }
        else cuoi = this._trong(tu, B, B + 30).filter((j) => this._giua(tu[j]) > B).slice(0, CHU_NGOAI);
      } else cuoi = this._trong(tu, B, B + 30).filter((j) => this._giua(tu[j]) > B).slice(0, CHU_NGOAI);
      const loc = chuaDung(nguon, tu, it.i);
      dau = dau.filter(loc);
      cuoi = cuoi.filter(loc);
      khoi.push({ it, nguon, tu, lech, A, B, giu, dau, vaiDau, cuoi });
    });
    return khoi;
  }

  // ---------- vẽ ----------
  ve() {
    const cuon = this.vb.scrollTop;
    this.vb.innerHTML = "";
    this.span.clear();
    this.dang = null;
    this._khoi = this._moHinhVanBan();
    const chon = this.ui.layChon();
    for (const k of this._khoi) {
      const it = k.it;
      if (k.chen) {
        this.vb.append(el("div", { class: "l-chen" }, `${it.loai === "intro" ? "Intro" : it.loai === "outro" ? "Outro" : "Đồ họa chèn"}: ${it.src.split("/").pop()}`));
        continue;
      }
      const p = el("div", { class: `l-doan${chon && chon.loai === "doan" && chon.i === it.i ? " chon" : ""}`, "data-i": it.i });
      p.append(el("span", { class: "l-so", contenteditable: "false" }, String(it.i + 1)));
      if (k.thieu) {
        p.append(el("span", { class: "nhat" }, "Chưa có mốc lời cho file này: nhắn Claude chạy moc-tu.py."));
        this.vb.append(p);
        continue;
      }
      const them = (j, vai) => {
        const w = k.tu[j];
        const s = el("span", { class: `w ${vai}${TU_DEM.has(w.w) ? " dem" : ""}`, "data-j": j, "data-i": it.i, "data-vai": vai }, (w.h || w.w));
        p.append(s, " ");
        return s;
      };
      if (k.dau.length && k.vaiDau === "ngoai" && k.tu[k.dau[0]] && k.dau[0] > 0) p.append(el("span", { class: "w ngoai ba-cham" }, "… "));
      k.dau.forEach((j) => them(j, k.vaiDau === "bo" ? "bo" : "ngoai-truoc"));
      let truoc = null;
      k.giu.forEach((j) => {
        if (truoc !== null) {
          const lang = k.tu[j].s - k.tu[truoc].e;
          if (lang >= LANG_HIEN) p.append(el("span", { class: "l-lang", title: `lặng ${giay(lang, 1)}` }, `· ${String(Math.round(lang * 10) / 10).replace(".", ",")}s `));
        }
        this.span.set(`${it.i}:${j}`, them(j, "giu"));
        truoc = j;
      });
      if (!k.giu.length) p.append(el("span", { class: "nhat" }, "(đoạn không có lời) "));
      k.cuoi.forEach((j) => them(j, "ngoai-sau"));
      if (k.cuoi.length) p.append(el("span", { class: "w ngoai ba-cham" }, "…"));
      this.vb.append(p);
    }
    this.vb.scrollTop = cuon;
    this.datDauDoc(this.xem.T, false);
  }

  /** Tô chữ đang phát; dangPhat: cuộn theo. */
  datDauDoc(T, dangPhat) {
    if (!this._khoi) return;
    const it = this.mh.mucTai(T);
    let s = null;
    if (it && it.loai === "doan") {
      const k = this._khoi.find((x) => x.it.i === it.i && !x.chen);
      if (k && k.tu) {
        const t = it.a + (T - it.t0) + k.lech;
        const j = timTruoc(k.tu, t + 0.02, (w) => w.s);
        if (j >= 0 && k.tu[j].e + 0.15 >= t) s = this.span.get(`${it.i}:${j}`) || null;
      }
    }
    if (s === this.dang) return;
    if (this.dang) this.dang.classList.remove("dang");
    this.dang = s;
    if (s) {
      s.classList.add("dang");
      if (dangPhat && this.theo && this.goc.offsetParent) {
        const r = s.getBoundingClientRect(), v = this.vb.getBoundingClientRect();
        if (r.top < v.top + 20 || r.bottom > v.bottom - 20) this.vb.scrollTop += r.top - v.top - v.height * 0.3;
      }
    }
  }

  cuonToiDoan(i) {
    const p = this.vb.querySelector(`.l-doan[data-i="${i}"]`);
    if (!p) return;
    const r = p.getBoundingClientRect(), v = this.vb.getBoundingClientRect();
    if (r.top < v.top || r.top > v.bottom - 40) this.vb.scrollTop += r.top - v.top - 12;
  }

  // ---------- chọn ----------
  _chonTrong() {
    const s = getSelection();
    return s && s.rangeCount && !s.isCollapsed && this.vb.contains(s.anchorNode) && this.vb.contains(s.focusNode);
  }
  /** Vùng chọn hiện tại: {i, vai, js} hoặc {loi: "..."}; null khi không chọn gì trong khung. */
  layVungChon() {
    if (!this._chonTrong()) return null;
    const r = getSelection().getRangeAt(0);
    const ds = [...this.vb.querySelectorAll(".w[data-j]")].filter((s) => r.intersectsNode(s.firstChild || s));
    // bỏ chữ chỉ bị chạm mép (con trỏ đứng ở đầu/cuối chữ)
    const that = ds.filter((s) => {
      const t = s.firstChild;
      if (!t) return false;
      if (t === r.endContainer && r.endOffset === 0) return false;
      if (t === r.startContainer && r.startOffset >= t.length) return false;
      return true;
    });
    if (!that.length) return null;
    const i = new Set(that.map((s) => +s.dataset.i));
    if (i.size > 1) return { loi: "Chỉ chọn chữ trong cùng một đoạn." };
    const vai = new Set(that.map((s) => s.dataset.vai));
    if (vai.size > 1) return { loi: vai.has("giu") ? "Vùng chọn lẫn cả chữ đang dùng và chữ mờ: chọn riêng từng loại." : "Chọn riêng chữ mờ phía trước hoặc phía sau." };
    return { i: [...i][0], vai: [...vai][0], js: that.map((s) => +s.dataset.j).sort((a, b) => a - b), ds: that };
  }

  _capNhatChon() {
    const v = this.layVungChon();
    if (!v) { this._anThanh(); return; }
    const r = getSelection().getRangeAt(0).getBoundingClientRect();
    this.thanh.innerHTML = "";
    if (v.loi) {
      this.thanh.append(el("span", {}, v.loi));
    } else {
      const k = this._khoi.find((x) => x.it.i === v.i && !x.chen);
      const dai = k.tu[v.js[v.js.length - 1]].e - k.tu[v.js[0]].s;
      const thongTin = el("span", { class: "nhat" }, `${v.js.length} chữ · ${giay(dai, 1)}`);
      if (v.vai === "giu") this.thanh.append(el("button", { class: "nut chinh nho", onclick: () => this.bo() }, "Bỏ (Delete)"), thongTin);
      else this.thanh.append(el("button", { class: "nut chinh nho", onclick: () => this.khoiPhuc() }, "Khôi phục (Enter)"), thongTin);
    }
    this.thanh.style.display = "flex";
    const w = this.thanh.offsetWidth;
    this.thanh.style.left = clamp(r.left + r.width / 2 - w / 2, 8, innerWidth - w - 8) + "px";
    this.thanh.style.top = Math.max(8, r.top - 40) + "px";
  }
  _anThanh() { this.thanh.style.display = "none"; }

  _bam(e) {
    const s = e.target.closest(".w[data-j]");
    if (!s || this._chonTrong()) return;
    const i = +s.dataset.i, j = +s.dataset.j;
    const k = this._khoi.find((x) => x.it.i === i && !x.chen);
    if (!k) return;
    this.ui.chon({ loai: "doan", i }, false, "loi");
    if (s.dataset.vai === "giu") {
      const T = k.it.t0 + (k.tu[j].s - k.A);
      this.xem.tua(clamp(T, k.it.t0, k.it.t1 - 0.01));
    } else {
      this.ui.bao(s.dataset.vai === "bo" ? "Chữ gạch là phần đã cắt bỏ. Bôi đen rồi Enter để khôi phục." : "Chữ mờ chưa có trong clip. Bôi đen rồi Enter để kéo dài đoạn tới đó.");
    }
  }

  // ---------- máy chủ ----------
  async _cat(nguon, body) {
    const r = await fetch(`/api/cat?duAn=${encodeURIComponent(this.mh.duAn)}`, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(Object.assign({ src: nguon }, body)),
    });
    const j = await r.json();
    if (!r.ok) throw new Error(j.loi || r.status);
    return j;
  }

  /** Ranh giới bi (giữa chữ bi và bi+1) dính liền: hỏi bạn nới hay thu vùng bỏ.
   *  phia "trai": ranh trái vùng (bi = p-1), "phai": ranh phải (bi = q). Trả bi mới, hoặc null nếu huỷ. */
  async _quyetRanh(k, bi, phia, p, q, loaiKhe, kieu) {
    const ds = (a, b) => k.tu.slice(a, b + 1).map((w) => w.h || w.w).join(" ");
    const sach = (x) => loaiKhe[x] && loaiKhe[x].loai !== "gat";
    const cungKhuc = (x) => x >= 0 && x + 1 < k.tu.length && k.tu[x].k === k.tu[x + 1].k;
    let ngoai = null, trong = null;
    // "bỏ": nới ra ngoài là bỏ thêm chữ; "khôi phục": nới ra ngoài là lấy lại thêm chữ
    for (let d = 1; d <= 4; d++) {
      const x = phia === "phai" ? bi + d : bi - d;
      if (ngoai === null && sach(x)) ngoai = x;
      if (!cungKhuc(x)) break;
    }
    for (let d = 1; d <= 4; d++) {
      const x = phia === "phai" ? bi - d : bi + d;
      if (phia === "phai" ? x < p : x >= q) break;
      if (sach(x)) { trong = x; break; }
    }
    const nut = [];
    const chuNgoai = ngoai === null ? "" : phia === "phai" ? ds(bi + 1, ngoai) : ds(ngoai + 1, bi);
    const chuTrong = trong === null ? "" : phia === "phai" ? ds(trong + 1, bi) : ds(bi + 1, trong);
    const tu = kieu === "bo" ? ["Bỏ luôn", "Giữ lại"] : ["Lấy luôn", "Không lấy"];
    if (ngoai !== null) nut.push(["ngoai", `${tu[0]} "${chuNgoai}"`, "chinh"]);
    if (trong !== null) nut.push(["trong", `${tu[1]} "${chuTrong}"`]);
    nut.push(["ep", "Vẫn cắt đúng chỗ đã chọn"], [null, "Thôi"]);
    const ben = phia === "phai" ? `"${k.tu[bi].h || k.tu[bi].w}" và "${k.tu[bi + 1].h || k.tu[bi + 1].w}"` :
      `"${k.tu[bi].h || k.tu[bi].w}" và "${k.tu[bi + 1].h || k.tu[bi + 1].w}"`;
    const v = await this.ui.hopThoai("Hai chữ dính liền", `${ben} nói liền một hơi, không có khe để cắt sạch. Cắt đúng chỗ đó có thể nghe gượng.`, nut);
    if (v === "ngoai") return ngoai;
    if (v === "trong") return trong;
    if (v === "ep") return bi;
    return null;
  }

  async _loaiKhe(nguon, a, b) {
    const ds = [];
    for (let x = Math.max(-1, a); x <= b; x++) ds.push(x);
    const r = await this._cat(nguon, { khe: ds });
    return r.khe || {};
  }

  // ---------- bỏ ----------
  async bo() {
    const v = this.layVungChon();
    if (!v || v.loi || v.vai !== "giu") return;
    getSelection().removeAllRanges();
    this._anThanh();
    const k = this._khoi.find((x) => x.it.i === v.i && !x.chen);
    let p = v.js[0], q = v.js[v.js.length - 1];
    const f = k.giu[0], l = k.giu[k.giu.length - 1];
    const i = v.i;
    if (p <= f && q >= l) {
      this.mh.sua(`Bỏ cả đoạn ${i + 1} bằng lời`, (tl) => { tl.segments.splice(i, 1); });
      this.ui.chon(null);
      return this.ui.bao("Đã bỏ cả đoạn. Cmd+Z để lấy lại.");
    }
    let loaiKhe;
    try { loaiKhe = await this._loaiKhe(k.nguon, p - 6, q + 5); } catch (e) { return this.ui.bao(`Không tính được điểm cắt: ${e.message}`, "loi"); }
    const gat = (x) => !loaiKhe[x] || loaiKhe[x].loai === "gat";
    if (p > f && gat(p - 1)) { const x = await this._quyetRanh(k, p - 1, "trai", p, q, loaiKhe, "bo"); if (x === null) return; p = x + 1; }
    if (q < l && gat(q)) { const x = await this._quyetRanh(k, q, "phai", p, q, loaiKhe, "bo"); if (x === null) return; q = x; }
    const dau = p <= f, cuoi = q >= l;
    if (dau && cuoi) {
      this.mh.sua(`Bỏ cả đoạn ${i + 1} bằng lời`, (tl) => { tl.segments.splice(i, 1); });
      this.ui.chon(null);
      return this.ui.bao("Đã bỏ cả đoạn. Cmd+Z để lấy lại.");
    }
    const yeu = {};
    if (!cuoi) yeu.vao = q + 1;
    if (!dau) yeu.ra = p - 1;
    let r;
    try { r = await this._cat(k.nguon, yeu); } catch (e) { return this.ui.bao(`Không tính được điểm cắt: ${e.message}`, "loi"); }
    const lech = k.lech;
    const chu = k.tu.slice(p, q + 1).map((w) => w.h || w.w).join(" ");
    if (dau) {
      const a = r.vao.t - lech;
      this.mh.sua(`Bỏ "${chu}" ở đầu đoạn ${i + 1}`, (tl) => this.mh.tiaVao(tl, i, a));
      this.xem.tua(k.it.t0);
    } else if (cuoi) {
      const b = r.ra.t - lech;
      this.mh.sua(`Bỏ "${chu}" ở cuối đoạn ${i + 1}`, (tl) => this.mh.tiaRa(tl, i, b));
    } else {
      const ra = r.ra.t - lech, vao = r.vao.t - lech;
      let ok = true;
      this.mh.sua(`Bỏ "${chu}" giữa đoạn ${i + 1}`, (tl) => {
        const sau = this.mh.tach(tl, i, ra);
        if (sau < 0) { ok = false; return; }
        this.mh.tiaVao(tl, sau, vao);
      });
      if (!ok) return this.ui.bao("Chỗ bỏ quá sát mép đoạn: bỏ luôn tới mép (chọn tới chữ đầu hoặc cuối đoạn).");
      this.xem.tua(k.it.t0 + Math.max(0, ra - k.it.a) - 1.5);
    }
    this.ui.chon({ loai: "doan", i }, false, "loi");
    const gatDung = (r.vao && r.vao.gat) || (r.ra && r.ra.gat);
    this.ui.bao(gatDung ? `Đã bỏ "${chu}" (cắt ở chỗ tiếng thấp nhất, nghe lại xem có gượng không). Cmd+Z để lấy lại.` : `Đã bỏ "${chu}". Cmd+Z để lấy lại.`);
  }

  // ---------- khôi phục ----------
  async khoiPhuc() {
    const v = this.layVungChon();
    if (!v || v.loi || v.vai === "giu") return;
    getSelection().removeAllRanges();
    this._anThanh();
    const i = v.i;
    const k = this._khoi.find((x) => x.it.i === i && !x.chen);
    let p = v.js[0], q = v.js[v.js.length - 1];
    let loaiKhe;
    try { loaiKhe = await this._loaiKhe(k.nguon, p - 6, q + 5); } catch (e) { return this.ui.bao(`Không tính được điểm cắt: ${e.message}`, "loi"); }
    const gat = (x) => !loaiKhe[x] || loaiKhe[x].loai === "gat";
    const chuCua = (a, b) => k.tu.slice(a, b + 1).map((w) => w.h || w.w).join(" ");
    const dauDoan = async () => {          // kéo dài đầu đoạn i tới chữ p
      if (gat(p - 1)) { const x = await this._quyetRanh(k, p - 1, "trai", p, q, loaiKhe, "lay"); if (x === null) return false; p = x + 1; }
      const r = await this._cat(k.nguon, { vao: p });
      const a = r.vao.t - k.lech;
      this.mh.sua(`Khôi phục "${chuCua(p, k.giu.length ? k.giu[0] - 1 : q)}" ở đầu đoạn ${i + 1}`, (tl) => this.mh.tiaVao(tl, i, a));
      return true;
    };
    if (v.vai === "ngoai-truoc") { if (await dauDoan()) this._xong(i); return; }
    if (v.vai === "ngoai-sau") {
      if (gat(q)) { const x = await this._quyetRanh(k, q, "phai", p, q, loaiKhe, "lay"); if (x === null) return; q = x; }
      const r = await this._cat(k.nguon, { ra: q });
      const b = r.ra.t - k.lech;
      this.mh.sua(`Khôi phục "${chuCua(k.giu.length ? k.giu[k.giu.length - 1] + 1 : p, q)}" ở cuối đoạn ${i + 1}`, (tl) => this.mh.tiaRa(tl, i, b));
      this._xong(i);
      return;
    }
    // chữ bị bỏ giữa đoạn i-1 và đoạn i
    const gap = k.dau;
    const het = p <= gap[0] && q >= gap[gap.length - 1];
    if (het && this.mh.coTheNoiQuaKhoang(this.mh.tl, i - 1)) {
      this.mh.sua(`Khôi phục "${chuCua(gap[0], gap[gap.length - 1])}" (nối lại đoạn ${i} và ${i + 1})`, (tl) => this.mh.noiQuaKhoang(tl, i - 1));
      this._xong(i - 1);
      return;
    }
    if (q >= gap[gap.length - 1] || p > gap[0]) { if (await dauDoan()) this._xong(i); return; }
    // chạm đầu khoảng: kéo dài cuối đoạn trước
    if (gat(q)) { const x = await this._quyetRanh(k, q, "phai", p, q, loaiKhe, "lay"); if (x === null) return; q = x; }
    const r = await this._cat(k.nguon, { ra: q });
    const truoc = this.mh.boCuc().items.find((x) => x.loai === "doan" && x.i === i - 1);
    const b = r.ra.t - this._lech(truoc);
    this.mh.sua(`Khôi phục "${chuCua(p, q)}" ở cuối đoạn ${i}`, (tl) => this.mh.tiaRa(tl, i - 1, b));
    this._xong(i - 1);
  }

  _xong(i) {
    this.ui.chon({ loai: "doan", i }, false, "loi");
    this.ui.bao("Đã khôi phục. Cmd+Z để hoàn tác.");
  }
}

export { r3, laInsert, dsOverlay };
