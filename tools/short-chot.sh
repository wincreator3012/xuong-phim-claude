#!/bin/bash
# CHỐT MỘT SHORT: kiểm gói đăng tải, đặt vào Thanh pham/<dự án>/Short NN <slug>/ (video đạt nghiệm thu, nghiem-thu.json, dang-tai/).
#   bash tools/short-chot.sh "<thư mục dự án>" "<tên dự án trong Thanh pham>" <slug> <NN> [tệp thương hiệu đăng tải, ví dụ brand-yln.json]
# Chạy từ gốc xưởng. Không ghi đè file đã có (cp -n) trừ dang-tai/ (cp -rf, vì gói đăng tải sửa tới phút chót). Sau "duyệt" mới giao (tools/giao-thanh-pham.py).
P=$1; TEN=$2; S=$3; N=$4; BR=$5
[ -z "$P" ] || [ -z "$TEN" ] || [ -z "$S" ] || [ -z "$N" ] && { echo "dùng: bash tools/short-chot.sh \"<dự án>\" \"<tên Thanh pham>\" <slug> <NN> [brand.json]"; exit 2; }
T="../Thanh pham/$TEN/Short $N $S"
python3 tools/dang-tai.py kiem "$P/dang-tai/$S" 2>&1 | tail -8
mkdir -p "$T/dang-tai"
cp -n "$P/xuat-hoan-chinh/$S-doc.mp4" "$T/$N-$S-doc.mp4"
cp -n "$P/xuat-hoan-chinh/$S-doc.nghiem-thu.json" "$T/$N-$S-doc.nghiem-thu.json"
cp -rf "$P/dang-tai/$S/." "$T/dang-tai/"
[ -n "$BR" ] && cp -f "$P/dang-tai/$BR" "$T/dang-tai/"
sed -i "s#\"video\": \"[^\"]*\"#\"video\": \"../$N-$S-doc.mp4\"#" "$T/dang-tai/dang-tai.json"
python3 tools/dang-tai.py kiem "$T/dang-tai" 2>&1 | tail -4
cmp "$P/xuat-hoan-chinh/$S-doc.mp4" "$T/$N-$S-doc.mp4" && echo "video giống nhau"; ls "$T"
