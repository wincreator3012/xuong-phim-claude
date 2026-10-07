# Giới thiệu xưởng cho người mới: nói gì, theo thứ tự nào

Tài liệu này là kịch bản cho Claude (hoặc trợ lý AI khác đọc `CLAUDE.md`) khi người dùng vừa thiết lập xong xưởng, hoặc bất cứ lúc nào họ hỏi "xưởng làm được gì", "tôi nên dùng thế nào", "hướng dẫn tôi", "mới vào chưa biết bắt đầu từ đâu". Mục tiêu: sau khoảng 10 phút, người dùng hiểu xưởng làm ra được gì cho họ, biết một dự án chạy thế nào, nắm vài thói quen dùng hiệu quả, và có một bước đầu tiên cụ thể để làm ngay.

## Nguyên tắc trình bày

- **Có hệ thống, nhưng từng chặng một.** Sáu chặng dưới đây theo thứ tự cố định. Mỗi lượt trả lời chỉ nói một chặng (vài đoạn ngắn), rồi hỏi một câu để người dùng chọn đi tiếp, đi sâu hay bỏ qua. Không đổ cả danh mục một lần.
- **Lời thường, không thuật ngữ kỹ thuật.** Không nhắc ffmpeg, Remotion, LUFS, timeline, sandbox trừ khi người dùng hỏi. Nói theo thứ họ sẽ thấy: "bản nháp", "bảng phương án", "gói đăng tải".
- **Cá nhân hoá bằng `phong-cach/PHONG-CACH.md`.** Loại clip họ chọn ở bước thiết lập (bài giảng, clip ngắn, podcast...) thì đưa lên đầu ở chặng 2 và dùng ví dụ từ lĩnh vực của họ.
- **Chỉ nói điều xưởng thật sự có.** Nguồn sự thật: bảng skill trong `CLAUDE.md`, `README.md`, `HUONG-DAN.md`. Không hứa tính năng chưa có; chỗ nào chưa chắc thì nói là chưa chắc.
- **Người dùng vắng mặt hoặc muốn bỏ qua:** tóm tắt chặng 1 và 6 trong một tin nhắn, ghi `da_gioi_thieu` (chặng 6) và nói họ có thể gọi lại bằng câu "giới thiệu lại xưởng".

## Chặng 1. Xưởng là gì, và ba lời hứa

Một câu mở đầu: "Bạn thả video hoặc giọng nói quay thô vào một thư mục và nói bằng lời thường bạn muốn gì; mình làm toàn bộ phần kỹ thuật rồi giao thành phẩm đã kiểm chất lượng, kèm gói đăng tải."

Rồi ba lời hứa, mỗi lời một hai câu:

1. **Mọi clip mang dấu ấn của bạn.** Tên, chức danh nguyên văn, màu sắc, nhạc, thông điệp kết đã điền ở bước thiết lập được áp đều cho mọi clip; đổi bằng một câu nói.
2. **Chưa qua cổng máy đo thì chưa báo xong.** Hình khớp tiếng, âm lượng chuẩn, không khoảng đen, không đứng hình: máy đo chứ không phải mình tự thấy ổn.
3. **Video của bạn không rời máy bạn.** Gỡ băng và dựng chạy tại máy; chỉ đồ họa (không có hình bạn) được dựng ở môi trường đám mây rồi ghép về.

Thêm một ý quan trọng: **bạn luôn là người quyết.** Có hai chốt duyệt bắt buộc (phương án cắt, bản nháp), và xưởng làm việc bằng nguyên lý chứ không bằng khuôn: mặc định là điểm xuất phát, không phải đáp án.

Kết chặng: "Bạn muốn xem xưởng làm ra được những gì không?"

## Chặng 2. Bản đồ năng lực: bạn đang có gì, xưởng làm ra gì

Mở bằng câu hỏi "bạn đang có gì trong tay?" rồi trình bảng. Đưa các dòng khớp với phong cách của người dùng lên đầu, các dòng còn lại gói trong một câu "ngoài ra xưởng còn...". Mỗi dòng kèm một câu mẫu để người dùng thấy cách nói.

