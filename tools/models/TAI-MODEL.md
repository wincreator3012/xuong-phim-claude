# Model nhận dạng giọng nói (tools/cai-dat.py tự tải vào đây)

Whisper chạy ngay trên máy qua sherpa-onnx: video và giọng nói của bạn không rời máy. Thư mục này trống trong repo (model nặng ~1GB); sau khi cài có:

- `silero_vad.onnx`: phát hiện đoạn có tiếng nói
- `sherpa-onnx-whisper-turbo/`: large-v3-turbo int8, mặc định (chính xác tốt với tiếng Việt, chạy ổn trên Apple Silicon)
- `sherpa-onnx-whisper-small/`: tuỳ chọn khi cần nhanh hơn (`python3 tools/cai-dat.py --model small`)

Nguồn: GitHub releases chính thức của k2-fsa/sherpa-onnx:
`https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-whisper-<tên>.tar.bz2`

Nếu máy ảo không tải được (mạng chặn), tự tải file .tar.bz2 bằng trình duyệt từ link trên, thả vào thư mục này rồi chạy lại `python3 tools/cai-dat.py` - script sẽ giải nén (chỉ giữ file int8 + tokens).

Ngôn ngữ mặc định của transcribe.py là tiếng Việt (`--lang vi`); bài giảng tiếng Anh dùng `--lang en`.
