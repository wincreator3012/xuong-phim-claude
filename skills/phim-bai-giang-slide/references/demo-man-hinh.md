# Bài giảng có quay màn hình (demo trực tiếp): hình động, phóng vùng và giữ kín thông tin riêng tư

Đọc cùng `skills/phim-bai-giang-slide/SKILL.md`. Tài liệu này thêm những gì riêng của buổi giảng có CHIA SẺ MÀN HÌNH (live thực hành công cụ, demo phần mềm, hướng dẫn thao tác): hình động thay cho ảnh slide tĩnh, người xem cần thấy rõ vùng đang thao tác, và màn hình người giảng luôn có thể lộ thông tin họ không định cho ai xem. Rút từ một buổi live 64 phút có slide lẫn demo trực tiếp, dựng ngang 1080p (2026-10-09). Chi tiết kỹ thuật từng bài học ở `docs/BAI-HOC.md` mục 24.

## 1. Nguồn: bản ghi Zoom tách luồng

Bản ghi Zoom chọn "ghi riêng từng luồng" cho hai file: `Speakers only.mp4` (người đang nói, 1280x720) và `Screen only.mp4` (màn hình chia sẻ, thường 2560x1440). Cả hai cùng trục thời gian của phiên, nên đa số trường hợp `screenOffset` bằng 0; nghi ngờ thì đối chiếu một sự kiện thấy được ở cả hai file (chuyển slide, con trỏ bấm một nút) để đo. Chép hai file vào `nguon/` thành `mat.mp4` và `man-hinh.mp4` (chép nguyên byte, đối chiếu mã băm), kèm file slide gốc nếu có. Gỡ băng làm từ tiếng của `mat.mp4`; phụ đề giao kèm tính theo thời gian của video nguồn, không phải của phim đã cắt (ghi rõ trong mục lục giao).

Bản ghi tách luồng chỉ cho người đang nói và màn hình; người nghe không có trong hình. Nhờ vậy khung mặt sạch (không lộ gương mặt người tham dự), nhưng màn hình thì không sạch, xem mục 4.

## 2. Hai kiểu "slide" trong timeline

- Slide tĩnh (PPTX, PDF): `"layout": "ca-hai"`, `"slide": "slide/slide-NN.png"`, như SKILL.md.
- Hình động từ quay màn hình: `"layout": "ca-hai"`, `"screen": "nguon/man-hinh.mp4"` thay cho `slide` (tùy chọn `"screenOffset": giây`). Ô lớn lấy VIDEO màn hình đúng đoạn `in`..`out` của segment, ô mặt nhỏ vẫn từ `src`. Từ `assemble.py` phiên bản `2026-10-09.r9`.

Một dự án thường xen cả ba: `mat` (kể chuyện, chuyển ý), `ca-hai` slide tĩnh (khung khái niệm), `ca-hai` màn hình (demo). Quyết định theo nội dung lời nói, như SKILL.md: đang nói về thao tác thì cho màn hình, đang kể thì cho mặt.

## 3. Phóng vùng (`slideZoom`) để người xem thấy rõ

Màn hình chia sẻ nguyên khung 16:9 trong ô 73% của `ca-hai` làm chữ nhỏ đến mức khó đọc trên điện thoại, và chứa cả những vùng không liên quan tới thao tác. Mỗi segment `screen` đặt `"slideZoom": [x, y, w, h]` (tỉ lệ 0-1 của khung nguồn, khung nguồn 16:9 nên chọn `w = h` để vùng cắt vẫn 16:9) là một vùng CỐ ĐỊNH suốt segment. Vùng quan tâm đổi thì chia segment ở một điểm ngắt hơi (`snap`), không cố bám con trỏ.

Lập bảng vùng phóng đặt tên theo thứ nhìn thấy, dùng chung cả dự án (ví dụ), rồi gọi theo tên trong tập lệnh sinh timeline:

