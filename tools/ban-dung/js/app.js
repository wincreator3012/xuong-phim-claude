// Bàn dựng: nối mô hình, bộ xem, dòng thời gian, bảng thuộc tính; phím tắt; lưu.

import { clamp, dongHo, el, tenFile, veKhung } from "./tien-ich.js";
import { MoHinh, dsOverlay, laInsert } from "./mo-hinh.js";
import { BoXem } from "./xem.js";
import { DongThoiGian } from "./dong-thoi-gian.js";
import { BangThuocTinh } from "./thuoc-tinh.js";
import { KhungLoi } from "./loi.js";

const $ = (s) => document.querySelector(s);
const api = async (url, opt) => {
  const r = await fetch(url, opt);
  const j = await r.json().catch(() => ({}));
  return { ok: r.ok, code: r.status, j };
};
const nho = {
  doc(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
  ghi(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* trình duyệt chặn bộ nhớ: bỏ qua */ } },
};

let mh = null, xem = null, dtg = null, bang = null, loi = null, chon = null, tab = "loi";

// ---------- thông báo ----------
function bao(chu, loai = "") {
  const t = el("div", { class: `toast ${loai}` }, chu);
  $("#toasts").append(t);
  setTimeout(() => t.classList.add("an"), loai === "loi" ? 7000 : 3800);
  setTimeout(() => t.remove(), loai === "loi" ? 7600 : 4400);
}
function hopThoai(tieuDe, noiDung, nut) {
  return new Promise((ok) => {
    const nen = el("div", { class: "nen-hop" });
    const dong = (v) => { nen.remove(); ok(v); };
    nen.append(el("div", { class: "hop" }, [
      el("h3", {}, tieuDe),
      typeof noiDung === "string" ? el("p", {}, noiDung) : noiDung,
      el("div", { class: "hang-nut" }, nut.map(([v, t, phu]) => el("button", { class: `nut ${phu || ""}`, onclick: () => dong(v) }, t))),
    ]));
    nen.addEventListener("pointerdown", (e) => { if (e.target === nen) dong(null); });
    document.body.append(nen);
    const dau = nen.querySelector(".nut.chinh") || nen.querySelector(".nut");
    if (dau) dau.focus();
  });
}

// ---------- chọn dự án ----------
async function moChonDuAn(batBuoc = false) {
  const { j } = await api("/api/danh-sach");
  const ds = j.ds || [];
  const list = el("div", { class: "ds-du-an" });
  let chiaPhu = false;
  for (const x of ds) {
    if (x.phu && !chiaPhu) { list.append(el("h4", {}, "Dự án thử của xưởng")); chiaPhu = true; }
    const ngay = new Date(x.luc * 1000);
    list.append(el("button", { class: "dong-du-an", onclick: () => { nen.remove(); moTimeline(x.p); } }, [
      el("b", {}, x.tenDuAn), el("span", {}, `${x.file}${x.khung === "doc" ? " · dọc" : ""}`),
      el("small", {}, `${x.doan} đoạn · sửa ${ngay.toLocaleDateString("vi-VN")} ${ngay.toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}${x.chinhTay ? " · đã chỉnh tay" : ""}`),
    ]));
  }
  if (!ds.length) list.append(el("p", {}, "Chưa có timeline nào trong thư mục Du an. Nhờ Claude dựng phương án cắt trước."));
  const nen = el("div", { class: "nen-hop" }, [el("div", { class: "hop hop-rong" }, [
    el("h3", {}, "Mở timeline nào?"),
    el("p", { class: "nhat" }, "Mỗi dòng là một timeline Claude đã dựng. Bàn dựng sửa đúng file đó; bản cũ luôn được cất lại."),
    list,
    batBuoc ? null : el("div", { class: "hang-nut" }, [el("button", { class: "nut", onclick: () => nen.remove() }, "Đóng")]),
  ])]);
  document.body.append(nen);
}

