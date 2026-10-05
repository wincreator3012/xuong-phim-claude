# Clip giảng trên sân khấu: keynote, talk, buổi nói chuyện có khán giả tại chỗ

Đọc cùng `skills/phim-dung-bai/SKILL.md` và `skills/phim-bai-giang-slide/SKILL.md`. Tài liệu này chỉ thêm những gì riêng của clip quay ở một sự kiện thật: khán giả nằm trong khung, nguồn quay dài và nặng, slide có sẵn file, người xem YouTube không ngồi trong phòng. Rút từ một keynote 40 phút có slide, quay 4K, dựng ngang 1080p và đăng YouTube (2026-10-04). Chi tiết kỹ thuật từng bài học nằm ở `docs/BAI-HOC.md`; ở đây là thứ tự làm việc và những chỗ dễ sai.

## 1. Người xem YouTube khác người ngồi trong phòng

Người xem không có tài liệu trên bàn, không nghe MC nhắc việc, không thấy phản ứng của cả phòng. Vì vậy, ở bảng phương án cắt, chủ động đề xuất bỏ:

- phần hành chính chỉ có nghĩa tại chỗ: gửi slide qua nhóm chat, nhắc việc, kiểm âm, MC giới thiệu quá dài;
- phần hướng dẫn khán phòng thực hành với công cụ ngay tại chỗ (đưa slide lên AI, quét mã), trừ khi đó chính là nội dung của clip;
- bài tập tương tác giữa phòng khi người xem ở nhà không làm được.

Clip bắt đầu ở chỗ nội dung thật sự mở ra và kết ở câu chốt tự nhiên. Mốc vào và ra do người dùng chốt thắng mọi đề xuất: ghi đúng mốc đó vào bảng, cắt đúng chỗ, kể cả cắt giữa một file nguồn. Câu mở mạnh thì dùng hook trước intro; bảng tên người nói đặt ở lần đầu họ lên hình.

## 2. Nguồn quay thô của một sự kiện

Thường gặp bốn loại nguồn, mỗi loại một cách xử lý:

- **Góc chính 4K** quay cả sân khấu lẫn màn chiếu, hay bị máy chia thành nhiều file liền nhau. Coi các file là một trục thời gian, đo và ghi offset từng file, không dựng từng file như một clip riêng.
- **Tiếng chính từ bàn mix** tốt hơn tiếng mic máy. Đồng bộ với hình bằng đối chiếu âm thanh (`tools/multicam-khop.py`) hoặc offset đã đo, rồi kiểm bằng `tools/do-dong-bo.py` ở nghiệm thu.
- **B-roll** quay cầm tay hoặc flycam, thường không có tiếng. Chọn theo nội dung lời đang nói, ghi `from` và `duration` đúng; tiếng vẫn là tiếng chính liền mạch, không đổi.
- **File slide** (PPTX hay PDF) không kèm quay màn hình: nhập bằng `tools/slide-nguon.py`, khớp lời bằng `tools/slide-khop.py`, rồi người đọc lại bảng `slide/DAN-HINH.md`.

HEVC 4K giải mã rất chậm trong máy ảo (khoảng 2,7 giây CPU cho mỗi giây hình). Làm proxy 1080p 30 khung/giây trên Mac thật (`tools/proxy-mac.py`, xếp hàng bằng `tools/hang-doi-go-bang.py`), mọi bước phân tích và dựng chạy trên proxy; mốc `in`, `out` bám trục gốc nên không đổi. Khung dùng cho thumbnail thì cắt từ file 4K gốc để giữ độ nét. Gỡ băng bằng large-v3 trên Mac cho nguồn dài, rồi chạy `tools/nghiem-thu.py transcript`.

## 3. Hình: mặt, slide hay cả hai

- Có file slide thì `ca-hai` là mặc định: slide ở khung riêng, mặt người nói ở ô 4:5 góc dưới. Người nói đi lại trên sân khấu nên ô mặt phải bám theo họ: dò mặt (YuNet) rồi bám bằng một track riêng, và kiểm nhiều mốc trải khắp từng đoạn, nhìn cả hai mép. Trong keynote mẫu khoảng 84% thời lượng là `ca-hai`, 16% là `mat`.
- `mat` (mặt toàn khung) khi kể chuyện, chuyển ý, kết, hoặc người nói đang chỉ vào cái gì đó ngoài slide.
- **Không dùng `mat-chinh` (thẻ slide chồng góc trên phải) trong khung có khán phòng hay người ở phía sau người nói:** thẻ đè lên mặt họ. Xem mục 4.
- Slide chỉ lướt qua hay ít được nhắc (ví dụ danh sách đội hình ở cuối bài) thì không hiện; người xem không cần thấy thứ người nói cũng không bàn.
- Người nói chỉ vào một phần của slide dày thì dùng `slideZoom`.

## 4. Lớp phủ không bao giờ che mặt ai

