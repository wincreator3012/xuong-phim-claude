#!/usr/bin/env node
// canh.mjs - đóng gói, xem trước, chụp "cảnh minh hoạ" HTML ra video (chạy trong sandbox đám mây).
//
// Nguyên lý: cảnh là một trang web có thời gian ẢO (do-hoa-chung/canh-kit/canh.js). Công cụ mở
// trang trong Chromium không giao diện, tua đồng hồ tới từng khung (t = f / fps), chụp một ảnh,
// lặp tới hết, rồi ghép bằng ffmpeg. Máy chậm chỉ làm render lâu hơn, không rớt khung.
//
// Lệnh:
//   node tools/canh.mjs dong-goi <canh.html> --out <tep.html> [--theme dem|than|giay] [--khung ngang|doc] [--nen-anh <anh>]
//        → một file HTML tự chứa (font, CSS, JS nhúng sẵn) để xem trực tiếp hoặc đăng artifact
//   node tools/canh.mjs chup <canh.html> --out <tep.mp4|tep.webm> [--theme ..] [--khung ..] [--fps 30]
//        [--alpha] [--nen-anh <anh>] [--luong 2] [--tu <giây>] [--den <giây>] [--lam-lai]
//        [--pip] → mp4 (toàn khung, dùng làm broll) hoặc webm alpha (--alpha, nền trong suốt, dùng làm overlay);
//        --pip: hiện ô .o-pip chừa chỗ cho hình người nói, ghi toạ độ ô vào manifest cho tools/canh-ghep.py pip
//   node tools/canh.mjs anh <canh.html> --t 2,6.5,11 --out-dir <thư mục> [--theme ..] [--khung ..] [--nen-anh ..]
//        [--pip] [--xem-tren <khung hình thật>] [--alpha]   (--xem-tren: soi thẻ nổi trên hình thật, có che mặt không)
//        → ảnh tĩnh tại các mốc + một contact sheet (soi chữ, bố cục trước khi chụp cả cảnh)
//   node tools/canh.mjs phong-thu <canh.html> --out <tep.html> [--nen-anh <anh>] [--chan "<dòng ghi chú>"]
//        → trang "phòng thử" (đăng bằng Artifact) để anh xem cảnh chạy thật, đổi họ màu, khung, cách chèn
//   node tools/canh.mjs kiem <canh.html> [--theme ..] [--khung ..]
//        → kiểm tất định: tua thẳng tới một mốc phải ra đúng ảnh như khi chạy tuần tự tới mốc đó
//
// Ghi do-hoa-manifest.json cạnh file ra (cùng định dạng render-do-hoa.mjs) để assemble/nghiệm thu
// đọc chung; cảnh đã chụp đúng nội dung và tuỳ chọn thì bỏ qua (dấu vân tay nội dung).

import {execFileSync, spawnSync} from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';

const HERE = path.dirname(fileURLToPath(import.meta.url));
const XUONG = path.resolve(HERE, '..');
const KIT = path.join(XUONG, 'do-hoa-chung', 'canh-kit');

function loadPlaywright() {
  const require = createRequire(import.meta.url);
  const tries = ['playwright', 'playwright-core'];
  for (const t of tries) { try { return require(t); } catch (e) { /* thử tiếp */ } }
  try {
    const g = execFileSync('npm', ['root', '-g'], {encoding: 'utf8'}).trim();
    for (const t of tries) { try { return require(path.join(g, t)); } catch (e) { /* thử tiếp */ } }
  } catch (e) { /* không có npm */ }
  console.error('Thiếu playwright. Trong sandbox: npm i -g playwright (Chromium có sẵn ở /opt/pw-browsers).');
  process.exit(1);
}

// ---------- tham số ----------
const argv = process.argv.slice(2);
const lenh = argv[0];
const nguon = argv[1];
const co = (k) => argv.includes(k);
const gt = (k, d) => { const i = argv.indexOf(k); return i >= 0 && argv[i + 1] !== undefined ? argv[i + 1] : d; };
if (!lenh || !nguon || !['dong-goi', 'phong-thu', 'chup', 'anh', 'kiem'].includes(lenh)) {
  console.error('Cách dùng: node tools/canh.mjs <dong-goi|phong-thu|chup|anh|kiem> <canh.html> [tuỳ chọn] (xem đầu file)');
  process.exit(1);
}
const theme = gt('--theme', null);
const khung = gt('--khung', null);
const nenAnh = gt('--nen-anh', null);
const xemTren = gt('--xem-tren', null);
const alpha = co('--alpha');
const pip = co('--pip');

