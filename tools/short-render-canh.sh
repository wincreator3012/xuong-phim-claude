#!/bin/bash
# CHỤP CẢNH của một short ra webm alpha, TRONG SANDBOX ĐÁM MÂY (cần node, Chromium, tools/canh.mjs, do-hoa-chung/canh-kit/ ở gốc xưởng dựng trên sandbox).
#   bash tools/short-render-canh.sh <thư mục canh đã stage: có *.html và cau-hinh.json> <thư mục ra> [số tiến trình song song, mặc định 2]
# Sandbox chỉ có 2 CPU: chạy 3 tiến trình song song không nhanh hơn, và hai short cùng lúc làm chậm cả hai. Chụp xong, commit từng .webm về
# máy ngay (device_commit_files, force), kiểm md5 hai đầu: lượt commit đầu tiên ngay sau render từng ghi file cũ; commit lại rồi so lại.
# Trên máy, đặt webm vào <dự án>/clip-ngan/<slug>/do-hoa/doc/ rồi chạy short-xuat.sh với EP=1.
SRC=$1; OUT=$2; PAR=${3:-2}
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
[ -z "$SRC" ] || [ -z "$OUT" ] && { echo "dùng: bash tools/short-render-canh.sh <thư mục canh> <thư mục ra> [song song]"; exit 2; }
mkdir -p "$OUT"; cd "$ROOT"
python3 - "$SRC" "$OUT" <<'P' | xargs -P "$PAR" -L 1 bash -c 'node tools/canh.mjs chup "$0" --out "$1" --alpha --khung doc --fps 30 --lam-lai 2>&1 | tail -n 1'
import json, sys, os
src, out = sys.argv[1:3]
for c in json.load(open(os.path.join(src, 'cau-hinh.json'), encoding='utf-8')):
    print(os.path.join(os.path.abspath(src), os.path.basename(c['file'])), os.path.join(os.path.abspath(out), c['out']))
P
echo "XONG: $OUT"; ls -la "$OUT"
