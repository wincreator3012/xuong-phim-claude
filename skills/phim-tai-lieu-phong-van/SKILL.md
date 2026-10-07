---
name: "phim-tai-lieu-phong-van"
description: "Làm phim tài liệu ngắn dựa trên phỏng vấn nhiều nhân vật, giới thiệu một dự án, chương trình hay sự kiện có thật cho nhà tài trợ, đối tác và công chúng, đi hai pha: trước quay lên Kế hoạch ghi hình (phỏng vấn ai, hỏi gì, quay cảnh trám nào, checklist ngày quay), sau quay kiểm kê tư liệu, viết kịch bản thực tế có kiểm chứng dữ kiện rồi mới dựng và nhận góp ý theo nhãn đoạn. Kích hoạt khi user nói \"phim tài liệu\", \"phóng sự phỏng vấn\", \"phim giới thiệu dự án\", \"video gây quỹ\", \"phim cho nhà tài trợ\", \"lên kế hoạch quay phỏng vấn\", hoặc thả nhiều file phỏng vấn của nhiều người vào dự án. KHÔNG dùng cho bài giảng một người nói (phim-dung-bai), podcast hay buổi quay nhiều góc máy của cùng một cuộc trò chuyện (phim-multicam), clip ngắn cắt từ tư liệu có sẵn (phim-clip-ngan), hay video chỉ có giọng ghi âm (phim-infomotion)."
---

# Phim tài liệu phỏng vấn

Mục tiêu: từ một dự án hay sự kiện có thật, làm ra một phim ngắn (thường 4-7 phút, kèm bản gọn 60-90 giây khi cần) trong đó nhiều nhân vật kể MỘT câu chuyện, minh hoạ bằng hình ảnh thật, khiến người xem hiểu và muốn đồng hành. Khác với bài giảng một người (phim-dung-bai), lời nói đến từ nhiều file quay riêng và ý nghĩa của phim nằm ở cách dệt các giọng lại với nhau.

Bốn nguyên tắc xuyên suốt:

1. **Dệt giọng theo chủ đề, không theo người.** Không phát hết lời người này rồi tới người kia. Mỗi hồi mượn đúng câu của đúng người, xen hình ảnh thật.
2. **Người thụ hưởng ở trung tâm; cảm xúc trước, số liệu sau.** Khoảng 80% thời lượng là câu chuyện con người, 20% là con số (hiện bằng đồ họa, không đọc suông). Tổ chức và nhà tài trợ ở vai bối cảnh.
3. **Phẩm giá và đồng thuận.** Không đóng khung ai theo hướng thương hại, không kể "người hùng cứu giúp", không dàn dựng người khác kể điều không thuộc đời thật của họ. Đồng thuận bằng văn bản, trẻ em qua phụ huynh hoặc nhà trường. Danh mục "điều không nói, không hiện" lập từ đầu và giữ tới cuối.
4. **Chữ trên màn hình phải kiểm được; lời nhân vật giữ nguyên.** Mọi dữ kiện lên đồ họa (con số, năm, tên tổ chức, chức danh, trích dẫn, tác giả của một mô hình) có nguồn đối chiếu ghi ngay trong kịch bản thực tế. Nhân vật nói lệch dữ kiện thì không sửa lời, không dựng cho họ nói khác, không đè chữ đúng lên lời sai: chọn một trong ba cách ở Bước 2.3. Hình do AI tạo không thay cho hình thật về người, nơi chốn, sự kiện của dự án.

Đọc trước: `skills/_chung/van-hanh.md`, `skills/_chung/timeline-va-dung.md`, `skills/_chung/overlay-va-the.md`, `skills/_chung/nghiem-thu-dung-y.md`, `docs/BAI-HOC.md` chủ đề "Phim tài liệu phỏng vấn". Mẫu các file hồ sơ, checklist ngày quay và ngân hàng câu hỏi theo vai: `skills/phim-tai-lieu-phong-van/references/mau-ho-so.md`. Nền tảng kể chuyện, kỹ thuật phỏng vấn, định lượng cảnh trám, đạo đức, ba lớp đồ họa, nhãn đoạn và bài học dự án thật: `skills/phim-tai-lieu-phong-van/references/ke-chuyen-phong-van.md`.

