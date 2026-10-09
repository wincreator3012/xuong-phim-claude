# BẮT ĐẦU: nhờ AI dựng xưởng phim riêng cho bạn, từng bước

Tài liệu này dành cho người chưa từng dùng AI làm việc với file trên máy. Đọc hết một lần mất khoảng 10 phút; làm theo mất khoảng 45-60 phút, trong đó phần lớn là ngồi chờ máy và trả lời vài câu hỏi. Bạn không phải gõ lệnh nào, và cũng không phải tải repo này về.

Điều quan trọng nhất cần hiểu trước: repo này là **bản thiết kế**. Bạn không tải nó về để dùng nguyên. Bạn đưa đường link cho trợ lý AI, AI đọc bản thiết kế và dựng trên máy bạn một xưởng RIÊNG: mang tên bạn, phong cách bạn, có bộ skill mang tiền tố riêng của bạn. Xưởng đó là của bạn hoàn toàn, lớn lên theo góp ý của bạn, và không bao giờ bị bản thiết kế ghi đè.

## Trước khi bắt đầu, bạn cần

- **App Claude trên máy tính** (tải từ claude.ai/download) đã đăng nhập, và gói có **Cowork**. Cowork là chế độ để Claude làm việc trực tiếp với thư mục trên máy bạn
- **Máy Mac** với chip Apple Silicon (M1 trở lên) là lựa chọn chạy êm nhất. Windows và Linux dùng được nếu app Claude hỗ trợ Cowork trên máy đó
- **Khoảng 3 GB trống** trên ổ đĩa: 1 GB cho bộ nhận dạng giọng nói, phần còn lại cho thư viện và bản dựng
- **Mạng ổn định** trong lúc cài (tải khoảng 700 MB). Sau khi cài, gỡ băng và dựng clip chạy offline
- **45-60 phút** không bị ngắt, và một video ngắn bạn tự quay (1-3 phút, nói trước máy) để làm clip thử nếu muốn

Nếu bạn dùng hai máy (ví dụ laptop mang đi và máy bàn ở nhà), xem lưu ý cuối tài liệu.

## Bước 1: tạo một thư mục trống

Trong **Documents** (hoặc chỗ bạn hay để tài liệu, miễn không phải thư mục đồng bộ iCloud, Dropbox, OneDrive), tạo một thư mục tên **Xuong phim AI**. Để trống. Xưởng, dự án và thành phẩm của bạn sẽ được dựng bên trong:

```
Documents/
└── Xuong phim AI/
    ├── xuong-phim-<tiền tố của bạn>/   ← xưởng riêng của bạn (AI dựng)
    ├── Du an/                          ← dự án của bạn
    └── Thanh pham/                     ← sản phẩm để đăng
```

Vì sao tách ba thư mục: xưởng chỉ chứa "năng lực" (cách làm, công cụ, phong cách), còn video của bạn nằm riêng, nên lúc xưởng được cập nhật không đụng tới dự án nào.

## Bước 2: mở Cowork và thêm thư mục

Mở app Claude, chọn **Cowork** và bắt đầu một phiên làm việc mới. Tìm nút **Add folder** (thêm thư mục) và chọn thư mục **Xuong phim AI**. Từ lúc này Claude đọc và ghi được trong thư mục đó, và chỉ thư mục đó.

Lần đầu, hệ điều hành có thể hỏi quyền truy cập thư mục; bấm cho phép.

## Bước 3: nói câu đầu tiên

Gõ vào khung chat:

> Đọc bản thiết kế xưởng phim tại https://github.com/wincreator3012/xuong-phim-claude, bắt đầu từ file DUNG-XUONG.md, rồi dựng cho tôi một xưởng phim riêng trong thư mục Xuong phim AI. Đừng clone hay tải ZIP.

Câu cuối là để AI hiểu đúng ngay từ đầu: nó học từ repo rồi dựng xưởng cho bạn, chứ không lấy repo về dùng nguyên. Chuyện gì sẽ xảy ra, theo thứ tự:

