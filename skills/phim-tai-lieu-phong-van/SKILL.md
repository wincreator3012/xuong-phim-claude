---
name: phim-tai-lieu-phong-van
description: Làm phim tài liệu ngắn dựa trên phỏng vấn [interview-based documentary] giới thiệu một dự án, chương trình hay sự kiện cho nhà tài trợ, đối tác và công chúng, đi trọn hai pha. TRƯỚC QUAY, nhận mô tả hoặc kịch bản dự kiến của user rồi tạo dự án, định hướng kịch bản ba hồi, brainstorm cần phỏng vấn những ai với những câu nào và cần quay những cảnh trám nào, đóng thành Kế hoạch ghi hình để user duyệt rồi mang đi quay. SAU QUAY, nhận source, gỡ băng, kiểm kê tư liệu, đối chiếu với kế hoạch, viết kịch bản thực tế [paper edit] có mốc thời gian và ước tính thời lượng để user duyệt, rồi dựng nháp, nhận góp ý theo mốc phút-giây, hoàn thiện và nghiệm thu. Kích hoạt khi user nói "phim tài liệu", "phóng sự phỏng vấn", "phim giới thiệu dự án", "phim giới thiệu chương trình", "sắp có sự kiện muốn làm phim", "video gây quỹ", "impact story", "kể chuyện dự án bằng phỏng vấn", "phỏng vấn ai, hỏi gì", "cần quay cảnh trám nào", hoặc khi thả nhiều file phỏng vấn của nhiều nhân vật khác nhau vào một dự án. KHÔNG dùng cho bài giảng một người trước máy quay (phim-dung-bai), clip ngắn dọc (phim-clip-ngan), hay podcast nhiều góc quay cùng một buổi nói (phim-multicam) - skill này gọi các skill đó ở đúng bước.
---

# Phim tài liệu phỏng vấn

Mục tiêu: từ một dự án hay sự kiện có thật, làm ra một phim ngắn (thường 4-7 phút, kèm bản gọn 60-90 giây khi cần) trong đó nhiều nhân vật kể MỘT câu chuyện, minh hoạ bằng hình ảnh thật, khiến người xem hiểu và muốn đồng hành. Khác với bài giảng một người (phim-dung-bai), ở đây lời nói đến từ nhiều file quay riêng biệt và ý nghĩa của phim nằm ở cách dệt các giọng lại với nhau.

Ba nguyên tắc xuyên suốt:

1. **Dệt giọng theo chủ đề, không theo người.** Không phát hết lời người này rồi tới người kia. Mỗi hồi truyện mượn đúng câu của đúng người, xen hình ảnh thật. Bốn góc nhìn cộng hưởng thành một câu chuyện.
2. **Người thụ hưởng ở trung tâm; cảm xúc trước, số liệu sau.** Khoảng 80% thời lượng là câu chuyện con người, 20% là con số (và con số hiện bằng đồ họa, không đọc suông). Tổ chức và nhà tài trợ ở vai bối cảnh, không ở vai nhân vật chính.
3. **Phẩm giá và đồng thuận.** Không đóng khung ai theo hướng thương hại, không kể "người hùng cứu giúp", không dàn dựng người khác kể điều không thuộc đời thật của họ. Đồng thuận bằng văn bản, trẻ em qua phụ huynh hoặc nhà trường. Danh mục "điều không nói, không hiện" lập từ đầu và giữ tới cuối.

Đọc trước: `docs/QUY-TRINH-KY-THUAT.md` (môi trường, cổng nghiệm thu, hai hệ mốc thời gian) và `phong-cach/PHONG-CACH.md` (giọng, chữ trên màn hình, chức danh nguyên văn). Mẫu các file hồ sơ ở `references/mau-ho-so.md`; nền tảng kể chuyện, kỹ thuật phỏng vấn, định lượng cảnh trám và đạo đức ở `references/ke-chuyen-phong-van.md`.