| Bạn đang có | Xưởng làm ra | Cần chuẩn bị | Skill | Câu mẫu |
|---|---|---|---|---|
| Video bạn nói trước máy (bài giảng, chia sẻ, giới thiệu khoá học) | Clip ngang 16:9 hoàn chỉnh: cắt khoảng lặng và đoạn nói hỏng, intro/outro, nhãn từ khoá, nhạc, chương YouTube | video thô trong `nguon/` | `phim-dung-bai` | "Dựng bài giảng ngang từ du-an/bai-1" |
| Bài giảng kèm file slide | Xen mặt, slide, hoặc cả hai theo từng đoạn lời; không bao giờ che mặt ai; dùng được cho keynote và sự kiện có khán giả | video + PPTX, PDF hoặc ảnh slide | `phim-bai-giang-slide` | "Có video và file slide, hiện slide chỗ tôi giải thích sơ đồ" |
| Một bài dài, muốn clip ngắn cho mạng xã hội | Clip dọc 9:16 (Reels, Shorts, TikTok) hay clip quảng bá: chọn đoạn có hook, phụ đề burn-in, bảng tên, cảnh minh hoạ khi ý cần hình | bài đã dựng hoặc video thô | `phim-clip-ngan` | "Cắt hai clip dọc 60 giây, mỗi clip một ý trọn vẹn" |
| Podcast hoặc buổi quay nhiều máy | Tự đồng bộ các góc bằng âm thanh, chuyển góc theo người nói, chia phần có thẻ tên | mỗi máy một thư mục con | `phim-multicam` | "Ba góc quay, đồng bộ và chuyển góc theo người nói" |
| Một đoạn giải thích cơ chế, quy trình, so sánh, số liệu | Cảnh minh hoạ động kiểu explainer vẽ riêng cho đoạn đó, chèn vào bài hoặc làm clip riêng | chỉ cần nói đoạn nào | `phim-canh-minh-hoa` | "Làm cảnh minh hoạ động cho đoạn 6:20 tới 7:05" |
| Chỉ có file ghi âm giọng nói | Video giải thích bằng đồ họa thông tin tối giản (infomotion), hoặc phim hoạt hình vẽ bằng code có nhân vật và cảnh | file ghi âm | `phim-infomotion`, `phim-hoat-hoa` | "Làm video infomotion từ file ghi âm này" |
| Một dự án, chương trình, sự kiện cần phim giới thiệu từ phỏng vấn nhiều người | Phim tài liệu ngắn; có Kế hoạch ghi hình (phỏng vấn ai, hỏi gì, quay cảnh nào) trước khi quay, rồi kịch bản thực tế sau khi quay | mô tả dự án; sau đó là các file phỏng vấn | `phim-tai-lieu-phong-van` | "Giúp tôi lên kế hoạch quay phim giới thiệu dự án X" |
| Chỉ cần chữ | Transcript có mốc thời gian, phụ đề SRT, ngay trên máy | file video hay âm thanh | `phim-transcript` | "Gỡ băng clip này, cho tôi file SRT" |
| Cần hình minh hoạ | Hình và tư liệu đã kiểm bản quyền, ghi nguồn | nói đoạn nào cần | `phim-tu-lieu` | "Tìm hình minh hoạ sạch bản quyền cho đoạn này" |
| Intro, outro, bảng tên, thẻ chữ, infographic động | Đồ họa theo màu và chức danh của bạn | không cần gì | `phim-do-hoa` | "Làm bảng tên và thẻ chuyển phần" |
| Màu bạc, hai góc lệch màu, da không đẹp | Khám màu và căn chỉnh nhẹ khi thật cần | clip cần xem | `phim-mau-sac` | "Clip này màu bị bạc, xem giúp tôi" |
| Một clip đã dựng, sắp đăng | Gói đăng tải: ba tiêu đề, mô tả YouTube có chương, status Facebook, ba thumbnail từ khung hình thật; tự chạy sau mỗi clip | không cần gì | `phim-dang-tai` | "Soạn gói đăng tải cho clip này" |
| Bản nháp chỉ còn vài chỗ nhỏ | Bàn dựng trên Chrome: tỉa, đổi chỗ, chỉnh thẻ và nhạc; Dựng bằng lời: bôi đen chữ thừa, hình và tiếng cắt đúng chỗ | bản nháp đã có | `phim-ban-dung` | "Mở bàn dựng cho dự án này" |

Sau bảng, kể ba cách kết hợp phổ biến (chọn những cách hợp với người dùng):

- **Một buổi workshop hay bài giảng dài thành nhiều sản phẩm:** bài đầy đủ cho YouTube, ba tới năm clip dọc cho Reels hoặc Shorts, mỗi cái một gói đăng tải.
- **Một buổi podcast hay đối thoại:** bản dài nhiều góc, vài clip ngắn trích ý hay.
- **Một ý chiêm nghiệm hay khái niệm:** video infomotion hoặc hoạt hình từ chính giọng bạn, không cần lên hình.

Kết chặng: "Bạn muốn xem một dự án chạy từ đầu tới cuối trông thế nào không?"

## Chặng 3. Một dự án chạy thế nào

Kể sáu bước, nhấn rõ ai làm gì (đọc `HUONG-DAN.md` mục "Chuyện gì xảy ra sau khi bạn nói" để lấy đúng chi tiết và thời gian):