## Bối cảnh riêng của xưởng "xuong-phim-claude"

- Mẫu cấu trúc thư mục dự án: `tools/mau-du-an/tai-lieu-phong-van/`; bài học từ dự án thật đã chưng cất ở `ke-chuyen-phong-van.md` mục 6. Gặp tình huống lạ thì đọc mục đó trước khi nghĩ cách mới.
- Người dùng thường là một phần của đội dự án được làm phim. Hỏi sớm (Bước 1.1 hoặc 2.3) người dùng có muốn xuất hiện trong phim không; mặc định là không, để phim thuộc về nhân vật và người thụ hưởng. Nếu có, chức danh theo `phong-cach/PHONG-CACH.md` mục 1.
- Logo các bên thả vào `brand/logo/` và truyền qua props `logos` của preset intro, outro (hàng 1-3 logo).
- Cách kết mặc định: một câu tầm nhìn của nhân vật rồi một câu hỏi mở thật cho người xem, không lời kêu gọi tài trợ trực tiếp.

## Hai lối vào

- **Lối vào A - trước quay** (chuẩn): user mô tả sự kiện hay chương trình sắp diễn ra. Đi trọn Pha 1 rồi Pha 2.
- **Lối vào B - đã có source**: user thả file phỏng vấn và cảnh trám nhưng chưa có kế hoạch. Tạo `HO-SO-PHIM.md` hồi cố từ transcript và vài câu hỏi, viết ngắn phần định hướng (Bước 1.2) rồi vào thẳng Pha 2. Cảnh trám thiếu thì đề nghị quay bổ sung hoặc thay bằng ảnh tĩnh và đồ họa.

## Cấu trúc dự án

```
Du an/<tên phim>/
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
  SO-GOP-Y.md              từng vòng nháp: điểm góp ý, nhãn, mốc, xử lý, cách đã kiểm
  NHAN-DOAN.md             nhãn ổn định (A/B/T/M) đối chiếu mốc hiện tại, tools/nhan-doan.py tạo lại
  do-hoa/<ngang|doc>/ + do-hoa/job/   đồ họa render và job JSON gốc (giữ tới khi giao)
  timeline.json, xuat-nhap/, xuat-hoan-chinh/   như mọi dự án khác
```

User đã tự sắp thư mục theo cách khác (ví dụ "Lấy voice" / "Không lấy voice") thì giữ nguyên, ghi ánh xạ vào `HO-SO-PHIM.md`.

## Pha 1 - Trước quay

### Bước 1.1 - Nhận đầu vào, tạo hồ sơ

Đọc hết những gì user đưa. Hỏi MỘT lượt, tối đa bốn câu, chỉ những gì tài liệu không trả lời: (1) phim làm cho ai xem trước nhất và để họ làm gì sau khi xem; (2) độ dài và nơi phát; (3) ngày quay, thời gian với từng người, có máy thứ hai không; (4) điều không được nói hay hiện, và ai duyệt bản cuối. Không có câu trả lời thì mặc định bản đầy đủ 5-6 phút cho nhà tài trợ và đối tác, bản gọn 60-90 giây làm sau, ghi rõ là giả định. Tạo `Du an/<tên>/` và viết `HO-SO-PHIM.md` theo mẫu.

### Bước 1.2 - Định hướng kịch bản

Viết phần đầu `KE-HOACH-GHI-HINH.md` (lý do từng mục: `ke-chuyen-phong-van.md` mục 1):

