# Nghiệm thu đúng ý: sau cổng máy

Cổng máy (`tools/nghiem-thu.py`, `check_av()` trong assemble, `render-do-hoa.mjs` tự đo) kiểm thuộc tính kỹ thuật: hình = tiếng, thời lượng, LUFS, true peak, khung, im lặng, hình đứng. Chưa ĐẠT thì không giao, không nói "xong". Nhưng cổng máy KHÔNG đọc chữ trên hình và không biết hình có khớp ý câu đang nói; phần đó là việc của lớp soi mắt dưới đây, chạy SAU cổng máy, không thay cổng máy.

## Lệnh cổng máy

- Thành phẩm: `python3 tools/nghiem-thu.py video "<file.mp4>" --khung ngang|doc [--nhap] --anh` (ra kèm ảnh lưới `<file>.luoi.jpg`).
- Transcript: `python3 tools/nghiem-thu.py transcript "du-an/<x>" [--nguon <tên file>]`.
- Đồ họa đã render: `python3 tools/nghiem-thu.py do-hoa "du-an/<x>/do-hoa"`.
- Giấy (kịch bản infomotion, phim tài liệu): `python3 tools/uoc-luong.py "<kịch bản>"`.

## Năm việc soi mắt

1. **Cặp "hình - câu đang nói".** Với MỖI overlay hay đồ họa đồng bộ lời nói: tính mốc tuyệt đối từ `<thành phẩm>.map.json` (`part.start + overlay.at`), trích khung tại mốc đó cộng 0,7-1 giây (độ trễ hiện dần), đọc lại câu transcript bao quanh, ghi cặp vào báo cáo. Hình đúng chính tả mà sai ý câu là lỗi.
2. **Contact sheet cho chuỗi dài.** Đoạn nhiều overlay nối tiếp: trích một khung mỗi 2 giây xuyên suốt đoạn bằng một lệnh ffmpeg (`-vf fps=0.5,scale=480:-1`), ghép thành một ảnh lưới có nhãn thời gian (PIL), đọc một lần. Thấy được thứ tự, chồng lấn, thiếu, khoảng hở trong một lần nhìn. Lịch nối liền [gapless]: mốc kết thúc của khối trước bằng mốc bắt đầu khối sau (chênh dưới 0,01 giây là làm tròn).
3. **Trạng thái chật nhất trên khung thật.** Benefits tích luỹ kiểm ở khung cuối của chuỗi; khung có cả pill, LowerThird, phụ đề kiểm tại đúng lúc chồng lấn; cropFocus kiểm 5-6 mốc trải khắp đoạn dài, ở mỗi mốc nhìn cả hai mép, chọn khung đang khoát tay. Đồ họa nổi toàn khung kiểm trên đúng tỉ lệ khung đích (lỗi cỡ nhỏ không lộ qua still riêng lẻ).
4. **Chữ trên hình.** Sau mỗi lần sửa chữ: trích khung giữa đoạn đồ họa, xem đủ dấu, không tràn, không lộ placeholder.
5. **Xem như người xem lần đầu.** Trước khi giao nháp, đi lại toàn phim bằng lưới khung hình và vài quãng nghe thử với câu hỏi của người xem: 3 giây đầu có giữ được không; chỗ nào dồn quá, thưa quá, lặp khuôn; chữ có kịp đọc không; chuyển cảnh có làm lạc không; kết có để lại điều gì không. Ghi những chỗ Claude tự thấy chưa ổn vào báo cáo nháp, kể cả khi cổng máy đã ĐẠT.

## Mẹo kỹ thuật khi trích khung

- `-ss` đặt SAU `-i` (output-seek) khi cần PTS khớp phụ đề hay overlay; đặt trước làm tưởng phụ đề không hiện.
- Webm alpha tự ghép thử: `-c:v libvpx` (vp9: `-c:v libvpx-vp9`) ngay trước `-i`, nếu không ra nền đen đục.
- Không xem được ảnh: đọc màu một điểm ảnh góc khung (nền kem `#FAF7F1` khác cảnh quay) hoặc tìm "cao nguyên" độ lệch so với một khung tham chiếu chắc chắn chưa có overlay.
- File do một tiến trình từng bị timeout tạo ra: `ffprobe` thời lượng trước khi tin.
- Ảnh kiểm tra để trong thư mục nhà của VM hoặc sandbox, không để trong thư mục dự án.

## Khi đã sửa nhiều vòng vẫn bị chê lệch

Qua 2-3 vòng suy luận từ transcript mà người dùng vẫn thấy sai vị trí: nhờ người dùng ghi mốc phút giây trực tiếp trên bản render cho từng điểm, dùng mốc đó (lệch 1-3 giây do hiệu ứng hiện dần là tự nhiên). Chi tiết: `skills/phim-dung-bai/references/bien-tap.md` mục "Khi đã sửa nhiều vòng vẫn bị chê".