// ---------- mở timeline ----------
async function moTimeline(p) {
  if (mh && mh.thayDoi) {
    const v = await hopThoai("Chưa lưu", "Timeline đang mở có thay đổi chưa lưu. Bỏ thay đổi và mở timeline khác?", [["bo", "Bỏ thay đổi", "nguy"], [null, "Ở lại"]]);
    if (v !== "bo") return;
  }
  $("#trang-thai").textContent = "đang mở…";
  const { ok, j } = await api(`/api/timeline?p=${encodeURIComponent(p)}`);
  if (!ok) { bao(`Không mở được: ${j.loi || "lỗi"}`, "loi"); return moChonDuAn(true); }
  nho.ghi("ban-dung-cuoi", p);
  history.replaceState(null, "", `?p=${encodeURIComponent(p)}`);
  const san = $("#san");
  san.querySelectorAll("video").forEach((v) => { v.pause(); v.removeAttribute("src"); v.load(); v.remove(); });
  $("#dong-thoi-gian").innerHTML = "";
  chon = null;
  mh = new MoHinh(j.tl, { p: j.p, duAn: j.duAn, phienBan: j.phienBan });
  const url = (src) => `/m/${encodeURIComponent(mh.duAn)}::${encodeURIComponent(src)}`;
  san.classList.toggle("doc", mh.doc);
  xem = new BoXem(san, mh, url);
  const ui = {
    layChon: () => chon,
    chon: (s, imLang, nguon) => datChon(s, imLang, nguon),
    lenh: (ten) => lenh(ten),
    bao: (chu, loai) => bao(chu, loai),
    hopThoai: (t, n, nut) => hopThoai(t, n, nut),
  };
  dtg = new DongThoiGian($("#dong-thoi-gian"), mh, xem, ui);
  bang = new BangThuocTinh($("#thuoc-tinh"), mh, xem, ui);
  $("#khung-loi").innerHTML = "";
  document.querySelectorAll(".l-thanh").forEach((x) => x.remove());
  loi = new KhungLoi($("#khung-loi"), mh, xem, ui);
  $("#ten-du-an").textContent = `${j.duAn.split("/").pop()} · ${j.p.slice(j.duAn.length + 1)}`;
  document.title = `Bàn dựng · ${j.duAn.split("/").pop()}`;

  // đo thời lượng và nạp dữ liệu phụ
  const tl = mh.tl;
  const srcs = new Set();
  const nguonCat = new Set();
  if (tl.intro) srcs.add(tl.intro);
  if (tl.outro) srcs.add(tl.outro);
  if (tl.music && tl.music.src) srcs.add(tl.music.src);
  for (const s of tl.segments || []) {
    srcs.add(s.src);
    if (!laInsert(s)) nguonCat.add(s.src);
    if (s.audioSrc) { srcs.add(s.audioSrc); nguonCat.add(s.audioSrc); }
    for (const o of dsOverlay(s)) srcs.add(o.src);
    for (const b of s.broll || []) srcs.add(b.src);
  }
  const [dur] = await Promise.all([
    xem.doThoiLuong([...srcs]),
    Promise.all([...nguonCat].map(async (src) => {
      const r = await api(`/api/phu-tro?duAn=${encodeURIComponent(mh.duAn)}&src=${encodeURIComponent(src)}`);
      if (r.ok) mh.phu[src] = r.j;
    })),
  ]);
  mh.thoiLuong = dur;
  mh._bc = null;   // bố cục đã tính trước khi có thời lượng và khoảng lặng: tính lại
  const thieu = Object.entries(dur).filter(([, d]) => !isFinite(d)).map(([s]) => tenFile(s));
  if (thieu.length) bao(`Trình duyệt không mở được: ${thieu.join(", ")}. Khối đó tạm tính 5 s.`, "loi");
  mh.nghe.add(daDoi);
  xem.nghe.add(daChay);
  dtg.vuaKhung();
  xem.tua(0);
  capNhatDau();
  bang.ve();
  loi.ve();
  datTab(loi.coDuLieu() ? "loi" : "thuoc");
  $("#trang-thai").textContent = "";
  // năng lượng tiếng cho dạng sóng (nạp sau, không chặn)
  for (const src of nguonCat) {
    const p = mh.phu[src];
    if (p && p.nangLuong) {
      fetch(url(p.nangLuong.url)).then((r) => r.ok ? r.arrayBuffer() : null).then((b) => { if (b) dtg.datNangLuong(src, new Uint8Array(b)); });
    }
  }
}