- **Thông điệp lõi** một câu.
- **Khung ba hồi**: vấn đề (khoảng trống thật, qua một hoàn cảnh cụ thể) - can thiệp (ai làm gì, nhấn phần đã thành hình thật) - chuyển hoá và cam kết. Biến thể: sự kiện thì trước - trong - sau; hành trình cá nhân thì xuất phát - ngã rẽ - hiện tại. Mỗi hồi hai dòng: "cần lời của ai", "cần thấy gì".
- **Câu hỏi neo** dự kiến, hiện thành chữ trên hình cuối hồi 1.
- **Cách kết** theo giọng của người dùng, xem `phong-cach/PHONG-CACH.md` mục 3 và 6 (mặc định ở mục "Bối cảnh riêng"). User muốn lời mời hành động rõ thì ghi một dòng, đặt sau câu hỏi.
- **Hình ảnh mở đầu**: chuỗi 3-4 cảnh động thật ngắn (toàn cảnh, chi tiết tay hoặc vật, một khuôn mặt thoáng qua chưa nói), mỗi cảnh 1,5-2 giây, tổng 5-8 giây; rồi câu móc của một nhân vật; rồi thẻ chuyển tiêu đề.
- **Độ dài mục tiêu** và phân bổ thô theo hồi.

### Bước 1.3 - Nhân vật và câu hỏi

**Bảng nhân vật**: tên, chức danh hiển thị NGUYÊN VĂN (hỏi lại và ghi đúng, đây là chữ lên bảng tên), vai trong câu chuyện, phục vụ hồi nào, thời gian có được. Ba tới năm người là đủ cho phim 5-6 phút; ưu tiên người thụ hưởng và người thực hành trực tiếp; đề xuất cả góc nhìn user chưa nghĩ tới nếu câu chuyện thiếu.

Mỗi người **5-8 câu hỏi**, mỗi câu ghi hồi phục vụ, soundbite mong đợi (một câu trọn nghĩa 10-25 giây), gợi ý đào sâu. Quy tắc soạn câu hỏi, thứ tự, hai câu chốt và lời nhắc cho người phỏng vấn: `ke-chuyen-phong-van.md` mục 2. Ngân hàng câu hỏi theo vai: `mau-ho-so.md` mục "Ngân hàng câu hỏi theo vai", dùng làm điểm xuất phát rồi viết riêng theo tài liệu thật.

### Bước 1.4 - Danh mục cảnh trám

Mỗi cảnh ghi rõ nó làm việc nào trong bốn việc: **thiết lập**, **minh hoạ**, **che cắt**, **thở**. Suy danh mục ngược từ kịch bản; mỗi nhân vật cần một cảnh "đang làm việc của mình"; sự kiện cần đủ bộ toàn, trung, cận chi tiết, phản ứng người dự. Bảng: mã (T01...), chủ thể, cỡ, chuyển động, thời lượng tối thiểu, công dụng, phục vụ câu nào, có sẵn từ đâu. Định lượng (một cảnh cho mỗi 20-30 giây phim, quay gấp 2-3 danh mục, giữ máy tối thiểu 10 giây, ba cỡ mỗi chủ thể, 30 giây tiếng môi trường mỗi bối cảnh) và ví dụ dòng dùng được: `ke-chuyen-phong-van.md` mục 3.

### Bước 1.5 - Checklist ngày quay

Chép nguyên khối checklist từ `mau-ho-so.md` mục D vào cuối `KE-HOACH-GHI-HINH.md` (khung hình phỏng vấn, tiếng, máy thứ hai, cách hỏi, đồng thuận, sau buổi quay).

### Cổng duyệt 1 - Kế hoạch ghi hình

Trình `KE-HOACH-GHI-HINH.md` cho user duyệt hoặc sửa; đây là thứ user mang đi quay (cần mang ra hiện trường thì đề nghị xuất PDF hay DOCX). Ghi trạng thái vào `HO-SO-PHIM.md`. Trong lúc chờ quay, không làm gì thêm ở dự án này.

## Pha 2 - Sau quay

### Bước 2.1 - Nhận source, kiểm kê

