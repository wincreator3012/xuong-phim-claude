# Model nhận dạng giọng nói

Nguồn: GitHub releases chính thức của k2-fsa/sherpa-onnx (huggingface bị chặn trong VM).

Whisper chạy ngay trên máy qua sherpa-onnx: video và giọng nói không rời máy. Thư mục này trống trong repo (model nặng); `python3 tools/cai-dat.py` tự tải `silero_vad.onnx` và `sherpa-onnx-whisper-turbo/` (hoặc `--model small`). Máy ảo không tải được vì mạng chặn thì tải file `.tar.bz2` bằng trình duyệt từ link ở mục cuối, thả vào thư mục này rồi chạy lại `cai-dat.py` (script tự giải nén, chỉ giữ file int8 và tokens). Ngôn ngữ mặc định của `transcribe.py` là tiếng Việt (`--lang vi`); bài tiếng Anh dùng `--lang en`.

## Các model

- `silero_vad.onnx`: phát hiện tiếng nói.
- `sherpa-onnx-whisper-turbo/` (large-v3-turbo int8): mặc định sau khi cài, chạy được trong VM Cowork.
- `sherpa-onnx-whisper-small/`: dự phòng khi cần rất nhanh (`--model small`).
- `sherpa-onnx-whisper-large-v3/` (large-v3 int8, khoảng 1,7 GB): chất lượng cao nhất, chỉ chạy trên máy Mac thật đủ RAM; không tải sẵn, tải theo mục cuối với TÊN là `large-v3`.

## Chạy ở đâu, model nào

1. **Ưu tiên: gỡ băng trên Mac bằng large-v3** (cần tải `sherpa-onnx-whisper-large-v3/` trước; chưa có thì tool tự lùi về turbo và ghi rõ trong log). VM Cowork chỉ có khoảng 3-4 GB RAM nên large-v3 chết lặng trong VM (hết bộ nhớ, không báo lỗi). Máy Mac thật đủ RAM. Claude xếp việc bằng `python3 tools/hang-doi-go-bang.py them "<file>" --out-dir "<thư mục transcript>"`, người dùng bấm đúp `Go bang tren Mac.command` ở thư mục gốc, Terminal chạy lần lượt mọi việc đang chờ rồi báo "Gỡ băng xong". Claude đọc `python3 tools/hang-doi-go-bang.py trang-thai`, sau đó vẫn chạy `nghiem-thu.py transcript` như mọi lần.
   - Lần bấm đầu tiên trên mỗi máy tự dựng môi trường Python riêng ở `~/Library/Application Support/xuong-phim/venv-go-bang` (numpy, sherpa-onnx, imageio-ffmpeg), mất vài phút, cần mạng. Môi trường này nằm ngoài thư mục xưởng nên không đồng bộ sang máy khác; mỗi máy tự dựng lần đầu của nó.
   - macOS có thể chặn file lần đầu ("nhà phát triển không xác định"): bấm chuột phải, chọn Open, rồi Open lần nữa.
   - `--model auto` trên macOS chọn large-v3 khi tổng RAM từ 12 GB, dưới mức đó chọn turbo.
   - Lượt chạy đầu sau khi khởi động máy chậm hơn (đọc 1,7 GB model từ đĩa lần đầu).
2. **Dự phòng: gỡ băng trong VM** khi người dùng không ở máy hoặc cần ngay: `python3 tools/transcribe.py "<file>" --out-dir "<thư mục>"`. `--model auto` trong VM luôn ra turbo (dòng log "model tự chọn: whisper-turbo (RAM trống ... GB)"). Ghi rõ trong báo cáo là transcript chạy bằng turbo.

Dù chạy ở đâu, kết quả cùng định dạng (`*.transcript.json`, `*.srt`, `*.txt`, `*.silences.json`) và cùng qua cổng `nghiem-thu.py transcript`.

## Tải model khác nếu cần

Thay TÊN tương ứng, chạy lặp lệnh curl `-C -` tới khi đủ dung lượng rồi `tar xjf`; thêm TÊN vào `choices` của `--model` trong `tools/transcribe.py`. Tên thư mục giải nén phải đúng dạng `sherpa-onnx-whisper-TÊN/` với file `TÊN-encoder*.onnx`, `TÊN-decoder*.onnx`, `TÊN-tokens.txt` bên trong.

    cd "$HOME/mnt/<thư mục xưởng>/tools/models"
    timeout 160 curl -sL -C - -o sherpa-onnx-whisper-TÊN.tar.bz2 \
      https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-TÊN.tar.bz2