| Tên | `[x, y, w, h]` | Vùng |
|---|---|---|
| FULL | không đặt | toàn màn hình |
| CENTER | `[0.24, 0.10, 0.52, 0.52]` | giữa màn hình: nội dung chính của cửa sổ đang mở |
| TRAI | `[0.0, 0.03, 0.42, 0.42]` | góc trên trái: cột nguồn, danh sách |
| PHAI | `[0.58, 0.03, 0.42, 0.42]` | góc trên phải: bảng công cụ, kết quả sinh ra |
| HOP-THOAI | `[0.22, 0.12, 0.56, 0.56]` | hộp thoại giữa màn hình |
| DUOI-PHAI | `[0.30, 0.575, 0.425, 0.425]` | nửa dưới: phần cuối hộp thoại, nút bấm |

Bảng chỉ là điểm xuất phát đo trên một giao diện cụ thể: dự án khác phải xem khung thật rồi chỉnh vùng. Phép thử đọc được: thu khung đã phóng về 480 ngang, chữ thao tác vẫn đọc được thì đủ; chưa đọc được thì phóng sâu hơn (w nhỏ hơn).

Phóng vùng làm HAI việc cùng lúc: tăng độ rõ và che thông tin nằm ngoài vùng. Việc thứ hai là hệ quả nên không được dùng làm lý do duy nhất để tin một vùng an toàn (mục 4).

## 4. Rà thông tin riêng tư trên màn hình (bắt buộc, trước khi dựng và sau khi dựng)

Màn hình người giảng thường lộ: địa chỉ email và tên tài khoản (thanh góc, hộp thoại chia sẻ, bộ chọn tệp), tên khách hàng hay dự án trong danh sách thư viện hay danh mục, danh sách dự án của chính công cụ AI, thanh dấu trang và tab trình duyệt, thông báo nổi ở góc, trang khởi động có lối tắt cá nhân. Quy trình:

1. **Quét toàn bộ quãng có màn hình.** Với mỗi quãng demo, tạo bảng ảnh khung (contact sheet) mỗi 3-5 giây trên video màn hình gốc: `FILE=<video> SW=640 bash tools/xem-khung.sh <tên> <số cột> t1 t2 ...` (đầu ra mặc định `Du an/_tam/xem-khung/`, nhìn bằng stage rồi Read). Cả những khung chuyển trang, khung tải xong, khung hộp thoại vừa mở.
2. **Lập danh sách quãng nhạy cảm** (mốc từ đến, loại thông tin, vị trí trên khung). Ghi vào hồ sơ dự án.
3. **Chọn cách che theo từng quãng**, theo thứ tự ưu tiên:
   - Vùng phóng dời để thông tin nằm NGOÀI vùng suốt quãng (ví dụ hộp thoại chia sẻ có hàng tài khoản ở nửa trên: phóng nửa dưới, nơi chỉ có nút bấm). Kiểm CẢ HAI MÉP vùng cắt tại nhiều mốc trong quãng vì cửa sổ có thể trượt hay danh sách có thể cuộn.
   - Không có vùng nào an toàn thì đổi cả quãng sang `mat` (mặt toàn khung) và để lời nói mang nội dung, hoặc đổi sang một trang khác của cùng thao tác. Danh sách tên khách hàng, danh sách dự án luôn thuộc nhóm này.
   - Trang khởi động của trình duyệt (lối tắt, tab) thì bỏ qua bằng `mat` hay cắt bớt.