- `mediainfo.py` toàn bộ file. Phỏng vấn: gỡ băng theo phim-transcript rồi `nghiem-thu.py transcript`; khoảng im lặng dài thật (người nói dừng suy nghĩ) ghi chú lại để không nhầm với lỗi gỡ băng. Sự kiện có tiếng: chỉ gỡ băng nếu định dùng lời.
- Cảnh trám: `ffprobe` thời lượng THẬT từng file (clip bị khoá 5-6 giây phải biết ngay), trích lưới khung hình (một khung mỗi 2-3 giây, hoặc 6 khung mỗi clip) để xem bằng mắt và ghi nội dung thật, khoảnh khắc đáng dùng, lỗi. File "full" quay liên tục hàng chục phút: lấy mẫu rải rác, thường chỉ làm cảnh thiết lập.
- Khám màu theo phim-mau-sac, kê đơn theo từng file khi nhiều bối cảnh.

Viết `KIEM-KE-NGUON.md` theo mẫu; phần quan trọng nhất là **bảng đối chiếu kế hoạch với thực tế** (câu hỏi nào có lời đạt, cảnh trám nào quay được, những gì có mà ngoài kế hoạch). Lối vào B chỉ có cột "thực tế" và "còn thiếu".

### Bước 2.2 - Đọc transcript như biên tập viên

Đọc trọn transcript từng người trước khi cắt. Đánh dấu soundbite [selects] cho từng hồi kèm mốc, chấm ba mức: đắt, dùng được, dự phòng (câu đắt: cụ thể, có hình ảnh trong lời, có cảm xúc thật, đứng một mình vẫn hiểu). Ghi riêng **khoảnh khắc đắt nhất của cả phim** để dành cho hồi 3 và giữ mặt người nói suốt đoạn đó. Tìm câu hỏi neo và câu kết THẬT trong lời nhân vật. Ghi các cụm nhạy phải cắt kèm mốc, chất lượng tiếng từng bite, và mọi **dữ kiện kiểm được** trong lời (con số, năm, tên chương trình, người, tổ chức, trích dẫn) kèm mốc: đầu vào cho cột "Kiểm chứng".

### Bước 2.3 - Kịch bản thực tế [paper edit]

Viết `KICH-BAN-THUC-TE.md` theo mẫu: khung ba hồi đã điều chỉnh theo lời thật (kế hoạch phục vụ phim, không ngược lại), rồi từng dòng dựng theo thứ tự phát: **nhãn ổn định**, file nguồn, `in`-`out` (câu đầu, câu cuối của bite), thời lượng, trích lời rút gọn, cảnh trám phủ lên, đồ họa và vị trí dự kiến, cầu nối, cột "Kiểm chứng". Nhãn: `A<n>` đoạn lời liên tục, `T<n>` cầu nối độc lập, `M<n>` từng cú trong chuỗi mở đầu; `B<n>.<m>` không gán tay (`tools/nhan-doan.py` tự suy). Gán một lần ở đây, giữ nguyên qua mọi nháp (`ke-chuyen-phong-van.md` mục 8).

Nguyên tắc thể loại đã kiểm chứng (lý do và dự án gốc: `ke-chuyen-phong-van.md` mục 1, 4, 6): mở bằng chuỗi 3-4 cảnh động trước mặt người nói đầu tiên; cầu nối 2-3 giây bằng cảnh trám giữa hai nhân vật (segment riêng, fade khoảng 0,15 giây), không cắt thẳng mặt sang mặt; cắt câu nhiều vòng, mỗi lần neo vào khoảng lặng thật, ghi mốc cũ và mới vào `SO-GOP-Y.md`; câu hỏi neo và câu kết là overlay Benefits một mục đè lên cảnh thật; danh sách cấu phần là MỘT overlay tích luỹ; con số nổi bật làm pill hoặc `InfoStat` đúng lúc lời nhắc, khép vòng số liệu nếu được; đoạn đắt nhất ít cắt, ít đồ họa, giữ mặt người nói; cảnh sự kiện đặt đúng chỗ lời nói về cam kết.

