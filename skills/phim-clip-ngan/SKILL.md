---
name: phim-clip-ngan
description: Cắt clip ngắn Reels/Shorts/TikTok hoặc clip quảng bá 30-180 giây (khung dọc 9:16 hoặc ngang) từ bài giảng, podcast, buổi nói chuyện đã có trong thư mục xưởng (gốc repo xuong-phim-claude) - chọn đoạn có hook, dựng hook-trước-intro, burn phụ đề, nghiệm thu tự động. Kích hoạt khi user nói "cắt clip ngắn", "làm Reels", "Shorts", "TikTok", "clip dọc", "clip quảng bá chương trình", "cắt đoạn hay nhất", "làm teaser". Dựng bài dài dùng phim-dung-bai.
---

# Clip ngắn cho Reels, Shorts và quảng bá

Nghề khác với dựng bài dài: bài dài phục vụ người đã ngồi xuống học, clip ngắn phải TỰ giành lấy 3 giây đầu của người đang lướt. Nhưng vẫn là thương hiệu của một người làm nghề tri thức: giành sự chú ý bằng một câu hỏi hay một sự thật chạm đúng, không giật tít rẻ, không framing đua tranh hay bỏ lại ai. Giọng và giới hạn riêng của người dùng nằm ở `phong-cach/PHONG-CACH.md`.

## Bước 0 - nền tảng

Như mọi skill phim: đọc `CLAUDE.md`, `phong-cach/PHONG-CACH.md` (mục 2, 5, 7 quyết định khung, nhạc và phụ đề mặc định của clip ngắn) và `docs/QUY-TRINH-KY-THUAT.md` ở gốc thư mục xưởng (gốc repo xuong-phim-claude), làm mục "Khởi động phiên mới" nếu phiên chưa dựng môi trường đám mây. Cần transcript của tư liệu nguồn - nếu chưa có, chạy theo skill phim-transcript trước (kèm `python3 tools/nghiem-thu.py transcript` để chắc Whisper không bỏ đoạn - đoạn bị bỏ thường lại là đoạn nói hay). Clip ngắn thừa hưởng `mau-sac.json` của dự án gốc (skill phim-mau-sac), không khám màu lại.

## Bước 1 - đề xuất danh sách ứng viên (chốt duyệt số 1)

Đọc transcript, tìm 3-6 đoạn ứng viên. Một đoạn đáng làm clip ngắn khi có đủ ba tầng trong chính nó:

1. **Móc [hook]**: câu đầu tiên khiến người lạ dừng tay - một câu hỏi trúng nỗi băn khoăn, một khẳng định ngược trực giác, một con số, hoặc mở đầu một câu chuyện. Nếu ý hay nhưng câu mở yếu, tìm trong đoạn một câu đắt để đưa lên đầu làm thẻ mở (InfoQuote 2-3s) rồi mới vào lời giảng
2. **Thân trọn vẹn**: một ý duy nhất được giảng trọn - người chưa xem bài dài vẫn hiểu, không cần ngữ cảnh trước đó ("như phần trước mình nói" là dấu loại)
3. **Kết mở**: câu chốt tự nhiên của chính lời giảng; CTA để outro lo, không ép lời giảng thành lời mời chào

Độ dài: ưu tiên 45-90s; clip quảng bá chương trình có thể 60-180s. Trình user bảng: mốc nguồn, câu hook, ý chính, độ dài dự kiến, đề xuất khung (dọc/ngang). Chờ duyệt chọn đoạn nào làm.

## Bước 2 - dựng từng clip

Mỗi clip là một dự án con hoặc thư mục trong dự án gốc (`du-an/<tên>/clip-ngan/<slug>/` với timeline riêng), tái dùng transcript và nguồn của dự án gốc bằng đường dẫn tương đối gốc.

