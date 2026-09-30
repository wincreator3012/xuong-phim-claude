#!/usr/bin/env node
// Render đồ họa Remotion theo file job JSON (chạy trong sandbox đám mây).
// Cách dùng: node tools/render-do-hoa.mjs <job.json> [--studio <dir>]
//
// job.json:
// {
//   "aspect": "ngang" | "doc",          // mặc định "ngang"
//   "theme": "light" | "dark",          // mặc định "light"
//   "brandFile": "brand/brand.json",    // tùy chọn, ghi đè brand mặc định
//   "outDir": "out",
//   "jobs": [
//     {"comp": "Intro", "out": "intro.mp4",
//      "props": {"title": "…", "subtitle": "…", "durationInSeconds": 6}},
//     {"comp": "LowerThird", "out": "lt.webm", "alpha": true, "props": {…}},
//     {"comp": "Thumbnail", "out": "thumb-1.jpg", "still": true, "aspect": "ngang", "props": {…}}
//   ]
// }
// - "comp" không cần hậu tố -ngang/-doc: script tự thêm theo "aspect".
// - "still": true → ảnh tĩnh (jpg/png) bằng "remotion still", kiểm kích thước và giới hạn 2 MB.
// - "aspect" trong từng job ghi đè "aspect" chung (một job thumbnail có cả bản ngang lẫn dọc).
// - "alpha": true → xuất webm nền trong suốt (vp8 + yuva420p) để phủ lên video.
//   Mặc định đi đường nhanh: chuỗi PNG + ffmpeg libvpx (xem chú thích trong vòng lặp).
// Cờ: --lam-lai (render lại cả job đã có), --gioi-han <giây> (dừng gọn khi hết giờ, thoát mã 2,
//     chạy lại để tiếp), --alpha-remotion (dùng encoder vp8 chậm của Remotion).
// Job đã render đúng props được bỏ qua nhờ propsHash trong do-hoa-manifest.json.

import {execFileSync} from 'node:child_process';
import crypto from 'node:crypto';
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const jobFile = args[0];
if (!jobFile) {
  console.error('Thiếu file job JSON');
  process.exit(1);
}
const studioIdx = args.indexOf('--studio');
const studioDir = studioIdx >= 0 ? args[studioIdx + 1] : path.resolve(process.cwd(), 'studio');
const forceAll = args.includes('--lam-lai');          // render lại cả job đã có
const slowAlpha = args.includes('--alpha-remotion');  // dùng encoder vp8 của Remotion (chậm) thay ffmpeg
const budgetIdx = args.indexOf('--gioi-han');          // giây; hết giờ thì dừng gọn, chạy lại để tiếp
const budgetSec = budgetIdx >= 0 ? Number(args[budgetIdx + 1]) : Infinity;
const startedAt = Date.now();
const pending = [];
let hasLibvpx = false;
try {
  hasLibvpx = execFileSync('ffmpeg', ['-hide_banner', '-encoders'], {encoding: 'utf8'}).includes('libvpx');
} catch (e) {
  hasLibvpx = false;
}

const spec = JSON.parse(fs.readFileSync(jobFile, 'utf8'));
const aspect = spec.aspect ?? 'ngang';
const theme = spec.theme ?? 'light';
const outDir = path.resolve(path.dirname(jobFile), spec.outDir ?? 'out');
fs.mkdirSync(outDir, {recursive: true});

let brand = {};
if (spec.brandFile) {
  const brandPath = path.resolve(path.dirname(jobFile), spec.brandFile);
  brand = JSON.parse(fs.readFileSync(brandPath, 'utf8'));
  // Tự đồng bộ brand/logo/* vào studio/public/brand/ để staticFile tìm thấy
  const logoDir = path.join(path.dirname(brandPath), 'logo');
  if (fs.existsSync(logoDir)) {
    const dstDir = path.join(studioDir, 'public', 'brand');
    fs.mkdirSync(dstDir, {recursive: true});
    for (const f of fs.readdirSync(logoDir)) {
      if (/\.(png|jpg|jpeg|svg|webp)$/i.test(f)) {
        fs.copyFileSync(path.join(logoDir, f), path.join(dstDir, f));
      }
    }
  }
}

// "assets": các file (logo, QR…) copy vào studio/public/brand/ trước khi render.
// Đường dẫn tương đối so với file job.
// Mục dạng {"from": "<đường dẫn>", "as": "<tên trong public/brand>"} để đổi tên (ảnh khung thumbnail).
for (const asset of spec.assets ?? []) {
  const from = typeof asset === 'string' ? asset : asset.from;
  const src = path.resolve(path.dirname(jobFile), from);
  const dst = path.join(studioDir, 'public', 'brand', typeof asset === 'string' ? path.basename(asset) : asset.as);
  fs.mkdirSync(path.dirname(dst), {recursive: true});
  fs.copyFileSync(src, dst);
  console.log(`→ Asset: ${path.basename(dst)}`);
}