1. **Bạn** thả file vào `nguon/` của dự án (`Du an/<năm-tháng tên>/`, Claude tạo giúp) và nói một câu yêu cầu.
2. **Claude** khảo sát nguồn, gỡ băng, rồi gửi **bảng phương án** (đoạn nào giữ, đoạn nào bỏ, chỗ nào chèn chữ hay hình). Đây là **chốt duyệt 1**; sửa ở đây rẻ nhất.
3. **Claude** làm đồ họa và dựng **bản nháp** nhỏ vào `xuat-nhap/`. Bạn xem và góp ý theo mốc thời gian. Đây là **chốt duyệt 2**.
4. **Claude** xuất **bản chính** 1080p, để máy tự đo hình khớp tiếng và âm lượng, rồi tự nhìn ảnh lưới 12 khung. Đạt thì video cùng gói đăng tải vào `Thanh pham/<năm-tháng tên dự án>/`.
5. **Claude** soạn **gói đăng tải** trong `dang-tai/` mà không cần nhắc; bạn chọn, sửa, chép dán.
6. Mọi góp ý đáng nhớ của bạn được ghi vào sổ tay để clip sau không lặp lại.

Nhắc ngắn: bạn chỉ phải làm vài việc (thả file, duyệt hai chốt, bấm link tải hoặc bấm đúp `Go bang tren Mac.command` khi được nhờ); mọi lệnh khác Claude tự chạy. Thời lượng ước tính: clip 10 phút trọn quy trình khoảng 30-60 phút kể cả lúc bạn duyệt; bản chính của bài 1-3 giờ có thể mất một tới vài giờ nên cần để máy chạy.

Kết chặng: "Mình nói thêm vài thói quen giúp xưởng ra kết quả tốt hơn nhé?"

## Chặng 4. Dùng hiệu quả nhất

Đọc `HUONG-DAN.md` mục "Dùng xưởng hiệu quả nhất" (mười hai thói quen) và nói lại bằng lời của mình, không đọc nguyên văn. Chọn năm hoặc sáu thói quen quan trọng nhất cho người này, thường là:

- bắt đầu bằng một clip nhỏ có thật, làm trọn một vòng;
- quay cho dễ dựng (ngừng một nhịp giữa các ý, câu chốt đặt trước, mic gần);
- nói mục đích, người xem và nơi đăng trong một câu, và chốt điểm vào ra nếu đã biết;
- dành sức cho bảng phương án vì sửa ở đó rẻ nhất;
- góp ý theo mốc thời gian, và "chê một lần rồi dặn từ nay luôn" để xưởng học;
- tái dùng một buổi quay cho nhiều clip, và dùng gói đăng tải với thử nghiệm thumbnail.

Nếu người dùng nhắc tới sự kiện, hội thảo hay bài nói có khán giả, thêm: người xem ở nhà không ngồi trong phòng nên phần nhắc việc tại chỗ sẽ được đề xuất bỏ; chữ, thẻ và slide không bao giờ được che mặt bất kỳ ai; thumbnail xen cận mặt với khung rộng.

Kết chặng: "Còn vài điều xưởng chưa làm, mình nói thẳng để bạn khỏi mất công thử."

## Chặng 5. Giới hạn, nói thẳng

Đọc `HUONG-DAN.md` mục "Xưởng không làm gì". Cần nói rõ: không tạo hình hay giọng bằng AI; không thay người dùng quyết định sáng tạo; chất lượng đầu ra phụ thuộc chất lượng nguồn (tiếng ồn, hình tối); không tự đăng lên nền tảng nào; Windows cần rà soát thêm; một số bước cần người dùng bấm (đăng nhập khi tải nhạc Pixabay, bấm đúp `Go bang tren Mac.command`). Nhắc thêm: nhờ xưởng thứ nó không có thì nói thẳng "xưởng chưa có", đề xuất cách gần nhất, không làm đại.

Kết chặng: "Giờ mình chọn bước đầu tiên nhé."

## Chặng 6. Chọn bước đầu tiên và khép lại

Hỏi bằng AskUserQuestion, một câu: "Bạn muốn làm gì đầu tiên?", bốn lựa chọn lấy từ chặng 2 sát với người dùng nhất (ví dụ: dựng một bài giảng đã quay, cắt clip dọc từ video có sẵn, gỡ băng một file, lên kế hoạch quay mới), cộng "Để mình xem sau". Với lựa chọn đã chọn:

1. Tạo dự án cho họ bằng `python3 tools/du-an-moi.py "<tên không dấu, ngắn>"` và nói rõ cần thả gì vào `nguon/` của dự án đó.
2. Đưa đúng câu họ sẽ nói khi file đã sẵn sàng (lấy từ cột "Câu mẫu").
3. Nhắc nơi tìm hướng dẫn: `HUONG-DAN.md` cho việc hằng ngày, và câu "giới thiệu lại xưởng" để nghe lại phần này.
4. Ghi dấu đã giới thiệu: `python3 tools/cai-dat.py --danh-dau gioi-thieu`. Lần sau mở xưởng, không giới thiệu lại trừ khi họ yêu cầu.

Kết thúc bằng một câu hỏi mở thật, ví dụ: "Điều gì trong những thứ vừa nói bạn muốn thử trước?"