function daDoi(ly) {
  dtg.ve();
  if (ly !== "keo") { xem.boCucDoi(); loi.ve(); }
  bang.ve();
  capNhatDau();
}
function daChay(T, dangPhat) {
  dtg.datDauDoc(T, dangPhat);
  if (loi) loi.datDauDoc(T, dangPhat);
  $("#dong-ho").textContent = `${dongHo(T)} / ${dongHo(mh.boCuc().tong)}`;
  $("#nut-phat").textContent = dangPhat ? "Dừng" : "Phát";
  $("#nut-phat").classList.toggle("dang", dangPhat);
}
function datChon(s, imLang, nguon) {
  chon = s;
  if (!imLang) { dtg.ve(); bang.ve(); }
  document.querySelectorAll(".l-doan.chon").forEach((x) => x.classList.remove("chon"));
  if (s && s.loai === "doan") {
    const p = document.querySelector(`.l-doan[data-i="${s.i}"]`);
    if (p) p.classList.add("chon");
    if (nguon !== "loi" && loi && tab === "loi") loi.cuonToiDoan(s.i);
  } else if (s && nguon !== "loi") datTab("thuoc");
}
function datTab(t) {
  tab = t;
  document.querySelectorAll(".tab-phai button").forEach((b) => b.classList.toggle("dang", b.dataset.tab === t));
  $("#khung-loi").style.display = t === "loi" ? "" : "none";
  $("#thuoc-tinh").style.display = t === "thuoc" ? "" : "none";
}
function capNhatDau() {
  const doi = mh.thayDoi;
  $("#nut-luu").disabled = !doi;
  $("#nut-luu").classList.toggle("chinh", doi);
  $("#trang-luu").textContent = doi ? "Chưa lưu" : "Đã lưu";
  $("#trang-luu").classList.toggle("doi", doi);
  $("#nut-hoan").disabled = !mh.lich.length;
  $("#nut-lai").disabled = !mh.lai.length;
  $("#nut-hoan").title = mh.lich.length ? `Hoàn tác: ${mh.lich[mh.lich.length - 1].moTa} (Cmd+Z)` : "Hoàn tác (Cmd+Z)";
  const kq = mh.kiem();
  const chip = $("#chip-kiem");
  chip.textContent = kq.loi.length ? `${kq.loi.length} lỗi` : kq.canh.length ? `${kq.canh.length} cần xem` : "ổn";
  chip.className = `chip ${kq.loi.length ? "loi" : kq.canh.length ? "canh" : "on"}`;
}

// ---------- lệnh ----------
function doanTaiDauDoc() {
  const it = mh.mucTai(xem.T);
  return it && it.loai === "doan" ? it : null;
}
function lenh(ten) {
  if (!mh) return;
  const fps = mh.fps;
  switch (ten) {
    case "tach": {
      const it = doanTaiDauDoc();
      if (!it) return bao("Đặt đầu đọc vào giữa một đoạn quay rồi bấm S.");
      const x = veKhung(it.a + (xem.T - it.t0), fps);
      let moi = -1;
      mh.sua(`Tách đoạn ${it.i + 1}`, (tl) => { moi = mh.tach(tl, it.i, x); });
      if (moi < 0) return bao("Chỗ tách quá sát mép đoạn (mỗi nửa cần ít nhất 0,3 s).");
      datChon({ loai: "doan", i: moi });
      return;
    }
    case "tia-dau": case "tia-cuoi": {
      const it = doanTaiDauDoc();
      if (!it) return bao("Đặt đầu đọc vào một đoạn quay.");
      const x = veKhung(it.a + (xem.T - it.t0), fps);
      if (ten === "tia-dau") { mh.sua(`Tỉa đầu đoạn ${it.i + 1} tới đầu đọc`, (tl) => mh.tiaVao(tl, it.i, x)); xem.tua(it.t0); }
      else mh.sua(`Tỉa cuối đoạn ${it.i + 1} tới đầu đọc`, (tl) => mh.tiaRa(tl, it.i, x));
      datChon({ loai: "doan", i: it.i });
      return;
    }
    case "noi": {
      if (!chon || chon.loai !== "doan") return;
      if (!mh.coTheNoi(mh.tl, chon.i)) return bao("Chỉ nối được hai đoạn liền nhau trong cùng file nguồn.");
      mh.sua(`Nối đoạn ${chon.i + 1} với đoạn sau`, (tl) => mh.noi(tl, chon.i));
      datChon({ loai: "doan", i: chon.i });
      return;
    }
    case "xoa": {
      if (!chon) return;
      const s = chon;
      if (s.loai === "doan") {
        if (mh.tl.segments.length <= 1) return bao("Không xoá được đoạn cuối cùng.");
        mh.sua(`Xoá đoạn ${s.i + 1}`, (tl) => { tl.segments.splice(s.i, 1); });
        datChon(null);
      } else if (s.loai === "intro" || s.loai === "outro") {
        mh.sua(`Bỏ ${s.loai}`, (tl) => { delete tl[s.loai]; });
        datChon(null);
      } else if (s.loai === "overlay") {
        mh.sua("Xoá đồ họa nổi", (tl) => mh.xoaOverlay(tl, s.i, s.k));
        datChon({ loai: "doan", i: s.i });
      } else if (s.loai === "broll") {
        mh.sua("Xoá B-roll", (tl) => mh.xoaBroll(tl, s.i, s.k));
        datChon({ loai: "doan", i: s.i });
      } else if (s.loai === "nhac") {
        mh.sua("Bỏ nhạc nền", (tl) => { delete tl.music; });
        datChon(null);
      }
      bao("Đã xoá. Cmd+Z để lấy lại.");
      return;
    }
    case "hoan": { const m = mh.hoanTac(); if (m) bao(`Hoàn tác: ${m}`); return; }
    case "lai": { const m = mh.lamLai(); if (m) bao(`Làm lại: ${m}`); return; }
    case "luu": return luu();
  }
}