**Cổng kiểm chứng.** Mỗi dòng có đồ họa mang dữ kiện ghi nguồn vào cột "Kiểm chứng": tài liệu của tổ chức (tên file, trang), trang web chính thức, văn bản ký kết, chức danh nguyên văn trong bảng nhân vật hoặc `phong-cach/PHONG-CACH.md`, hoặc người có thẩm quyền đã xác nhận (ai, ngày nào). Dữ kiện công khai thì tra web và ghi đường dẫn; không tìm ra thì ghi "chưa kiểm được", không để trống. Callout biên tập (overlay không có câu nói tương ứng) cũng phải có nguồn. Dữ kiện chưa kiểm được hoặc lệch nguồn không lên đồ họa; đưa vào danh sách quyết định kèm bằng chứng và ba cách: (1) nhờ tổ chức hoặc nhân vật xác nhận rồi mới hiện; (2) giữ lời nguyên văn, đồ họa không lặp dữ kiện; (3) bỏ câu, thay bằng một bite khác cùng ý. Không tự chọn thay user.

Cuối kịch bản bắt buộc có: **tổng thời lượng ước tính** theo hồi do `python3 tools/uoc-luong.py "../Du an/<x>/KICH-BAN-THUC-TE.md"` cộng (không cộng tay); vượt mục tiêu quá 30% thì đề xuất ngay hai phương án (bản đầy đủ và bản gọn, ghi rõ bỏ bite nào) để user chọn TRƯỚC khi dựng; **danh sách quyết định cần user** (tên phim, dữ kiện chưa kiểm được, người tổ chức hay người quay có xuất hiện không, overlay không có câu nói tương ứng đặt ở đâu vì sao, cụm nhạy đã cắt); **cảnh trám còn thiếu** và cách bù (quay bổ sung theo mô tả Bước 1.4, ảnh tĩnh có nguồn qua phim-tu-lieu, đồ họa).

### Cổng duyệt 2 - Kịch bản thực tế

`uoc-luong.py` phải báo "KIỂM GIẤY: ĐẠT", hoặc mọi điểm "CẦN XEM" đã nằm trong danh sách quyết định. User đọc `KICH-BAN-THUC-TE.md` trong khoảng mười phút mà không cần mở video, trả lời các quyết định. Được duyệt mới dựng.

### Bước 2.4 - Dựng nháp

Chuyển kịch bản thành `timeline.json` theo phim-dung-bai và `_chung/timeline-va-dung.md`: mốc snap vào khoảng lặng thật; cụm nhạy giữa một câu gỡ băng dài thì tìm khoảng lặng bằng `silencedetect` trên cửa sổ 3-4 giây quanh vị trí ước lượng theo tỷ lệ ký tự, đặt `snap:false`; phim mở bằng câu móc rồi mới tới thẻ tiêu đề thì insert thẻ đó mang `"role": "intro"`. Chép nhãn vào trường `"label"` của từng segment (mọi sub-segment của cùng một dòng chung một nhãn); `chapter` theo hồi. Đồ họa theo phim-do-hoa; job JSON giữ trong `do-hoa/job/` tới khi giao.

Riêng thể loại này (chi tiết `ke-chuyen-phong-van.md` mục 6-7, bảng vị trí pill ở `_chung/overlay-va-the.md`):

- Ba lớp đồ họa không dùng lẫn: `LowerThird` cho mọi nhân vật khi xuất hiện lần đầu hoặc quay lại sau một khoảng dài (bắt buộc; chức danh nguyên văn từ bảng nhân vật), `Benefits` cho ý (`position:'bottom'` với phỏng vấn ngồi mặt ở nửa trên, kiểm ở trạng thái tích luỹ đầy đủ), `SectionTitle` cho ranh giới HỒI (`kicker` tên dự án lặp xuyên suốt, `title` tên hồi, `showLogos:true` ở ranh giới lớn). Cần LowerThird và pill cùng lúc thì kiểm tại đúng lúc chồng lấn.
- Quy tắc 5 giây áp cả cho một lần lộ mặt ngắn giữa hai cảnh trám: nối liền cảnh trám.
- Gộp khối cảnh trám theo thời lượng thật `ffprobe` (`at` sau = `at` trước + thời lượng), không giả định kéo dài được.
- Overlay cần hiện SAU cảnh trám trong cùng segment: tách thành hai sub-segment liền mạch.
- Cảnh thật có tiếng học sinh, đám đông: `volumeDb` khoảng -12 làm điểm khởi đầu; nghe lại rồi hạ hay nâng. Cảnh cầu nối tự nó có tiếng thì hạ tương tự.

