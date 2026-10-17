# spec.py - mau ban dung slideshow anh. Chep sang <du an>/slideshow/spec.py (lenh: run.py <du an> init), roi SUA SEQ theo cot truyen.
# Ban nhap tu dong duoi day xep moi anh theo thu tu tep de `plan`, `review`, `render` chay duoc ngay;
# ban dung that thi viet tay SEQ (xem skills/phim-slideshow-anh/references/cot-truyen-va-chuyen-canh.md).
from engine import *

TARGET = 600.0        # tong thoi luong (giay); thoi gian giu cua anh tu dan ra de vua dung con so nay
REMOVED = set()       # anh co chu dich khong dung (so thu tu hoac ten tep); `plan` se khong bao la thieu

def auto_seq():
    cycle = ['glow', 'dissolve', 'push', 'focus', 'dissolve', 'sweep', 'lightleak', 'dissolve']
    ids = [i for i in range(len(FACES)) if i not in {resolve(x) for x in REMOVED}]
    seq, k, n = [], 0, 0
    while k < len(ids):
        tr = cycle[n % len(cycle)]; n += 1
        a = Info.get(ids[k])
        if k + 1 < len(ids) and a.ratio < 0.95 and Info.get(ids[k + 1]).ratio < 0.95:
            seq.append(S([ids[k], ids[k + 1]], 6.2, tr)); k += 2      # hai anh doc: dat canh nhau
        else:
            seq.append(S(ids[k], 5.2, tr)); k += 1
    return seq

SEQ = [dict(card='title', hold=9.5, tr=None)] + auto_seq() + [dict(card='closing', hold=12.5, tr=('dissolve', 2.6))]
# Cac thanh phan viet tay (vi du):
#   S(12, 5.6, 'heart')                      # khoanh khac hon: mong mat hinh tim, can mat o giua
#   S([3, 4], 6.4, 'glow')                   # hai anh doc
#   S([22, 23, 24], 8.5, 'glow')             # ba anh
#   S([99, 100, 101, 102], 8.0, 'dissolve')  # luoi 2x2 (4 anh)
#   S([67, 71, 18], 8.5, 'focus', mood='mono')   # khung den trang (nen toi)
#   S(111, 6.8, 'focus', kb='hero')          # anh chu de, zoom cham vao nguoi
#   BURST(75)                                # nhom anh nhanh ~4.4s, chuyen 'quick'
#   dict(card='quote', hold=8.5, tr=('glow', 2.2))   # the chu khac, khai bao trong slideshow.json
# Chuyen canh: dissolve quick glow zoom push focus doors heart lightleak sweep. kb: in out pan_r pan_l drift burst hero.

def build(): return build_timeline(SEQ, TARGET)
