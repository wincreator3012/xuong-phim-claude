# HƯỚNG DẪN SỬ DỤNG: cách đặt yêu cầu và những gì xảy ra sau đó

Bạn đã cài xưởng và thiết lập phong cách (nếu chưa, xem `BAT-DAU.md`). Tài liệu này nói về việc dùng hằng ngày: chuẩn bị gì, nói gì, nhận gì, và làm gì khi có chuyện lạ.

## Một dự án trông như thế nào

Mỗi clip là một thư mục trong `du-an/`. Bạn chỉ cần tạo thư mục và thả file vào `nguon/`; các thư mục khác Claude tạo khi làm.

```
du-an/ten-du-an/
├── nguon/            ← BẠN thả video quay thô, cảnh trám, file slide vào đây
├── transcript/       ← lời giảng gỡ băng có mốc thời gian (Claude tạo; có sẵn thì thả vào)
├── tu-lieu/          ← hình minh hoạ đã kiểm định + ghi chú TU-LIEU.md (khi bạn cần hình)
├── do-hoa/           ← intro, outro, thẻ, nhãn từ khoá đã render
├── timeline.json     ← "kịch bản dựng" máy đọc (Claude soạn, bạn không cần mở)
├── xuat-nhap/        ← bản nháp 480p để bạn xem và góp ý
└── xuat-hoan-chinh/  ← THÀNH PHẨM. Chỉ file ở đây mới là bản đăng
```

Tên thư mục dự án nên không dấu, ngắn (`bai-1`, `gioi-thieu-khoa-hoc`). Có thể có dấu và khoảng trắng, nhưng không dấu thì đỡ lỗi khi đồng bộ đám mây.

## Quay thế nào để dựng dễ

Không cần quay hoàn hảo. Ba điều giúp nhiều nhất: **ngừng một nhịp** (một hơi thở) giữa các ý và trước khi nói lại một câu hỏng, vì Claude cắt vào đúng những khoảng ngừng đó; **nói câu chốt mạnh nhất ngay câu đầu** nếu clip dành cho mạng xã hội, vì clip ngắn mở bằng câu đó rồi mới tới intro; **để mic gần** hơn máy quay nếu có thể. Quay liền một mạch nhiều nội dung trong một file là bình thường, Claude tự tách.

Có slide: để file PPTX, PDF hoặc bộ ảnh slide vào `nguon/` cạnh video, bấm chuyển slide trong lúc quay hay không đều được. Quay nhiều máy: mỗi máy một thư mục con trong `nguon/` (`nguon/toan/`, `nguon/an/`, `nguon/khach/`), mỗi máy tự thu tiếng.

## Câu để nói với Claude

Nói tự nhiên, nêu rõ thư mục dự án và kết quả mong muốn. Vài mẫu:

**Bài giảng dài, khung ngang**
> Dựng bài giảng từ clip trong du-an/bai-1, cắt bỏ khoảng lặng và đoạn nói hỏng, thêm intro outro, chèn nhãn từ khoá khi tôi nhắc tới các bước của mô hình.

**Bài giảng có slide**
> Trong du-an/bai-2 có video và file slide PDF. Dựng bài giảng ngang, chỗ nào tôi giải thích sơ đồ thì hiện slide, chỗ kể chuyện thì hiện mặt.

**Clip ngắn dọc cho Reels/Shorts**
> Từ bài giảng du-an/bai-1, cắt hai clip dọc 60 giây có phụ đề, mỗi clip một ý trọn vẹn.

**Clip giới thiệu chương trình**
> Dựng clip giới thiệu khoá học từ du-an/gioi-thieu, khung ngang lẫn dọc, nhạc chạy suốt, cuối clip có QR đăng ký theo link này: ...

**Podcast hai người, ba máy**
> du-an/podcast-1 có ba góc quay (toan, an, khach). Đồng bộ, chuyển góc theo người nói, chia thành các phần có thẻ tên phần.

**Chỉ gỡ băng**
> Gỡ băng clip trong du-an/bai-3, cho tôi file SRT và bản text.

**Cần hình minh hoạ**
> Đoạn phút 4 tới 6 tôi nói về vỏ não trước trán, tìm hình minh hoạ sạch bản quyền.

**Đổi ý giữa chừng**
> Bỏ đoạn ví dụ thứ hai, thêm thẻ chuyển phần trước phần kết, nhạc nhỏ hơn.

Bạn không cần nhớ tên skill hay tên công cụ. Claude nhận ra loại việc từ câu bạn nói.

## Chuyện gì xảy ra sau khi bạn nói

