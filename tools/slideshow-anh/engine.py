# engine.py - dong co slideshow anh (numpy + OpenCV + PIL, ong dan ffmpeg). Dung chung cho moi du an slideshow.
# Du an nam o Du-an/<du an>/slideshow/ (spec.py + slideshow.json); run.py dat SLIDE_PROJ truoc khi nap tep nay.
import os, sys, json, math, subprocess, bisect
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont

cv2.setNumThreads(1)
W, H, FPS = 1920, 1080, 30
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.environ.get('SLIDE_PROJ') or ''
if not PROJ: raise SystemExit('Thieu SLIDE_PROJ: chay qua tools/slideshow-anh/run.py <thu muc du an> <lenh>')
TAM = os.path.join(PROJ, '.tam')
CFG_PATH = os.path.join(PROJ, 'slideshow', 'slideshow.json')
CFG = json.load(open(CFG_PATH, encoding='utf-8')) if os.path.exists(CFG_PATH) else {}

def _res_path(p): return p if os.path.isabs(p) else os.path.normpath(os.path.join(PROJ, p))
SRC = os.environ.get('SLIDE_SRC') or (_res_path(CFG['nguon']) if CFG.get('nguon') else '')
FONTS = os.path.join(HERE, 'fonts')
_FJ = os.path.join(TAM, 'faces.json')
FACES = json.load(open(_FJ, encoding='utf-8')) if os.path.exists(_FJ) else {}
IDX2NAME = {v['idx']: k for k, v in FACES.items()}

def resolve(k):
    """anh duoc goi bang so thu tu (int hoac chuoi so) hoac ten tep (co hay khong duoi .jpg)"""
    if isinstance(k, int): return k
    k = str(k)
    if k.isdigit(): return int(k)
    k = os.path.splitext(k)[0] if k.lower().endswith(('.jpg', '.jpeg', '.png')) else k
    if k not in FACES: raise KeyError('khong co anh ten ' + k)
    return FACES[k]['idx']

# palette (BGR). Ghi de bang CFG['palette'] = {"ivory": "#F7F2E8", ...} (RGB hex)
IVORY = (232, 242, 247)      # warm ivory paper
IVORY_HI = (240, 248, 252)
GOLD = (87, 141, 176)        # #B08D57
INK = (40, 47, 58)           # warm charcoal
FRAME = (240, 247, 250)      # photo border
WARMWHITE = (232, 243, 252)
def _bgr(h): h = h.lstrip('#'); return (int(h[4:6], 16), int(h[2:4], 16), int(h[0:2], 16))
for _k, _v in CFG.get('palette', {}).items():
    if _k.upper() in ('IVORY', 'IVORY_HI', 'GOLD', 'INK', 'FRAME', 'WARMWHITE'): globals()[_k.upper()] = _bgr(_v)

def clamp01(x): return 0.0 if x < 0 else (1.0 if x > 1 else x)
def smooth(x): x = clamp01(x); return x * x * (3 - 2 * x)
def smoother(x): x = clamp01(x); return x * x * x * (x * (6 * x - 15) + 10)
def ease_out(x): x = clamp01(x); return 1 - (1 - x) ** 3
def lerp(a, b, u): return a + (b - a) * u

# ------------------------------------------------------------------ photos
# idx: (cx, cy, halfw, halfh) tuong doi theo anh, cho anh ma nhan dien mat that bai (CFG['focus_override'])
FOCUS_OVERRIDE = {resolve(k): tuple(v) for k, v in CFG.get('focus_override', {}).items()}

class Info:
    _cache = {}
    def __init__(self, idx):
        self.idx = idx; self.name = IDX2NAME[idx]; d = FACES[self.name]
        self.w, self.h, self.faces = d['w'], d['h'], d['faces']
        self.path = os.path.join(SRC, self.name + '.jpg')
        self.ratio = self.w / self.h
    @classmethod
    def get(cls, idx):
        idx = resolve(idx)
        if idx not in cls._cache: cls._cache[idx] = Info(idx)
        return cls._cache[idx]
    def load(self):
        im = cv2.imread(self.path, cv2.IMREAD_COLOR)
        if im is None: raise RuntimeError('cannot read ' + self.path)
        return im
    def subject(self):
        """returns (fcx, fcy, (x0,y0,x1,y1) padded box, face_h) in source px"""
        w, h = self.w, self.h
        if self.idx in FOCUS_OVERRIDE:
            cx, cy, hw, hh = FOCUS_OVERRIDE[self.idx]
            return cx * w, cy * h, ((cx - hw) * w, (cy - hh) * h, (cx + hw) * w, (cy + hh) * h), 0.12 * h
        fs = [f for f in self.faces if f[4] >= 0.7] or list(self.faces)
        if not fs:
            return w / 2, h * 0.45, (w * .3, h * .2, w * .7, h * .7), 0.12 * h
        amax = max(f[2] * f[3] for f in fs)
        fs = [f for f in fs if f[2] * f[3] >= 0.2 * amax]
        x0 = min(f[0] for f in fs); y0 = min(f[1] for f in fs)
        x1 = max(f[0] + f[2] for f in fs); y1 = max(f[1] + f[3] for f in fs)
        bw = max(f[2] for f in fs); bh = max(f[3] for f in fs)
        box = (x0 - 0.6 * bw, y0 - 0.9 * bh, x1 + 0.6 * bw, y1 + 1.4 * bh)
        return (x0 + x1) / 2, (y0 + y1) / 2, box, bh

