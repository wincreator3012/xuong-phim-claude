#!/bin/bash
# SOI KHUNG short dọc bằng lưới ảnh (contact sheet). Chạy từ gốc xưởng, trên Mac.
#   bash tools/short-khung.sh "<thư mục dự án>" lat <slug> <t1> <t2> <t3> ...   lưới khung 360x640 của thành phẩm tại các giây (cần >= 3 mốc, tối đa 6 khung mỗi hàng)
#       -> <dự án>/xuat-nhap/lat-<slug>.jpg
#   bash tools/short-khung.sh "<thư mục dự án>" crop <focus 0-1> <zoom> <t1> <t2> ...   lưới ô mặt trên của nguồn, cắt đúng như layout mat-tren (cropFocus, cropZoom)
#       -> <dự án>/xuat-nhap/crop.jpg ; nguồn lấy từ biến NGUON (mặc định nguon/mat.mp4)
# Ghi ảnh ra xuat-nhap/ của dự án (ngoài repo), thư mục tạm ở $TMPDIR.
P=$1; MODE=$2; shift 2
W=$(mktemp -d)
case "$MODE" in
  lat)
    S=$1; shift; V="$P/xuat-hoan-chinh/$S-doc.mp4"; i=0; IN=""; LAY=""; n=$#
    [ "$n" -lt 3 ] && { echo "cần ít nhất 3 mốc thời gian (xstack lỗi khi ít hơn)"; exit 2; }
    for t in "$@"; do
      ffmpeg -y -v error -ss "$t" -i "$V" -frames:v 1 -vf "scale=360:640" "$W/q-$i.jpg"
      IN="$IN -i $W/q-$i.jpg"; LAY="$LAY|$((i%6*360))_$((i/6*640))"; i=$((i+1))
    done
    ffmpeg -y -v error $IN -filter_complex "xstack=inputs=$n:layout=${LAY#|}" "$P/xuat-nhap/lat-$S.jpg" && echo "-> $P/xuat-nhap/lat-$S.jpg" ;;
  crop)
    F=$1; Z=$2; shift 2; NG="${NGUON:-$P/nguon/mat.mp4}"; i=0; IN=""; LAY=""; n=$#
    [ "$n" -lt 3 ] && { echo "cần ít nhất 3 mốc thời gian"; exit 2; }
    for t in "$@"; do
      ffmpeg -y -v error -ss "$t" -i "$NG" -frames:v 1 -vf "crop='min(iw,ih*1.125)/$Z':'min(ih,iw/1.125)/$Z':'(iw-ow)*$F':0,scale=540:480" "$W/cr-$i.jpg"
      IN="$IN -i $W/cr-$i.jpg"; LAY="$LAY|$((i%4*540))_$((i/4*480))"; i=$((i+1))
    done
    ffmpeg -y -v error $IN -filter_complex "xstack=inputs=$n:layout=${LAY#|}" "$P/xuat-nhap/crop.jpg" && echo "-> $P/xuat-nhap/crop.jpg" ;;
  *) echo "lệnh: lat | crop"; exit 2 ;;
esac
rm -rf "$W"