**Hai câu hỏi nhỏ (1 phút).** Claude hỏi tiền tố cho skill của bạn (thường là chữ cái đầu họ tên, ví dụ Trần Minh An thì là `tma`) và tên thư mục xưởng (mặc định `xuong-phim-tma`).

**Dựng xưởng của bạn (10-20 phút, bạn chỉ chờ).** Claude đọc bản đồ tệp của bản thiết kế, chép từng phần năng lực đã kiểm chứng (công cụ, đồ họa, quy trình) vào xưởng mới, kiểm mã từng tệp cho chắc nguyên vẹn, rồi đổi tên, gắn tiền tố, tạo hai thư mục `Du an` và `Thanh pham`. Xưởng làm xong không còn liên kết nào với repo gốc.

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

**Lưu skill vào tài khoản (khoảng 10 phút).** Skill là bản quy trình chuẩn viết cho AI, giống cuốn sổ tay nghề của một người thợ lành nghề: khi nào dùng, làm từng bước ra sao, kiểm gì trước khi giao. Xưởng có mười lăm skill, mỗi loại việc một skill. Bản gốc nằm trong xưởng của bạn; Claude đóng gói một bản chép mang tiền tố của bạn (ví dụ `tma-phim-clip-ngan`) để bạn lưu vào tài khoản Claude. Lưu rồi thì ở bất kỳ phiên nào, bạn chỉ cần nói việc bằng lời thường, Claude tự mở đúng quy trình. Claude giải thích kỹ và hướng dẫn từng bước: bấm nút lưu trên thẻ tệp trong cuộc trò chuyện, hoặc vào **Customize > Skills**, bấm **+**, chọn **Create skill** rồi **Upload a skill**. Về sau, mỗi khi xưởng học thêm điều mới từ góp ý của bạn, Claude đóng gói lại đúng những skill đã đổi và nhờ bạn lưu lại; hỏi "skill nào cần lưu lại?" lúc nào cũng được.

**Buổi giới thiệu xưởng (khoảng 10 phút, Claude kể và bạn hỏi).** Cài xong, Claude không vội đưa bạn vào việc. Nó giải thích có hệ thống xưởng làm được gì cho bạn: một bản đồ các việc (dựng bài giảng, bài giảng có slide, clip ngắn cho mạng xã hội, podcast nhiều máy, cảnh minh hoạ, infomotion và phim hoạt hình, phim tài liệu, gói đăng tải), chọn ra hai ba việc hợp với loại clip bạn vừa kể, nói rõ xưởng không làm gì, và dặn các thói quen giúp dùng hiệu quả nhất (duyệt kế hoạch trước khi dựng, góp ý ở bản nháp, ghi phong cách một lần để dùng mãi). Bạn muốn xem lại lúc nào cũng được, chỉ cần hỏi "xưởng làm được gì" hoặc "dùng sao cho hiệu quả".

Kết thúc, Claude tóm tắt đã làm gì và gợi ý câu để làm clip đầu tiên, chọn đúng loại clip hợp với bạn nhất.

## Bước 4: làm clip đầu tiên

Nói với Claude "tạo dự án Bai 1": Claude tạo thư mục `Du an/<năm-tháng> Bai 1/` có sẵn `nguon/`. Thả video quay thô vào `nguon/` (kéo thả trong Finder), rồi nói:

> Dựng bài giảng ngang từ clip trong dự án Bai 1, cắt bỏ khoảng lặng và đoạn nói hỏng, thêm intro outro.

Claude sẽ gỡ băng (vài phút cho clip 10 phút), gửi bạn **một bảng phương án**: đoạn nào giữ, đoạn nào bỏ, vì sao, và chỗ nào định chèn nhãn từ khoá. Bạn đọc, sửa nếu cần, gật đầu. Claude dựng **bản nháp** nhỏ để bạn xem trong `xuat-nhap/` của dự án; bạn góp ý; Claude sửa. Ưng rồi Claude xuất **bản chính** 1080p, tự kiểm hình khớp tiếng và âm lượng, làm luôn gói đăng tải, và đặt cả hai vào `Thanh pham/<năm-tháng> Bai 1/`. Đó là file bạn đăng. Khi bạn nói "duyệt", Claude xin phép rồi dọn nháp cho nhẹ máy.