// Nghiệm thu ngay sau render (bản vá 2026-09-05): đo file bằng ffprobe, so với
// props.durationInSeconds; ghi do-hoa-manifest.json để assemble/nghiem-thu dùng lại.
function probeOut(file) {
  try {
    const out = execFileSync('ffprobe', ['-v', 'quiet', '-print_format', 'json',
      '-show_format', '-show_streams', file], {encoding: 'utf8'});
    const info = JSON.parse(out);
    const v = info.streams.find((s) => s.codec_type === 'video');
    const a = info.streams.find((s) => s.codec_type === 'audio');
    const [n, d] = (v?.r_frame_rate ?? '0/1').split('/').map(Number);
    let dur = Number(v?.duration ?? info.format?.duration ?? 0);
    if (!dur && v?.tags?.DURATION) {
      const [h, m, s] = v.tags.DURATION.split(':').map(Number);
      dur = h * 3600 + m * 60 + s;
    }
    return {
      durationMeasured: Math.round(dur * 1000) / 1000,
      fps: d ? n / d : 0,
      width: v?.width, height: v?.height,
      alpha: v?.pix_fmt?.startsWith('yuva') || String(v?.tags?.alpha_mode ?? v?.tags?.ALPHA_MODE ?? '') === '1',
      hasAudio: Boolean(a),
    };
  } catch (e) {
    return {error: String(e.message ?? e)};
  }
}
const manifestFile = path.join(outDir, 'do-hoa-manifest.json');
const manifest = fs.existsSync(manifestFile) ? JSON.parse(fs.readFileSync(manifestFile, 'utf8')) : {};
const failures = [];

