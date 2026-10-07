#!/bin/bash
# Gỡ băng trên máy Mac (ngoài VM Cowork) bằng whisper large-v3.
# Cách dùng: mở Finder, vào thư mục xưởng, bấm đúp file này.
# Lần đầu tiên (một lần cho mỗi máy): tự dựng môi trường Python riêng, mất vài phút.
# Việc cần gỡ băng do Claude xếp sẵn trong "Du an/_tam/go-bang/viec/" cạnh xưởng (tools/hang-doi-go-bang.py).
# Nếu macOS báo "không mở được vì từ nhà phát triển không xác định":
#   bấm chuột phải vào file, chọn Open (Mở), rồi Open lần nữa. Chỉ cần làm một lần.

cd "$(dirname "$0")" || exit 1
XUONG="$(pwd)"
echo "Xưởng phim: $XUONG"

if [ "$(uname)" = "Darwin" ]; then
  VENV="${XUONG_VENV:-$HOME/Library/Application Support/xuong-phim/venv-go-bang}"
  export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
else
  VENV="${XUONG_VENV:-$HOME/.xuong-phim/venv-go-bang}"
fi

ket_thuc() {
  echo
  if [ -t 0 ]; then read -r -n 1 -p "Bấm phím bất kỳ để đóng cửa sổ này..."; echo; fi
  exit "$1"
}

PY=""
for c in /opt/homebrew/bin/python3 /usr/local/bin/python3 /usr/bin/python3 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    PY="$c"; break
  fi
done
if [ -z "$PY" ]; then
  echo "Chưa có Python 3 trên máy. Mở Terminal, gõ:  xcode-select --install  rồi chạy lại file này."
  ket_thuc 1
fi

if [ ! -x "$VENV/bin/python" ] || [ ! -f "$VENV/.san-sang" ]; then
  echo "Lần đầu trên máy này: dựng môi trường gỡ băng (numpy, sherpa-onnx, ffmpeg)..."
  mkdir -p "$(dirname "$VENV")"
  "$PY" -m venv "$VENV" || { echo "Không tạo được môi trường Python."; ket_thuc 1; }
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  "$VENV/bin/python" -m pip install --quiet numpy sherpa-onnx imageio-ffmpeg \
    || { echo "Cài thư viện không thành công (kiểm tra mạng rồi bấm đúp lại)."; ket_thuc 1; }
  touch "$VENV/.san-sang"
fi

if ! command -v ffmpeg >/dev/null 2>&1; then
  FF="$("$VENV/bin/python" -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())' 2>/dev/null)"
  if [ -n "$FF" ] && [ -x "$FF" ]; then
    ln -sf "$FF" "$VENV/bin/ffmpeg"
  else
    echo "Không tìm được ffmpeg."; ket_thuc 1
  fi
fi
export PATH="$VENV/bin:$PATH"

"$VENV/bin/python" tools/hang-doi-go-bang.py chay
RC=$?
echo
if [ $RC -eq 0 ]; then
  echo "Gỡ băng xong. Quay lại Claude và nhắn: đã gỡ băng xong."
else
  echo "Có việc gỡ băng bị lỗi. Quay lại Claude và nhắn: gỡ băng bị lỗi (log nằm ở Du an/_tam/go-bang/log/)."
fi
ket_thuc $RC
