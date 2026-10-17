#!/usr/bin/env python3
"""run.py - bo lenh dung clip slideshow anh (xem skills/phim-slideshow-anh/SKILL.md)

  python3 -I tools/slideshow-anh/run.py "<Du-an/thu muc du an>" <lenh> ...

Du an can: <du an>/slideshow/spec.py + slideshow.json (mau: tools/slideshow-anh/mau/). Nhap, manh, anh thu o <du an>/.tam/.
Lenh:
  init <thu muc anh>     tao <du an>/slideshow/ tu mau (spec.py + slideshow.json)
  sheets                 bang anh nguon danh so (so thu tu dung trong spec) -> .tam/sheets/
  faces                  nhan dang mat (YuNet) -> .tam/faces.json (chay lai khi them hay bot anh)
  plan                   danh sach canh, tong thoi luong, anh thieu/trung, giu hinh toi thieu
  still <giay> ...       anh thu 1280x720 tai cac moc giay -> .tam/stills/
  strip <k>              6 khung cua chuyen canh vao canh thu k -> .tam/stills/
  review                 bang duyet moi canh 1 khung (12 canh/bang) -> .tam/review/
  chunk <k>              render doan 10 giay thu k
  render [luong] [giay]  render cac doan con thieu, song song (mac dinh 4 luong, ngan sach 150 giay, lap lai tong den het)
  concat <ra.mp4>        noi cac doan thanh phim (chi hinh, khong tieng)
  qc <phim.mp4>          kiem: thoi luong, so khung, khong co tieng, khop khung dau-cuoi (vong lap), bang khung mau
Moi lenh render chay duoc lap lai (bo qua doan da co), hop gioi han 180 giay cua lenh device_bash."""
import os, sys, time, json, subprocess, glob

HERE = os.path.dirname(os.path.abspath(__file__))
CMDS = {'init', 'sheets', 'faces', 'plan', 'still', 'strip', 'review', 'chunk', 'render', 'concat', 'qc'}
CH = 300   # khung hinh moi doan (10 giay o 30 fps)

def boot():
    args = sys.argv[1:]
    proj = os.environ.get('SLIDE_PROJ')
    if args and args[0] not in CMDS: proj = args.pop(0)
    if not proj or not args or args[0] not in CMDS: print(__doc__); sys.exit(2)
    proj = os.path.abspath(proj)
    if not os.path.isdir(proj): print('khong thay thu muc du an:', proj); sys.exit(2)
    os.environ['SLIDE_PROJ'] = proj
    return proj, args

PROJ, ARGS = boot()
TAM = os.path.join(PROJ, '.tam'); CHUNKS = os.path.join(TAM, 'chunks'); STILLS = os.path.join(TAM, 'stills')
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(PROJ, 'slideshow'))

def load():
    global engine, spec, np, cv2
    import numpy as np, cv2
    import engine, spec
    return engine, spec

def src_files():
    import engine
    if not engine.SRC or not os.path.isdir(engine.SRC): print('Chua co thu muc anh nguon: dat "nguon" trong slideshow.json'); sys.exit(2)
    return sorted(f for f in os.listdir(engine.SRC) if f.lower().endswith(('.jpg', '.jpeg')))