## Hai lối vào

- **Lối vào A - trước quay** (chuẩn): user mô tả sự kiện hay chương trình sắp diễn ra, kèm kịch bản hoặc mô tả dự kiến. Đi trọn Pha 1 rồi Pha 2.
- **Lối vào B - đã có source**: user thả file phỏng vấn và cảnh trám vào dự án nhưng chưa có kế hoạch. Tạo `HO-SO-PHIM.md` hồi cố từ transcript và vài câu hỏi, viết ngắn phần định hướng kịch bản (Bước 1.2) rồi vào thẳng Pha 2. Cảnh trám thiếu so với kịch bản thực tế thì đề nghị quay bổ sung hoặc thay bằng ảnh tĩnh và đồ họa.

## Cấu trúc dự án

```
du-an/<tên phim>/
  HO-SO-PHIM.md            nguồn sự thật giữa các phiên: bối cảnh, mục tiêu, khán giả, độ dài,
                           thông điệp lõi, tên phim tạm, điều không nói/không hiện, quyết định đã chốt,
                           trạng thái tiến độ
  KE-HOACH-GHI-HINH.md     Pha 1: định hướng kịch bản, nhân vật + câu hỏi, danh mục cảnh trám,
                           checklist ngày quay (Cổng duyệt 1)
  nguon/phong-van/         mỗi file một nhân vật (hoặc một phần), tên file = tên + vai
  nguon/canh-tram/         cảnh không lấy tiếng, tên file mô tả nội dung
  nguon/su-kien/           ghi hình sự kiện có tiếng (lễ ký kết, phát biểu) nếu có
  nguon/anh/               ảnh tĩnh
  transcript/              phim-transcript tạo
  KIEM-KE-NGUON.md         Pha 2: kiểm kê tư liệu thật, đối chiếu với kế hoạch
  KICH-BAN-THUC-TE.md      Pha 2: kịch bản thực tế có mốc thời gian (Cổng duyệt 2)
  SO-GOP-Y.md              từng vòng nháp: điểm góp ý, mốc, xử lý, cách đã kiểm
  do-hoa/<ngang|doc>/ + do-hoa/job/   đồ họa render và job JSON gốc (giữ tới khi giao)
  timeline.json, xuat-nhap/, xuat-hoan-chinh/   như mọi dự án khác
```

User đã tự sắp thư mục theo cách khác (ví dụ "Lấy voice" / "Không lấy voice") thì giữ nguyên, ghi ánh xạ vào `HO-SO-PHIM.md`, không bắt đổi tên.

## Pha 1 - Trước quay

### Bước 1.1 - Nhận đầu vào, tạo hồ sơ

Đọc hết những gì user đưa: mô tả chương trình, kịch bản dự kiến, tài liệu giới thiệu, danh sách người tham gia. Hỏi MỘT lượt, tối đa bốn câu, chỉ những gì tài liệu không trả lời: (1) phim làm cho ai xem trước nhất và để họ làm gì sau khi xem; (2) độ dài mong muốn và nơi phát (gửi riêng nhà tài trợ, website, mạng xã hội); (3) ngày quay, có bao nhiêu thời gian với từng người, có máy thứ hai không; (4) điều không được nói hay hiện, và ai có quyền duyệt bản cuối. Không có câu trả lời thì chọn mặc định (bản đầy đủ 5-6 phút cho nhà tài trợ và đối tác, bản gọn 60-90 giây cho mạng xã hội làm sau) và ghi rõ là giả định.

Tạo `du-an/<tên>/` với cấu trúc trên và viết `HO-SO-PHIM.md` theo mẫu.

### Bước 1.2 - Định hướng kịch bản

Viết phần đầu của `KE-HOACH-GHI-HINH.md`:

