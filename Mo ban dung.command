#!/bin/bash
# Mở BÀN DỰNG: tự tay tinh chỉnh timeline của một clip gần xong, xem trước ngay trên Chrome.
# Cách dùng: mở Finder, vào thư mục xưởng, bấm đúp file này.
# Giữ cửa sổ Terminal này mở trong lúc chỉnh; xong thì đóng cửa sổ.
# Nếu macOS báo "không mở được vì từ nhà phát triển không xác định":
#   bấm chuột phải vào file, chọn Open (Mở), rồi Open lần nữa. Chỉ cần làm một lần.

cd "$(dirname "$0")" || exit 1

PY=""
for c in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Chưa có Python 3 trên máy. Mở Terminal, gõ:  xcode-select --install  rồi bấm đúp lại file này."
  if [ -t 0 ]; then read -r -n 1 -p "Bấm phím bất kỳ để đóng cửa sổ này..."; fi
  exit 1
fi

"$PY" tools/ban-dung.py --mo
