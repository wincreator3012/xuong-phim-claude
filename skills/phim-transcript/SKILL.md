---
name: "phim-transcript"
description: "Tạo transcript tiếng Việt có mốc thời gian, phụ đề SRT và khoảng lặng cho file video/audio nằm trong thư mục \"xuong-phim-claude\" bằng Whisper chạy tại máy (sherpa-onnx, không đưa dữ liệu ra ngoài), rồi kiểm phủ kín lời nói và soát lỗi thuật ngữ. Kích hoạt khi user nói \"transcript\", \"gỡ băng\", \"chép lời\", \"phụ đề\", \"SRT\", \"đoạn X ở phút mấy\", \"tóm tắt nội dung clip này\", hoặc khi skill dựng phim cần transcript. Không dùng cho file ngoài thư mục mount."
---

# Transcript và phụ đề tại máy

Whisper + silero VAD qua sherpa-onnx, chạy trên máy của người dùng (Mac thật hoặc VM Cowork trên chính máy đó) - file media không rời máy, không cần môi trường đám mây. File nguồn phải nằm trong thư mục xưởng; nếu ở nơi khác, nhờ user kéo vào (ví dụ `Du an/<x>/nguon/`). Chi tiết model: `tools/models/TAI-MODEL.md`.

## Chạy ở đâu

Máy chưa cài sherpa-onnx và model (`python3 tools/cai-dat.py --trang-thai`): chạy skill phim-thiet-lap trước.

VM Cowork chỉ có khoảng 3-4 GB RAM nên large-v3 KHÔNG chạy được trong VM (chết lặng vì hết bộ nhớ). Vì vậy:

1. **Ưu tiên: large-v3 trên Mac, qua hàng đợi** (máy là Mac thật và đã tải `sherpa-onnx-whisper-large-v3/` theo `tools/models/TAI-MODEL.md`; chưa có thì tool tự lùi về turbo và ghi trong log; máy không phải Mac thì chỉ có đường 2). Claude xếp việc trong VM, người dùng bấm đúp một file trên Mac:

```
cd "$HOME/mnt/Xuong phim AI/xuong-phim-claude"
python3 tools/hang-doi-go-bang.py them "../Du an/<x>/nguon/<file>" --out-dir "../Du an/<x>/transcript"
```

   Rồi nhắn người dùng: mở Finder, vào thư mục xưởng, bấm đúp `Go bang tren Mac.command` (lần đầu trên mỗi máy tự dựng môi trường vài phút, cần mạng; macOS chặn thì bấm chuột phải, chọn Open). Terminal chạy lần lượt mọi việc đang chờ và báo "Gỡ băng xong". Khi người dùng báo lại, kiểm `python3 tools/hang-doi-go-bang.py trang-thai` (phải thấy `xong` và `model=large-v3`), rồi `don` để cất việc đã xong. Mac không bị giới hạn 180 giây mỗi lượt như `device_bash`, nên file dài chạy một mạch.

2. **Dự phòng: turbo trong VM**, khi người dùng không ở máy hoặc cần ngay:

```
python3 tools/transcribe.py "<đường dẫn file>" --out-dir "<thư mục kết quả>"
```

   `--model auto` (mặc định) trong VM luôn ra turbo (large-v3-turbo: nhanh, chất lượng vẫn tốt). Ghi rõ trong báo cáo là transcript chạy bằng turbo; nếu nội dung nhiều thuật ngữ khó, đề nghị chạy lại bằng large-v3 trên Mac. `--model small` chỉ dùng khi thật gấp. Lượt gọi `device_bash` tối đa 180s: chạy bằng script + `timeout 170` + log, gọi lặp đọc tiến độ (script tự in "x/y đoạn"). File >90 phút: tách audio thành khúc 30 phút bằng ffmpeg, transcript từng khúc, cộng offset khi ghép.

Dù chạy ở đâu, luôn qua cổng: `python3 tools/nghiem-thu.py transcript "../Du an/<x>" [--nguon <tên file>]`.

- `--lang vi` mặc định; đổi khi nội dung tiếng khác
- Kết quả 4 file cùng tên gốc: `.transcript.json` (mốc giây, dùng cho máy), `.srt` (phụ đề), `.txt` (dạng đọc: `[hh:mm:ss - hh:mm:ss] lời nói`), `.silences.json` (khoảng lặng - hệ thống cắt phim dùng)