const mime = (f) => ({'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
  '.svg': 'image/svg+xml', '.woff2': 'font/woff2'})[path.extname(f).toLowerCase()] || 'application/octet-stream';
const dataUri = (f) => `data:${mime(f)};base64,${fs.readFileSync(f).toString('base64')}`;

// ---------- đóng gói: nhúng kit, font, ảnh vào một file ----------
function dongGoi(file, {theme: th, khung: kh, nenAnh: na, pip: pp, xemTren: xt} = {}) {
  let html = fs.readFileSync(file, 'utf8');
  const dir = path.dirname(path.resolve(file));
  const fontCss = fs.readFileSync(path.join(KIT, 'fonts', 'fonts.css'), 'utf8')
    .replace(/url\(\.\/([^)]+)\)/g, (_, f) => `url(${dataUri(path.join(KIT, 'fonts', f))})`);
  const css = fs.readFileSync(path.join(KIT, 'canh.css'), 'utf8');
  const js = fs.readFileSync(path.join(KIT, 'canh.js'), 'utf8');
  if (!html.includes('<!-- canh-kit -->')) throw new Error(`${file}: thiếu dấu <!-- canh-kit --> trong <head>`);
  const kit = `<style>${fontCss}\n${css}</style>\n<script>${js}</script>`;
  html = html.replace('<!-- canh-kit -->', () => kit);
  // ảnh tương đối trong cảnh (src="anh/x.png", url(anh/x.png)) → data URI
  html = html.replace(/(src|href)="(?!data:|https?:|#)([^"]+\.(?:png|jpe?g|webp|svg))"/g,
    (m, a, f) => { const p = path.resolve(dir, f); return fs.existsSync(p) ? `${a}="${dataUri(p)}"` : m; });
  html = html.replace(/url\((['"]?)(?!data:|https?:)([^)'"]+\.(?:png|jpe?g|webp|svg))\1\)/g,
    (m, q, f) => { const p = path.resolve(dir, f); return fs.existsSync(p) ? `url(${dataUri(p)})` : m; });
  if (th) html = html.replace(/data-theme="[^"]*"/, `data-theme="${th}"`);
  if (kh) html = html.replace(/data-khung="[^"]*"/, `data-khung="${kh}"`);
  if (pp) html = html.replace(/<html([^>]*)>/, '<html$1 data-pip="1">');
  if (na) {
    const layer = `<div class="nen-anh" style="background-image:url(${dataUri(path.resolve(na))})"></div><div class="nen-phu"></div>`;
    html = html.replace(/(<div class="san"[^>]*>)/, `$1${layer}`);
  }
  if (xt) {
    // soi đồ họa nổi trên khung hình thật: ảnh rõ, không mờ, nằm dưới cùng
    html = html.replace(/(<div class="san"[^>]*>)/, `$1<div class="nen-that" style="background-image:url(${dataUri(path.resolve(xt))})"></div>`);
  }
  return html;
}

function dauVanTay(html, extra) {
  return crypto.createHash('sha1').update(html).update(JSON.stringify(extra)).digest('hex');
}

async function moTrang(browser, html, {chup = true, alpha: a = false} = {}) {
  const tmp = path.join(os.tmpdir(), `canh-${process.pid}-${crypto.randomBytes(4).toString('hex')}.html`);
  fs.writeFileSync(tmp, html);
  const khungTrang = /data-khung="doc"/.test(html) ? 'doc' : 'ngang';
  const [W, H] = khungTrang === 'doc' ? [1080, 1920] : [1920, 1080];
  const ctx = await browser.newContext({viewport: {width: W, height: H}, deviceScaleFactor: 1});
  await ctx.addInitScript((o) => { window.__CANH_OPT__ = o; }, {chup, alpha: a});
  const page = await ctx.newPage();
  const loi = [];
  page.on('pageerror', (e) => loi.push(String(e)));
  page.on('console', (m) => { if (m.type() === 'error') loi.push(m.text()); });
  await page.goto('file://' + tmp);
  await page.waitForFunction(() => window.__canh && window.__canh.san === true, null, {timeout: 20000})
    .catch(() => { throw new Error('Cảnh không báo sẵn sàng (thiếu CANH.canh(...)?) ' + loi.join(' | ')); });
  if (loi.length) throw new Error('Lỗi JavaScript trong cảnh: ' + loi.join(' | '));
  const info = await page.evaluate(() => window.__canh);
  return {page, ctx, info, W, H, tmp, khung: khungTrang};
}

async function chupKhung(page, t, a, nhanh = false) {
  await page.evaluate((tt) => window.__canhSeek(tt), t);
  // nền đặc khi chụp video: JPEG chất lượng 95 nhanh gần gấp đôi PNG, mắt không phân biệt sau H.264
  if (nhanh && !a) return page.screenshot({type: 'jpeg', quality: 95, animations: 'allow', caret: 'initial'});
  return page.screenshot({type: 'png', omitBackground: a, animations: 'allow', caret: 'initial'});
}

function probe(file) {
  const out = execFileSync('ffprobe', ['-v', 'quiet', '-print_format', 'json', '-show_format', '-show_streams', file], {encoding: 'utf8'});
  const info = JSON.parse(out);
  const v = info.streams.find((s) => s.codec_type === 'video');
  const [n, d] = (v?.r_frame_rate ?? '0/1').split('/').map(Number);
  let dur = Number(v?.duration ?? info.format?.duration ?? 0);
  if (!dur && v?.tags?.DURATION) { const [h, m, s] = v.tags.DURATION.split(':').map(Number); dur = h * 3600 + m * 60 + s; }
  return {durationMeasured: Math.round(dur * 1000) / 1000, fps: d ? n / d : 0, width: v?.width, height: v?.height,
    alpha: v?.pix_fmt?.startsWith('yuva') || String(v?.tags?.alpha_mode ?? v?.tags?.ALPHA_MODE ?? '') === '1', hasAudio: false};
}

if (lenh === 'phong-thu') {
  const out = gt('--out', nguon.replace(/\.html$/, '.phong-thu.html'));
  const goi = dongGoi(nguon, {});
  const ten = (/<title>([^<]*)<\/title>/.exec(goi) || [, 'Cảnh minh hoạ'])[1].trim();
  const chan = gt('--chan', 'Mốc thời gian theo kịch bản cảnh; góp ý theo số giây trên thanh tua.');
  const esc = (x) => x.replace(/&/g, '&amp;').replace(/</g, '&lt;');
  let tpl = fs.readFileSync(path.join(KIT, 'phong-thu', 'phong-thu.html'), 'utf8');
  tpl = tpl.split('__TITLE__').join(esc(ten)).replace('__CHAN__', () => esc(chan))
    .replace('__GOI__', () => Buffer.from(goi, 'utf8').toString('base64'))
    .replace('__NEN__', () => (nenAnh ? dataUri(path.resolve(nenAnh)) : ''));
  fs.writeFileSync(out, tpl);
  console.log(`→ ${out} (${(fs.statSync(out).size / 1024).toFixed(0)} KB) - đăng bằng Artifact để anh xem trực tiếp`);
  process.exit(0);
}

const {chromium} = loadPlaywright();

// ---------- lệnh ----------
if (lenh === 'dong-goi') {
  const out = gt('--out', nguon.replace(/\.html$/, '.goi.html'));
  fs.writeFileSync(out, dongGoi(nguon, {theme, khung, nenAnh}));
  console.log(`→ ${out} (${(fs.statSync(out).size / 1024).toFixed(0)} KB, tự chứa)`);
  process.exit(0);
}

const browser = await chromium.launch({headless: true, args: ['--font-render-hinting=none', '--disable-gpu-vsync']});
try {
  if (lenh === 'anh') {
    const html = dongGoi(nguon, {theme, khung, nenAnh, pip, xemTren});
    const outDir = gt('--out-dir', path.join(path.dirname(nguon), 'anh-' + path.basename(nguon, '.html')));
    fs.mkdirSync(outDir, {recursive: true});
    const {page, info} = await moTrang(browser, html, {chup: true, alpha});
    const ts = (gt('--t', '') || '').split(',').filter(Boolean).map(Number);
    const moc = ts.length ? ts : [0.25, 0.5, 0.75, 1].map((x) => +(info.thoiLuong * x - (x === 1 ? 0.05 : 0)).toFixed(2));
    const files = [];
    for (const t of moc) {
      const f = path.join(outDir, `t${String(t.toFixed(2)).replace('.', '_')}.png`);
      fs.writeFileSync(f, await chupKhung(page, t, alpha));
      files.push(f);
      console.log(`  ảnh t=${t}s → ${f}`);
    }
    if (files.length > 1) {
      const sheet = path.join(outDir, 'contact-sheet.jpg');
      const cot = Math.min(files.length, info.W > info.H ? 2 : 4);
      const w = info.W > info.H ? 960 : 360;
      execFileSync('ffmpeg', ['-y', '-v', 'error', ...files.flatMap((f) => ['-i', f]), '-filter_complex',
        files.map((_, i) => `[${i}:v]scale=${w}:-1,drawtext=text='t=${moc[i]}s':x=12:y=12:fontsize=22:fontcolor=white:box=1:boxcolor=black@0.55[v${i}]`).join(';') + ';' +
        files.map((_, i) => `[v${i}]`).join('') + `xstack=inputs=${files.length}:layout=` +
        files.map((_, i) => { const c = i % cot, r = Math.floor(i / cot); return `${c ? Array(c).fill('w0').join('+') : '0'}_${r ? Array(r).fill('h0').join('+') : '0'}`; }).join('|') +
        (files.length % cot ? ':fill=black' : '') + '[o]', '-map', '[o]', '-q:v', '3', sheet]);
      console.log(`→ contact sheet: ${sheet}`);
    }
  }

  if (lenh === 'kiem') {
    const html = dongGoi(nguon, {theme, khung, nenAnh, pip});
    const a = await moTrang(browser, html, {chup: true});
    const b = await moTrang(browser, html, {chup: true});
    const T = a.info.thoiLuong;
    const moc = [0.37, 0.61, 0.83].map((x) => +(T * x).toFixed(3));
    // a: chạy tuần tự từ 0 tới từng mốc (30 fps); b: tua thẳng, đi lùi
    const ia = {}, ib = {};
    let f = 0;
    for (const m of moc) {
      for (; f / 30 < m; f++) await a.page.evaluate((tt) => window.__canhSeek(tt), f / 30);
      ia[m] = await chupKhung(a.page, m, false);
    }
    for (const m of [...moc].reverse()) ib[m] = await chupKhung(b.page, m, false);
    // so từng điểm ảnh; khác thì đo PSNR: >= 40 dB chỉ là khử răng cưa của lớp compositing
    // (chữ đang chuyển động), dưới 40 dB là trạng thái phụ thuộc lịch sử tua - lỗi thật
    const ketQua = moc.map((m) => {
      if (Buffer.compare(ia[m], ib[m]) === 0) return {m, db: Infinity};
      const fa = path.join(os.tmpdir(), `kiem-a-${m}.png`), fb = path.join(os.tmpdir(), `kiem-b-${m}.png`);
      fs.writeFileSync(fa, ia[m]); fs.writeFileSync(fb, ib[m]);
      let db = 0;
      try {
        const r = spawnSync('ffmpeg', ['-v', 'info', '-i', fa, '-i', fb, '-lavfi', 'psnr', '-f', 'null', '-'], {encoding: 'utf8'});
        const mm = /average:([\d.]+|inf)/.exec(r.stderr || '');
        db = mm ? (mm[1] === 'inf' ? Infinity : Number(mm[1])) : 0;
      } catch (e) { db = 0; }
      return {m, db};
    });
    const sai = ketQua.filter((k) => k.db < 40);
    const gan = ketQua.filter((k) => k.db >= 40 && k.db !== Infinity);
    if (sai.length) {
      console.log(`KIỂM TẤT ĐỊNH: KHÔNG ĐẠT tại ${sai.map((k) => `${k.m} s (${k.db.toFixed(1)} dB)`).join(', ')} - trạng thái phụ thuộc lịch sử tua (biến cộng dồn, Math.random, transition CSS, setTimeout...)`);
      process.exitCode = 2;
    } else console.log(`KIỂM TẤT ĐỊNH: ĐẠT (${moc.length} mốc, tua thẳng = chạy tuần tự` +
      (gan.length ? `; ${gan.length} mốc lệch nhẹ khử răng cưa, ≥ 40 dB` : '') + ')');
  }

  if (lenh === 'chup') {
    const out = path.resolve(gt('--out', nguon.replace(/\.html$/, alpha ? '.webm' : '.mp4')));
    const fps = Number(gt('--fps', 30));
    const luong = Math.max(1, Number(gt('--luong', Math.min(2, os.cpus().length))));
    if (xemTren) { console.error('--xem-tren chỉ dùng với lệnh anh (soi), không chụp vào video'); process.exit(1); }
    const html = dongGoi(nguon, {theme, khung, nenAnh, pip});
    const tuyChon = {fps, alpha, pip, tu: gt('--tu', null), den: gt('--den', null)};
    const hash = dauVanTay(html, tuyChon);
    const outDir = path.dirname(out);
    fs.mkdirSync(outDir, {recursive: true});
    const mfFile = path.join(outDir, 'do-hoa-manifest.json');
    const mf = fs.existsSync(mfFile) ? JSON.parse(fs.readFileSync(mfFile, 'utf8')) : {};
    const prev = mf[path.basename(out)];
    if (!co('--lam-lai') && prev && prev.propsHash === hash && fs.existsSync(out) && !prev.error) {
      console.log(`= bỏ qua ${path.basename(out)} (đã chụp đúng nội dung này; --lam-lai để chụp lại)`);
    } else {
      const probePage = await moTrang(browser, html, {chup: true, alpha});
      const T = probePage.info.thoiLuong;
      const tu = Number(tuyChon.tu ?? 0), den = Number(tuyChon.den ?? T);
      const n = Math.round((den - tu) * fps);
      // kiểu chèn "thu vào góc": đo khung trong của ô .o-pip ở cuối cảnh để canh-ghep.py đặt hình thật
      let oPip = null;
      if (pip) {
        await probePage.page.evaluate((tt) => window.__canhSeek(tt), Math.max(0, den - 0.05));
        oPip = await probePage.page.evaluate(() => {
          const el = document.querySelector('.o-pip');
          if (!el) return null;
          const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
          const b = parseFloat(cs.borderTopWidth) || 0;
          const chan = (v) => Math.round(v / 2) * 2;
          return {x: chan(r.left + b), y: chan(r.top + b), w: chan(r.width - 2 * b), h: chan(r.height - 2 * b),
            r: Math.max(0, Math.round((parseFloat(cs.borderTopLeftRadius) || 0) - b))};
        });
        if (!oPip) throw new Error('Chụp với --pip nhưng cảnh không có phần tử .o-pip');
      }
      await probePage.ctx.close();
      const frames = fs.mkdtempSync(path.join(os.tmpdir(), 'canh-frames-'));
      const bd = Date.now();
      console.log(`Chụp ${path.basename(nguon)}: ${n} khung (${(den - tu).toFixed(2)} s × ${fps} fps), ${luong} luồng, ${alpha ? 'nền trong suốt' : 'nền đặc'}`);
      let xong = 0;
      await Promise.all(Array.from({length: luong}, async (_, w) => {
        const {page, ctx} = await moTrang(browser, html, {chup: true, alpha});
        for (let i = w; i < n; i += luong) {
          const buf = await chupKhung(page, tu + i / fps, alpha, true);
          fs.writeFileSync(path.join(frames, `f${String(i).padStart(6, '0')}.${alpha ? 'png' : 'jpg'}`), buf);
          xong++;
          if (xong % 60 === 0) console.log(`  ${xong}/${n} khung, ${((Date.now() - bd) / 1000).toFixed(0)} s`);
        }
        await ctx.close();
      }));
      const vao = ['-y', '-v', 'error', '-framerate', String(fps), '-i', path.join(frames, `f%06d.${alpha ? 'png' : 'jpg'}`)];
      const ma = alpha
        ? ['-c:v', 'libvpx', '-deadline', 'realtime', '-cpu-used', '8', '-auto-alt-ref', '0', '-b:v', '2M', '-pix_fmt', 'yuva420p']
        : ['-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', '-movflags', '+faststart'];
      execFileSync('ffmpeg', [...vao, ...ma, '-r', String(fps), out], {stdio: 'inherit'});
      fs.rmSync(frames, {recursive: true, force: true});
      const m = probe(out);
      const lech = Math.abs(m.durationMeasured - n / fps);
      mf[path.basename(out)] = {comp: 'canh:' + path.basename(nguon), durationInSeconds: n / fps, propsHash: hash, ...m,
        theme: theme ?? 'mac-dinh', khung: khung ?? 'mac-dinh', ok: lech < 0.1, ...(oPip ? {pip: oPip} : {})};
      fs.writeFileSync(mfFile, JSON.stringify(mf, null, 1));
      console.log(`→ ${out}: ${m.durationMeasured} s, ${m.width}x${m.height}, ${m.fps} fps${m.alpha ? ', alpha' : ''}, ` +
        `${((Date.now() - bd) / 1000).toFixed(0)} s chụp` + (lech >= 0.1 ? `  CẢNH BÁO: lệch ${lech.toFixed(2)} s so với dự kiến` : ''));
    }
  }
} finally {
  await browser.close();
}