def cmd_init(nguon):
    import shutil
    d = os.path.join(PROJ, 'slideshow'); os.makedirs(d, exist_ok=True)
    for src, dst in (('spec.mau.py', 'spec.py'), ('slideshow.mau.json', 'slideshow.json')):
        p = os.path.join(d, dst)
        if os.path.exists(p): print('da co', p, '(giu nguyen)'); continue
        shutil.copy(os.path.join(HERE, 'mau', src), p)
    p = os.path.join(d, 'slideshow.json'); c = json.load(open(p, encoding='utf-8')); c['nguon'] = nguon
    json.dump(c, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('da tao', d, '- buoc ke: faces, sheets, roi sua slideshow.json (cac the chu) va spec.py (cot truyen)')

def cmd_sheets():
    from PIL import Image, ImageDraw, ImageFont
    import engine
    files = src_files(); out = os.path.join(TAM, 'sheets'); os.makedirs(out, exist_ok=True)
    per, cols, cw, ch = 20, 5, 380, 300
    try: font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 16)
    except Exception: font = ImageFont.load_default()
    for s in range(0, len(files), per):
        chunk = files[s:s + per]; rows = (len(chunk) + cols - 1) // cols
        sheet = Image.new('RGB', (cols * cw, rows * ch), (30, 30, 30)); d = ImageDraw.Draw(sheet)
        for i, f in enumerate(chunk):
            im = Image.open(os.path.join(engine.SRC, f)).convert('RGB'); im.thumbnail((cw - 8, ch - 30))
            x = (i % cols) * cw + 4; y = (i // cols) * ch + 4; sheet.paste(im, (x, y))
            d.text((x, y + ch - 28), '%03d %s' % (s + i, os.path.splitext(f)[0]), fill=(255, 255, 255), font=font)
        sheet.save(os.path.join(out, 'sheet%02d.jpg' % (s // per)), quality=82)
    print('anh', len(files), 'bang', (len(files) + per - 1) // per, '->', out)

def cmd_faces():
    import cv2, numpy as np
    import engine
    model = os.path.join(HERE, '..', 'models', 'face_detection_yunet_2023mar.onnx')
    if not os.path.exists(model): print('Thieu model nhan dang mat:', os.path.normpath(model), '(face_detection_yunet_2023mar.onnx, OpenCV Zoo)'); sys.exit(2)
    det = cv2.FaceDetectorYN.create(model, '', (320, 320), 0.6, 0.3, 5000); res = {}
    for i, f in enumerate(src_files()):
        im = cv2.imread(os.path.join(engine.SRC, f)); h, w = im.shape[:2]; boxes = []
        for up in (1.0, 1.8):
            img = im if up == 1.0 else cv2.resize(im, None, fx=up, fy=up, interpolation=cv2.INTER_CUBIC)
            det.setInputSize((img.shape[1], img.shape[0])); _, fs = det.detect(img)
            if fs is not None:
                for fc in fs: boxes.append([float(fc[0] / up), float(fc[1] / up), float(fc[2] / up), float(fc[3] / up), float(fc[14])])
        keep = []
        for b in sorted(boxes, key=lambda b: -b[4]):
            ok = True
            for k in keep:
                ix = max(0, min(b[0] + b[2], k[0] + k[2]) - max(b[0], k[0])); iy = max(0, min(b[1] + b[3], k[1] + k[3]) - max(b[1], k[1]))
                if ix * iy > 0.3 * min(b[2] * b[3], k[2] * k[3]): ok = False; break
            if ok: keep.append(b)
        res[os.path.splitext(f)[0]] = {'idx': i, 'w': w, 'h': h, 'faces': keep}
    os.makedirs(TAM, exist_ok=True); json.dump(res, open(os.path.join(TAM, 'faces.json'), 'w', encoding='utf-8'), indent=1)
    print(len(res), 'anh;', sum(1 for v in res.values() if v['faces']), 'co mat; anh khong thay mat (can focus_override neu zoom lech):')
    print('  ' + ', '.join('%d %s' % (v['idx'], k) for k, v in res.items() if not v['faces']))

def cmd_plan():
    engine, spec = load(); tl = spec.build(); seen = []
    print('canh', len(tl.items), 'tong %.2fs' % tl.total, 'khung', tl.nframes)
    for i, it in enumerate(tl.items):
        e = it['desc']; ids = e.get('ids', e.get('card')); tr = it['tr']
        print('%3d %7.2f giu %5.2f  %-14s %-22s %s' % (i, tl.a[i], it['hold'], type(it['scene']).__name__, ids, (tr[0] + ' %.1f' % tr[1]) if tr else '-'))
        if 'ids' in e: seen += [engine.resolve(x) for x in e['ids']]
    excl = sorted(engine.resolve(x) for x in getattr(spec, 'REMOVED', ()))
    missing = sorted(set(range(len(engine.FACES))) - set(seen) - set(excl)); dup = sorted(x for x in set(seen) if seen.count(x) > 1)
    print('anh dung', len(seen), '| bo co chu dich', excl, '| THIEU', missing, '| TRUNG', dup)
    mn = min((it['hold'] - (it['tr'][1] / 2 if it['tr'] else 0) - (tl.items[i + 1]['tr'][1] / 2 if i + 1 < len(tl.items) and tl.items[i + 1]['tr'] else 0)) for i, it in enumerate(tl.items))
    print('giu hinh ro toi thieu %.2fs' % mn)
    if missing or dup: print('CHU Y: co anh thieu hoac trung')

def cmd_still(ts):
    engine, spec = load(); os.makedirs(STILLS, exist_ok=True); tl = spec.build()
    for t in ts:
        t0 = time.time(); fr = tl.frame(int(round(float(t) * engine.FPS)))
        cv2.imwrite(os.path.join(STILLS, 't%07.2f.jpg' % float(t)), cv2.resize(fr, (1280, 720), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 88])
        print(t, '%.2fs' % (time.time() - t0))

def cmd_strip(k, nfr=6):
    engine, spec = load(); os.makedirs(STILLS, exist_ok=True); tl = spec.build(); it = tl.items[k]; name, T = it['tr']
    t_start = tl.a[k] - T / 2; tiles = []
    for j in range(nfr):
        p = (j + 0.5) / nfr; fr = tl.frame(int(round((t_start + p * T) * engine.FPS)))
        tiles.append(cv2.resize(fr, (640, 360), interpolation=cv2.INTER_AREA))
    cv2.imwrite(os.path.join(STILLS, 'strip_%03d_%s.jpg' % (k, name)), np.vstack([np.hstack(tiles[:3]), np.hstack(tiles[3:6])]), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print('strip', k, name)

def cmd_review():
    engine, spec = load(); out = os.path.join(TAM, 'review'); os.makedirs(out, exist_ok=True)
    tl = spec.build(); cw, ch, cols, rows = 640, 360, 3, 4; per = cols * rows; frames = []
    for i, it in enumerate(tl.items):
        t = tl.a[i] + it['hold'] * 0.62
        fr = cv2.resize(tl.frame(int(round(t * engine.FPS))), (cw, ch), interpolation=cv2.INTER_AREA)
        for col, th in (((255, 255, 255), 2), ((0, 0, 0), 1)): cv2.putText(fr, '%d %.0fs' % (i, t), (8, 24), cv2.FONT_HERSHEY_SIMPLEX, 0.7, col, th, cv2.LINE_AA)
        frames.append(fr)
    for s in range(0, len(frames), per):
        chunk = frames[s:s + per]
        while len(chunk) < per: chunk.append(np.zeros((ch, cw, 3), np.uint8))
        cv2.imwrite(os.path.join(out, 'rev%02d.jpg' % (s // per)), np.vstack([np.hstack(chunk[r * cols:(r + 1) * cols]) for r in range(rows)]), [cv2.IMWRITE_JPEG_QUALITY, 86])
    print('bang duyet', (len(frames) + per - 1) // per, '->', out)

def cmd_chunk(k):
    engine, spec = load(); os.makedirs(CHUNKS, exist_ok=True); tl = spec.build()
    f0, f1 = k * CH, min((k + 1) * CH, tl.nframes)
    out = os.path.join(CHUNKS, 'c%04d.mp4' % k); tmp = out + '.part.mp4'
    if os.path.exists(out): print('bo qua', k); return
    t0 = time.time(); pr = engine.open_writer(tmp)
    for n in range(f0, f1): pr.stdin.write(np.ascontiguousarray(tl.frame(n)).tobytes())
    pr.stdin.close()
    if pr.wait() != 0: print('ffmpeg loi'); sys.exit(1)
    os.replace(tmp, out); print('doan %d xong %.1fs' % (k, time.time() - t0))

def cmd_render(workers=4, budget=150):
    engine, spec = load(); tl = spec.build(); nch = (tl.nframes + CH - 1) // CH; os.makedirs(CHUNKS, exist_ok=True)
    # khong xoa .part cu: VM khong cho xoa khi chua xin quyen; doan dang do se bi ghi de
    pending = [k for k in range(nch) if not os.path.exists(os.path.join(CHUNKS, 'c%04d.mp4' % k))]
    print('doan tong', nch, 'con thieu', len(pending)); t0 = time.time(); running = {}; durs = []
    while pending or running:
        for k, (pr, ts) in list(running.items()):
            if pr.poll() is not None:
                running.pop(k); durs.append(time.time() - ts)
                if pr.returncode != 0: print('doan', k, 'LOI')
        avg = (sum(durs) / len(durs)) if durs else 70.0
        while pending and len(running) < workers and ((time.time() - t0) + avg * 1.15 < budget or (not running and not durs)):
            k = pending.pop(0)
            running[k] = (subprocess.Popen([sys.executable, '-I', os.path.join(HERE, 'run.py'), PROJ, 'chunk', str(k)], stdout=subprocess.DEVNULL), time.time())
        if not running and pending: break
        time.sleep(0.5)
    done = sum(os.path.exists(os.path.join(CHUNKS, 'c%04d.mp4' % k)) for k in range(nch))
    print('xong doan %d/%d trong %.0fs (trung binh %.0fs/doan)%s' % (done, nch, time.time() - t0, (sum(durs) / len(durs)) if durs else 0, '' if done < nch else '  XONG-RENDER'))

def cmd_concat(out):
    engine, spec = load(); tl = spec.build(); nch = (tl.nframes + CH - 1) // CH
    miss = [k for k in range(nch) if not os.path.exists(os.path.join(CHUNKS, 'c%04d.mp4' % k))]
    if miss: print('con thieu doan', miss, '- chay lai render'); sys.exit(75)
    lst = os.path.join(TAM, 'concat.txt')
    with open(lst, 'w') as f:
        for k in range(nch): f.write("file '%s'\n" % os.path.join(CHUNKS, 'c%04d.mp4' % k))
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    subprocess.check_call(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', out])
    print('da ghi', out)

def cmd_qc(video):
    engine, spec = load(); tl = spec.build(); bad = []
    pj = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-count_frames', '-show_entries', 'stream=codec_type,codec_name,width,height,r_frame_rate,nb_read_frames,duration', '-of', 'json', video]))
    st = pj['streams']; vs = [s for s in st if s['codec_type'] == 'video']; au = [s for s in st if s['codec_type'] == 'audio']
    v = vs[0]; nf = int(v['nb_read_frames']); dur = float(v['duration'])
    print('video %s %sx%s %s | %d khung | %.3fs | tieng: %d luong' % (v['codec_name'], v['width'], v['height'], v['r_frame_rate'], nf, dur, len(au)))
    if (v['width'], v['height']) != (engine.W, engine.H): bad.append('sai khung hinh')
    if nf != tl.nframes: bad.append('so khung %d khac ke hoach %d' % (nf, tl.nframes))
    if abs(dur - tl.total) > 0.05: bad.append('thoi luong %.2fs khac ke hoach %.2fs' % (dur, tl.total))
    if au: bad.append('phim co luong tieng (phim nay phai im lang)')
    qc = os.path.join(TAM, 'qc'); os.makedirs(qc, exist_ok=True)
    def grab(t, name):
        p = os.path.join(qc, name); subprocess.check_call(['ffmpeg', '-v', 'error', '-y'] + (['-sseof', '-0.04'] if t < 0 else ['-ss', '%.3f' % t]) + ['-i', video, '-frames:v', '1', p]); return p
    first, last = cv2.imread(grab(0, 'first.png')).astype(float), cv2.imread(grab(-1, 'last.png')).astype(float)
    d = float(abs(first - last).mean()); print('khop vong lap: khung dau va cuoi lech trung binh %.2f/255' % d)
    if d > 3.0: bad.append('khung dau va cuoi khong khop (vong lap bi giat)')
    ts = [0.5] + [k * CH / engine.FPS + dt for k in (1, 2, nf // CH // 2, nf // CH - 1) for dt in (-0.05, 0.05)] + [dur - 0.5]
    tiles = []
    for i, t in enumerate(sorted(x for x in ts if 0 <= x < dur)):
        tiles.append(cv2.resize(cv2.imread(grab(t, 'q%02d.png' % i)), (640, 360), interpolation=cv2.INTER_AREA))
    while len(tiles) % 3: tiles.append(np.zeros((360, 640, 3), np.uint8))
    cv2.imwrite(os.path.join(qc, 'qc.jpg'), np.vstack([np.hstack(tiles[i:i + 3]) for i in range(0, len(tiles), 3)]), [cv2.IMWRITE_JPEG_QUALITY, 85])
    print('bang khung mau (nhin bang mat, nhat la cac moc noi doan):', os.path.join(qc, 'qc.jpg'))
    print('DAT' if not bad else 'KHONG DAT: ' + '; '.join(bad)); sys.exit(0 if not bad else 1)

if __name__ == '__main__':
    c, a = ARGS[0], ARGS[1:]
    if c == 'init': cmd_init(a[0])
    elif c == 'sheets': cmd_sheets()
    elif c == 'faces': cmd_faces()
    elif c == 'plan': cmd_plan()
    elif c == 'still': cmd_still(a)
    elif c == 'strip': cmd_strip(int(a[0]))
    elif c == 'review': cmd_review()
    elif c == 'chunk': cmd_chunk(int(a[0]))
    elif c == 'render': cmd_render(int(a[0]) if a else 4, float(a[1]) if len(a) > 1 else 150)
    elif c == 'concat': cmd_concat(a[0])
    elif c == 'qc': cmd_qc(a[0])
