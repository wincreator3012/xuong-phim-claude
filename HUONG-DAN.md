# HƯỚNG DẪN SỬ DỤNG: cách đặt yêu cầu và những gì xảy ra sau đó

Bạn đã cài xưởng và thiết lập phong cách (nếu chưa, xem `BAT-DAU.md`). Tài liệu này nói về việc dùng hằng ngày: chuẩn bị gì, nói gì, nhận gì, và làm gì khi có chuyện lạ.

## Một dự án trông như thế nào

Mỗi dự án là một thư mục trong `Du an/` (cạnh thư mục xưởng, trong `Xuong phim AI`). Nói "tạo dự án <tên>" để Claude tạo, hoặc tự tạo thư mục rồi thả file vào `nguon/`; các thư mục khác Claude tạo khi làm. Sản phẩm cuối nằm ở `Thanh pham/`.

```
Du an/2026-11 Ten du an/
├── nguon/            ← BẠN thả video quay thô, cảnh trám, file slide vào đây
├── transcript/       ← lời giảng gỡ băng có mốc thời gian (Claude tạo; có sẵn thì thả vào)
├── tu-lieu/          ← hình minh hoạ đã kiểm định + ghi chú TU-LIEU.md (khi bạn cần hình)
├── do-hoa/           ← intro, outro, thẻ, nhãn từ khoá đã render
├── timeline.json     ← "kịch bản dựng" máy đọc (Claude soạn, bạn không cần mở)
├── xuat-nhap/        ← bản nháp 480p để bạn xem và góp ý
└── xuat-hoan-chinh/  ← bản đạt nghiệm thu, trước khi Claude đặt vào Thanh pham/

Thanh pham/2026-11 Ten du an/
├── 00 Video day du/  ← video dài và gói đăng tải (tiêu đề, mô tả, status, thumbnail)
└── Short 01 <tên>/   ← mỗi clip ngắn một thư mục: video, kết quả nghiệm thu, gói đăng tải
```

Tên dự án nên không dấu, ngắn (`Bai 1`, `Gioi thieu khoa hoc`); Claude tự thêm năm-tháng ở đầu để dự án xếp theo thời gian. Khi bạn nói "duyệt", Claude xin phép rồi dọn bản nháp, proxy, việc tạm; hồ sơ dự án chỉ còn phần nhẹ để dựng lại khi cần.

## Quay thế nào để dựng dễ

Không cần quay hoàn hảo. Ba điều giúp nhiều nhất: **ngừng một nhịp** (một hơi thở) giữa các ý và trước khi nói lại một câu hỏng, vì Claude cắt vào đúng những khoảng ngừng đó; **nói câu chốt mạnh nhất ngay câu đầu** nếu clip dành cho mạng xã hội, vì clip ngắn mở bằng câu đó rồi mới tới intro; **để mic gần** hơn máy quay nếu có thể. Quay liền một mạch nhiều nội dung trong một file là bình thường, Claude tự tách.

Có slide: để file PPTX, PDF hoặc bộ ảnh slide vào `nguon/` cạnh video, bấm chuyển slide trong lúc quay hay không đều được. Quay nhiều máy: mỗi máy một thư mục con trong `nguon/` (`nguon/toan/`, `nguon/an/`, `nguon/khach/`), mỗi máy tự thu tiếng.

## Câu để nói với Claude

Nói tự nhiên, nêu rõ thư mục dự án và kết quả mong muốn. Vài mẫu:

**Bài giảng dài, khung ngang**
> Dựng bài giảng từ clip trong dự án bai-1, cắt bỏ khoảng lặng và đoạn nói hỏng, thêm intro outro, chèn nhãn từ khoá khi tôi nhắc tới các bước của mô hình.

**Bài giảng có slide**
> Trong dự án bai-2 có video và file slide PDF. Dựng bài giảng ngang, chỗ nào tôi giải thích sơ đồ thì hiện slide, chỗ kể chuyện thì hiện mặt.

**Bài nói trên sân khấu, có khán giả (keynote, talk, sự kiện)**
> Dựng clip từ buổi nói trong dự án keynote-1: có hai file quay 4K, file tiếng từ bàn âm thanh và file slide PPTX. Bắt đầu từ phút 3:14, dừng ở hết câu "...rất là hiệu quả". Bỏ phần nhắc việc tại chỗ. Hiện slide cạnh mặt tôi, không để chữ hay thẻ nào che mặt ai. Đăng YouTube.