Đây là lỗi người dùng chê thẳng ("rất là kỳ") và đã xảy ra ba lần trong một nháp đầu. Quy tắc cứng: **không lớp phủ nào (slide thẻ, pill, bảng tên, thẻ chữ) được che mặt BẤT KỲ AI trong khung**: người nói chính, người ngồi hoặc đứng phía sau, người đang được gửi hình lên slide, người đang nghe.

- Chọn kiểu hiện không chồng lên cảnh quay: `ca-hai`, `mat`, hoặc overlay ở vùng khung trống. Có người ở nền thì thà bỏ lớp phủ còn hơn đánh đổi.
- Nghiệm thu: trích khung thật tại MỌI mốc có lớp phủ (keynote mẫu có 29 mốc) và nhìn từng khung, cả hai mép trên; không chỉ vài mốc đại diện, không chỉ khung đầu của chuỗi tích luỹ.
- Có nghi ngờ thì đo bằng mắt chứ không đoán theo vị trí đã đặt: người ở nền thường nằm đúng chỗ pill hay thẻ góc quen đặt.

## 5. Người thứ hai trong clip (khách, người trả lời, MC)

- Chức danh nguyên văn do người dùng cung cấp (ví dụ vai trò hiện tại cộng tư cách học viên của chương trình); chưa rõ thì ghi chức danh tạm vào phần giả định và hỏi ở chốt duyệt. Người dùng sửa chức danh sau nháp thì sửa MỌI nơi: bảng tên trên hình, mô tả YouTube, status Facebook, `dang-tai.json`.
- Bảng tên người dẫn chỉ đặt ở lần đầu họ thật sự lên hình; nếu họ chỉ xuất hiện ở đoạn hook thì đặt ở đó.
- Không đưa tên người thứ ba (người được nhắc tên trong lời nói) lên chữ đăng tải; ghi vào `ghi_chu_kiem`.

## 6. Clip dài trên máy ảo

Clip hơn 35 phút với hàng trăm đoạn `ca-hai` dễ chạm giới hạn gọi lệnh (khoảng 120 giây mỗi lần, tiến trình nền bị giết khi lệnh kết thúc). Cách đã chạy được, chi tiết ở `docs/BAI-HOC.md` mục 13:

- cắt đoạn `ca-hai` thành các part khoảng 13 giây, mã hoá 4 worker song song, chia việc theo ngân sách thời gian, mọi bước resume được;
- nướng sẵn (bake) khung nền và slide thành một ảnh, chỉ overlay ô mặt: nhanh gấp khoảng 3 lần, hình tương đương;
- ghép cuối làm từng chặng nhỏ có đánh dấu hoàn thành;
- **chốt thông số âm thanh (âm lượng, đỉnh tiếng) trước khi bấm bản chính:** sau finalize các part bị truncate, nên đổi bất kỳ tham số nào là mã hoá lại từ đầu;
- không dùng `pkill -f ffmpeg` (giết luôn shell của chính mình).

## 7. Chương, tiêu đề, thumbnail

- Chương lấy từ công cụ (`tools/chuong-youtube.py` hoặc `.chapters.txt` của assemble), không gõ tay; mỗi chương tối thiểu 10 giây, chương mở đầu quá ngắn thì gộp vào chương kế.
- Tiêu đề YouTube mở bằng khái niệm hay ý chính mà người xem hiểu ngay và có thể đang tìm; ẩn dụ hay hình ảnh thơ ("vé lên tàu") chỉ làm câu phụ, không làm câu chủ. Tên khái niệm lấy từ chính slide hay lời người nói.
- Thumbnail xen kẽ: ít nhất một cận mặt (mặt khoảng 30-34% chiều cao ô) và ít nhất một khung rộng zoom out (khoảng 13-16%) có chính slide của khái niệm ở phía sau người giảng. Chữ trên thumbnail khớp thứ nhìn thấy trong ảnh. Tìm khung rộng bằng `tools/quet-mat-theo-giay.py` trên file gốc; chi tiết ở `skills/phim-dang-tai/SKILL.md` mục 3.

## 8. Danh sách kiểm trước khi báo xong

1. Điểm vào và ra đúng mốc người dùng chốt; phần chỉ có nghĩa tại chỗ đã bỏ.
2. Không lớp phủ nào che mặt ai, đã nhìn khung tại từng mốc.
3. `mat-chinh` không xuất hiện ở khung có người phía sau.
4. Chức danh mọi người nguyên văn, nhất quán ở hình, mô tả, status.
5. Chương đạt luật 10 giây, lấy từ công cụ.
6. Thông số âm thanh chốt trước bản chính; `tools/nghiem-thu.py video` ĐẠT; ảnh lưới đã xem.
7. Gói đăng tải: ba thumbnail có cận mặt và khung rộng, tiêu đề mở bằng khái niệm, `tools/dang-tai.py kiem` ĐẠT.