Cách đặt yêu cầu cho từng loại clip, ví dụ câu nói, và xử lý khi có gì lạ: đọc tiếp [HUONG-DAN.md](HUONG-DAN.md).

## Những điều nên biết

- **Giữ app Claude mở và máy không ngủ** khi Claude đang gỡ băng hay xuất bản chính. Bài giảng dài một giờ có thể mất một giờ để xuất; Claude tự nối tiếp nếu bị ngắt, nhưng máy ngủ thì dừng
- **Bản nháp nhỏ (480p), bản chính 1080p.** Xem nháp để góp ý bố cục và nhịp, không đánh giá độ nét ở bản nháp
- **Video của bạn không rời máy.** Gỡ băng và dựng chạy trên máy bạn. Chỉ đồ họa (intro, thẻ chữ, không có hình bạn) được dựng trong sandbox của Claude rồi ghép về
- **Lần đầu trên một máy** có thể cần cấp thêm quyền (thư mục Downloads, cho phép trình duyệt tải nhiều file). Claude sẽ nhờ khi cần
- **Dùng trên hai máy**: đồng bộ đám mây (iCloud, Dropbox) dễ kẹt với file video lớn, nên đừng đặt cả `Xuong phim AI` vào đó. Cách gọn: chép thư mục xưởng của bạn (chỉ thư mục xưởng, không cần `Du an`) sang máy thứ hai bằng ổ ngoài, rồi nói với Claude trên máy đó "cài lại môi trường cho xưởng này"; dự án nào dựng ở máy nào thì để ở máy đó. Muốn quản lý phiên bản xưởng của riêng bạn thì có thể dùng git với một repo riêng tư của bạn; đừng trỏ nó về repo bản thiết kế. Skill trong tài khoản thì tự có mặt ở mọi máy bạn đăng nhập. File `Go bang tren Mac.command` tự cài môi trường riêng trên từng máy, nên lần đầu bấm trên máy mới sẽ chờ vài phút
- **Gỡ băng chất lượng cao nhất trên Mac (tuỳ chọn).** Xưởng mặc định dùng model turbo. Muốn dùng large-v3, nhờ Claude tải theo `tools/models/TAI-MODEL.md` (khoảng 1,7 GB). Khi Claude nhờ, bấm đúp file `Go bang tren Mac.command` trong Finder; lần đầu trên mỗi máy cần mạng và mất vài phút. macOS chặn thì bấm chuột phải, chọn Open, rồi Open lần nữa. Chưa tải large-v3 thì xưởng tự dùng turbo
- **Quay hình để dựng dễ hơn**: nói trước máy, để mặt rõ và sáng; quay liền một mạch, nghỉ vài giây giữa các ý để chỗ cắt rơi vào khoảng lặng; clip nói trên sân khấu thì giữ nguyên khuôn mặt người nói trên hình, xưởng không che mặt bằng bảng chữ hay đồ họa
- **Muốn đổi phong cách** (màu, chức danh, nhạc): nói với Claude "đổi phong cách" và nêu điều muốn đổi. Không cần làm lại từ đầu

## Khi có gì không chạy

Nói với Claude điều bạn thấy, bằng lời thường ("nó dừng ở chỗ tải", "không thấy file xuất"). Claude có tài liệu chẩn đoán bên trong thư mục. Ba việc bạn tự kiểm được: thư mục xưởng còn được thêm vào phiên Cowork không; máy còn mạng không (lúc cài); ổ đĩa còn chỗ không. Muốn Claude tự kiểm toàn bộ, nói: "chạy kiểm tra xưởng".
