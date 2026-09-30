# Phụ đề burn-in cho clip dọc (phim-clip-ngan)

Chi tiết kỹ thuật của Bước 3 trong SKILL.md: tính mốc, sinh file `.ass`, burn, kiểm, và cách tránh chồng lấn với LowerThird. Bài học gốc: `docs/BAI-HOC.md` chủ đề "Phụ đề".

## 1. Quy trình và mẫu `.ass`

Phần lớn người lướt không bật tiếng - clip dọc mặc định burn phụ đề, trừ khi user từ chối. Quy trình:

1. Tính lại mốc phụ đề từ SRT gốc bằng `<clip>.map.json` mà assemble ghi cạnh thành phẩm: với từng part `kind: "cut"`, giữ cue có `in ≤ t < out` và đặt mốc mới = `start + (t - in)`; part `insert` (thẻ, intro) không có cue nhưng đã được tính sẵn trong `start` của các part sau - không còn phải tự cộng trừ thời lượng thẻ chèn (nguồn lỗi lệch phụ đề trước đây). Cách thay thế khi map.json không có: transcript lại chính file clip đã dựng (nhanh vì ngắn)
2. Soát lời phụ đề theo transcript thật, sửa lỗi nhận dạng, ngắt dòng tối đa ~38 ký tự, 1-2 dòng mỗi phụ đề
3. Burn bằng file `.ass` sinh từ SRT (KHÔNG dùng `subtitles=...:force_style='Key1=Val1,Key2=Val2,...'` - đã xác nhận libass 0.15.2 trên VM không đáng tin khi truyền nhiều key cùng dấu phẩy, chỉ áp key đầu tiên hoặc rơi về mặc định Arial/16/MarginV=10 một cách im lặng dù không báo lỗi). Sinh `.ass` với khối `[Script Info]` đặt `PlayResX`/`PlayResY` ĐÚNG BẰNG độ phân giải thật của video xuất (vd 1080x1920 cho khung dọc - thiếu khối này libass tự giả định độ phân giải thấp ~288px chiều cao rồi nhân tỷ lệ FontSize/margin theo tỷ lệ thật/giả định, gây mập mờ khi tinh chỉnh) và khối `[V4+ Styles]` khai đủ font/cỡ chữ/màu/`MarginV`:

```
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Be Vietnam Pro,54,&H00FFFFFF,&H000000FF,&H80000000,&H00000000,1,0,0,0,100,100,0,0,1,3,0,2,60,60,110,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,<start>,<end>,Default,,0,0,0,,<text với \N cho xuống dòng>
```

rồi burn bằng `ffmpeg -i clip.mp4 -vf "ass=clip.ass:fontsdir=." -c:a copy clip-phude.mp4`. `PlayResX`/`PlayResY` đúng khiến `FontSize`/`MarginV` là pixel thật 1:1 - tinh chỉnh bằng cách đo hàng pixel thật trên frame trích ra, đừng tin so sánh bằng mắt ở ảnh thu nhỏ (chênh 60-170px trên nền phức tạp dễ bị nhìn nhầm "không đổi gì").

Lần đầu dùng trên máy: kiểm tra fontconfig thấy font Việt (`fc-list | grep -i "be vietnam"`; chưa có thì làm theo mục 3). Test một khung hình đơn lẻ tại mốc có cue PHẢI dùng output-seek (`-ss` đặt SAU `-i`), không dùng input-seek (`-ss` trước `-i` làm PTS rebase, subtitle/ass filter không khớp cue, lặng lẽ ra khung hình không chữ trông như "không hoạt động"). Xuất 2 frame kiểm tra dấu tiếng Việt hiển thị đúng trước khi burn cả clip.

File đã burn phụ đề là bản HOÀN CHỈNH cuối cùng - ghi vào `du-an/<x>/xuat-hoan-chinh/<slug>-doc.mp4` (không phải `xuat-nhap/`, nơi đó chỉ chứa bản `assemble.py` xuất thô chưa phụ đề và các bản nháp preview). Burn là một lượt encode mới nên file này phải qua cổng nghiệm thu ở Bước 4 một lần nữa.

## 2. Tránh chồng lấn phụ đề với LowerThird

**Phụ đề burn-in CHỒNG LẤN với `LowerThird` khi cả hai cùng hiện, vì cả hai đều neo gần đáy khung dọc - phải chủ động tránh, không chỉ tin bằng mắt lúc soạn:** đo trên component thật (`unit = min(W,H)/100`, khung 1080x1920 thì unit=10.8): `LowerThird` neo `bottom: unit*9` cao thêm khoảng 105px nữa (~unit*9.7), chiếm dải từ ~97px tới ~202px tính từ mép đáy; phụ đề mặc định (`MarginV:110`, cỡ chữ 54) chiếm dải ~110px tới ~175px - hai dải ĐÈ LÊN NHAU, chữ nào cũng khó đọc nếu không xử lý. Cách sửa: thêm một style phụ đề thứ hai trong cùng file `.ass` (ví dụ tên `Raised`, giữ nguyên mọi thuộc tính của `Default` chỉ tăng `MarginV` lên khoảng 230 để có khoảng đệm rõ ràng trên đỉnh `LowerThird`), chỉ áp style này cho các dòng phụ đề rơi vào đúng khung giờ `LowerThird` đang hiện (từ `overlay.at` của LowerThird tới `at + durationInSeconds`, tính theo mốc clip-time của .ass, tức là mốc trong `<thành phẩm>.map.json` chứ không phải mốc trong file nguồn) - các dòng phụ đề còn lại trong clip vẫn dùng style `Default` bình thường. Luôn trích khung hình thật ở đúng khung giờ `LowerThird` đang hiện (không chỉ tin số đo) để xác nhận bằng mắt không còn chồng lấn, cả lúc `LowerThird` mới fade-in lẫn lúc sắp fade-out.

## 3. Font tiếng Việt: một cách duy nhất

Tải `BeVietnamPro-SemiBold.ttf` (và các độ đậm cần) từ `raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro/` vào CÙNG thư mục với file `.ass` rồi burn với `fontsdir=.` chạy từ thư mục đó (hoặc `fontsdir=<đường dẫn thư mục chứa TTF>`). Kiểm trước bằng hai khung trích tại mốc có cue: chữ Việt đủ dấu, đúng font. Không có mạng thì dùng DejaVu Sans có sẵn và ghi rõ trong báo cáo.