DENOISE = {resolve(k) for k in CFG.get('denoise', [])}   # anh den trang nhieu hat: khu nhieu, khong lam net

def prep(info, tw, th, zmax):
    img = info.load(); iw, ih = info.w, info.h
    noisy = info.idx in DENOISE
    if noisy: img = cv2.fastNlMeansDenoisingColored(img, None, 6, 6, 7, 21)
    base = max(tw / iw, th / ih); sp = base * zmax
    if sp > 1.0:
        pre = cv2.resize(img, None, fx=sp, fy=sp, interpolation=cv2.INTER_LANCZOS4)
        if not noisy:
            blur = cv2.GaussianBlur(pre, (0, 0), 1.2)
            pre = cv2.addWeighted(pre, 1.30, blur, -0.30, 0)
    else:
        pre = cv2.resize(img, None, fx=sp, fy=sp, interpolation=cv2.INTER_AREA)
    return pre, pre.shape[1] / iw, base

class KB:
    def __init__(self, info, tw, th, kind='in', zhi=None):
        iw, ih = info.w, info.h
        self.tw, self.th = tw, th
        self.base = base = max(tw / iw, th / ih)
        fcx, fcy, (bx0, by0, bx1, by1), fh = info.subject()
        self.fcx, self.fcy = fcx, fcy
        rel = fh / ih
        if zhi is None: zhi = 1.30 if rel < 0.04 else (1.20 if rel < 0.07 else 1.12)
        mx = lambda a, b, u: a + (b - a) * u
        def fix(z, cx, cy):
            hw, hh = tw / (base * z) / 2, th / (base * z) / 2
            lo, hi = bx1 - hw, bx0 + hw
            if lo <= hi: cx = min(max(cx, lo), hi)
            lo, hi = by1 - hh, by0 + hh
            if lo <= hi: cy = min(max(cy, lo), hi)
            cx = min(max(cx, hw), iw - hw); cy = min(max(cy, hh), ih - hh)
            return (z, cx, cy)
        ccx, ccy = iw / 2, ih / 2
        if kind in ('in', 'out'):
            a = fix(1.0, mx(ccx, fcx, .35), mx(ccy, fcy, .35)); b = fix(zhi, mx(ccx, fcx, .85), mx(ccy, fcy, .85))
            if kind == 'out': a, b = b, a
        elif kind in ('pan_r', 'pan_l'):
            z = min(zhi, 1.12) if zhi > 1.08 else 1.10
            hw = tw / (base * z) / 2; slack = iw - 2 * hw
            if slack < 0.03 * iw: return self.__init__(info, tw, th, 'in', zhi)
            xl, xr = hw + 0.12 * slack, iw - hw - 0.12 * slack
            cy = mx(ccy, fcy, .6)
            a = fix(z, xl, cy); b = fix(z, xr, cy)
            if kind == 'pan_l': a, b = b, a
        elif kind == 'drift':
            a = fix(1.02, mx(ccx, fcx, .4), mx(ccy, fcy, .4)); b = fix(1.08, mx(ccx, fcx, .6), mx(ccy, fcy, .6))
        elif kind == 'burst':
            a = fix(1.05, mx(ccx, fcx, .9), mx(ccy, fcy, .9)); b = fix(1.08, mx(ccx, fcx, .9), mx(ccy, fcy, .9))
        elif kind == 'hero':
            a = fix(1.0, mx(ccx, fcx, .5), mx(ccy, fcy, .5)); b = fix(max(zhi, 1.22), mx(ccx, fcx, .95), mx(ccy, fcy, .95))
        elif kind == 'tile':
            a = fix(1.0, mx(ccx, fcx, .3), mx(ccy, fcy, .3)); b = fix(1.07, mx(ccx, fcx, .8), mx(ccy, fcy, .8))
        elif kind == 'tile_out':
            b = fix(1.0, mx(ccx, fcx, .3), mx(ccy, fcy, .3)); a = fix(1.07, mx(ccx, fcx, .8), mx(ccy, fcy, .8))
        else: raise ValueError(kind)
        self.a, self.b = a, b
        self.zmax = max(a[0], b[0])
    def at(self, u):
        u = clamp01(u)
        return tuple(self.a[i] + (self.b[i] - self.a[i]) * u for i in range(3))