// Nếu brand có logo, file logo phải nằm ở studio/public/brand/
for (const job of spec.jobs) {
  const compId = `${job.comp}-${job.aspect ?? aspect}`; // job được ghi đè khung riêng (vd thumbnail ngang + dọc)
  const props = {theme, brand, ...(job.props ?? {})};
  const propsFile = path.join(outDir, `.props-${job.comp}-${Date.now()}.json`);
  fs.writeFileSync(propsFile, JSON.stringify(props));
  const outFile = path.join(outDir, job.out);

  const cliArgs = [
    'remotion',
    'render',
    'src/index.ts',
    compId,
    outFile,
    `--props=${propsFile}`,
    '--log=error',
  ];
  // Bỏ qua job đã render đúng props (cho phép chạy lại nhiều lượt khi mỗi lượt gọi tool bị giới hạn
  // thời gian): so dấu vân tay props với manifest và file còn đó. --lam-lai để ép render lại.
  const propsHash = crypto.createHash('sha1').update(JSON.stringify({compId, props, alpha: !!job.alpha, still: !!job.still})).digest('hex');
  const prev = manifest[path.basename(outFile)];
  if (!forceAll && prev && prev.propsHash === propsHash && !prev.error && prev.ok !== false &&
      fs.existsSync(outFile) && fs.statSync(outFile).size > 1000) {
    console.log(`→ Bỏ qua ${path.basename(outFile)} (đã render đúng props)`);
    fs.unlinkSync(propsFile);
    continue;
  }
  if (Date.now() - startedAt > budgetSec * 1000) {
    fs.unlinkSync(propsFile);
    pending.push(job.out);
    continue;
  }
  console.log(`→ Render ${compId} → ${path.basename(outFile)}`);
  if (job.still) {
    // Ảnh tĩnh (thumbnail): "remotion still", jpg chất lượng 90 (YouTube giới hạn 2 MB khi tải từ điện thoại)
    const isPng = /\.png$/i.test(outFile);
    execFileSync('npx', ['remotion', 'still', 'src/index.ts', compId, outFile, `--props=${propsFile}`, '--log=error',
      ...(isPng ? ['--image-format=png'] : ['--image-format=jpeg', `--jpeg-quality=${job.jpegQuality ?? 90}`])],
    {cwd: studioDir, stdio: 'inherit'});
  } else if (job.alpha && hasLibvpx && !slowAlpha) {
    // Đường nhanh cho alpha (2026-09-29): Remotion encode vp8 alpha bằng một luồng, một lower-third
    // 4.5 s mất ~90 s trên máy 2 lõi. Render chuỗi PNG (~10 s) rồi để ffmpeg libvpx realtime encode
    // (~5 s) cho cùng kết quả vp8 + yuva420p (alpha_mode=1), nhanh ~6 lần.
    const seqDir = path.join(outDir, `_seq_${Date.now()}`);
    fs.rmSync(seqDir, {recursive: true, force: true});
    execFileSync('npx', ['remotion', 'render', 'src/index.ts', compId, seqDir, '--sequence',
      `--props=${propsFile}`, '--image-format=png', '--log=error'], {cwd: studioDir, stdio: 'inherit'});
    const pngs = fs.readdirSync(seqDir).filter((f) => f.endsWith('.png')).sort();
    const m = pngs[0]?.match(/^(.*?)(\d+)\.png$/);
    if (!m) throw new Error(`Không thấy khung PNG trong ${seqDir}`);
    const pattern = path.join(seqDir, `${m[1]}%0${m[2].length}d.png`);
    const fps = job.fps ?? spec.fps ?? 30;
    execFileSync('ffmpeg', ['-v', 'error', '-y', '-framerate', String(fps), '-start_number', String(Number(m[2])),
      '-i', pattern, '-c:v', 'libvpx', '-deadline', 'realtime', '-cpu-used', '8', '-auto-alt-ref', '0',
      '-b:v', '2M', '-pix_fmt', 'yuva420p', outFile], {stdio: 'inherit'});
    fs.rmSync(seqDir, {recursive: true, force: true});
  } else {
    if (job.alpha) {
      cliArgs.push('--codec=vp8', '--image-format=png', '--pixel-format=yuva420p');
    } else {
      cliArgs.push('--codec=h264', '--crf=17');
    }
    execFileSync('npx', cliArgs, {cwd: studioDir, stdio: 'inherit'});
  }
  fs.unlinkSync(propsFile);

  // Nghiệm thu file vừa render
  if (job.still) {
    const m = probeOut(outFile);
    const bytes = fs.existsSync(outFile) ? fs.statSync(outFile).size : 0;
    const entry = {comp: compId, still: true, propsHash, width: m.width, height: m.height, bytes};
    const probs = [];
    if (m.error || !bytes) probs.push('không đọc được ảnh');
    if (bytes > 2 * 1024 * 1024) probs.push(`nặng ${(bytes / 1048576).toFixed(2)} MB, vượt 2 MB (hạ jpegQuality)`);
    entry.ok = probs.length === 0;
    manifest[path.basename(outFile)] = entry;
    fs.writeFileSync(manifestFile, JSON.stringify(manifest, null, 1));
    if (probs.length) failures.push(`${job.out}: ${probs.join('; ')}`);
    else console.log(`   ✓ ${path.basename(outFile)}: ${m.width}x${m.height}, ${(bytes / 1024).toFixed(0)} KB`);
    continue;
  }
  const m = probeOut(outFile);
  const expected = job.props?.durationInSeconds ?? null;
  const entry = {comp: compId, durationInSeconds: expected, propsHash, ...m};
  entry.ok = !m.error && !(expected != null && Math.abs(m.durationMeasured - expected) > 0.1) &&
    !(job.alpha && !m.alpha);
  manifest[path.basename(outFile)] = entry;
  fs.writeFileSync(manifestFile, JSON.stringify(manifest, null, 1)); // ghi ngay: lượt sau bỏ qua được job này
  if (m.error) {
    failures.push(`${job.out}: không đọc được (${m.error})`);
  } else {
    if (expected != null && Math.abs(m.durationMeasured - expected) > 0.1) {
      failures.push(`${job.out}: dài ${m.durationMeasured}s nhưng props yêu cầu ${expected}s`);
    }
    if (job.alpha && !m.alpha) {
      failures.push(`${job.out}: yêu cầu alpha nhưng file không có kênh alpha`);
    }
    console.log(`   ✓ ${path.basename(outFile)}: ${m.durationMeasured}s, ${m.fps}fps, ${m.width}x${m.height}` +
      (job.alpha ? `, alpha=${m.alpha}` : ''));
  }
}
fs.writeFileSync(manifestFile, JSON.stringify(manifest, null, 1));
console.log('→ Manifest:', manifestFile);
if (pending.length) {
  console.log(`\n⏸ Hết giới hạn thời gian, còn ${pending.length} job chưa render: ${pending.join(', ')}`);
  console.log('  Chạy lại đúng lệnh này để render tiếp (job đã xong được bỏ qua).');
  process.exit(2);
}
if (failures.length) {
  console.error('\n✗ NGHIỆM THU ĐỒ HỌA KHÔNG ĐẠT:\n  - ' + failures.join('\n  - '));
  process.exit(1);
}
console.log('✓ Hoàn tất render đồ họa:', outDir);