1. **Khảo sát**: Claude đọc thông số video, khám màu (đa số không cần chỉnh), hỏi vài điều còn thiếu nếu `PHONG-CACH.md` chưa trả lời (ngang hay dọc, độ dài, nhạc nào)
2. **Gỡ băng**: vài phút cho mỗi 10 phút video; bài dài hơn một giờ thì lâu tương ứng. Máy tự kiểm xem có đoạn nào bị bỏ sót
3. **Phương án cắt và nhãn** (bạn duyệt lần 1): một bảng ghi đoạn nào giữ, đoạn nào bỏ, vì sao, và các chỗ định chèn nhãn từ khoá, thẻ chuyển phần, cảnh trám. Sửa gì cứ nói
4. **Đồ họa và bản nháp** (bạn duyệt lần 2): Claude render intro, outro, nhãn, rồi dựng bản nháp 480p vào `xuat-nhap/`. Mở xem trên máy, góp ý về nhịp, bố cục, chỗ nào chữ hiện sai lúc. Lặp tới khi ưng
5. **Bản chính**: xuất 1080p, máy đo hình khớp tiếng, âm lượng chuẩn, không khoảng đen, rồi Claude nhìn ảnh lưới 12 khung. Đạt thì copy vào `xuat-hoan-chinh/` và báo bạn: tên file, thời lượng, dung lượng, danh sách chương (nếu có), dòng ghi công nhạc cần dán vào mô tả video (nếu dùng track CC-BY)

Clip 10 phút trọn quy trình thường mất 30-60 phút kể cả thời gian bạn duyệt. Bản chính của bài dài (1-3 giờ) xuất trong một tới vài giờ; để máy chạy.

## Góp ý sao cho Claude sửa đúng

Nói theo mốc thời gian trên bản bạn đang xem: "ở 2:14 nhãn hiện sớm quá, phải lúc tôi nói xong từ 'ba bước'", "từ 7:10 tới 7:40 lộn thứ tự". Mốc bạn đọc trên bản render đáng tin hơn mọi suy luận của Claude. Góp ý về chữ (chức danh, tên chương trình, thuật ngữ) Claude sẽ sửa tận gốc để clip sau không lặp lại, và ghi vào "Sổ tay góp ý" cuối `phong-cach/PHONG-CACH.md`.

## Nhạc, hình, và bản quyền

Nhạc chỉ lấy từ thư viện đã kiểm định (`nhac-nen/THU-VIEN.md`) hoặc từ `nhac-nen/rieng/` nếu là nhạc bạn có quyền dùng. Track Kevin MacLeod (CC-BY) cần một dòng ghi công trong mô tả video; Claude sẽ đưa sẵn dòng đó khi giao file. Hình minh hoạ Claude chỉ lấy từ nguồn mở có giấy phép rõ, ghi lại URL trang nguồn trong `tu-lieu/TU-LIEU.md`; không lấy từ Google Images hay mạng xã hội. Muốn thêm nhạc vào thư viện: nói với Claude, nó theo quy tắc trong `thu-vien/AM-THANH.md` (kiểm Content ID trước khi tải).

## Sự cố thường gặp

**Claude nói không thấy thư mục xưởng.** Phiên Cowork chưa thêm thư mục, hoặc thư mục đã đổi tên/di chuyển. Thêm lại bằng nút "Add folder".

**Dừng giữa chừng khi tải hoặc xuất.** Bình thường với việc dài: mỗi lệnh có giới hạn thời gian, Claude tự gọi lại và nối tiếp. Nếu Claude không tự tiếp, nói "tiếp tục". Nếu máy vừa ngủ, mở lại và nói "tiếp tục dựng du-an/...".

**File trong nguon/ có icon đám mây (iCloud, Dropbox).** File chưa tải hết về máy. Chờ tải xong rồi mới dựng, hoặc bấm tải về trong Finder.

**Bản nháp có chỗ giật hay lệch tiếng.** Nói rõ mốc thời gian. Claude kiểm mối nối theo bản đồ thời gian của bản dựng. Bản chính luôn qua máy đo hình khớp tiếng nên lệch cộng dồn không lọt được.

**Chữ Việt trên đồ họa mất dấu hoặc tràn khung.** Nói với Claude kèm mốc thời gian; đây là lỗi hiển thị và Claude phải sửa rồi xem lại khung hình thật trước khi báo xong.

**Whisper nghe sai thuật ngữ, tên riêng.** Bổ sung từ đó vào mục 4 của `PHONG-CACH.md` ("từ ngữ phải viết đúng"), Claude sẽ đối chiếu mỗi lần gỡ băng.

**Muốn kiểm xem xưởng còn khoẻ không** (sau khi cập nhật repo hay đổi máy): nói "chạy kiểm tra xưởng". Claude chạy một bản dựng thử nhỏ qua cổng nghiệm thu.

## Cập nhật xưởng

Tải bản mới của repo và chép đè các thư mục `tools/`, `studio/`, `skills/`, `docs/`, `thu-vien/` lên bản cũ; giữ nguyên `phong-cach/`, `brand/`, `nhac-nen/`, `hieu-ung/`, `du-an/` của bạn. Sau đó nói "chạy kiểm tra xưởng". Nếu dùng `git`, `git pull` làm việc này gọn hơn; các thư mục riêng của bạn đã được để ngoài theo dõi (`.gitignore`) trừ `phong-cach/PHONG-CACH.md` và `brand/brand.json`, hai file bạn nên giữ bản của mình khi có xung đột.