def warp_cover(pre, sp, base, z, cx, cy, tw, th):
    s = (base * z) / sp
    M = np.float32([[s, 0, tw / 2 - s * cx * sp], [0, s, th / 2 - s * cy * sp]])
    return cv2.warpAffine(pre, M, (tw, th), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

# ------------------------------------------------------------------ scenes
class Scene:
    t_in = 0.0; span = 1.0
    def focus(self, t): return (W / 2, H / 2)

class CoverScene(Scene):
    def __init__(self, ids, kind='in', zhi=None):
        self.info = Info.get(ids[0]); self.kind = kind
        self.kb = KB(self.info, W, H, kind, zhi); self._pre = None
    def render(self, t):
        if self._pre is None: self._pre = prep(self.info, W, H, self.kb.zmax)
        pre, sp, base = self._pre
        z, cx, cy = self.kb.at(t / self.span)
        return warp_cover(pre, sp, base, z, cx, cy, W, H)
    def focus(self, t):
        z, cx, cy = self.kb.at(t / self.span); s = self.kb.base * z
        return (W / 2 + (self.kb.fcx - cx) * s, H / 2 + (self.kb.fcy - cy) * s)

def make_bg(infos, mood):
    Wb, Hb = int(W * 1.12), int(H * 1.12); lw, lh = Wb // 8, Hb // 8
    n = len(infos); low = np.zeros((lh, lw, 3), np.uint8)
    for k, inf in enumerate(infos):
        x0 = (lw * k) // n; x1 = (lw * (k + 1)) // n; sw = x1 - x0
        img = cv2.resize(inf.load(), (inf.w // 4, inf.h // 4), interpolation=cv2.INTER_AREA)
        s = max((sw + 8) / img.shape[1], lh / img.shape[0])
        img = cv2.resize(img, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        fcx, fcy, _, _ = inf.subject(); cx = fcx / inf.w * img.shape[1]; cy = fcy / inf.h * img.shape[0]
        sx = int(min(max(cx - sw / 2, 0), img.shape[1] - sw)); sy = int(min(max(cy - lh / 2, 0), img.shape[0] - lh))
        low[:, x0:x1] = img[sy:sy + lh, sx:sx + sw]
    low = cv2.GaussianBlur(low, (0, 0), 4.5)
    bg = cv2.resize(low, (Wb, Hb), interpolation=cv2.INTER_CUBIC).astype(np.float32)
    if mood == 'mono':
        g = bg.mean(axis=2, keepdims=True); bg = np.repeat(g, 3, axis=2) * 0.42 + 10
    else:
        bg = bg * 0.72 + np.array(IVORY, np.float32) * 0.28; bg *= 1.03
    rng = np.random.RandomState(5)
    bg += rng.normal(0, 1.4, (Hb, Wb, 1)).astype(np.float32)
    return np.clip(bg, 0, 255).astype(np.uint8)

def make_sprites(tw, th, b=10, m=70):
    sw, sh = tw + 2 * b, th + 2 * b
    frame = np.empty((sh, sw, 3), np.uint8); frame[:] = FRAME
    alpha = np.full((sh, sw), 255, np.uint8)
    shadow = np.zeros((sh + 2 * m, sw + 2 * m), np.float32)
    shadow[m + 16:m + 16 + sh, m:m + sw] = 255
    shadow = cv2.GaussianBlur(shadow, (0, 0), 24) * 0.52
    return frame, alpha, shadow.astype(np.uint8), m

class TileScene(Scene):
    B = 10; GAP = 44
    def __init__(self, ids, mood='light'):
        self.infos = [Info.get(i) for i in ids]; self.mood = mood; n = len(ids)
        rs = [i.ratio for i in self.infos]
        th = {1: 960, 2: 920, 3: 800}[n]
        if n == 1 and rs[0] > 0.95: th = 800 if rs[0] >= 1.2 else 880
        while True:
            tws = [int(round(th * r)) for r in rs]
            total = sum(tws) + 2 * self.B * n + self.GAP * (n - 1)
            if total <= W - 150: break
            th -= 10
        self.th, self.tws = th, tws
        x = (W - total) / 2; self.cxs = []
        for tw in tws:
            self.cxs.append(x + (tw + 2 * self.B) / 2); x += tw + 2 * self.B + self.GAP
        self.cy = H / 2 - 4
        self.kbs = [KB(inf, tw, th, 'tile' if k % 2 == 0 else 'tile_out') for k, (inf, tw) in enumerate(zip(self.infos, tws))]
        self.pres = None; self.bg = None; self.sprites = None
    def _prepare(self):
        self.pres = [prep(inf, tw, self.th, kb.zmax) for inf, tw, kb in zip(self.infos, self.tws, self.kbs)]
        self.bg = make_bg(self.infos, self.mood)
        self.sprites = [make_sprites(tw, self.th, self.B) for tw in self.tws]
    def render(self, t):
        if self.pres is None: self._prepare()
        u = clamp01(t / self.span)
        Hb, Wb = self.bg.shape[:2]
        s = 1.0 + 0.035 * u; dx = (-12 + 24 * u); dy = (6 - 12 * u)
        M = np.float32([[s, 0, W / 2 - s * Wb / 2 + dx], [0, s, H / 2 - s * Hb / 2 + dy]])
        canvas = cv2.warpAffine(self.bg, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        for k in range(len(self.infos)):
            a = 1.0 if k == 0 else ease_out((t - self.t_in - 0.30 - 0.55 * (k - 1)) / 0.95)
            if a <= 0.001: continue
            pre, sp, base = self.pres[k]; z, cx, cy = self.kbs[k].at(u)
            win = warp_cover(pre, sp, base, z, cx, cy, self.tws[k], self.th)
            frame, alpha, shadow, m = self.sprites[k]
            spr = frame.copy(); spr[self.B:self.B + self.th, self.B:self.B + self.tws[k]] = win
            sh_, sw_ = spr.shape[:2]
            sc = 1.0 + 0.012 * u + (0.02 * (a - 1) if k else 0)
            px = self.cxs[k]; py = self.cy + (1 - a) * 34 * (1 if k else 0)
            self._blit(canvas, spr, alpha, shadow, m, px, py, sc, a)
        return canvas
    @staticmethod
    def _blit(canvas, spr, alpha, shadow, m, cx, cy, sc, a):
        sh_, sw_ = spr.shape[:2]; shh, shw = shadow.shape[:2]
        x0 = int(max(0, math.floor(cx - shw * sc / 2) - 2)); x1 = int(min(W, math.ceil(cx + shw * sc / 2) + 2))
        y0 = int(max(0, math.floor(cy - shh * sc / 2) - 2)); y1 = int(min(H, math.ceil(cy + shh * sc / 2) + 2))
        if x1 <= x0 or y1 <= y0: return
        roi = canvas[y0:y1, x0:x1].astype(np.float32)
        def mat(w_, h_): return np.float32([[sc, 0, cx - sc * w_ / 2 - x0], [0, sc, cy - sc * h_ / 2 - y0]])
        sd = cv2.warpAffine(shadow, mat(shw, shh), (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR).astype(np.float32) / 255.0
        roi *= (1 - sd * a)[..., None]
        sp_ = cv2.warpAffine(spr, mat(sw_, sh_), (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE).astype(np.float32)
        al = cv2.warpAffine(alpha, mat(sw_, sh_), (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR).astype(np.float32) / 255.0 * a
        roi = roi * (1 - al[..., None]) + sp_ * al[..., None]
        canvas[y0:y1, x0:x1] = np.clip(roi + 0.5, 0, 255).astype(np.uint8)
    def focus(self, t):
        inf = self.infos[0]; fcx, fcy, _, _ = inf.subject()
        return (self.cxs[0] + (fcx / inf.w - 0.5) * self.tws[0], self.cy + (fcy / inf.h - 0.5) * self.th)

class MosaicScene(Scene):
    def __init__(self, ids, mood='light'):
        self.infos = [Info.get(i) for i in ids]; self.mood = mood
        mar, gap = 40, 8
        cw, ch = (W - 2 * mar - gap) // 2, (H - 2 * mar - gap) // 2
        self.cw, self.ch = cw, ch
        self.pos = [(mar, mar), (mar + cw + gap, mar), (mar, mar + ch + gap), (mar + cw + gap, mar + ch + gap)]
        kinds = ['in', 'out', 'out', 'in']
        self.kbs = [KB(inf, cw, ch, kinds[k], 1.10) for k, inf in enumerate(self.infos)]
        self.pres = None
        self.bgc = np.empty((H, W, 3), np.uint8); self.bgc[:] = (26, 26, 26) if mood == 'mono' else IVORY
    def render(self, t):
        if self.pres is None: self.pres = [prep(inf, self.cw, self.ch, kb.zmax) for inf, kb in zip(self.infos, self.kbs)]
        u = clamp01(t / self.span); canvas = self.bgc.copy()
        order = [0, 1, 3, 2]
        for r, k in enumerate(order):
            a = 1.0 if r == 0 else ease_out((t - self.t_in - 0.25 - 0.55 * (r - 1)) / 0.9)
            if a <= 0.001: continue
            pre, sp, base = self.pres[k]; z, cx, cy = self.kbs[k].at(u)
            win = warp_cover(pre, sp, base, z, cx, cy, self.cw, self.ch)
            x, y = self.pos[k]
            roi = canvas[y:y + self.ch, x:x + self.cw]
            canvas[y:y + self.ch, x:x + self.cw] = win if a >= 0.999 else cv2.addWeighted(roi, 1 - a, win, a, 0)
        return canvas

# ------------------------------------------------------------------ text cards
def load_font(name, size, wght=None):
    f = ImageFont.truetype(os.path.join(FONTS, name), size)
    if wght is not None:
        try: f.set_variation_by_axes([wght])
        except Exception: pass
    return f

def text_mask(text, font, tracking=0.0, cx=W // 2, base_y=H // 2):
    """returns (mask uint8 HxW, bbox). tracking in em. centered horizontally at cx, baseline at base_y"""
    size = font.size; adv = [font.getlength(c) + tracking * size for c in text]
    total = sum(adv) - tracking * size
    img = Image.new('L', (W, H), 0); d = ImageDraw.Draw(img); x = cx - total / 2
    for c, a in zip(text, adv):
        d.text((x, base_y), c, font=font, fill=255, anchor='ls'); x += a
    m = np.array(img); ys, xs = np.nonzero(m)
    bb = (int(xs.min()) - 6, int(ys.min()) - 6, int(xs.max()) + 7, int(ys.max()) + 7) if len(xs) else (0, 0, 1, 1)
    return m, bb

def card_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.72)) ** 2)
    k = np.clip(1 - r, 0, 1)[..., None] ** 1.3
    bg = np.array(IVORY, np.float32) * (1 - k) + np.array(IVORY_HI, np.float32) * k
    rng = np.random.RandomState(11); bg += rng.normal(0, 1.1, (H, W, 1)).astype(np.float32)
    bg = np.clip(bg, 0, 255).astype(np.uint8)
    for inset, th_, col in ((54, 2, GOLD), (68, 1, GOLD)):
        cv2.rectangle(bg, (inset, inset), (W - inset, H - inset), col, th_, cv2.LINE_AA)
    return bg

CARD_COLORS = {'gold': 'GOLD', 'ink': 'INK'}

class CardScene(Scene):
    """the chu: noi dung o CFG['cards'][ten]: {"els":[{text,font,size,tracking,y,color,t0,t1,mode}], "line":[t0,t1,y], "fade_out":[t0,t1]}
    font: caps (Cormorant 600), italic (Cormorant Italic 500), script (Great Vibes, tu co lai cho vua max_w); mode: fade | wipe"""
    def __init__(self, kind):
        if kind not in CFG.get('cards', {}): raise KeyError('slideshow.json chua co the ' + kind)
        self.kind = kind; self.cfg = CFG['cards'][kind]; self.bg = None; self.els = None
        rs = np.random.RandomState(7); n = 38
        self.px = rs.uniform(0, W, n); self.py = rs.uniform(0, H + 80, n); self.pr = rs.uniform(3, 11, n)
        self.ps = rs.uniform(5, 16, n); self.pph = rs.uniform(0, 6.28, n); self.pf = rs.uniform(0.4, 1.1, n)
        self.line = tuple(self.cfg['line']) if self.cfg.get('line') else None
        self.fade_out_at = tuple(self.cfg['fade_out']) if self.cfg.get('fade_out') else None
    @staticmethod
    def _font(el):
        kind, size = el.get('font', 'caps'), int(el.get('size', 42))
        if kind == 'caps': return load_font('CormorantGaramond[wght].ttf', size, el.get('wght', 600))
        if kind == 'italic': return load_font('CormorantGaramond-Italic[wght].ttf', size, el.get('wght', 500))
        if kind == 'script':
            f = load_font('GreatVibes-Regular.ttf', size); mw = el.get('max_w', 1380)
            while f.getlength(el['text']) > mw and size > 40:
                size -= 6; f = load_font('GreatVibes-Regular.ttf', size)
            return f
        raise ValueError('font la: caps | italic | script')
    def _build(self):
        self.bg = card_bg(); self.els = []
        for el in self.cfg['els']:
            col = globals()[CARD_COLORS[el.get('color', 'ink')]]
            m, bb = text_mask(el['text'], self._font(el), el.get('tracking', 0.0), W // 2, int(el['y']))
            self.els.append((m[bb[1]:bb[3], bb[0]:bb[2]], bb, col, el['t0'], el['t1'], el.get('mode', 'fade')))
    def render(self, t):
        if self.bg is None: self._build()
        canvas = self.bg.copy(); fo = 1.0
        if self.fade_out_at: fo = 1 - smooth((t - self.fade_out_at[0]) / (self.fade_out_at[1] - self.fade_out_at[0]))
        # particles
        pa = smooth((t - 0.6) / 3.0) * fo
        if pa > 0.01:
            lay = np.zeros((H // 4, W // 4), np.float32)
            for i in range(len(self.px)):
                y = (self.py[i] - self.ps[i] * t) % (H + 80) - 40; x = self.px[i] + 16 * math.sin(0.35 * t + self.pph[i])
                tw = 0.5 + 0.5 * math.sin(self.pf[i] * t * 2 + self.pph[i])
                cv2.circle(lay, (int(x / 4), int(y / 4)), max(1, int(self.pr[i] / 4)), float(0.25 + 0.75 * tw), -1, cv2.LINE_AA)
            lay = cv2.GaussianBlur(lay, (0, 0), 1.4); lay = cv2.resize(lay, (W, H), interpolation=cv2.INTER_LINEAR)
            a = (lay * 0.38 * pa)[..., None]
            canvas = np.clip(canvas.astype(np.float32) * (1 - a) + np.array(GOLD, np.float32) * a, 0, 255).astype(np.uint8)
        # divider line
        l0, l1, ly = self.line if self.line else (0, 1, 0)
        la = smooth((t - l0) / (l1 - l0)) * fo if self.line else 0.0
        if la > 0.01:
            half = int(170 * la); ov = canvas.copy()
            cv2.line(ov, (W // 2 - half, ly), (W // 2 + half, ly), GOLD, 2, cv2.LINE_AA)
            d = 7; cv2.polylines(ov, [np.array([[W // 2, ly - d], [W // 2 + d, ly], [W // 2, ly + d], [W // 2 - d, ly]], np.int32)], True, GOLD, 2, cv2.LINE_AA)
            canvas = cv2.addWeighted(canvas, 1 - la, ov, la, 0)
        # texts
        for m, bb, col, t0, t1, mode in self.els:
            a = smooth((t - t0) / (t1 - t0)) * fo
            if a <= 0.002: continue
            x0, y0, x1, y1 = bb; mm = m.astype(np.float32) / 255.0
            if mode == 'wipe':
                wd = x1 - x0; xs = np.arange(wd, dtype=np.float32)[None, :]
                prog = smooth((t - t0) / (t1 - t0)) * (wd + 260) - 130
                mm = mm * np.clip((prog - xs) / 130.0 + 0.5, 0, 1)
                a = fo
            else:
                y0 += int(round((1 - a) * 10)); y1 += int(round((1 - a) * 10))
            y0c, y1c = max(0, y0), min(H, y1)
            if y1c <= y0c: continue
            mm = mm[(y0c - y0):(y0c - y0) + (y1c - y0c)]
            roi = canvas[y0c:y1c, x0:x1].astype(np.float32); am = (mm * a)[..., None]
            canvas[y0c:y1c, x0:x1] = np.clip(roi * (1 - am) + np.array(col, np.float32) * am, 0, 255).astype(np.uint8)
        return canvas

# ------------------------------------------------------------------ transitions
def mixf(A, B, a): return cv2.addWeighted(A, 1 - a, B, a, 0)

def blur_fast(img, sigma):
    if sigma < 0.6: return img
    f = 4 if sigma > 8 else 2
    sm = cv2.resize(img, (W // f, H // f), interpolation=cv2.INTER_AREA)
    sm = cv2.GaussianBlur(sm, (0, 0), sigma / f)
    return cv2.resize(sm, (W, H), interpolation=cv2.INTER_LINEAR)

def tr_dissolve(A, B, p, c): return mixf(A, B, smooth(p))

def tr_glow(A, B, p, c):
    a = smooth(p); mix = mixf(A, B, a); w = (math.sin(math.pi * p) ** 2) * 0.80
    if w > 0.08:
        bl = blur_fast(mix, 7 * math.sin(math.pi * p)); mix = mixf(mix, bl, min(0.8, w))
    white = np.empty_like(mix); white[:] = WARMWHITE
    return mixf(mix, white, w)

def scale_about(img, s, cx=W / 2, cy=H / 2):
    M = np.float32([[s, 0, cx - s * cx], [0, s, cy - s * cy]])
    return cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

def tr_zoom(A, B, p, c):
    e = smoother(p); a = smooth(p)
    return mixf(scale_about(A, 1 + 0.14 * e), scale_about(B, 0.92 + 0.08 * e), a)

def tr_push(A, B, p, c):
    e = smoother(p); d = c.get('dir', 1); off = W * e
    MA = np.float32([[1, 0, -d * off], [0, 1, 0]]); MB = np.float32([[1, 0, d * (W - off)], [0, 1, 0]])
    wa = cv2.warpAffine(A, MA, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    wb = cv2.warpAffine(B, MB, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
    xs = int(round(W - off)) if d > 0 else int(round(off))
    out = np.empty_like(A)
    if d > 0: out[:, :xs] = wa[:, :xs]; out[:, xs:] = wb[:, xs:]
    else: out[:, :xs] = wb[:, :xs]; out[:, xs:] = wa[:, xs:]
    k = 1 + int(16 * (math.sin(math.pi * p) ** 1.4)) * 2
    if k > 3: out = cv2.blur(out, (k, 1))
    return out

def tr_focus(A, B, p, c):
    e = smooth(p); sa = 24 * (e ** 0.8); sb = 24 * ((1 - e) ** 0.8)
    out = mixf(blur_fast(A, sa), blur_fast(B, sb), e)
    w = 0.10 * math.sin(math.pi * p); white = np.empty_like(out); white[:] = WARMWHITE
    return mixf(out, white, w) if w > 0.01 else out

def tr_doors(A, B, p, c):
    e = smoother(p); off = int(round(W / 2 * e)); half = W // 2
    Bz = scale_about(B, 1.07 - 0.07 * e)
    out = Bz.copy()
    if off > 0:
        xl, xr = half - off, half + off
        xs = np.arange(xl, xr, dtype=np.float32); d = np.minimum(xs - xl, xr - xs)
        mult = (1 - 0.42 * min(1.0, off / 40.0) * np.exp(-d / 48.0))[None, :, None]
        out[:, xl:xr] = (Bz[:, xl:xr].astype(np.float32) * mult).astype(np.uint8)
    if half - off > 0:
        out[:, :half - off] = A[:, off:half]
        out[:, half + off:] = A[:, half:W - off]
        for x in (half - off, half + off):
            if 0 < x < W: out[:, max(0, x - 1):min(W, x + 1)] = (235, 245, 252)
    return out

_HEART_RMIN = None
def heart_rmin(yc):
    global _HEART_RMIN
    if _HEART_RMIN is None:
        best = 9.0
        for th in np.linspace(0, 2 * math.pi, 361):
            lo, hi = 0.0, 3.0
            for _ in range(30):
                r = (lo + hi) / 2; X = r * math.cos(th); Y = yc + r * math.sin(th)
                f = (X * X + Y * Y - 1) ** 3 - X * X * Y ** 3
                if f <= 0: lo = r
                else: hi = r
            best = min(best, lo)
        _HEART_RMIN = best
    return _HEART_RMIN

def tr_heart(A, B, p, c):
    fx, fy = c.get('focus', (W / 2, H / 2)); yc = 0.15
    e = smooth(p)
    if p >= 0.985: return B
    dmax = max(math.hypot(fx - x, fy - y) for x in (0, W) for y in (0, H))
    s0, s1 = 24.0, dmax / heart_rmin(yc) * 1.06
    s = s0 * (s1 / s0) ** e
    hw, hh = W // 2, H // 2
    xs = ((np.arange(hw, dtype=np.float32) * 2 - fx) / s)[None, :]
    ys = -((np.arange(hh, dtype=np.float32) * 2 - fy) / s)[:, None] + yc
    f = (xs * xs + ys * ys - 1) ** 3 - xs * xs * ys ** 3
    m = (f <= 0).astype(np.float32)
    m = cv2.GaussianBlur(m, (0, 0), float(np.clip(s * 0.012, 1.4, 9)))
    m = cv2.resize(m, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    Bz = scale_about(B, 1.12 - 0.12 * e, fx, fy)
    Ad = (A.astype(np.float32) * (1 - 0.20 * e))
    edge = 4 * m * (1 - m)
    out = Ad * (1 - m) + Bz.astype(np.float32) * m + np.array((240, 248, 252), np.float32) * edge * 0.55
    return np.clip(out, 0, 255).astype(np.uint8)

def tr_lightleak(A, B, p, c):
    mix = mixf(A, B, smooth(p)); I = (math.sin(math.pi * p)) ** 1.25
    lw, lh = 192, 108; xs = np.linspace(0, W, lw, dtype=np.float32)[None, :]; ys = np.linspace(0, H, lh, dtype=np.float32)[:, None]
    d = c.get('dir', 1); q = p if d > 0 else 1 - p
    blobs = [((W * (0.05 + 0.9 * q), H * 0.15), W * 0.34, (40, 120, 255)),
             ((W * (0.95 - 0.8 * q), H * 0.92), W * 0.30, (140, 80, 255)),
             ((W * (0.30 + 0.4 * q), H * 0.5), W * 0.26, (110, 215, 255))]
    leak = np.zeros((lh, lw, 3), np.float32)
    for (bx, by), sg, col in blobs:
        g = np.exp(-((xs - bx) ** 2 + (ys - by) ** 2) / (2 * sg * sg))
        leak += g[..., None] * np.array(col, np.float32)
    leak = cv2.resize(leak, (W, H), interpolation=cv2.INTER_LINEAR) * (I * 0.62)
    out = 255 - (255 - mix.astype(np.float32)) * (255 - np.clip(leak, 0, 255)) / 255.0
    return np.clip(out, 0, 255).astype(np.uint8)

def tr_sweep(A, B, p, c):
    e = smoother(p); lw, lh = 480, 270
    xs = np.linspace(0, 1, lw, dtype=np.float32)[None, :]; ys = np.linspace(0, H / W, lh, dtype=np.float32)[:, None]
    th = math.radians(18 * c.get('dir', 1)); D = xs * math.cos(th) + ys * math.sin(th)
    D = (D - D.min()) / (D.max() - D.min())
    f = 0.16; L = -f + (1 + 2 * f) * e
    m = np.clip((L - D) / (2 * f) + 0.5, 0, 1); m = m * m * (3 - 2 * m)
    g = np.exp(-(((D - L) / 0.06) ** 2)) * 0.36 * math.sin(math.pi * p) ** 0.6
    m = cv2.resize(m.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    g = cv2.resize(g.astype(np.float32), (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    out = A.astype(np.float32) * (1 - m) + B.astype(np.float32) * m + g * np.array((200, 235, 255), np.float32)
    return np.clip(out, 0, 255).astype(np.uint8)

TRANS = {'dissolve': (tr_dissolve, 1.5), 'quick': (tr_dissolve, 0.8), 'glow': (tr_glow, 2.1), 'zoom': (tr_zoom, 1.6),
         'push': (tr_push, 1.3), 'focus': (tr_focus, 1.8), 'doors': (tr_doors, 2.0), 'heart': (tr_heart, 2.4),
         'lightleak': (tr_lightleak, 2.0), 'sweep': (tr_sweep, 1.8)}

# ------------------------------------------------------------------ timeline
class Timeline:
    def __init__(self, items):
        """items: list of dict(scene=Scene, hold=float, tr=(name,T) or None) ; tr = incoming transition"""
        self.items = items; self.a = []; t = 0.0
        for it in items: self.a.append(t); t += it['hold']
        self.total = t; n = len(items)
        for i, it in enumerate(items):
            tin = it['tr'][1] if it.get('tr') else 0.0
            tout = items[i + 1]['tr'][1] if i + 1 < n and items[i + 1].get('tr') else 0.0
            it['start'] = self.a[i] - tin / 2; it['end'] = self.a[i] + it['hold'] + tout / 2
            sc = it['scene']; sc.t_in = tin; sc.span = it['end'] - it['start']
        self.nframes = int(round(self.total * FPS))
    def _scene_frame(self, i, t):
        it = self.items[i]; return it['scene'].render(max(0.0, t - it['start']))
    def frame(self, n):
        t = n / FPS; it = self.items; k = bisect.bisect_right(self.a, t + 1e-9) - 1; k = max(0, min(k, len(it) - 1))
        if it[k].get('tr') and t < self.a[k] + it[k]['tr'][1] / 2:
            return self._trans(k - 1, k, t)
        if k + 1 < len(it) and it[k + 1].get('tr') and t >= self.a[k + 1] - it[k + 1]['tr'][1] / 2:
            return self._trans(k, k + 1, t)
        return self._scene_frame(k, t)
    def _trans(self, i, j, t):
        name, T = self.items[j]['tr']; fn = TRANS[name][0]
        p = clamp01((t - (self.a[j] - T / 2)) / T)
        B_t = max(0.0, t - self.items[j]['start'])
        ctx = {'dir': self.items[j].get('dir', 1), 'focus': self.items[j]['scene'].focus(B_t)}
        return fn(self._scene_frame(i, t), self._scene_frame(j, t), p, ctx)

# ------------------------------------------------------------------ cach dung nhanh trong spec.py
def S(ids, hold, tr='dissolve', **kw):
    """mot canh: ids = 1 anh | 2-3 anh (khung roi) | 4 anh (luoi 2x2); hold = giay giu (truoc khi co dan thoi luong); tr = chuyen canh VAO canh nay"""
    return dict(ids=ids if isinstance(ids, list) else [ids], hold=hold, tr=tr, **kw)
def BURST(i, hold=4.4, tr='quick'): return dict(ids=[i], hold=hold, tr=tr, kb='burst')

KB_CYCLE = ['in', 'pan_r', 'out', 'pan_l', 'drift', 'in', 'pan_l', 'out', 'pan_r']

def build_timeline(SEQ, target=600.0, kb_cycle=KB_CYCLE):
    """SEQ: danh sach S(...) va dict(card=<ten the trong slideshow.json>, hold=giay, tr=None|ten|(ten, giay)).
    Thoi gian giu cua anh duoc nhan he so f de tong dung bang target (the chu giu nguyen thoi gian)."""
    cards = sum(e['hold'] for e in SEQ if 'card' in e); photos = sum(e['hold'] for e in SEQ if 'ids' in e)
    f = (target - cards) / photos; items = []; kbi = 0; dirc = 1
    for e in SEQ:
        if 'card' in e:
            sc = CardScene(e['card']); hold = e['hold']
        else:
            ids = e['ids']; hold = e['hold'] * f; mood = e.get('mood', 'light')
            if len(ids) == 4: sc = MosaicScene(ids, mood)
            elif len(ids) >= 2: sc = TileScene(ids, mood)
            else:
                inf = Info.get(ids[0]); mode = e.get('mode') or ('cover' if inf.ratio >= 1.35 else 'tile')
                if mode == 'cover':
                    kind = e.get('kb') or kb_cycle[kbi % len(kb_cycle)]
                    if not e.get('kb'): kbi += 1
                    sc = CoverScene(ids, kind)
                else: sc = TileScene(ids, mood)
        tr = e.get('tr')
        if isinstance(tr, str): tr = (tr, TRANS[tr][1])
        it = dict(scene=sc, hold=hold, tr=tr, desc=e)
        if tr and tr[0] in ('push', 'sweep', 'lightleak'): it['dir'] = dirc; dirc = -dirc
        items.append(it)
    return Timeline(items)

def open_writer(path, fps=FPS, crf=17, threads=2):
    cmd = ['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{W}x{H}', '-r', str(fps), '-i', '-',
           '-vf', 'scale=out_color_matrix=bt709:out_range=tv,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', str(crf),
           '-tune', 'stillimage', '-x264-params', 'keyint=60:min-keyint=60:scenecut=0:aq-mode=3', '-profile:v', 'high', '-level', '4.2',
           '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-threads', str(threads), '-an', path]
    return subprocess.Popen(cmd, stdin=subprocess.PIPE)