function ranhGioi(huong) {
  const ds = [0];
  for (const it of mh.boCuc().items) ds.push(it.t0, it.t1);
  const T = xem.T;
  const sap = [...new Set(ds.map((x) => Math.round(x * 1000) / 1000))].sort((a, b) => a - b);
  if (huong > 0) return sap.find((x) => x > T + 0.01) ?? T;
  return [...sap].reverse().find((x) => x < T - 0.01) ?? 0;
}

// ---------- lưu ----------
async function luu(ghiDe = false) {
  if (!mh || (!mh.thayDoi && !ghiDe)) return;
  const kq = mh.kiem();
  if (kq.loi.length) {
    await hopThoai("Chưa lưu được", el("ul", {}, kq.loi.map((x) => el("li", {}, x.chu))), [[null, "Để em sửa", "chinh"]]);
    return;
  }
  const tl = mh.banGhi();
  const { ok, code, j } = await api(`/api/timeline?p=${encodeURIComponent(mh.p)}`, {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ tl, phienBanCu: mh.phienBan, ghiDe }),
  });
  if (code === 409) {
    const v = await hopThoai("Timeline vừa đổi ở nơi khác",
      "Từ lúc bạn mở, file này đã được sửa (Claude vừa sửa, hoặc máy kia đồng bộ qua iCloud). Bạn muốn làm gì?",
      [["nap", "Nạp bản mới (bỏ thay đổi của bạn)", "nguy"], ["de", "Ghi đè bằng bản của bạn"], [null, "Để sau"]]);
    if (v === "de") return luu(true);
    if (v === "nap") { mh.daLuu = JSON.stringify(mh.tl); return moTimeline(mh.p); }
    return;
  }
  if (!ok) return bao(`Không lưu được: ${j.loi || code}`, "loi");
  mh.daGhi(j.phienBan, { _chinhTay: j.chinhTay });
  bao("Đã lưu. Bản cũ cất trong ke-hoach-dung/_phien-ban. Nhắn Claude là đã chỉnh xong để dựng lại bản nháp.", "tot");
}

// ---------- phím tắt ----------
const PHIM = [
  ["Space", "Phát / dừng"], ["K", "Dừng"], ["L", "Phát; bấm thêm để nhanh 1,5x, 2x"], ["J", "Lùi 2 giây"],
  ["← →", "Lùi / tiến một khung hình"], ["Shift + ← →", "Lùi / tiến 1 giây"], ["↑ ↓", "Nhảy tới ranh giới đoạn trước / sau"],
  ["S", "Tách đoạn tại đầu đọc"], ["[", "Tỉa đầu đoạn tới đầu đọc"], ["]", "Tỉa cuối đoạn tới đầu đọc"],
  ["Delete", "Xoá mục đang chọn"], ["Cmd + Z", "Hoàn tác"], ["Cmd + Shift + Z", "Làm lại"], ["Cmd + S", "Lưu"],
  ["= / -", "Phóng to / thu nhỏ dòng thời gian"], ["Shift + Z", "Vừa khung"], ["Esc", "Bỏ chọn"],
  ["Kéo mép khối", "Tỉa (khung xem hiện đúng khung hình ở mép)"], ["Kéo thân khối", "Đổi thứ tự đoạn, dời đồ họa nổi hoặc B-roll"],
  ["Cmd + con lăn", "Phóng to / thu nhỏ quanh con trỏ"], ["Bấm đúp", "Đưa đầu đọc tới chỗ bấm"],
];
function moPhim() {
  hopThoai("Phím tắt", el("table", { class: "bang-phim" }, PHIM.map(([k, t]) => el("tr", {}, [el("td", {}, el("kbd", {}, k)), el("td", {}, t)]))), [[null, "Đóng", "chinh"]]);
}