Người xem ở nhà không ngồi trong phòng, nên Claude sẽ đề xuất bỏ những gì chỉ có nghĩa tại chỗ (nhắc việc, hướng dẫn dùng tài liệu, bài tập tương tác) và bạn là người chốt. Quay sự kiện: nếu được, xin thêm file tiếng từ bàn âm thanh và file slide gốc; nguồn 4K nặng thì Claude làm bản xem nhẹ trước khi dựng.

**Clip ngắn dọc cho Reels/Shorts**
> Từ bài giảng dự án bai-1, cắt hai clip dọc 60 giây có phụ đề, mỗi clip một ý trọn vẹn.

**Clip giới thiệu chương trình**
> Dựng clip giới thiệu khoá học từ dự án gioi-thieu, khung ngang lẫn dọc, nhạc chạy suốt, cuối clip có QR đăng ký theo link này: ...

**Podcast hai người, ba máy**
> dự án podcast-1 có ba góc quay (toan, an, khach). Đồng bộ, chuyển góc theo người nói, chia thành các phần có thẻ tên phần.

**Phim tài liệu phỏng vấn, trước khi quay**
> Tháng sau chúng tôi ký kết hợp tác ba năm với trường X, muốn làm một phim 5 phút giới thiệu dự án cho nhà tài trợ. Đây là mô tả chương trình và kịch bản dự kiến. Giúp tôi lên kế hoạch: phỏng vấn ai, hỏi gì, quay cảnh nào.

**Phim tài liệu phỏng vấn, sau khi quay**
> Đã quay xong theo kế hoạch, source trong dự án phim-du-an-x/nguon. Gỡ băng, đối chiếu với kế hoạch rồi viết kịch bản thực tế cho tôi duyệt trước khi dựng.

**Cảnh minh hoạ cho đoạn đang giải thích**
> Trong dự án bai-1, đoạn phút 6:20 tới 7:05 tôi giải thích vòng lặp căng thẳng và hồi phục. Làm một cảnh minh hoạ động cho đoạn đó, lấy một khung hình của chính đoạn quay làm nền mờ.

Bốn kiểu chèn để chọn: toàn khung, nền là khung hình mờ, thẻ nổi cạnh bạn (vẫn thấy mặt), bạn thu vào góc nhỏ. Không nói rõ thì Claude đề xuất kiểu hợp từng đoạn ở bảng phương án và gửi một trang xem thử để bạn duyệt chuyển động trước khi render. Gửi kèm một hình mẫu phong cách bạn thích cũng được.

**Chỉ có file ghi âm, muốn video giải thích**
> Trong dự án bai-4 có file ghi âm bài nói 6 phút. Làm video infomotion khung ngang, hình minh hoạ theo từng ý tôi nói.

Mặc định hình phủ kín, nền trống không quá 1 giây. Muốn thoáng hơn thì nói rõ. Đoạn nói về cơ chế, quy trình, số liệu, Claude dùng cảnh minh hoạ kiểu sơ đồ; đoạn chiêm nghiệm dùng nét vẽ ẩn dụ tối giản.

**Phim hoạt hình từ lời nói hay một câu chuyện**
> Từ file ghi âm trong dự án chuyen-1, làm phim hoạt hình khoảng 90 giây có một nhân vật và cảnh vẽ tay, kết bằng một câu hỏi mở.

**Gói đăng tải**
> Soạn tiêu đề, mô tả YouTube và status Facebook cho bản đã xuất của dự án Bai 1, kèm ba thumbnail.

Sau mỗi clip dựng trong xưởng, Claude tự làm bước này mà không cần nhắc; câu trên dùng cho clip cũ hay clip dựng ở nơi khác.

**Chỉ gỡ băng**
> Gỡ băng clip trong dự án bai-3, cho tôi file SRT và bản text.

**Cần hình minh hoạ**
> Đoạn phút 4 tới 6 tôi nói về vỏ não trước trán, tìm hình minh hoạ sạch bản quyền.

**Đổi ý giữa chừng**
> Bỏ đoạn ví dụ thứ hai, thêm thẻ chuyển phần trước phần kết, nhạc nhỏ hơn.

Bạn không cần nhớ tên skill hay tên công cụ. Claude nhận ra loại việc từ câu bạn nói.

## Chuyện gì xảy ra sau khi bạn nói

