# BẮT ĐẦU: cài xưởng lần đầu, từng bước

Tài liệu này dành cho người chưa từng dùng AI làm việc với file trên máy. Đọc hết một lần mất khoảng 10 phút; làm theo mất khoảng 30-45 phút, trong đó phần lớn là ngồi chờ máy tải và trả lời vài câu hỏi. Bạn không phải gõ lệnh nào.

## Trước khi bắt đầu, bạn cần

- **App Claude trên máy tính** (tải từ claude.ai/download) đã đăng nhập, và gói có **Cowork**. Cowork là chế độ để Claude làm việc trực tiếp với thư mục trên máy bạn
- **Máy Mac** với chip Apple Silicon (M1 trở lên) là lựa chọn chạy êm nhất. Windows và Linux dùng được nếu app Claude hỗ trợ Cowork trên máy đó
- **Khoảng 3 GB trống** trên ổ đĩa: 1 GB cho bộ nhận dạng giọng nói, phần còn lại cho thư viện và bản dựng
- **Mạng ổn định** trong lúc cài (tải khoảng 700 MB). Sau khi cài, gỡ băng và dựng clip chạy offline
- **30-45 phút** không bị ngắt, và một video ngắn bạn tự quay (1-3 phút, nói trước máy) để làm clip thử nếu muốn

Nếu bạn dùng hai máy (ví dụ laptop mang đi và máy bàn ở nhà), đặt thư mục xưởng vào nơi đồng bộ (iCloud Drive, Dropbox, OneDrive) là dùng chung được; xem lưu ý cuối tài liệu.

## Bước 1: tải xưởng về máy

Trên trang GitHub của repo, bấm nút xanh **Code**, chọn **Download ZIP**. Giải nén (bấm đúp file ZIP trên Mac). Bạn có một thư mục tên `xuong-phim-claude-main` hoặc tương tự; đổi tên thành gì dễ nhớ, ví dụ `Xuong phim`, và kéo vào **Documents** (hoặc bất kỳ chỗ nào bạn hay để tài liệu).

Nếu bạn quen dùng Terminal: `git clone <địa chỉ repo>` cho kết quả tương tự và sau này cập nhật dễ hơn.

Bên trong thư mục có sẵn mọi thứ Claude cần, trừ ba thứ sẽ tải lúc cài: bộ nhận dạng giọng nói, thư viện Python, và nhạc.

## Bước 2: mở Cowork và thêm thư mục

Mở app Claude, chọn **Cowork** và bắt đầu một phiên làm việc mới. Tìm nút **Add folder** (thêm thư mục) và chọn thư mục xưởng vừa giải nén. Từ lúc này Claude đọc và ghi được trong thư mục đó, và chỉ thư mục đó.

Lần đầu, hệ điều hành có thể hỏi quyền truy cập thư mục; bấm cho phép.

## Bước 3: nói câu đầu tiên

Gõ vào khung chat:

> Đọc file CLAUDE.md trong thư mục này rồi thiết lập xưởng phim cho tôi.

Claude sẽ đọc hướng dẫn bên trong thư mục và bắt đầu thiết lập. Chuyện gì sẽ xảy ra, theo thứ tự:

**Cài môi trường (10-20 phút, bạn chỉ chờ).** Claude chạy một lệnh cài đặt tự động: kiểm công cụ có sẵn, cài thư viện, tải bộ nhận dạng giọng nói (khoảng 560 MB, tải nối tiếp nhiều lần, Claude sẽ báo tiến độ), rồi dựng thử một clip giả nhỏ để chắc mọi thứ chạy đúng trên máy bạn. Bạn sẽ thấy dòng "dựng thử ĐẠT".

Nếu Claude báo mạng không tải được bộ nhận dạng: nó sẽ đưa bạn một đường link để tự tải bằng trình duyệt rồi thả file vào `tools/models/`. Làm theo là xong.

**Vài câu hỏi về bạn (10 phút).** Claude hỏi ba lượt ngắn, mỗi lượt vài câu có sẵn lựa chọn để bấm:

- Bạn là ai: tên hiện trên clip, chức danh đúng nguyên văn (Claude sẽ giữ y như vậy, không tự rút gọn), đơn vị, khán giả
- Bạn hay làm loại clip gì, đăng ở đâu, muốn cảm giác nào. Có bốn mẫu để chọn: *Tĩnh lặng* (giấy ngà, mực than, một điểm lục trầm), *Ấm áp* (kem và đất nung), *Hiện đại* (trắng xanh sạch), *Học thuật* (ngà cũ, xanh rêu, đỏ rượu). Không ưng cái nào thì mô tả ba từ về cảm giác, Claude pha bảng màu riêng
- Chữ trên màn hình viết thế nào, nhạc chạy suốt hay chỉ hai đầu, thông điệp kết và cách liên hệ, có logo không