document.addEventListener("keydown", (e) => {
  if (!mh) return;
  const tag = (e.target.tagName || "").toLowerCase();
  if (tag === "input" || tag === "select" || tag === "textarea") return;
  if (document.querySelector(".nen-hop")) { if (e.key === "Escape") document.querySelector(".nen-hop").remove(); return; }
  // đang bôi đen chữ trong khung Lời: Delete bỏ, Enter khôi phục
  if (loi && !e.metaKey && !e.ctrlKey && ["Delete", "Backspace", "Enter"].includes(e.key)) {
    const v = loi.layVungChon();
    if (v) {
      e.preventDefault();
      if (v.loi) bao(v.loi);
      else if (e.key === "Enter") loi.khoiPhuc(); else loi.bo();
      return;
    }
  }
  const cmd = e.metaKey || e.ctrlKey;
  const fps = mh.fps;
  const k = e.key;
  let xong = true;
  if (cmd && (k === "z" || k === "Z")) lenh(e.shiftKey ? "lai" : "hoan");
  else if (cmd && (k === "y")) lenh("lai");
  else if (cmd && k === "s") lenh("luu");
  else if (cmd) xong = false;
  else if (k === " ") xem.batTat();
  else if (k === "k" || k === "K") { xem.dung(); xem.datToc(1); }
  else if (k === "l" || k === "L") {
    if (xem.dangPhat) xem.datToc(xem.toc >= 2 ? 2 : xem.toc + 0.5); else { xem.datToc(1); xem.phat(); }
    if (xem.toc > 1) bao(`Tốc độ ${String(xem.toc).replace(".", ",")}x`);
  }
  else if (k === "j" || k === "J") xem.tua(xem.T - 2);
  else if (k === "ArrowLeft") { xem.dung(); xem.tua(xem.T - (e.shiftKey ? 1 : 1 / fps)); }
  else if (k === "ArrowRight") { xem.dung(); xem.tua(xem.T + (e.shiftKey ? 1 : 1 / fps)); }
  else if (k === "ArrowUp") xem.tua(ranhGioi(-1));
  else if (k === "ArrowDown") xem.tua(ranhGioi(1));
  else if (k === "Home") xem.tua(0);
  else if (k === "End") xem.tua(mh.boCuc().tong);
  else if (k === "s" || k === "S") lenh("tach");
  else if (k === "[") lenh("tia-dau");
  else if (k === "]") lenh("tia-cuoi");
  else if (k === "Delete" || k === "Backspace") lenh("xoa");
  else if (k === "=" || k === "+") dtg.phong(1.4);
  else if (k === "-" || k === "_") dtg.phong(1 / 1.4);
  else if (k === "Z" && e.shiftKey) dtg.vuaKhung();
  else if (k === "Escape") datChon(null);
  else if (k === "?") moPhim();
  else xong = false;
  if (xong) e.preventDefault();
});

window.addEventListener("beforeunload", (e) => {
  if (mh && mh.thayDoi) { e.preventDefault(); e.returnValue = ""; }
});

// ---------- khởi động ----------
$("#nut-phat").addEventListener("click", () => xem && xem.batTat());
$("#nut-dau").addEventListener("click", () => xem && xem.tua(0));
$("#nut-lui").addEventListener("click", () => xem && xem.tua(ranhGioi(-1)));
$("#nut-toi").addEventListener("click", () => xem && xem.tua(ranhGioi(1)));
$("#nut-luu").addEventListener("click", () => lenh("luu"));
$("#nut-hoan").addEventListener("click", () => lenh("hoan"));
$("#nut-lai").addEventListener("click", () => lenh("lai"));
$("#nut-tach").addEventListener("click", () => lenh("tach"));
$("#nut-xoa").addEventListener("click", () => lenh("xoa"));
$("#nut-to").addEventListener("click", () => dtg && dtg.phong(1.4));
$("#nut-nho").addEventListener("click", () => dtg && dtg.phong(1 / 1.4));
$("#nut-vua").addEventListener("click", () => dtg && dtg.vuaKhung());
$("#nut-phim").addEventListener("click", moPhim);
$("#ten-du-an").addEventListener("click", () => moChonDuAn());
$("#chip-kiem").addEventListener("click", () => { datChon(null); datTab("thuoc"); });
document.querySelectorAll(".tab-phai button").forEach((b) => b.addEventListener("click", () => datTab(b.dataset.tab)));

(async () => {
  const q = new URLSearchParams(location.search).get("p") || nho.doc("ban-dung-cuoi");
  if (q) {
    const { ok } = await api(`/api/timeline?p=${encodeURIComponent(q)}`);
    if (ok) return moTimeline(q);
  }
  moChonDuAn(true);
})();

window.__banDung = { get mh() { return mh; }, get xem() { return xem; }, get dtg() { return dtg; }, get loi() { return loi; }, lenh, clamp, datTab };