- **Thông điệp lõi** một câu: người xem đi ra khỏi phim với điều gì trong đầu.
- **Khung ba hồi**: vấn đề (khoảng trống thật, kể qua một hoàn cảnh cụ thể) - can thiệp (ai làm gì, mô hình ra sao, nhấn vào phần đã thành hình thật) - chuyển hoá và cam kết (khoảnh khắc thay đổi cụ thể, rồi cam kết cho chặng tới). Với phim về một sự kiện, biến thể là trước - trong - sau; với hành trình cá nhân, biến thể là xuất phát - ngã rẽ - hiện tại. Mỗi hồi ghi hai dòng: "cần lời của ai" và "cần thấy gì".
- **Câu hỏi neo** dự kiến: câu hỏi mà cả phim cùng trả lời, sẽ hiện thành chữ trên hình ở cuối hồi 1.
- **Cách kết**: theo giọng của user trong `PHONG-CACH.md`; mặc định là một câu tầm nhìn của nhân vật rồi một câu hỏi mở cho người xem, không lời kêu gọi khô cứng. User muốn có lời mời hành động rõ thì ghi một dòng, đặt sau câu hỏi.
- **Hình ảnh mở đầu**: 1,5-2 giây cảnh động thật (không mở thẳng bằng mặt người nói), rồi câu móc [hook] của một nhân vật, rồi thẻ tiêu đề.
- **Độ dài mục tiêu** và phân bổ thô theo hồi (ví dụ 25 giây mở, 70 giây hồi 1, 100 giây hồi 2, 110 giây hồi 3, 15 giây kết).

### Bước 1.3 - Nhân vật và câu hỏi

Lập **bảng nhân vật**: tên, chức danh hiển thị chính xác (hỏi lại và ghi nguyên văn, đây là chữ sẽ lên bảng tên), vai trong câu chuyện, phục vụ hồi nào, thời gian có được. Vai thường gặp: người thụ hưởng hoặc người gần họ nhất, người thực hành tại chỗ, người khởi xướng, đối tác hay lãnh đạo cam kết, người quan sát độc lập. Ba tới năm người là đủ cho phim 5-6 phút; ưu tiên người thụ hưởng và người thực hành trực tiếp, người của tổ chức ở vai bối cảnh. Đề xuất cả những người user chưa nghĩ tới nếu câu chuyện thiếu một góc nhìn.

Với mỗi người soạn **5-8 câu hỏi**, mỗi câu ghi: hồi phục vụ, soundbite mong đợi (một câu trọn nghĩa 10-25 giây), gợi ý đào sâu nếu câu trả lời còn chung chung. Quy tắc soạn:

- Câu mở, bắt đầu bằng "kể cho tôi nghe về...", "điều gì khiến...", "chị còn nhớ lần...". Không hỏi có/không, không hỏi câu dẫn sẵn đáp án, mỗi câu một ý.
- Xin **khoảnh khắc cụ thể** thay vì đánh giá chung: "lần đầu một em tự tìm đến chị là lúc nào, chuyện gì xảy ra" cho ra lời đắt hơn "chương trình hiệu quả thế nào".
- Luôn có một câu để lấy lời cho cảnh thiết lập: "chị mô tả nơi này cho người chưa từng tới" hoặc "một ngày ở đây bắt đầu thế nào".
- Thứ tự: câu dễ, ấm trước; câu về khoảnh khắc chuyển hoá đặt giữa buổi khi người nói đã thoải mái; hai câu chốt luôn có: "còn điều gì chị muốn nói mà tôi chưa hỏi" và "nếu nói một câu với <khán giả của phim>, chị sẽ nói gì".
- Ghi kèm lời nhắc cho người phỏng vấn: nhắc nhân vật nói trọn câu không phụ thuộc vào câu hỏi (đưa chủ ngữ vào câu trả lời), im lặng 2-3 giây sau mỗi câu trả lời, vấp thì nói lại từ đầu câu, câu đắt thì xin nói lại một lần cho bản sạch.