1. **Khảo sát**: Claude đọc thông số video, khám màu (đa số không cần chỉnh), hỏi vài điều còn thiếu nếu `PHONG-CACH.md` chưa trả lời (ngang hay dọc, độ dài, nhạc nào)
2. **Gỡ băng**: vài phút cho mỗi 10 phút video; bài dài hơn một giờ thì lâu tương ứng. Máy tự kiểm xem có đoạn nào bị bỏ sót. Trên Mac, Claude có thể nhờ bạn bấm đúp `Go bang tren Mac.command` để gỡ băng bằng large-v3 (chính xác nhất)
3. **Phương án cắt và nhãn** (bạn duyệt lần 1): một bảng ghi đoạn nào giữ, đoạn nào bỏ, vì sao, và các chỗ định chèn nhãn từ khoá, thẻ chuyển phần, cảnh trám. Sửa gì cứ nói
4. **Đồ họa và bản nháp** (bạn duyệt lần 2): Claude render intro, outro, nhãn, rồi dựng bản nháp 480p vào `xuat-nhap/`. Mở xem trên máy, góp ý về nhịp, bố cục, chỗ nào chữ hiện sai lúc. Lặp tới khi ưng
5. **Bản chính**: xuất 1080p, máy đo hình khớp tiếng, âm lượng chuẩn, không khoảng đen, rồi Claude nhìn ảnh lưới 12 khung. Đạt thì copy vào `xuat-hoan-chinh/` và báo bạn: tên file, thời lượng, dung lượng, danh sách chương (nếu có), dòng ghi công nhạc cần dán vào mô tả video (nếu dùng track CC-BY)
6. **Gói đăng tải**: ngay sau đó Claude soạn trong `dang-tai/` của dự án (rồi đặt cùng video vào `Thanh pham/`) ba phương án tiêu đề, mô tả YouTube, status Facebook và ba thumbnail từ khung hình thật; bạn chọn, sửa, rồi chép dán khi đăng

Clip 10 phút trọn quy trình thường mất 30-60 phút kể cả thời gian bạn duyệt. Bản chính của bài dài (1-3 giờ) xuất trong một tới vài giờ; để máy chạy.

## Dùng xưởng hiệu quả nhất

Mười hai thói quen rút từ các dự án thật. Không cần nhớ hết: đọc một lần, quay lại khi thấy kết quả chưa ưng.

**Trước khi quay và thả file**

1. **Bắt đầu bằng một clip nhỏ có thật.** Chọn một đoạn 3-10 phút bạn sắp đăng, không chọn dự án lớn nhất. Làm trọn một vòng (nháp, bản chính, gói đăng tải) sẽ dạy bạn nhiều hơn đọc tài liệu, và những góp ý đầu tiên của bạn định hình xưởng cho mọi clip sau.
2. **Quay cho dễ dựng.** Ngừng một nhịp giữa các ý và trước khi nói lại câu hỏng; nói câu chốt mạnh nhất ngay câu đầu nếu clip dành cho mạng xã hội; để mic gần nhất có thể. Quay sự kiện thì xin thêm file tiếng từ bàn âm thanh và file slide gốc.
3. **Đặt tên thư mục và file rõ ràng.** Một dự án một thư mục trong `Du an/`, video và slide vào `nguon/`. Quay nhiều máy thì mỗi máy một thư mục con.

**Khi nói yêu cầu**

4. **Nói mục đích, người xem và nơi đăng trong một câu.** "Clip này đăng YouTube cho giảng viên mới dùng AI" giúp Claude quyết cắt gì, nhịp nào, tiêu đề ra sao; "clip này để gửi riêng cho nhà tài trợ" cho kết quả khác hẳn.
5. **Chốt những gì bạn đã biết.** Điểm vào và điểm ra mong muốn, đoạn phải giữ nguyên, tên người hay số liệu không muốn xuất hiện. Mốc bạn chốt luôn thắng đề xuất của Claude.
6. **Nhớ rằng người xem ở nhà không ngồi trong phòng.** Với bài nói có khán giả tại chỗ, để Claude đề xuất bỏ phần chỉ có nghĩa tại chỗ rồi bạn duyệt.

**Khi duyệt**

