---
name: "phim-clip-ngan"
description: "Cắt clip ngắn Reels/Shorts/TikTok hoặc clip quảng bá 30-180 giây (khung dọc 9:16 hoặc ngang) từ bài giảng, podcast, buổi nói chuyện, phim đã có trong thư mục \"xuong-phim-claude\" - chọn đoạn có hook, dựng hook-trước-intro, bảng tên cho người nói, burn phụ đề, nghiệm thu tự động. Kích hoạt khi user nói \"cắt clip ngắn\", \"làm Reels\", \"Shorts\", \"TikTok\", \"clip dọc\", \"clip quảng bá chương trình\", \"cắt đoạn hay nhất\", \"làm teaser\", \"bản gọn 60-90 giây\". KHÔNG dùng để dựng bài dài hoàn chỉnh (phim-dung-bai), dàn góc podcast nhiều máy (phim-multicam), hay phim tài liệu phỏng vấn (phim-tai-lieu-phong-van)."
---

# Clip ngắn cho Reels, Shorts và quảng bá

Nghề khác với dựng bài dài: bài dài phục vụ người đã ngồi xuống học, clip ngắn phải TỰ giành lấy 3 giây đầu của người đang lướt. Nhưng vẫn là thương hiệu của một người làm nghề tri thức: giành sự chú ý bằng một câu hỏi hay một sự thật chạm đúng, không giật tít rẻ, không framing đua tranh hay bỏ lại ai (tông và cách nói ở `phong-cach/PHONG-CACH.md` mục 3 và 6).

## Bước 0 - nền tảng

Đọc `skills/_chung/van-hanh.md`, `skills/_chung/timeline-va-dung.md`, `skills/_chung/overlay-va-the.md`, `skills/_chung/nghiem-thu-dung-y.md`. Cần transcript của tư liệu nguồn: chưa có thì chạy phim-transcript trước và qua `nghiem-thu.py transcript` (đoạn Whisper bỏ sót thường lại là đoạn nói hay). Clip ngắn thừa hưởng `mau-sac.json` của dự án gốc, không khám màu lại. Trước khi đề xuất, đọc `phong-cach/PHONG-CACH.md` mục 2 (loại clip), 5 (nhạc) và 7 (phụ đề).

## Bước 1 - đề xuất danh sách ứng viên (chốt duyệt số 1)

Đọc transcript, tìm 3-6 đoạn ứng viên. Một đoạn đáng làm clip ngắn khi có đủ ba tầng trong chính nó:

1. **Móc [hook]**: câu đầu tiên khiến người lạ dừng tay - một câu hỏi trúng nỗi băn khoăn, một khẳng định ngược trực giác, một con số, hoặc mở đầu một câu chuyện. Ý hay nhưng câu mở yếu thì tìm trong đoạn một câu đắt đưa lên đầu (cắt câu đó làm segment hook, có thể kèm dải chữ Benefits một mục hiện nguyên văn câu) rồi mới vào lời giảng.
2. **Thân trọn vẹn**: một ý duy nhất được giảng trọn - người chưa xem bài dài vẫn hiểu ("như phần trước mình nói" là dấu loại).
3. **Kết mở**: câu chốt tự nhiên của chính lời giảng; lời mời để outro lo, không ép lời giảng thành lời mời chào.

Độ dài: ưu tiên 45-90 giây; clip quảng bá chương trình có thể 60-180 giây. Trình bảng: mốc nguồn, câu hook, ý chính, độ dài dự kiến, khung đề xuất (dọc, ngang). Chờ người dùng chọn.

## Bước 2 - dựng từng clip

Mỗi clip là một dự án con `du-an/<tên>/clip-ngan/<slug>/` với `timeline.json` riêng; mọi `src` viết tương đối so với THƯ MỤC DỰ ÁN GỐC. `--project` luôn trỏ dự án gốc (để tìm đúng `transcript/*.silences.json` cho snap):

```
python3 tools/assemble.py --project "du-an/<tên>" --timeline "clip-ngan/<slug>/timeline.json" --kiem-tra
python3 tools/assemble.py --project "du-an/<tên>" --timeline "clip-ngan/<slug>/timeline.json" --preview --out "<slug>-<khung>-nhap1"
python3 tools/assemble.py --project "du-an/<tên>" --timeline "clip-ngan/<slug>/timeline.json" --out "<slug>-<khung>"
```

Nháp tăng số mỗi vòng để không ghi đè bản người dùng đang xem; bản chính bỏ đuôi nháp.