Trả lời tới đâu Claude ghi tới đó vào `phong-cach/PHONG-CACH.md`. Sau này bạn mở file đó đọc lại được, sửa tay được, hoặc chỉ cần nói "từ nay đổi X thành Y".

**Logo (nếu có).** Thả file logo (PNG nền trong suốt là tốt nhất) vào `brand/logo/` rồi báo Claude. Không có logo cũng được, intro sẽ hiện tên bạn bằng chữ.

**Tải nhạc theo mẫu bạn chọn (5-10 phút).** Repo không kèm file nhạc, chỉ kèm danh mục đã kiểm bản quyền. Claude tải những track tải thẳng được; những track còn lại (từ Pixabay) cần bấm nút tải trên trang web: Claude sẽ tự bấm nếu được phép điều khiển trình duyệt, hoặc gửi bạn danh sách link để bấm. File về thư mục Downloads, Claude tự chuyển vào đúng chỗ. Hai track là đủ để bắt đầu.

**Render thử intro để bạn xem (5 phút).** Claude dựng một intro và outro với tên, chức danh, màu của bạn, gửi ảnh cho bạn xem. Bạn góp ý về màu, chữ, logo; Claude sửa tới khi bạn ưng.

Kết thúc, Claude tóm tắt đã làm gì và gợi ý câu để làm clip đầu tiên.

## Bước 4: làm clip đầu tiên

Tạo thư mục cho clip trong `du-an/`, ví dụ `du-an/bai-1/`, bên trong tạo `nguon/` và thả video quay thô vào đó (kéo thả trong Finder). Hoặc nhờ Claude tạo giúp. Rồi nói:

> Dựng bài giảng ngang từ clip trong du-an/bai-1, cắt bỏ khoảng lặng và đoạn nói hỏng, thêm intro outro.

Claude sẽ gỡ băng (vài phút cho clip 10 phút), gửi bạn **một bảng phương án**: đoạn nào giữ, đoạn nào bỏ, vì sao, và chỗ nào định chèn nhãn từ khoá. Bạn đọc, sửa nếu cần, gật đầu. Claude dựng **bản nháp** nhỏ để bạn xem trong `du-an/bai-1/xuat-nhap/`; bạn góp ý; Claude sửa. Ưng rồi Claude xuất **bản chính** 1080p, tự kiểm hình khớp tiếng và âm lượng, đặt vào `du-an/bai-1/xuat-hoan-chinh/`. Đó là file bạn đăng.

Cách đặt yêu cầu cho từng loại clip, ví dụ câu nói, và xử lý khi có gì lạ: đọc tiếp [HUONG-DAN.md](HUONG-DAN.md).

## Những điều nên biết

- **Giữ app Claude mở và máy không ngủ** khi Claude đang gỡ băng hay xuất bản chính. Bài giảng dài một giờ có thể mất một giờ để xuất; Claude tự nối tiếp nếu bị ngắt, nhưng máy ngủ thì dừng
- **Bản nháp nhỏ (480p), bản chính 1080p.** Xem nháp để góp ý bố cục và nhịp, không đánh giá độ nét ở bản nháp
- **Video của bạn không rời máy.** Gỡ băng và dựng chạy trên máy bạn. Chỉ đồ họa (intro, thẻ chữ, không có hình bạn) được dựng trong sandbox của Claude rồi ghép về
- **Lần đầu trên một máy** có thể cần cấp thêm quyền (thư mục Downloads, cho phép trình duyệt tải nhiều file). Claude sẽ nhờ khi cần
- **Dùng trên hai máy**: đặt thư mục xưởng vào iCloud Drive/Dropbox. Bộ nhận dạng giọng nói và thư viện nằm trong thư mục nên đồng bộ theo; trước khi dựng bài lớn, chờ file tải hết về máy đang ngồi (Finder không còn icon đám mây)
- **Muốn đổi phong cách** (màu, chức danh, nhạc): nói với Claude "đổi phong cách" và nêu điều muốn đổi. Không cần làm lại từ đầu

## Khi có gì không chạy

Nói với Claude điều bạn thấy, bằng lời thường ("nó dừng ở chỗ tải", "không thấy file xuất"). Claude có tài liệu chẩn đoán bên trong thư mục. Ba việc bạn tự kiểm được: thư mục xưởng còn được thêm vào phiên Cowork không; máy còn mạng không (lúc cài); ổ đĩa còn chỗ không. Muốn Claude tự kiểm toàn bộ, nói: "chạy kiểm tra xưởng".
