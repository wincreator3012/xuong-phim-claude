#!/bin/bash
# BẢNG KHUNG HÌNH: chụp nhiều khung của một video đã dựng thành MỘT ảnh lưới để Claude NHÌN (kiểm riêng tư, kiểm chữ,
# kiểm layout) mà không phải mở từng khung. Dùng sau mỗi lần dựng bản nháp và bản final.
#   FILE=<video.mp4> SW=640 bash tools/xem-khung.sh <tên> <số-cột> <giây1> <giây2> ...
#   FILE   video cần xem (bắt buộc)
#   SW     bề rộng mỗi ô (mặc định 480; chữ nhỏ trên màn hình demo cần 640 trở lên)
#   RA     thư mục ra (mặc định ../Du an/_tam/xem-khung)
# Ảnh ra: $RA/<tên>.jpg, mỗi ô có nhãn phút:giây ở góc trái trên. Nhớ stage ảnh rồi Read để nhìn.
# Mẹo: lấy mốc dày (mỗi 10 đến 20 giây) ở các đoạn demo màn hình và trước/sau mỗi đoạn có chữ riêng tư.
[ -z "$FILE" ] && { echo "Thiếu FILE=<video>"; exit 2; }
XUONG="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${RA:-$XUONG/../Du an/_tam/xem-khung}"; mkdir -p "$OUT"
TMP="${TMPDIR:-/tmp}/xem-khung-$$"; mkdir -p "$TMP"
name=$1; cols=$2; shift 2; n=$#; rows=$(( (n+cols-1)/cols )); i=0
for t in "$@"; do
  s=${t%.*}; mm=$(printf "%d:%02d" $((s/60)) $((s%60)))
  ffmpeg -nostdin -loglevel error -y -ss "$t" -i "$FILE" -frames:v 1 \
    -vf "scale=${SW:-480}:-2,drawtext=text='$mm':x=6:y=6:fontcolor=yellow:fontsize=20:box=1:boxcolor=black@0.6" \
    "$TMP/fr_$(printf %03d $i).jpg"
  i=$((i+1))
done
ffmpeg -nostdin -loglevel error -y -framerate 1 -i "$TMP/fr_%03d.jpg" -vf "tile=${cols}x${rows}:padding=4" -frames:v 1 -q:v 3 "$OUT/$name.jpg" \
  && echo "→ $OUT/$name.jpg"
rm -rf "$TMP"