Ngân hàng câu hỏi theo vai ở `references/mau-ho-so.md`, dùng làm điểm xuất phát rồi viết riêng cho từng người theo tài liệu thật.

### Bước 1.4 - Danh mục cảnh trám

Cảnh trám [B-roll] làm bốn việc, mỗi cảnh trong danh mục phải ghi rõ nó làm việc nào: **thiết lập** (người xem biết mình đang ở đâu), **minh hoạ** (cho thấy đúng điều đang được nói), **che cắt** (giấu mối nối giữa hai câu), **thở** (nghỉ mắt sau đoạn dày). Suy danh mục ngược từ kịch bản: mỗi ý hay lời khẳng định trong ba hồi cần một cảnh minh hoạ cụ thể; mỗi lần chuyển hồi hay đổi bối cảnh cần một cảnh thiết lập; mỗi nhân vật cần một cảnh "đang làm việc của mình" để giới thiệu họ bằng hình trước khi họ nói; các cảnh tương tác thật giữa người với người (không dàn dựng) là chất liệu quý nhất; sự kiện cần đủ bộ: toàn cảnh, trung cảnh, cận chi tiết (tay ký, bắt tay, chữ trên văn bản), phản ứng người dự.

Bảng danh mục: mã (T01, T02...), chủ thể, cỡ cảnh (toàn / trung / cận), chuyển động (tĩnh hoặc lướt chậm), thời lượng tối thiểu, công dụng, phục vụ câu nói hay hồi nào. Một dòng "sinh hoạt đầu giờ" là chưa dùng được; "cận, tay học sinh xếp ghế, máy tĩnh, 12 giây, minh hoạ cho lời cô hiệu trưởng về nếp sinh hoạt" mới dùng được.

Định lượng: một cảnh dùng được cho mỗi 20-30 giây phim hoàn chỉnh; quay gấp 2-3 lần danh mục (nhiều góc, nhiều cỡ); **mỗi cảnh giữ máy tối thiểu 10 giây** (cảnh bị khoá 5-6 giây là thiếu hụt hay gặp nhất ở bước dựng); ba cỡ cảnh cho mỗi chủ thể; ghi 30 giây tiếng môi trường ở mỗi bối cảnh. Ghi thêm cột "có sẵn từ đâu" cho những gì user đã có (ảnh cũ, clip cũ).

### Bước 1.5 - Checklist ngày quay

Chép nguyên khối checklist từ mẫu vào cuối `KE-HOACH-GHI-HINH.md`: khung hình phỏng vấn (ngang 16:9, người ở một phần ba khung, chừa một phần ba dưới trống cho bảng tên và chữ nổi bật, không quay cận sát mặt, nền không rối, nhìn người hỏi ngồi cạnh máy), tiếng (mic gần, ghi tiếng phòng 20-30 giây, không quay cạnh máy lạnh hay đường lớn), máy thứ hai nếu có (góc chéo hoặc cỡ khác, tự thu tiếng, để phim-multicam khớp bằng âm thanh), đồng thuận (giấy đồng thuận hình ảnh nêu dùng ở đâu, bao lâu, quyền rút lại; trẻ em qua phụ huynh hoặc nhà trường; hỏi ai cần xem trước bản cuối), đặt tên file theo nội dung ngay khi chép vào máy.

### Cổng duyệt 1 - Kế hoạch ghi hình

Trình `KE-HOACH-GHI-HINH.md` cho user duyệt hoặc sửa. Kế hoạch được duyệt là thứ user mang đi quay; nếu user cần mang ra hiện trường, đề nghị xuất PDF hay DOCX theo skill tương ứng. Ghi trạng thái vào `HO-SO-PHIM.md`. Trong lúc chờ quay, không làm gì thêm ở dự án này.

## Pha 2 - Sau quay

### Bước 2.1 - Nhận source, kiểm kê

