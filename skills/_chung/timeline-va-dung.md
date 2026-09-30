# Timeline và dựng: những điều mọi skill dùng chung

Schema đầy đủ của `timeline.json` nằm trong docstring đầu `tools/assemble.py`. File này gom những điểm hay nhầm.

## Hai hệ mốc thời gian

- `in`, `out`, `broll[].at` là mốc TRONG FILE NGUỒN.
- `overlay[].at` là giây TƯƠNG ĐỐI từ đầu đoạn (sau snap); `revealAt` bên trong props của Benefits dùng cùng mốc 0 đó.
- Overlay muốn hiện lúc lời nói ở mốc nguồn T: `at = T - in`. B-roll muốn vào sau đầu đoạn s giây: `at = in + s` (đặt `at` nhỏ hơn `in` thì B-roll bật ngay đầu đoạn).
- `overlay` nhận một dict hoặc một list nhiều lớp không chồng khoảng hiển thị; overlay chỉ phủ tới B-roll đầu tiên của đoạn. Overlay cần hiện SAU một B-roll trong cùng đoạn: tách đoạn thành hai sub-segment liền mạch (`out` đoạn trước = `in` đoạn sau) tại điểm B-roll kết thúc.
- Mốc overlay đồng bộ lời nói: neo theo tỷ lệ ký tự trong câu Whisper (`frac = vị trí ký tự / độ dài câu`, mốc = `start + frac * (end - start)`), không cộng dồn thời lượng danh nghĩa. Kỹ thuật và bẫy: `skills/phim-dung-bai/references/bien-tap.md` mục "Xác định mốc `at` cho overlay".
- Chạy `assemble.py --kiem-tra` trước khi dựng: bắt file thiếu, mốc vượt nguồn, nhầm hai hệ mốc, B-roll chồng nhau.

## Tên file xuất

- Luôn truyền `--out` tường minh: nháp `<tên>-<khung>-nhapN` (tăng N mỗi vòng, kể cả nháp đầu), bản chính `<tên>-<khung>`. Để tên mặc định từng làm nháp sau ghi đè nháp trước.
- assemble ghi vào `du-an/<x>/xuat-nhap/`; bản đạt nghiệm thu (clip dọc: bản đã burn phụ đề) copy sang `xuat-hoan-chinh/`.
- Gọi lặp y nguyên lệnh (cùng `--out`) khi một lượt bị ngắt; part đã đúng tự bỏ qua.

## Dự án con (clip ngắn cắt từ một dự án)

`--project` trỏ DỰ ÁN GỐC (để dùng chung `transcript/`, `.tam/`), `--timeline "clip-ngan/<slug>/timeline.json"`, `--out "<slug>-<khung>[-nhapN]"`. Đồ họa riêng đặt trong `clip-ngan/<slug>/do-hoa/`, đường dẫn trong timeline tương đối so với dự án gốc.

## Hook trước intro, intro và outro

- Câu mở đã là câu chốt mạnh thì hook đứng trước, intro sau; clip ngắn không bao giờ mở bằng intro.
- Intro đặt trong `segments` là một `insert` mang `"role": "intro"`; outro chèn giữa danh sách mang `"role": "outro"`. Nhạc `bookends` bám theo `intro`/`outro` cấp cao nhất hoặc các insert có role; timeline `bookends` không có intro, outro nào thì assemble báo lỗi.
- Intro, outro luôn từ preset `do-hoa-chung/preset-intro-outro-<ngang|doc>.json`; không dùng kicker thì đặt `"subtitle": ""` tường minh.
- Đồ họa chèn có đuôi tiếng AAC thừa 0,02-0,06 giây: assemble tự cắt về bằng hình và in một dòng thông báo. Không strip `-an`, không ép `-t` bằng tay.
- Giữa hai thẻ toàn màn hình liên tiếp có ít nhất 5 giây cảnh quay chính (xem `skills/_chung/overlay-va-the.md`).

## Điểm cắt, fade, kết

- Điểm cắt hút về khoảng lặng thật (`snap: true`); đọc log `đoạn N: ... [X → Y]` sau khi dựng để biết mốc thật đã dùng. Vùng có tạp âm nền không phải chỗ đặt mối nối: gộp thành một đoạn liên tục, dùng overlay nếu cần.
- Cắt giữa câu không có khoảng lặng rõ: `silencedetect` ngưỡng nhạy trên cửa sổ 3-4 giây quanh điểm nghi (chưa thấy thì nới tới 6 giây), hoặc tìm khoảng trũng năng lượng 20 ms trên 4-6 giây; neo vào đó và đặt `snap:false` cho đoạn ấy.
- Giữa các câu nói không fade. Đoạn nội dung cuối (trước outro) đặt `fadeOut` 0,4-0,6 giây; chỉ muốn tiếng tắt dần mà hình cắt thẳng thì dùng `fadeOutAudio` (đặt cả hai thì `fadeOut` thắng).
- Phim kết bằng thẻ tĩnh (outro không chuyển động): mờ dần CẢ hình lẫn tiếng khoảng 1,5 giây; chỉ mờ tiếng vẫn thấy đột ngột.

## Nhạc và tiếng nền

- Track và `gainDb` theo từng track, từng chế độ (full khác bookends) trong `thu-vien/AM-THANH.md`; không dùng một khoảng cố định chung.
- Bài giảng: `bookends`. Clip quảng bá, highlight: `full` + `duck` (sidechain, gainDb full có thể cao hơn trực giác); người dùng muốn nhạc êm không dập dồn thì `"duck": false`.
- Không để nhạc nghe rõ giai điệu hơn lời. Track Kevin MacLeod kèm dòng ghi công CC-BY trong mô tả video.
- Tiếng nền cảnh thật (`volumeDb`): khoảng -12 là điểm khởi đầu, nghe lại từng dự án rồi hạ hay nâng.

## Sau khi dựng: dùng `map.json`

`<thành phẩm>.map.json` ghi mốc thật từng part trên thành phẩm. Mọi mốc suy ra (phụ đề, chương YouTube bằng `tools/chuong-youtube.py`, nhãn đoạn bằng `tools/nhan-doan.py`, mốc trích khung nghiệm thu) tính từ đây: cue có `in ≤ t < out` thì mốc mới `start + (t - in)`; mốc tuyệt đối của một overlay = `part.start + overlay.at`. Không cộng trừ tay.