7. **Dành sức cho bảng phương án.** Sửa ở bảng chỉ mất một câu nói; sửa ở bản chính có thể mất cả giờ dựng lại. Đọc kỹ hai điều: đoạn nào bỏ, và chỗ nào định chèn chữ hay hình.
8. **Góp ý theo mốc thời gian, bằng lời bạn thấy.** "Ở 14:20 chữ che mặt người ngồi sau tôi" đủ để Claude sửa; không cần thuật ngữ nào.
9. **Chê một lần, rồi dặn "từ nay luôn...".** Claude ghi vào "Sổ tay góp ý" của `phong-cach/PHONG-CACH.md`, và góp ý nào lặp lại lần hai sẽ thành mặc định của xưởng. Quy tắc "không bao giờ để chữ, thẻ hay slide che mặt bất kỳ ai" đã trở thành luật cứng theo đúng cách đó. Góp ý chạm tới cách làm (không chỉ phong cách) thì Claude sửa luôn skill gốc trong xưởng, rồi gửi bạn bản đóng gói mới để lưu lại vào tài khoản.

**Sau khi dựng**

10. **Dùng gói đăng tải Claude soạn.** Ba tiêu đề, mô tả có chương, status Facebook và ba thumbnail khác nhau (cận mặt, khung rộng, chữ làm chủ). Bật "Thử nghiệm và so sánh" của YouTube để dữ liệu chọn giúp bạn.
11. **Tái dùng một buổi quay cho nhiều clip.** Một buổi dài có thể thành bài đầy đủ, vài clip dọc ngắn cho Reels, một video infomotion từ chính giọng nói, mỗi cái một gói đăng tải. Nói với Claude ngay từ đầu bạn muốn những sản phẩm nào để nó chọn đoạn từ đầu.
12. **Để máy chạy, giữ phiên mở, và nói "tiếp tục" khi bị ngắt.** Việc nặng (gỡ băng bài dài, bản chính hàng giờ) tự nối tiếp được. Thấy gì lạ thì nói "chạy kiểm tra xưởng".

## Xưởng không làm gì

Xưởng không tạo hình hay giọng nói bằng AI: mọi cảnh quay là của bạn, đồ họa và hoạt hình được vẽ bằng mã. Xưởng không thay bạn quyết định sáng tạo: hai chốt duyệt (phương án và bản nháp) luôn thuộc về bạn. Chất lượng đầu ra phụ thuộc nguồn: tiếng quá nhỏ hay ồn thì gỡ băng sai nhiều, hình quá tối thì khó cứu. Xưởng không tự đăng lên nền tảng nào; nó chuẩn bị đủ để bạn chép dán. Trên Windows xưởng dùng được nhưng cần Claude rà soát thêm.

## Tự tay chỉnh nhỏ bằng Bàn dựng

Khi bản nháp chỉ còn vài chỗ nhỏ (bỏ một tiếng "ờ" ở đầu đoạn, cho nhãn hiện lâu hơn một chút, nhạc nhỏ đi), bạn có thể tự chỉnh thay vì mô tả cho Claude:

1. Bấm đúp `Mo ban dung.command` ở thư mục xưởng. Chrome tự mở trang Bàn dựng; giữ cửa sổ Terminal mở trong lúc chỉnh.
2. Chọn timeline cần chỉnh. Phía dưới là các kênh: chương, đồ họa nổi, B-roll, hình chính (có chữ bạn nói trong từng khối), tiếng lời, nhạc nền.
3. Kéo mép khối để tỉa hoặc đổi thời lượng nhãn, kéo thân khối để đổi chỗ, bấm S để tách tại đầu đọc, bấm vào khối để chỉnh số liệu ở thẻ "Thuộc tính". Bấm ? để xem phím tắt. Sai thì Cmd+Z.
4. Bỏ chữ thừa: mở thẻ "Lời", bôi đen chữ rồi bấm Delete; chữ mờ hoặc gạch là phần chưa dùng hay đã bỏ, bôi đen rồi Enter để lấy lại. Hai chữ nói liền một hơi thì trang hỏi bạn bỏ thêm hay giữ lại cho khỏi gượng.
5. Bấm Lưu (Cmd+S), rồi nói với Claude "tôi chỉnh xong rồi". Claude dựng lại bản nháp và kiểm như mọi lần; bản cũ luôn được cất lại.

Lần đầu dùng với một dự án, Claude cần vài phút chuẩn bị mốc lời (`tools/moc-tu.py`). Khung xem trong Bàn dựng là xem nhanh: bố cục slide, chỉnh màu, phụ đề và độ to chuẩn chỉ có ở bản dựng thật.

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

**Whisper nghe sai thuật ngữ, tên riêng.** Bổ sung từ đó vào mục 4 của `PHONG-CACH.md` ("từ ngữ phải viết đúng"), Claude sẽ đối chiếu mỗi lần gỡ băng. Nếu đang dùng turbo, nhờ Claude gỡ băng lại bằng large-v3 trên Mac.