- `mediainfo.py` toàn bộ file. Phỏng vấn: gỡ băng theo phim-transcript rồi `nghiem-thu.py transcript`; các đoạn im lặng dài thật (người nói dừng suy nghĩ) là bình thường, ghi chú lại để không nhầm với lỗi gỡ băng. Sự kiện có tiếng: chỉ gỡ băng nếu có lời phát biểu định dùng; lễ ký kết thường chỉ cần hình.
- Cảnh trám: `ffprobe` thời lượng THẬT từng file (clip bị khoá 5-6 giây phải biết ngay từ đây), trích lưới khung hình (một khung mỗi 2-3 giây, hoặc 6 khung mỗi clip) để xem bằng mắt và ghi nội dung thật, khoảnh khắc đáng dùng (ánh mắt, nụ cười, tương tác), lỗi (rung, ngược sáng, người nhìn máy, lộ điều không được hiện). File "full" quay liên tục hàng chục phút: lấy mẫu rải rác, thường chỉ dùng làm cảnh thiết lập, không săn khoảnh khắc trong đó nếu đã có clip ngắn lọc sẵn.
- Khám màu toàn bộ nguồn theo phim-mau-sac; phỏng vấn nhiều người ở nhiều bối cảnh thì kê đơn theo từng file, không ép một đơn chung.
- Ảnh tĩnh: liệt kê, ghi dùng cho đâu.

Viết `KIEM-KE-NGUON.md` theo mẫu, phần quan trọng nhất là **bảng đối chiếu kế hoạch với thực tế**: từng câu hỏi dự kiến có lời đạt không, từng cảnh trám dự kiến có quay được không, những gì có mà không nằm trong kế hoạch (thường là quà: phát hiện đẹp ngoài dự tính). Lối vào B không có kế hoạch để đối chiếu thì bảng này chỉ có cột "thực tế" và "còn thiếu".

### Bước 2.2 - Đọc transcript như biên tập viên

Đọc trọn transcript từng người một lượt trước khi cắt. Đánh dấu soundbite [selects] cho từng hồi kèm mốc `start`-`end`, chấm ba mức: đắt (giữ gần nguyên văn), dùng được (có thể rút gọn), dự phòng. Tiêu chí câu đắt: cụ thể, có hình ảnh trong lời, có cảm xúc thật, đứng một mình vẫn hiểu. Ghi riêng **khoảnh khắc đắt nhất của cả phim** (thường là một câu chuyện nhỏ có lời thoại) để dành cho vị trí đẹp nhất ở hồi 3 và giữ hình người nói suốt đoạn đó. Tìm câu hỏi neo và câu kết THẬT trong lời nhân vật (thay cho câu dự kiến nếu lời thật hay hơn). Ghi các cụm nhạy phải cắt (tên riêng, chi tiết trong danh mục không nói) kèm mốc, và chất lượng tiếng từng bite.

### Bước 2.3 - Kịch bản thực tế [paper edit]

Viết `KICH-BAN-THUC-TE.md` theo mẫu: khung ba hồi đã điều chỉnh theo lời thật (kế hoạch phục vụ phim, không ngược lại), rồi từng dòng dựng theo thứ tự phát: file nguồn, `in`-`out` theo transcript (ghi câu đầu và câu cuối của bite), thời lượng, trích lời rút gọn, cảnh trám phủ lên (file, đoạn, lý do), đồ họa (pill, thẻ, số liệu) và vị trí dự kiến, cầu nối giữa hai người nói. Nguyên tắc thể loại đã kiểm chứng:

- Mở đầu bằng 1,5-2 giây cảnh động thật trước khi thấy mặt người nói đầu tiên; câu móc rồi mới tới thẻ tiêu đề.
- Giữa hai nhân vật khác nhau chèn một cầu nối 2-3 giây bằng một hoặc hai cảnh trám (segment riêng, `fadeIn`/`fadeOut` khoảng 0,15 giây), không cắt thẳng mặt sang mặt.
- Câu hỏi neo và câu kết chiêm nghiệm hiện dưới dạng overlay bán trong suốt (Benefits một mục, `wrap:true`) đè lên cảnh thật, không cắt sang thẻ toàn màn hình.
- Danh sách cấu phần (các gói, các bước) làm MỘT overlay tích luỹ (các mục hiện dần và ở lại), không phải nhiều pill rời hiện rồi mất.
- Con số nổi bật (số năm, số tháng, số người) làm pill hoặc `InfoStat` đúng lúc lời nói nhắc tới; khép vòng số liệu nếu được (ví dụ "3 năm đã qua" ở hồi 2 và "3 năm tới" ở hồi 3).
- Đoạn đắt nhất: ít cắt, ít đồ họa, giữ mặt người nói; cảnh trám chỉ dùng khi lời nhắc tới một hình ảnh cụ thể có sẵn trong nguồn.
- Cảnh sự kiện (ký kết) đặt ở chỗ lời nói về cam kết, không rải khắp phim.

Cuối kịch bản bắt buộc có: **tổng thời lượng ước tính** theo hồi (cộng các bite và cầu nối); nếu vượt mục tiêu quá 30% thì đề xuất ngay hai phương án (bản đầy đủ và bản gọn, ghi rõ bỏ bite nào) để user chọn TRƯỚC khi dựng, không dựng bản dài rồi cắt qua nhiều vòng; **danh sách quyết định cần user**: tên phim cho thẻ tiêu đề, người tổ chức hay người quay có xuất hiện trong phim không, overlay nào không có câu nói tương ứng trong lời (callout biên tập) và đặt ở đâu vì sao, cụm nhạy nào đã cắt; **cảnh trám còn thiếu** và cách bù (quay bổ sung với mô tả cụ thể theo Bước 1.4, ảnh tĩnh qua Ken Burns theo phim-tu-lieu, hay đồ họa).

### Cổng duyệt 2 - Kịch bản thực tế

User đọc `KICH-BAN-THUC-TE.md` trong khoảng mười phút mà không cần mở video, trả lời các quyết định, sửa gì cứ nói. Được duyệt mới dựng.

### Bước 2.4 - Dựng nháp

Chuyển kịch bản thành `timeline.json` theo phim-dung-bai và `references/bien-tap.md` của skill đó (mốc `in`/`out` snap vào khoảng lặng thật; cụm nhạy nằm giữa một chunk gỡ băng thì tìm khoảng lặng bằng `silencedetect` trên cửa sổ 3-4 giây quanh vị trí ước lượng theo tỷ lệ ký tự, đặt `snap:false` cho đoạn đó). Đồ họa theo phim-do-hoa; intro, outro, thẻ chuyển dùng làm `insert` phải ép lại tiếng bằng đúng thời lượng hình ngay sau khi render (`ffmpeg -i x.mp4 -t <thời lượng hình> -c:v copy -c:a aac -b:a 192k`) rồi `ffprobe` kiểm hình bằng tiếng trước khi vào timeline. Job JSON của mọi đồ họa lưu trong `do-hoa/job/` của dự án cho tới khi giao xong, vì vòng góp ý sau thường chỉ cần đổi một trường rồi render lại.

Quy tắc riêng của thể loại khi soạn timeline:

