/* canh.js - runtime cho "cảnh minh hoạ" bằng HTML của xưởng phim.
 *
 * Một cảnh là một trang HTML có thời gian ẢO: mọi chuyển động là hàm của t (giây).
 * Cùng một file chạy được hai chế độ:
 *   - Xem trực tiếp (trình duyệt, artifact): tự chạy lặp, có thanh tua, chọn theme, chọn khung.
 *   - Chụp (tools/canh.mjs chup): công cụ gọi window.__canhSeek(t) cho từng khung rồi chụp ảnh,
 *     nên máy chậm chỉ làm render lâu hơn, không bao giờ rớt khung.
 *
 * Cách viết cảnh:
 *   CANH.canh({
 *     thoiLuong: 14,                 // giây
 *     khung: ['ngang', 'doc'],       // khung cảnh này hỗ trợ
 *     ve(t, K) { ... }               // đặt trạng thái của mọi phần tử tại thời điểm t
 *   });
 * Luật tất định (bắt buộc): trạng thái chỉ phụ thuộc t. Không dùng Date, Math.random không hạt,
 * setTimeout, CSS transition. CSS @keyframes được phép: runtime tự dừng và tua chúng theo t.
 */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const opt = Object.assign({}, window.__CANH_OPT__ || {});
  const CHUP = !!opt.chup || qs.has('chup');
  const root = document.documentElement;
  const theme = opt.theme || qs.get('theme') || root.dataset.theme || 'dem';
  const khung = opt.khung || qs.get('khung') || root.dataset.khung || 'ngang';
  const alpha = !!opt.alpha || qs.has('alpha');
  root.dataset.theme = theme;
  root.dataset.khung = khung;
  if (alpha) root.dataset.alpha = '1';
  if (CHUP) root.dataset.chup = '1';

  const W = khung === 'doc' ? 1080 : 1920;
  const H = khung === 'doc' ? 1920 : 1080;
  root.style.setProperty('--W', W + 'px');
  root.style.setProperty('--H', H + 'px');

  // ---- easing: cubic-bezier giải bằng Newton (giống CSS) ----
  function bezier(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = (u) => ((ax * u + bx) * u + cx) * u;
    const sy = (u) => ((ay * u + by) * u + cy) * u;
    const dx = (u) => (3 * ax * u + 2 * bx) * u + cx;
    return function (x) {
      if (x <= 0) return 0;
      if (x >= 1) return 1;
      let u = x;
      for (let i = 0; i < 8; i++) {
        const e = sx(u) - x;
        if (Math.abs(e) < 1e-6) break;
        const d = dx(u);
        if (Math.abs(d) < 1e-6) break;
        u -= e / d;
      }
      let lo = 0, hi = 1;
      for (let i = 0; i < 20 && Math.abs(sx(u) - x) > 1e-6; i++) {
        if (sx(u) < x) lo = u; else hi = u;
        u = (lo + hi) / 2;
      }
      return sy(u);
    };
  }
  const E = {
    em: bezier(0.22, 1, 0.36, 1),     // chữ ký của xưởng: vào nhanh, lắng chậm
    deu: (x) => x,
    vaora: bezier(0.65, 0, 0.35, 1),  // đi từ A sang B có chủ đích (vẽ đường, di chuyển)
    ra: bezier(0.55, 0, 1, 0.45),     // rời đi
  };

  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const lerp = (a, b, x) => a + (b - a) * x;
  // tiến độ đã easing của một chuyển động bắt đầu ở `bd`, dài `dai` giây
  function p(t, bd, dai = 0.8, e = E.em) {
    if (dai <= 0) return t >= bd ? 1 : 0;
    return e(clamp((t - bd) / dai));
  }
  // hiện rồi ẩn: vào ở bd, ra ở kt
  function pVaoRa(t, bd, kt, vao = 0.6, ra = 0.5) {
    return Math.min(p(t, bd, vao), 1 - p(t, kt - ra, ra, E.ra));
  }

  const $ = (sel, g = document) => (typeof sel === 'string' ? g.querySelector(sel) : sel);
  const $$ = (sel, g = document) => Array.from(g.querySelectorAll(sel));

  // hiện một phần tử: mờ -> rõ, trồi nhẹ; tuỳ chọn phóng, nhoè
  function hien(el, x, o = {}) {
    el = $(el);
    if (!el) return;
    const y = o.y ?? 24, xx = o.x ?? 0, s0 = o.s ?? 1, blur = o.blur ?? 0;
    if (x >= 1) {
      // đã lắng: trả phần tử về trạng thái tĩnh, bỏ lớp compositing, để khung chụp khi tua thẳng
      // và khi chạy tuần tự giống hệt nhau từng điểm ảnh
      el.style.opacity = ''; el.style.transform = ''; el.style.filter = ''; el.style.visibility = '';
      return;
    }
    el.style.opacity = String(clamp(x));
    const s = lerp(s0, 1, x);
    el.style.transform = `translate(${(1 - x) * xx}px, ${(1 - x) * y}px)` + (s !== 1 ? ` scale(${s})` : '');
    el.style.filter = blur ? `blur(${(1 - x) * blur}px)` : '';
    el.style.visibility = x <= 0.001 ? 'hidden' : 'visible';
  }
  // vẽ nét SVG theo tiến độ x
  function ve(path, x) {
    path = $(path);
    if (!path) return;
    const L = path.__L || (path.__L = path.getTotalLength());
    path.style.strokeDasharray = `${L} ${L}`;
    path.style.strokeDashoffset = String(L * (1 - clamp(x)));
  }
  // điểm trên đường tại tiến độ x
  function diem(path, x) {
    path = $(path);
    const L = path.__L || (path.__L = path.getTotalLength());
    return path.getPointAtLength(L * clamp(x));
  }
  // số đếm dồn, định dạng kiểu Việt (1.240; 3,5)
  function dem(tu, den, x, le = 0) {
    const v = lerp(tu, den, clamp(x));
    return v.toLocaleString('vi-VN', {minimumFractionDigits: le, maximumFractionDigits: le});
  }
  // gõ chữ: trả về phần chữ đã gõ (an toàn với dấu tiếng Việt tổ hợp)
  function go(chu, x) {
    const g = Array.from(chu.normalize('NFC'));
    return g.slice(0, Math.round(g.length * clamp(x))).join('');
  }
  // nhiễu tất định có hạt (cho lung linh, rung nhẹ)
  function hat(n) {
    const s = Math.sin(n * 127.1 + 311.7) * 43758.5453;
    return s - Math.floor(s);
  }
  const song = (t, chuKy = 3, bien = 1, pha = 0) => Math.sin((t / chuKy) * Math.PI * 2 + pha) * bien;

  let scene = null;
  let tNow = 0;

  function apDung(t) {
    tNow = t;
    // CSS @keyframes: dừng và tua theo t
    for (const a of document.getAnimations()) {
      try {
        a.pause();
        a.currentTime = t * 1000;
      } catch (e) { /* bỏ qua */ }
    }
    if (scene && scene.ve) scene.ve(t, K);
  }

  const K = {W, H, khung, theme, alpha, CHUP, E, p, pVaoRa, clamp, lerp, $, $$, hien, ve, diem, dem, go, hat, song};

  // hợp đồng với công cụ chụp
  window.__canhSeek = function (t) {
    apDung(t);
    return new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(() => r(true))));
  };

  function canh(def) {
    scene = def;
    window.__canh = {thoiLuong: def.thoiLuong, khung: def.khung || ['ngang', 'doc'], W, H, san: false};
    const batDau = () => {
      apDung(0);
      window.__canh.san = true;
      if (!CHUP) preview();
    };
    const fontsReady = document.fonts && document.fonts.ready ? document.fonts.ready : Promise.resolve();
    Promise.all([fontsReady, new Promise((r) => (document.readyState === 'complete' ? r() : addEventListener('load', r)))])
      .then(() => (def.chuanBi ? def.chuanBi(K) : null))
      .then(batDau);
  }

  // ---- chế độ xem trực tiếp: khớp khung vào cửa sổ, thanh điều khiển ----
  function preview() {
    const san = document.querySelector('.san');
    const bar = document.createElement('div');
    bar.className = 'canh-bar';
    const themes = [['dem', 'Đêm xanh'], ['than', 'Than đồng'], ['giay', 'Giấy mực']];
    // nằm trong khung của trang khác (phòng xem thử): trang cha lo theme và khung, chỉ giữ chạy/tua
    const trongKhung = window.parent !== window;
    const coKhung = trongKhung ? [khung] : window.__canh.khung;
    bar.innerHTML =
      '<button class="cb-play" aria-label="Chạy hoặc dừng">❚❚</button>' +
      '<input class="cb-tua" type="range" min="0" step="0.01" aria-label="Tua">' +
      '<span class="cb-gio">0,0 s</span>' +
      (trongKhung ? '' : '<select class="cb-theme" aria-label="Họ màu">' +
        themes.map(([k, v]) => `<option value="${k}"${k === theme ? ' selected' : ''}>${v}</option>`).join('') +
        '</select>') +
      (coKhung.length > 1
        ? '<select class="cb-khung" aria-label="Khung">' +
          [['ngang', 'Ngang 16:9'], ['doc', 'Dọc 9:16']].filter(([k]) => coKhung.includes(k))
            .map(([k, v]) => `<option value="${k}"${k === khung ? ' selected' : ''}>${v}</option>`).join('') +
          '</select>'
        : '');
    document.body.appendChild(bar);
    const tua = bar.querySelector('.cb-tua');
    const gio = bar.querySelector('.cb-gio');
    const nut = bar.querySelector('.cb-play');
    tua.max = String(scene.thoiLuong);
    const doiThamSo = (k, v) => {
      const u = new URL(location.href);
      u.searchParams.set(k, v);
      u.searchParams.set('t', tNow.toFixed(2));
      location.replace(u.toString());
    };
    const st = bar.querySelector('.cb-theme');
    if (st) st.onchange = (e) => doiThamSo('theme', e.target.value);
    const sk = bar.querySelector('.cb-khung');
    if (sk) sk.onchange = (e) => doiThamSo('khung', e.target.value);

    function khop() {
      const avW = innerWidth, avH = innerHeight - 56;
      const s = Math.min(avW / W, avH / H);
      san.style.transform = `scale(${s})`;
      san.style.left = `${(avW - W * s) / 2}px`;
      san.style.top = `${(avH - H * s) / 2}px`;
    }
    addEventListener('resize', khop);
    khop();

    let chay = true;
    let goc = performance.now() - (Number(qs.get('t')) || 0) * 1000;
    nut.onclick = () => {
      chay = !chay;
      nut.textContent = chay ? '❚❚' : '▶';
      goc = performance.now() - tNow * 1000;
    };
    tua.oninput = () => {
      chay = false;
      nut.textContent = '▶';
      apDung(Number(tua.value));
    };
    function vong(now) {
      if (chay) {
        let t = (now - goc) / 1000;
        if (t > scene.thoiLuong + 1.2) { goc = now; t = 0; }
        apDung(Math.min(t, scene.thoiLuong));
      }
      tua.value = String(tNow);
      gio.textContent = tNow.toLocaleString('vi-VN', {minimumFractionDigits: 1, maximumFractionDigits: 1}) + ' / ' +
        scene.thoiLuong.toLocaleString('vi-VN') + ' s';
      requestAnimationFrame(vong);
    }
    requestAnimationFrame(vong);
  }

  window.CANH = {canh, E, p, pVaoRa, clamp, lerp, hien, ve, diem, dem, go, hat, song, K};
})();
