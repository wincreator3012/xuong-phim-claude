---
name: phim-transcript
description: Tạo transcript tiếng Việt có mốc thời gian, phụ đề SRT và khoảng lặng cho file video/audio nằm trong thư mục xưởng (gốc repo xuong-phim-claude) bằng Whisper chạy tại máy (sherpa-onnx, không đưa dữ liệu ra ngoài), rồi kiểm phủ kín lời nói và soát lỗi thuật ngữ. Kích hoạt khi user nói "transcript", "gỡ băng", "chép lời", "phụ đề", "SRT", "đoạn X ở phút mấy", "tóm tắt nội dung clip này", hoặc khi skill dựng phim cần transcript. Không dùng cho file ngoài thư mục mount.
---

# Transcript và phụ đề tại máy

Whisper (large-v3-turbo mặc định) + silero VAD chạy trong VM cục bộ qua sherpa-onnx - file media của user không rời máy. Môi trường, giới hạn và cách chạy việc dài: `docs/QUY-TRINH-KY-THUAT.md` ở gốc thư mục xưởng (đọc trước khi chạy; không cần dựng môi trường đám mây cho việc này). File nguồn phải nằm trong thư mục mount xưởng; nếu ở nơi khác trên máy, nhờ user kéo vào (ví dụ vào `du-an/<x>/nguon/`).

## Chạy

```
cd "<gốc xưởng>"   # device_bash: "$HOME/mnt/<tên thư mục đã kết nối>"
python3 tools/transcribe.py "<đường dẫn file>" --out-dir "<thư mục kết quả>"
python3 tools/nghiem-thu.py transcript "du-an/<x>" [--nguon <tên file>]
```

- `--model turbo` (mặc định): chất lượng cao nhất trên máy. `--model small`: nhanh hơn khi cần gấp hoặc file rất dài
- `--lang vi` mặc định; đổi khi nội dung tiếng khác
- Kết quả 4 file cùng tên gốc: `.transcript.json` (mốc giây, dùng cho máy), `.srt` (phụ đề), `.txt` (dạng đọc: `[hh:mm:ss - hh:mm:ss] lời nói`), `.silences.json` (khoảng lặng - hệ thống cắt phim dùng)
- Thời gian chạy vượt 180s mỗi lần gọi device_bash: chạy bằng script + `timeout 170` + log, gọi lặp đọc tiến độ (script tự in "x/y đoạn"). File >90 phút: tách audio thành từng khúc 30 phút bằng ffmpeg rồi transcript từng khúc, cộng offset khi ghép kết quả

## Cổng nghiệm thu transcript (bắt buộc trước khi dùng hay giao)

`tools/nghiem-thu.py transcript` đối chiếu `.transcript.json` với `.silences.json` và thời lượng nguồn, báo KHÔNG ĐẠT khi:

- Có quãng dài hơn 8 giây CÓ TIẾNG (không nằm trong khoảng lặng) mà không có câu nào - dấu hiệu Whisper bỏ đoạn (hay xảy ra sau khoảng lặng dài, khi nói nhanh, hoặc ở ranh giới các khúc 30 phút). Xử lý: nhận dạng lại RIÊNG quãng đó nhưng với cửa sổ RỘNG (bao thêm 30-60 giây hai bên, xem lưu ý hallucination bên dưới), rồi ghép câu vào đúng vị trí theo mốc tuyệt đối, sắp lại thứ tự, ghi lại cả 3 file json/srt/txt
- Mốc thời gian đảo hoặc chồng lấn giữa các câu (thường do cộng offset sai khi ghép khúc) - sửa offset, không sửa tay từng câu

Cảnh báo (không chặn): câu dài hơn 25 giây (Whisper gộp câu - phụ đề sẽ quá dài, cần tách khi làm SRT). Transcript chưa qua cổng này mà đem lên phương án cắt sẽ bỏ oan nội dung, còn đem làm phụ đề sẽ lệch.

## Sau khi có transcript

- Luôn SOÁT LỖI trước khi giao: Whisper tiếng Việt hay sai thuật ngữ chuyên môn và tên riêng - đối chiếu danh sách "từ ngữ phải viết đúng" ở mục 4 của `phong-cach/PHONG-CACH.md` (tên chương trình, thuật ngữ nghề, tên riêng) và sửa trong bản giao, giữ nguyên bản máy tạo
- User cần bản đọc: giao `.txt` hoặc chuyển thành văn bản mạch lạc (bỏ mốc thời gian, ngắt đoạn theo ý) tùy yêu cầu - hỏi nếu chưa rõ dùng để làm gì
- User cần phụ đề: giao `.srt`; nếu để upload YouTube thì soát ngắt dòng (≤2 dòng, ~38 ký tự/dòng). Phụ đề cho video ĐÃ DỰNG: tính lại mốc bằng `<thành phẩm>.map.json` của assemble (giữ cue có in ≤ t < out của từng part, mốc mới = start + (t - in)) thay vì cộng trừ tay
- User hỏi "đoạn X ở phút mấy": grep trong `.txt` theo từ khóa và các cách diễn đạt gần nghĩa, trả lời mốc thời gian kèm trích nguyên văn
- Transcript phục vụ dựng phim: giữ nguyên vị trí `du-an/<x>/transcript/` để assemble tự tìm silences.json
- **Nghi ngờ một đoạn là Whisper hallucinate (câu lạc quẻ, đứt quãng, nhắc tên/thương hiệu không khớp ngữ cảnh) - đừng vội kết luận chỉ dựa vào việc transcript RIÊNG một cửa sổ ngắn (vài giây) quanh đoạn đó để kiểm tra**: bản thân việc cắt ngắn/tách rời khỏi ngữ cảnh xung quanh có thể LÀ NGUYÊN NHÂN khiến Whisper đoán sai, không phải vì audio gốc có vấn đề. Đã gặp thực tế: một đoạn 2.7s bị nhận nhầm thành câu quảng cáo kênh khi transcript riêng cửa sổ ngắn, nhưng ra chữ hoàn toàn mạch lạc khi transcript lại nguyên khối dài hơn (cả đoạn liên tục, hoặc cả file). Quy trình đúng: nghi ngờ → thử transcript lại một cửa sổ RỘNG HƠN nhiều (30-60s bao quanh, hoặc cả đoạn liên tục nếu không quá dài) trước khi kết luận là lỗi nhận dạng thật
- Khi cập nhật skill này qua propose_skills, giữ trường `description` là mô tả KÍCH HOẠT (khi nào dùng skill), không ghi changelog vào đó