4. **Biên cắt chỉ được dịch theo hướng mở rộng đoạn an toàn** (`mat`), không bao giờ nới đoạn có màn hình sang quãng nhạy cảm sát bên cạnh. Điểm ngắt hơi cắt gần thì dành 0,3-0,5 giây dư cho phía `mat`.
5. **Rà lại trên phim đã dựng**, không chỉ trên nguồn: trích khung tại MỌI mốc biên của đoạn màn hình và vài mốc giữa đoạn, nhìn từng khung (kể cả thông báo nổi ở góc có thể rơi vào vùng phóng).
6. **Ghi cho người dùng trong `ghi_chu_kiem`** những quãng đã che và cách che, những khung có người khác (trẻ em ngồi cạnh, người đi ngang) và tên riêng nhạy cảm trong lời nói, để người dùng quyết định cuối trước khi đăng. Không khẳng định "đã sạch hoàn toàn" khi mới rà bằng mắt; viết "đã rà các mốc sau, không thấy: ...".

Việc che luôn đi cùng quy tắc cứng "không lớp phủ nào che mặt ai" của skill dựng bài: pill, thẻ khái niệm đặt ở dải dưới trống của `ca-hai`, không đè lên vùng người giảng đang chỉ.

## 5. Nhịp và cắt trong demo

- Cắt quãng chờ (tải, sinh nội dung) 5-7 giây bằng cách kết thúc đoạn ở khoảng lặng ngay trước và vào đoạn kế ở khoảng lặng ngay sau; không giữ cảnh màn hình đứng im.
- Nhãn khái niệm (pill) đặt ở lúc người giảng xướng tên bước hay khái niệm, theo từ neo trong transcript; ước lượng số trong pill (ví dụ số công cụ) phải khớp lời nói và ghi vào `ghi_chu_kiem`.
- Sau quãng demo dài quay về `mat` để người xem thở và nghe chuyển ý.

## 6. Dựng phim dài trên máy ảo

Phim từ khoảng 30 phút, nhất là có hàng trăm part `ca-hai`, không chạy trọn một lượt `assemble.py` được trên máy có giới hạn khoảng 120 giây mỗi lệnh. Dùng `tools/dung-dai.py` (xem `skills/phim-dung-bai/SKILL.md` Bước 6): `song-song` (lặp đến khi in `XONG-SONG-SONG`), `ghep`, `tron`, `mux-a`, `mux-b`. Giữ nguyên MỘT cách viết đường dẫn dự án (tuyệt đối) trong mọi lệnh, vì chữ ký part chứa đường dẫn. Đổi từ nháp sang bản chính là encode lại toàn bộ part: chốt thông số rồi mới bấm.

## 7. Thumbnail từ khung rộng có slide hay màn hình

Khung rộng zoom out (người nói nhỏ, slide hay màn hình rõ phía sau) là ứng viên tốt cho thumbnail về khái niệm, nhưng bố cục `toan-anh` bị gradient phủ che mất slide; dùng `chia-doi` kèm `focusX`, `focusY`, `faceScale` đặt tay trong `chinh_anh` để mặt và slide cùng rõ. Tiêu đề trên slide bị cắt giữa chữ ở mép ô thì vẽ lại ô tiêu đề bằng màu thẻ hoặc chọn khung khác; luôn soát ảnh `soi-thumbnail.jpg` ở cỡ nhỏ.

## 8. Danh sách kiểm trước khi báo xong

1. Mọi quãng có màn hình đã quét khung (mục 4), danh sách quãng nhạy cảm đã ghi, mỗi quãng một cách che đã chọn.
2. Khung phim đã dựng tại mọi mốc biên và vài mốc giữa đoạn không còn email, tên tài khoản, tên khách hàng hay dự án, danh sách riêng, thông báo nổi.
3. Chữ thao tác đọc được ở 480 ngang; mỗi vùng phóng cố định trong segment, đổi vùng chỉ ở điểm ngắt hơi.
4. Không lớp phủ nào che mặt ai; không `mat-chinh` khi khung có người phía sau.
5. Cổng `tools/nghiem-thu.py video` ĐẠT; quãng `ca-hai` màn hình tĩnh có thể bị báo "hình đứng" (dương tính giả, đối chiếu `map.json`).
6. `ghi_chu_kiem` ghi quãng đã che, khung có người khác, tên riêng nhạy cảm, cú nối đáng nghe lại.