- **Hook trước, intro sau (bắt buộc)**: hook (3-10 giây lời đắt nhất) → intro NGẮN 2,5-4 giây từ preset (hoặc bỏ hẳn intro, dồn nhận diện về outro) → thân → outro. Không dùng trường `intro`/`outro` cấp cao nhất; đưa intro, outro vào `segments` như insert thường, intro đặt sau segment hook, gắn `"role": "intro"` / `"role": "outro"` (nhạc bookends và `--kiem-tra` dựa vào `role`). Không đặt thêm một thẻ toàn màn hình dính liền intro (quy tắc 5 giây ở `_chung/overlay-va-the.md`); cần nhấn một khái niệm ngay sau hook thì dùng Benefits hiện dần theo lời.
- **LowerThird bắt buộc ngay sau intro cho mọi nhân vật xuất hiện lần đầu**, kể cả chính người dùng trong clip quảng bá: intro nói về CHƯƠNG TRÌNH, LowerThird nói về NGƯỜI; người xem lạ vào giữa clip không quay lại xem intro. Hiện khoảng 4-4,5 giây trên chính footage, neo dưới trái. `name`/`role` theo `_chung/van-hanh.md` mục "Chữ và chức danh" (không suy từ `Intro.props.subtitle`). Ghép bằng `overlay` dạng list trên cùng segment, ví dụ `[{"src": "...lowerthird.webm", "at": 0.3}, {"src": "...pill.webm", "at": 5.0}]`; mọi overlay phải chạy xong trước B-roll đầu tiên của segment đó, nên bỏ hoặc dời B-roll của segment mang cặp overlay này.
- **Phụ đề và LowerThird cùng neo gần đáy khung dọc nên chồng nhau**: dùng style phụ đề thứ hai nâng cao cho đúng khung giờ LowerThird đang hiện (số đo và mẫu: `skills/phim-clip-ngan/references/phu-de-ass.md` mục 2); kiểm bằng khung thật lúc LowerThird vừa hiện và sắp tắt.
- **Pill và phụ đề trên khung dọc**: phụ đề sát đáy, pill `position:'bottom'` + `edgeInset: 0.3`; không che mặt, kiểm ở trạng thái tích luỹ đầy đủ trên khung thật (`_chung/overlay-va-the.md`).
- **Khung dọc, cropFocus**: kiểm bằng nhiều khung thử (ffmpeg crop + scale) trước khi dựng, chụp ở khung ĐANG CỬ CHỈ TAY; tiêu chí là "người và cử chỉ còn đủ trong khung", không chỉ "mặt giữa khung"; đầu không chạm mép trên. Đoạn dài hơn khoảng một phút hoặc có người, vật khác trong khung rộng: kiểm 5-6 mốc trải khắp đoạn, ở mỗi mốc nhìn cả hai mép; chấp nhận thu hẹp qua vài vòng (ví dụ 0,68 → 0,64 → 0,60) hơn là chốt sớm.
- **Tách câu ghép để chèn thẻ ở giữa** khi silencedetect không tách được hai vế: kỹ thuật khoảng trũng năng lượng 20 ms trong `skills/phim-dung-bai/references/bien-tap.md` mục "Nhịp và điểm cắt".
- **Đồ họa dọc** từ preset `do-hoa-chung/preset-intro-outro-doc.json`; outro clip ngắn 5-6 giây một dòng lời mời, có QR thì 8-9 giây. `render-do-hoa.mjs` thoát mã 1 thì sửa job, không dùng file sai.
- **Nhạc**: `full` + duck, track và `gainDb` theo từng track trong `thu-vien/AM-THANH.md`; nhạc là lớp năng lượng nền, không lấn lời.
- **Nhịp cắt**: được phép sát hơn bài dài, bỏ mọi khoảng thở trên 0,8 giây trừ khoảng lặng có chủ đích trước câu chốt.
- Hai hệ mốc và các điểm hay nhầm khác: `_chung/timeline-va-dung.md`. assemble tự kiểm hình = tiếng từng part và thành phẩm, dừng khi KHÔNG ĐẠT: đọc bảng chẩn đoán, tìm nguyên nhân rồi mới chạy lại.

## Bước 3 - phụ đề (mặc định CÓ cho clip dọc)

Phần lớn người lướt không bật tiếng: clip dọc mặc định burn phụ đề, trừ khi người dùng từ chối.

1. Tính mốc phụ đề từ SRT gốc bằng `<clip>.map.json` (cue có `in ≤ t < out` → `start + (t - in)`), không tự cộng trừ thời lượng thẻ chèn.
2. Soát lời theo transcript thật, sửa lỗi nhận dạng và thuật ngữ, ngắt dòng tối đa khoảng 38 ký tự, 1-2 dòng mỗi cue.
3. Burn bằng file `.ass` có `PlayResX`/`PlayResY` đúng độ phân giải thật (không dùng `force_style` nhiều key); mẫu `.ass`, lệnh burn, font và cách đo MarginV: `references/phu-de-ass.md`.
4. Kiểm hai khung tại mốc có cue bằng output-seek (`-ss` sau `-i`) trước khi burn cả clip.

File đã burn là bản HOÀN CHỈNH: ghi vào `du-an/<x>/xuat-hoan-chinh/<slug>-doc.mp4`. Burn là một lượt encode mới nên phải qua cổng nghiệm thu lần nữa.

## Bước 4 - nghiệm thu

1. Cổng máy trên file CUỐI trong `xuat-hoan-chinh/`: `python3 tools/nghiem-thu.py video "<file>" --khung doc --anh` phải ĐẠT (hình = tiếng trong 0,06 giây, -14 ± 1 LUFS, true peak không quá -1 dB, 1080x1920, 30 fps, không im lặng hay hình đứng bất thường).
2. Xem khung ĐẦU TIÊN của ảnh lưới: hook đọc được ngay, không bị logo hay giao diện nền tảng che, phụ đề cách mép dưới đủ xa; thứ tự hook → intro → thân → outro đúng.
3. Phụ đề: 2-3 khung tại mốc có cue, đối chiếu lời đang nói.
4. Thời lượng đúng giới hạn nền tảng người dùng nhắm (Shorts tối đa 3 phút, Reels ưu tiên dưới 90 giây); tên file rõ `<slug>-doc.mp4`.

Báo kết quả kèm dòng "nghiệm thu máy: ĐẠT". Một bài giảng tốt thường ra 3-5 clip: sau khi người dùng duyệt clip đầu, đề nghị dựng loạt còn lại cùng format cho đồng đều.

<!-- ban-nguon: phim-clip-ngan 2026-09-30 11d333f5 -->