- Khung hình phỏng vấn ngồi có mặt ở nửa trên khung: pill dùng `position:'bottom'` (đã là mặc định của Benefits), vẫn phải kiểm bằng khung hình thật ở trạng thái tích luỹ đầy đủ; không bao giờ che mặt.
- Quy tắc tối thiểu 5 giây cảnh chính giữa hai thẻ toàn màn hình áp dụng cả cho một lần lộ mặt ngắn dưới 5 giây xen giữa hai cảnh trám: nối liền cảnh trám thay vì để khe hở lộ mặt.
- Gộp khối cảnh trám: `ffprobe` thời lượng thật từng clip trước, clip bị khoá thời lượng thì xếp nối đuôi ở đúng trần đó (`at` sau = `at` trước cộng thời lượng) để tạo khối liên tục, không giả định kéo dài được.
- Overlay cần hiện SAU khi cảnh trám trong cùng segment đã kết thúc: tách segment tại đúng điểm cảnh trám kết thúc thành hai sub-segment liền mạch (`out` = `in` kế tiếp), overlay tính `at` từ sub-segment mới.
- Cảnh thật có tiếng học sinh, đám đông: `volumeDb` khoảng -12 để làm nền dưới lời nói; cảnh cầu nối tự nó có tiếng thì cũng hạ tương tự.
- `chapter` đặt theo hồi để có danh sách chương khi đăng.

Dựng: `assemble.py --kiem-tra`, rồi `--preview` với `--out "<tên>-<khung>-nhap1"` tường minh ngay từ nháp đầu (mọi nháp sau tăng số, không để tên mặc định vì sẽ ghi đè lẫn nhau), rồi `nghiem-thu.py video --nhap --anh`. Ngoài cổng máy, tự kiểm bằng mắt: lưới khung hình toàn phim, và với TỪNG overlay trích khung hình tại mốc thật tính từ `<thành phẩm>.map.json` rồi đọc đoạn transcript bao quanh để chắc chữ khớp ý đang nói, không chỉ khớp chính tả.

### Bước 2.5 - Vòng góp ý

User góp ý theo mốc phút-giây trên chính bản nháp đang xem (mốc trên bản render đáng tin hơn mọi suy luận ngược). Ghi mọi điểm vào `SO-GOP-Y.md` theo mẫu: nháp số, điểm số, mốc, nội dung góp ý, cách xử lý, cách đã kiểm (khung hình tại mốc nào của `map.json` mới). Mỗi vòng dựng ra `nhapN+1` với `--out` tường minh, tính lại mọi mốc kiểm từ `map.json` của chính bản mới. Điểm góp ý neo vào một từ khoá mà transcript gần đó không có: dùng điểm ngắt câu sạch gần nhất và BÁO RÕ cho user, không lặng lẽ giả định. Một loại góp ý lặp lần thứ hai (pill che mặt, chữ sai chức danh) là tín hiệu sửa nguồn mặc định (defaultProps, brand, preset) chứ không chỉ sửa dự án này, ghi vào "Sổ tay góp ý" trong `PHONG-CACH.md`.

### Bước 2.6 - Bản chính và bàn giao

Xuất 1080p với `--out` tường minh, `nghiem-thu.py video` ĐẠT, lưới khung hình đọc lại lần cuối, copy vào `xuat-hoan-chinh/`. Báo user: tên file, thời lượng, dung lượng, danh sách chương, dòng ghi công nhạc nếu dùng track CC-BY, "nghiệm thu máy: ĐẠT". Đề xuất bước tiếp: bản gọn 60-90 giây cho mạng xã hội bằng phim-clip-ngan (cắt từ đoạn đắt nhất, câu hỏi neo, hình sự kiện); bản riêng cho từng đối tác nếu họ cần dùng logo riêng; gửi nhân vật xem trước nếu đã hứa ở Bước 1.5. Cập nhật `HO-SO-PHIM.md` trạng thái hoàn tất và những gì đã học, bài học kỹ thuật đáng giữ ghi vào `docs/BAI-HOC.md`.

## Khi kết thúc mỗi phiên

Dự án này luôn kéo qua nhiều phiên (chờ quay, chờ duyệt, chờ góp ý). Trước khi dừng, `HO-SO-PHIM.md` phải nói được: đang ở bước nào, chờ ai, quyết định nào đã chốt, file nháp mới nhất tên gì. Phiên sau đọc file đó trước, không hỏi lại điều đã chốt.
