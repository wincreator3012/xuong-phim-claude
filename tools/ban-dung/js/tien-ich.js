// Tiện ích chung của Bàn dựng.

export const clamp = (x, a, b) => Math.min(b, Math.max(a, x));
export const r3 = (x) => Math.round(x * 1000) / 1000;
export const dbSangHeSo = (db) => Math.pow(10, db / 20);

/** Làm tròn mốc giây về khung hình gần nhất. */
export function veKhung(t, fps) {
  return r3(Math.round(t * fps) / fps);
}

/** 83.4 -> "1:23.40"; có giờ thì "1:01:23.40". */
export function dongHo(t, chiTiet = true) {
  if (!isFinite(t)) return "--:--";
  const am = t < 0;
  t = Math.abs(t);
  const h = Math.floor(t / 3600);
  const m = Math.floor((t % 3600) / 60);
  const s = t % 60;
  const ss = chiTiet ? s.toFixed(2).padStart(5, "0") : String(Math.floor(s)).padStart(2, "0");
  return (am ? "-" : "") + (h ? `${h}:${String(m).padStart(2, "0")}:${ss}` : `${m}:${ss}`);
}

/** Số giây dạng Việt: 1,25 s */
export function giay(t, chuSo = 2) {
  return `${(Math.round(t * 10 ** chuSo) / 10 ** chuSo).toLocaleString("vi-VN", { maximumFractionDigits: chuSo })} s`;
}

export function tenFile(p) {
  return (p || "").split("/").pop();
}

/** Tạo phần tử: el("div", {class: "x", onclick: fn}, [con...]) */
export function el(tag, thuoc = {}, con = []) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(thuoc)) {
    if (v === undefined || v === null || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "style" && typeof v === "object") Object.assign(e.style, v);
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else if (k === "text") e.textContent = v;
    else if (k === "html") e.innerHTML = v;
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of [].concat(con)) {
    if (c === null || c === undefined || c === false) continue;
    e.append(c instanceof Node ? c : document.createTextNode(String(c)));
  }
  return e;
}

/** Tìm phần tử cuối cùng có khoa(x) <= t trong mảng đã sắp. */
export function timTruoc(arr, t, khoa) {
  let lo = 0, hi = arr.length - 1, kq = -1;
  while (lo <= hi) {
    const mid = (lo + hi) >> 1;
    if (khoa(arr[mid]) <= t) { kq = mid; lo = mid + 1; } else hi = mid - 1;
  }
  return kq;
}

export function sao(x) {
  return JSON.parse(JSON.stringify(x));
}
