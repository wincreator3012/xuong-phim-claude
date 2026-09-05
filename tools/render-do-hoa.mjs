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
//     {"comp": "LowerThird", "out": "lt.webm", "alpha": true, "props": {…}}
//   ]
// }
// - "comp" không cần hậu tố -ngang/-doc: script tự thêm theo "aspect".
// - "alpha": true → xuất webm nền trong suốt (vp8 + yuva420p) để phủ lên video.

import {execFileSync} from 'node:child_process';
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
for (const asset of spec.assets ?? []) {
  const src = path.resolve(path.dirname(jobFile), asset);
  const dst = path.join(studioDir, 'public', 'brand', path.basename(asset));
  fs.mkdirSync(path.dirname(dst), {recursive: true});
  fs.copyFileSync(src, dst);
  console.log(`→ Asset: ${path.basename(asset)}`);
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
      alpha: v?.pix_fmt?.startsWith('yuva') || v?.tags?.alpha_mode === '1',
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
  const compId = `${job.comp}-${aspect}`;
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
  if (job.alpha) {
    cliArgs.push('--codec=vp8', '--image-format=png', '--pixel-format=yuva420p');
  } else {
    cliArgs.push('--codec=h264', '--crf=17');
  }
  console.log(`→ Render ${compId} → ${path.basename(outFile)}`);
  execFileSync('npx', cliArgs, {cwd: studioDir, stdio: 'inherit'});
  fs.unlinkSync(propsFile);

  // Nghiệm thu file vừa render
  const m = probeOut(outFile);
  const expected = job.props?.durationInSeconds ?? null;
  const entry = {comp: compId, durationInSeconds: expected, ...m};
  manifest[path.basename(outFile)] = entry;
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
if (failures.length) {
  console.error('\n✗ NGHIỆM THU ĐỒ HỌA KHÔNG ĐẠT:\n  - ' + failures.join('\n  - '));
  process.exit(1);
}
console.log('✓ Hoàn tất render đồ họa:', outDir);
