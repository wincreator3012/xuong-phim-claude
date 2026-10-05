# Overlay, pill và thẻ: quy tắc chung

## Chọn kỹ thuật: overlay, B-roll hay thẻ toàn màn hình

- Hỏi trước: đoạn này có phải cắt cảnh không, hay chỉ cần một lớp chữ đè lên. Lời cần liền mạch thì dùng `overlay` (một lần encode, không có mối nối). `broll` chỉ khi phải đổi hẳn sang cảnh quay khác. Thẻ toàn màn hình (`insert`) chỉ ở ranh giới chuyển phần thật.
- Đoạn giải thích cần một sơ đồ động vẽ riêng: cảnh minh hoạ (skill phim-canh-minh-hoa) với bốn kiểu chèn. Thẻ nổi cạnh người nói là `overlay` (theo mọi quy tắc không che mặt dưới đây); toàn khung, nền là khung hình mờ và người nói thu vào góc là `broll` với `at` theo mốc nguồn.
- Chủ động rà transcript và đề xuất overlay cùng phương án cắt cho ba loại nội dung: tên chương trình, chuyên đề hay framework; các bước hay cấu phần; key message.
- Thời lượng hiện overlay theo nội dung: lớn hơn giữa thời gian người nói bàn về ý đó và thời gian đọc chữ, cộng 1-2 giây.

## Không che mặt, kiểm ở trạng thái tích luỹ

- Thứ tự ưu tiên cho mọi chữ, pill, đồ họa đè lên hình người nói: (1) không che cả người lẫn mặt nếu tránh được; (2) buộc đánh đổi thì tuyệt đối không che mặt, chấp nhận che một phần thân. "Mặt" là mặt BẤT KỲ AI trong khung: người nói chính, người ngồi hoặc đứng phía sau (khán phòng, sân khấu), người đang được gửi hình lên slide. Khung có người ở nền thì không dùng kiểu thẻ chồng lên cảnh quay (ví dụ `mat-chinh`); chọn `ca-hai`, `mat` hoặc vùng khung trống, hay bỏ hẳn lớp phủ ít quan trọng.
- Benefits nhiều mục tích luỹ thành một khối lớn dần (mục cũ thu nhỏ, không biến mất): kiểm ở khung CUỐI của chuỗi, chồng lên khung hình THẬT của nguồn, không phải nền màu đặc.
- Trước khi chọn vị trí, trích một khung ở đúng đoạn sẽ overlay để xem người nói nằm đâu.
- Nghiệm thu: trích khung thật tại MỌI mốc có lớp phủ và nhìn từng khung, cả hai mép trên, không chỉ vài mốc đại diện (clip sân khấu 40 phút có 29 mốc).

## Vị trí pill Benefits theo thể loại

Mặc định của component là `position:'bottom'`. Chọn theo khung hình thật:

| Tình huống | Vị trí | Lý do |
|---|---|---|
| Phỏng vấn ngồi, mặt ở nửa trên khung | `bottom` | pill ở trên hay che đầu (lỗi lặp ba lần ở một phim tài liệu phỏng vấn) |
| Người nói giữa khung, còn trống hai bên; hoặc clip dài có nhiều pill dồn dập | `left` / `right` (cột dọc bám cạnh), list dài chia hai cột xen kẽ mục | `bottom` dễ bị hiểu là phụ đề; `top` với 3-4 mục dễ xuống hai hàng đè mặt |
| Khung dọc có cả pill lẫn phụ đề burn-in | phụ đề sát đáy, pill `bottom` + `edgeInset: 0.3` | không chồng phụ đề, không che mặt |
| Cần cả LowerThird lẫn pill cùng lúc | LowerThird dưới trái; pill nhích lên bằng `edgeInset` hoặc sang `right` | hai lớp không đè nhau; kiểm tại đúng lúc chồng lấn |
| Infomotion, hoạt hình (không có người trong khung) | đồ họa nổi canh giữa (mặc định của YNiem, YCanh), lấp phần lớn khung, giàu chi tiết; khi dựng clip hỏi người dùng có muốn đổi vị trí không | toàn khung là canvas |

Cỡ chữ nhãn khoảng `unit*4.5` (dọc), `unit*4.0` (ngang); `scale` 1,1-1,15 khi cần to hơn cả khối. Framework nhiều bước: đề xuất thêm một overlay tổng kết đặt đúng lúc người nói tự tổng kết.

## Quy tắc 5 giây giữa hai thẻ toàn màn hình

- Giữa hai thẻ toàn màn hình liên tiếp có ít nhất 5 giây cảnh quay chính (thấy người nói). Một lần lộ mặt ngắn dưới 5 giây xen giữa hai B-roll cũng tính: nối liền B-roll thay vì giữ khe.
- Cần nhấn thêm khi chưa đủ 5 giây: đổi sang overlay bán trong suốt (Benefits một mục), overlay không tính vào quy tắc này.
- Clip ngắn: hook bằng lời rồi intro ngắn; không đặt thẻ mở InfoQuote dính liền intro.
- Không áp cho infomotion: không có mặt người để định hướng lại; hai đồ họa toàn khung liên tiếp chuyển liền mạch trên cùng màu nền.

## Ba lớp đồ họa không thay nhau

1. **LowerThird** (thẻ nhận diện, thông tin về NGƯỜI): tên và chức danh, neo dưới trái, hiện vài giây khi một người xuất hiện lần đầu hoặc quay lại sau một khoảng dài; không tích luỹ. Bắt buộc cho mọi nhân vật xuất hiện lần đầu, kể cả chính người dẫn trong clip quảng bá; đặt ngay sau intro (intro nói về chương trình, LowerThird nói về người). Chức danh theo `skills/_chung/van-hanh.md` mục "Chữ và chức danh".
2. **Benefits** (pill nhấn mạnh, thông tin về Ý): từ khoá, con số, danh sách cấu phần đúng lúc lời nhắc tới; danh sách cấu phần là MỘT overlay tích luỹ. Một mục `showIndex:false`, `wrap:true` là một dòng chữ nổi (câu hook, câu hỏi neo, câu kết chiêm nghiệm đè lên cảnh thật). Studio KHÔNG có composition `Caption`.
3. **SectionTitle** (thẻ chuyển, ranh giới HỒI hay phần lớn, không phải ranh giới người nói): `kicker` là tên dự án hay chương trình viết hoa lặp xuyên suốt, `title` là tên hồi hoặc câu hỏi định hướng (mảng dòng để tự quyết điểm xuống dòng), `showLogos:true` ở ranh giới lớn.

## Chữ trên thẻ

- Theo `phong-cach/PHONG-CACH.md` mục 4. Chữ đè hình là cụm nhấn, không chép lại lời đang nói; giữ đúng thuật ngữ người dùng hay dùng.
- Tiêu đề dài: tách sang `description`, `creditLines` của Intro; điểm xuống dòng kiểm soát bằng mảng dòng + `nowrap`, không đoán bằng `\n` hay giảm cỡ chữ.
- Prop có giá trị mặc định kiểu placeholder (ví dụ `subtitle` của Intro là "Tên chuỗi chương trình"): không dùng thì đặt tường minh `""`, không chỉ bỏ trống key.
- Sau mỗi lần sửa chữ trên đồ họa, trích khung tại đúng mốc và xem bằng mắt: cổng máy không đọc chữ.
