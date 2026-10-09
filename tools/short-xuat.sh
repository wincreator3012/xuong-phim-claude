#!/bin/bash
# XUẤT MỘT SHORT DỌC (mặt trên, cảnh dưới): dựng -> phụ đề .ass -> đốt phụ đề + nén + âm lượng -> nghiệm thu.
#   bash tools/short-xuat.sh "<thư mục dự án>" <slug> [VOL dB, mặc định 3.7]      (chạy từ gốc xưởng, trên Mac qua device_bash)
# Biến môi trường:  SKIP_ASSEMBLE=1  bỏ bước dựng (dùng lại xuat-nhap/<slug>-doc.mp4 sẵn có, chỉ đốt phụ đề lại)
#                   EP=1             thêm --ep-encode-lai vào assemble.py (bắt buộc sau khi chép lại các webm cảnh mới về máy)
# Lượng VOL: lời một người nói qua Zoom, nhạc xuong-guitar-am hạ -23 dB, VOL 2.4 cho khoảng -13,5 LUFS (BAI-HOC, chủ đề short mặt trên).
# Mỗi lượt gọi lệnh trên máy tối đa 180 giây: bước dựng có timeout 170 giây, hết giờ thì chạy lại đúng lệnh (assemble làm tiếp từ cache).
P=$1; S=$2; VOL=${3:-3.7}
[ -z "$P" ] || [ -z "$S" ] && { echo "dùng: bash tools/short-xuat.sh \"<thư mục dự án>\" <slug> [VOL dB]"; exit 2; }
mkdir -p "$P/xuat-nhap" "$P/xuat-hoan-chinh"
LOG="$P/xuat-nhap/run-$S.log"
if [ -z "$SKIP_ASSEMBLE" ]; then
  EPF=""; [ -n "$EP" ] && EPF="--ep-encode-lai"
  timeout 170 python3 tools/assemble.py --project "$P" --timeline "clip-ngan/$S/timeline.json" --out "$S-doc" $EPF >> "$LOG" 2>&1 || true
  tail -3 "$LOG"
fi
python3 tools/short-dung.py ass "$S" --du-an "$P" | tail -3
TMPASS="${TMPDIR:-/tmp}/x-$S.ass"
cp "$P/clip-ngan/$S/phu-de/$S-doc.ass" "$TMPASS"
ffmpeg -y -v error -i "$P/xuat-nhap/$S-doc.mp4" -vf "ass=$TMPASS" -af "acompressor=threshold=0.063:ratio=3:attack=8:release=120:makeup=2.5,volume=${VOL}dB,alimiter=limit=0.8:attack=5:release=80:level=disabled" -c:v libx264 -preset fast -crf 17 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart "$P/xuat-hoan-chinh/$S-doc.mp4"
python3 tools/nghiem-thu.py video "$P/xuat-hoan-chinh/$S-doc.mp4" --khung doc --anh 2>&1 | grep -E "ĐẠT|CẢNH BÁO|KHÔNG|KẾT LUẬN|LUFS|dB"