Dựng: `assemble.py --kiem-tra`, rồi `--preview --out "<tên>-<khung>-nhap1"` (mọi nháp sau tăng số), `nghiem-thu.py video --nhap --anh`, rồi `tools/nhan-doan.py <timeline.json> <thành phẩm>.map.json --out NHAN-DOAN.md`. Soi mắt theo `_chung/nghiem-thu-dung-y.md`: lưới khung hình toàn phim, và với TỪNG overlay cặp "hình - câu đang nói" từ `map.json`.

### Bước 2.5 - Vòng góp ý

User góp ý chủ yếu theo nhãn tra trong `NHAN-DOAN.md`, kèm mốc phút giây khi cần chỉ rõ vị trí bên trong một đoạn dài; dịch nhãn sang `in`/`out` là việc của Claude. Ghi mọi điểm vào `SO-GOP-Y.md` theo mẫu (nháp, nhãn, mốc, góp ý, xử lý, cách đã kiểm). Mỗi vòng dựng `nhapN+1`, tính lại mọi mốc kiểm từ `map.json` của bản mới, chạy lại `nhan-doan.py`. Điểm góp ý neo vào một từ khoá không có trong transcript gần đó: dùng điểm ngắt câu sạch gần nhất và BÁO RÕ. Góp ý lặp lần hai (pill che mặt, sai chức danh) là tín hiệu sửa nguồn mặc định, ghi vào sổ tay góp ý của PHONG-CACH. Trước khi báo hoàn tất, một vòng tự nghe lại và siết câu chữ thêm một lượt vẫn đáng làm.

### Bước 2.6 - Bản chính và bàn giao

Xuất 1080p với `--out "<tên>-<khung>"`, `nghiem-thu.py video` ĐẠT, lưới khung hình đọc lại lần cuối, copy vào `xuat-hoan-chinh/`. Báo theo `_chung/van-hanh.md` (kèm danh sách chương, ghi công nhạc CC-BY nếu có). Đề xuất bước tiếp: bản gọn 60-90 giây bằng phim-clip-ngan; bản riêng cho từng đối tác nếu cần logo riêng; gửi nhân vật xem trước nếu đã hứa. Cập nhật `HO-SO-PHIM.md` trạng thái hoàn tất; bài học kỹ thuật vào `docs/BAI-HOC.md`, bài học kể chuyện vào `ke-chuyen-phong-van.md` mục 6.

## Khi một khâu hỏng

Nguyên tắc chung ở `_chung/van-hanh.md`. Riêng thể loại này:

- Gỡ băng một file phỏng vấn không qua `nghiem-thu.py transcript`: gỡ lại cửa sổ rộng quanh chỗ hỏng; hai lần cho kết quả khác hẳn nhau thì dừng đoạn đó, nhờ user nghe tại mốc cụ thể. Các file khác vẫn làm tiếp.
- Cảnh trám thiếu hoặc bị khoá thời lượng: không kéo dài bằng khung đứng, không lặp clip, không thay bằng hình do AI tạo; ghi vào "Cảnh trám còn thiếu" với ba cách bù để user chọn.
- Dữ kiện không kiểm được: không phải lỗi kỹ thuật, là một quyết định của user (Cổng kiểm chứng).
- Một đồ họa render lỗi: dừng riêng dòng đó, các dòng khác vẫn làm; không thay bằng đồ họa khác nội dung khi chưa hỏi.
- Dựng không qua `check_av()` hoặc `nghiem-thu.py video`: dừng, đọc bảng chẩn đoán, không giao nháp lỗi.

## Khi kết thúc mỗi phiên

Dự án này luôn kéo qua nhiều phiên. Trước khi dừng, `HO-SO-PHIM.md` phải nói được: đang ở bước nào, chờ ai, quyết định nào đã chốt, nháp mới nhất tên gì. Phiên sau đọc file đó trước, không hỏi lại điều đã chốt.

<!-- ban-nguon: phim-tai-lieu-phong-van 2026-10-07 95203654 -->