**Cảnh minh hoạ báo thiếu Playwright hay Chromium.** Cảnh minh hoạ được chụp trong sandbox của Claude, nơi thường có sẵn hai thứ này. Nếu Claude chạy thẳng trên máy bạn, nói "cài Playwright cho cảnh minh hoạ"; Claude cài `playwright` và trình duyệt Chromium đi kèm (cần mạng, khoảng 150 MB).

**Muốn kiểm xem xưởng còn khoẻ không** (sau khi cập nhật xưởng hay đổi máy): nói "chạy kiểm tra xưởng". Claude chạy một bản dựng thử nhỏ qua cổng nghiệm thu.

## Skill trong tài khoản

Mười lăm skill của xưởng (quy trình chuẩn cho từng loại việc) có bản gốc trong thư mục `skills/` của xưởng, và bản chép mang tiền tố của bạn (ví dụ `tma-phim-dung-bai`) trong tài khoản AI. Bản chép giúp AI tự nhận ra việc bạn nhờ ở mọi phiên; bản gốc là thứ lớn lên theo góp ý của bạn.

- Nói việc bằng lời thường là đủ. Muốn chắc chắn thì gọi tên: "dùng skill tma-phim-clip-ngan".
- Hỏi "skill nào cần lưu lại?" bất cứ lúc nào: Claude so bản trong tài khoản với bản gốc và đóng gói lại đúng những skill đã đổi.
- Lưu một tệp skill: bấm nút lưu trên thẻ tệp trong cuộc trò chuyện, hoặc vào Customize > Skills, bấm "+", chọn "Create skill", rồi "Upload a skill" (không nhận đuôi `.skill` thì đổi thành `.zip`). Có bản cùng tên thì thay bản cũ.
- Skill chỉ chứa cách làm, không chứa video hay phong cách của bạn; nó cần thư mục `Xuong phim AI` được thêm vào phiên làm việc mới chạy được.

Giải thích đầy đủ: `skills/phim-thiet-lap/references/skill-trong-tai-khoan.md`.

## Cập nhật xưởng

Xưởng của bạn là xưởng riêng, dựng từ bản thiết kế trên GitHub; nó không tự cập nhật và không bao giờ nên bị chép đè. Khi muốn xem bản thiết kế có gì mới, nói với Claude: "xem bản thiết kế có gì mới". Claude đọc nhật ký thay đổi của bản thiết kế (THAY-DOI.md trên GitHub) từ ngày bạn dựng xưởng, so từng tệp liên quan với xưởng của bạn, rồi trình danh sách: lấy gì, vì sao đáng lấy, ảnh hưởng gì tới cách bạn đang làm. Bạn duyệt điều nào, Claude ghi điều đó, chạy kiểm tra xưởng, và đóng gói lại những skill đã đổi để bạn lưu vào tài khoản.

Những phần là của riêng bạn không bao giờ bị ghi đè: `phong-cach/`, `brand/`, nhạc và hiệu ứng, hai preset intro/outro bạn đã sửa, từ điển ẩn dụ, hình vẽ riêng của phim infomotion hay hoạt hình, và những skill bạn đã tinh chỉnh (khi bản thiết kế có cải tiến cho skill đó, Claude hợp nhất có chọn lọc và hỏi bạn).

**Đã tải bản cũ của repo về dùng (bản ZIP hay `git clone`)?** Xưởng vẫn chạy. Muốn chuyển sang cách mới, nói với Claude "chuyển thư mục này thành xưởng riêng của tôi": Claude hỏi tiền tố skill, chạy bước cá nhân hoá ngay tại chỗ (tools/cai-dat.py --dung-xuong), đóng gói skill cho bạn lưu vào tài khoản, và nếu thư mục còn là bản clone thì đề nghị gỡ liên kết về repo gốc (bạn không push, không pull về đó nữa). Muốn đổi tên thư mục cho khớp, đổi trong Finder rồi thêm lại thư mục mẹ vào phiên.

**Dự án còn nằm trong `du-an/` bên trong thư mục xưởng (bản rất cũ)?** Nói với Claude "dời dự án ra ngoài xưởng": Claude tạo `Du an/` và `Thanh pham/` cạnh xưởng, dời từng dự án sang `Du an/` (giữ nguyên bên trong, thêm năm-tháng vào tên), sửa đường dẫn trong file dựng nếu cần, rồi bỏ `du-an/` rỗng. Trong lúc chưa dời, công cụ vẫn đọc được `du-an/` kiểu cũ.