- **Cấu trúc bắt buộc - HOOK TRƯỚC, INTRO SAU**: clip ngắn KHÔNG BAO GIỜ mở bằng intro - người lướt sẽ trượt qua trước khi thấy nội dung. Thứ tự chuẩn: hook (3-10 giây lời giảng đắt nhất, hoặc thẻ mở InfoQuote 2-3s) → intro NGẮN 2.5-4 giây từ preset (hoặc bỏ hẳn intro, dồn nhận diện thương hiệu về outro) → thân → outro CTA. Trong timeline.json: trường "intro"/"outro" cấp cao nhất của assemble luôn đứng đầu/cuối, nên với clip ngắn KHÔNG dùng hai trường đó mà đưa intro/outro vào danh sách segments như các insert thường, đặt intro sau segment hook
- **Hai hệ mốc thời gian**: `in`/`out`/`broll.at` theo mốc TRONG FILE NGUỒN; `overlay.at` TƯƠNG ĐỐI từ đầu đoạn (at = mốc nguồn - in). Soạn xong timeline chạy `python3 tools/assemble.py --project "<thư mục clip>" --kiem-tra` để bắt lỗi mốc/file trước khi encode
- **Tách câu ghép để chèn thẻ ở giữa (ví dụ tách câu Hook khỏi câu kế tiếp để chèn slide tiêu đề)**: nếu VAD/silencedetect không tách được ranh giới hai vế (báo liên tục một đoạn, thường do người nói không ngừng hơi giữa hai vế dù văn viết có dấu phẩy/chấm câu), dùng kỹ thuật năng lượng ngắn hạn trong `bien-tap.md` (trích 4-6 giây quanh điểm nghi ngờ, tính RMS từng khung 20ms, cắt vào giữa khoảng trũng nhỏ nhất) thay vì cắt ngay tại ranh giới chữ trên văn bản - cắt vào giữa khoảng trũng cho biên độ an toàn cả hai phía
- **Khung dọc**: kiểm tra cropFocus bằng 1 frame thử trước khi dựng (ffmpeg crop + scale, xem hình). Người nói phải nằm giữa khung dọc, đầu không chạm mép trên
- **Đồ họa dọc**: render từ preset `do-hoa-chung/preset-intro-outro-doc.json` (placeholder đầy đủ: title/subtitle, thông điệp kết, liên hệ, QR - xem `do-hoa-chung/GHI-CHU.md`); outro clip ngắn 5-6s CTA một dòng, có QR thì 8-9s. Thẻ InfoQuote/SectionTitle dọc dùng làm thẻ mở khi cần. `render-do-hoa.mjs` tự nghiệm thu file render (thời lượng, fps, alpha) - thoát mã 1 thì sửa job, không dùng file sai
- **Khoảng cách hook/intro với slide toàn màn hình kế tiếp**: clip ngắn hay dồn hook + intro + đồ họa sát nhau trong vài giây đầu - áp dụng quy tắc tối thiểu 5 giây cảnh quay chính giữa hai thẻ toàn màn hình (xem `bien-tap.md` mục "Khoảng cách tối thiểu giữa các thẻ/slide toàn màn hình"). Khi cần nhấn một khái niệm/framework ngay sau hook mà chưa đủ 5 giây, dùng overlay bán trong suốt hiện dần theo lời nói (`Benefits` với `revealAt` từng mục) thay vì cắt sang một slide toàn màn hình mới - vừa giữ mạch nhìn thấy người nói, vừa không phải chờ đủ 5 giây vì overlay không tính vào quy tắc đó
- **Nhạc**: mode `full` + duck, gainDb -20 đến -24; nhạc là lớp năng lượng nền, không lấn lời
- **Nhịp cắt**: trong clip ngắn được phép cắt sát hơn bài dài - bỏ mọi khoảng thở >0.8s trừ khoảng lặng có chủ đích trước câu chốt
- Dựng bằng `python3 tools/assemble.py --project "<thư mục clip>" [--preview]`; assemble tự kiểm hình = tiếng từng part và thành phẩm, dừng khi KHÔNG ĐẠT - tìm nguyên nhân, không dùng `--ep-encode-lai` để đi tiếp

## Bước 3 - phụ đề (mặc định CÓ cho clip dọc)

Phần lớn người lướt không bật tiếng - clip dọc mặc định burn phụ đề, trừ khi user từ chối. Quy trình:

1. Tính lại mốc phụ đề từ SRT gốc bằng `<clip>.map.json` mà assemble ghi cạnh thành phẩm: với từng part `kind: "cut"`, giữ cue có `in ≤ t < out` và đặt mốc mới = `start + (t - in)`; part `insert` (thẻ, intro) không có cue nhưng đã được tính sẵn trong `start` của các part sau - không còn phải tự cộng trừ thời lượng thẻ chèn (nguồn lỗi lệch phụ đề trước đây). Cách thay thế khi map.json không có: transcript lại chính file clip đã dựng (nhanh vì ngắn)
2. Soát lời phụ đề theo transcript thật, sửa lỗi nhận dạng, ngắt dòng tối đa ~38 ký tự, 1-2 dòng mỗi phụ đề
3. Burn bằng ffmpeg subtitles filter lên bản đã dựng (encode lại một lần, clip ngắn nên nhanh):

```
ffmpeg -i clip.mp4 -vf "subtitles=clip.srt:force_style='FontName=Be Vietnam Pro,FontSize=13,PrimaryColour=&HFFFFFF&,OutlineColour=&H66000000&,BorderStyle=1,Outline=1,Shadow=0,MarginV=46'" -c:a copy clip-phude.mp4
```

Lần đầu dùng trên máy: kiểm tra fontconfig thấy font Việt (`fc-list | grep -i "be vietnam"` - nếu chưa có, dùng font hệ có sẵn hỗ trợ tiếng Việt như DejaVu Sans, hoặc tải TTF Be Vietnam Pro từ google/fonts trên GitHub raw - github được phép). Xuất 2 frame kiểm tra dấu tiếng Việt hiển thị đúng trước khi burn cả clip.

File đã burn phụ đề là bản HOÀN CHỈNH cuối cùng - ghi vào `du-an/<x>/xuat-hoan-chinh/<slug>-doc.mp4` (không phải `xuat-nhap/`, nơi đó chỉ chứa bản `assemble.py` xuất thô chưa phụ đề và các bản nháp preview). Burn là một lượt encode mới nên file này phải qua cổng nghiệm thu ở Bước 4 một lần nữa.

## Bước 4 - nghiệm thu

1. Cổng máy đo bắt buộc trên file CUỐI trong `xuat-hoan-chinh/`: `python3 tools/nghiem-thu.py video "<file>" --khung doc --anh` phải ĐẠT (hình = tiếng trong 0.06s, -14±1 LUFS, 1080x1920, 30fps, không im lặng/hình đứng bất thường)
2. Stage `<file>.luoi.jpg` và xem frame ĐẦU TIÊN: hook phải đọc được ngay, không bị logo/UI platform che - phụ đề cách mép dưới đủ xa; thứ tự hook → intro → thân → outro đúng
3. Phụ đề: xuất 2-3 frame tại mốc có cue và đối chiếu lời đang nói (map.json đúng thì chữ khớp miệng)
4. Thời lượng đúng giới hạn platform user nhắm (Shorts ≤3 phút, Reels ≤90s ưu tiên), file đặt tên rõ: `<slug>-doc.mp4`

Báo kết quả kèm một dòng "nghiệm thu máy: ĐẠT". Một bài giảng tốt thường ra 3-5 clip - sau khi user duyệt clip đầu, đề nghị dựng loạt còn lại cùng format cho đồng đều.