## Cổng nghiệm thu transcript (bắt buộc trước khi dùng hay giao)

`tools/nghiem-thu.py transcript` đối chiếu `.transcript.json` với `.silences.json` và thời lượng nguồn, báo KHÔNG ĐẠT khi:

- Có quãng dài hơn 8 giây CÓ TIẾNG (không nằm trong khoảng lặng) mà không có câu nào - dấu hiệu Whisper bỏ đoạn (hay xảy ra sau khoảng lặng dài, khi nói nhanh, hoặc ở ranh giới các khúc 30 phút). Xử lý: nhận dạng lại RIÊNG quãng đó nhưng với cửa sổ RỘNG (bao thêm 30-60 giây hai bên, xem lưu ý hallucination bên dưới), rồi ghép câu vào đúng vị trí theo mốc tuyệt đối, sắp lại thứ tự, ghi lại cả 3 file json/srt/txt
- Mốc thời gian đảo hoặc chồng lấn giữa các câu (thường do cộng offset sai khi ghép khúc) - sửa offset, không sửa tay từng câu

Cảnh báo (không chặn): câu dài hơn 25 giây (Whisper gộp câu - phụ đề sẽ quá dài, cần tách khi làm SRT). Transcript chưa qua cổng này mà đem lên phương án cắt sẽ bỏ oan nội dung, còn đem làm phụ đề sẽ lệch.

## Sau khi có transcript

- Luôn SOÁT LỖI trước khi giao: Whisper tiếng Việt hay sai thuật ngữ chuyên môn và tên riêng - đối chiếu từ vựng user hay dùng (danh sách ở `phong-cach/PHONG-CACH.md` mục 4, tên chương trình, "trắc ẩn", "chánh niệm"...) và sửa trong bản giao, giữ nguyên bản máy tạo
- User cần bản đọc: giao `.txt` hoặc chuyển thành văn bản mạch lạc (bỏ mốc thời gian, ngắt đoạn theo ý) tùy yêu cầu - hỏi nếu chưa rõ dùng để làm gì
- User cần phụ đề: giao `.srt`; nếu để upload YouTube thì soát ngắt dòng (≤2 dòng, ~38 ký tự/dòng). Phụ đề cho video ĐÃ DỰNG: tính lại mốc bằng `<thành phẩm>.map.json` của assemble (giữ cue có in ≤ t < out của từng part, mốc mới = start + (t - in)) thay vì cộng trừ tay
- User hỏi "đoạn X ở phút mấy": grep trong `.txt` theo từ khóa và các cách diễn đạt gần nghĩa, trả lời mốc thời gian kèm trích nguyên văn
- Transcript phục vụ dựng phim: giữ nguyên vị trí `Du an/<x>/transcript/` để assemble tự tìm silences.json
- **Nghi ngờ một đoạn là Whisper hallucinate (câu lạc quẻ, đứt quãng, nhắc tên/thương hiệu không khớp ngữ cảnh) - đừng vội kết luận chỉ dựa vào việc transcript RIÊNG một cửa sổ ngắn (vài giây) quanh đoạn đó để kiểm tra**: bản thân việc cắt ngắn/tách rời khỏi ngữ cảnh xung quanh có thể LÀ NGUYÊN NHÂN khiến Whisper đoán sai, không phải vì audio gốc có vấn đề. Đã gặp thực tế: một đoạn 2.7s bị nhận nhầm thành câu quảng cáo kênh khi transcript riêng cửa sổ ngắn, nhưng ra chữ hoàn toàn mạch lạc khi transcript lại nguyên khối dài hơn (cả đoạn liên tục, hoặc cả file). Quy trình đúng: nghi ngờ → thử transcript lại một cửa sổ RỘNG HƠN nhiều (30-60s bao quanh, hoặc cả đoạn liên tục nếu không quá dài) trước khi kết luận là lỗi nhận dạng thật
- Sửa skill này theo `skills/_chung/bao-tri-skill.md`; bài học gỡ băng và phụ đề mới vào `docs/BAI-HOC.md` chủ đề "Gỡ băng", "Phụ đề"

<!-- ban-nguon: phim-transcript 2026-10-07 fd5c5f61 -->
