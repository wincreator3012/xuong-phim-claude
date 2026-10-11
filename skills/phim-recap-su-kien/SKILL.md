---
name: "phim-recap-su-kien"
description: "Dựng nhanh clip RECAP, highlight, tổng kết một sự kiện hay buổi workshop từ nhiều clip quay rời (điện thoại, máy ảnh, hàng chục tệp ngắn và vài tệp dài) trong thư mục \"xuong-phim-claude\": kiểm kê và đổi tên nguồn theo giờ quay, khảo sát bằng ảnh lưới, dựng mạch theo các phần của chương trình, nhạc nền làm chính xen vài câu nói của người tổ chức, chữ nổi trích ý chính, cắt cảnh vào phách nhạc, giữ kín lời chia sẻ của người tham dự, nghiệm thu và giao. Kích hoạt khi user nói \"recap\", \"clip recap\", \"highlight sự kiện\", \"clip tổng kết\", \"ôn lại buổi hôm đó\", \"kỷ niệm buổi workshop\", \"after movie\", \"clip cảm ơn khách hàng sau chương trình\", hoặc thả một thư mục nhiều clip quay rời của một buổi. KHÔNG dùng cho bài giảng một người nói (phim-dung-bai), keynote có slide (phim-bai-giang-slide), podcast nhiều góc máy (phim-multicam), phim kể chuyện qua phỏng vấn nhiều nhân vật (phim-tai-lieu-phong-van), hay clip ngắn cắt từ một bài nói (phim-clip-ngan)."
---

# Recap sự kiện: clip tổng kết từ nhiều clip quay rời

Recap khác dựng bài: người xem chính là người đã có mặt (hoặc tổ chức đã mời người dùng đến), họ xem để sống lại vài khoảnh khắc và nhớ lại điều cốt lõi, không để học trọn một bài giảng. Vì vậy phim đi theo nhạc và khoảnh khắc, lời nói chỉ là vài điểm neo ngắn của người tổ chức. Người ta nhớ một trải nghiệm chủ yếu qua đỉnh cảm xúc và đoạn kết [peak-end rule], nên phim khép bằng khoảnh khắc chung của cả nhóm rồi mới tới lời cảm ơn. Nguồn nghiên cứu và thực hành nghề: `skills/phim-recap-su-kien/references/nghien-cuu-recap.md`.

Nguồn thường là vài chục clip điện thoại 4K HEVC (vài giây đến vài chục phút, cầm tay, tiếng phòng ồn, song ngữ). Máy làm phần đếm, cắt, đo; Claude nhìn ảnh khảo sát và chọn; người dùng duyệt mạch và nghe nhạc. Bộ lệnh: `tools/recap.py` (docstring đầu tệp liệt kê đủ lệnh và tệp sinh ra).

## Bước 0 - nền tảng và bốn câu hỏi

Đọc `skills/_chung/van-hanh.md`, `skills/_chung/timeline-va-dung.md`, `skills/_chung/overlay-va-the.md`. Tạo hồ sơ `python3 tools/du-an-moi.py "<tên>" --loai recap`. Nguồn để nguyên chỗ người dùng đặt (ổ ngoài hay thư mục đã gắn), không chép vào `nguon/`: `nguon/` chỉ chứa proxy đã cắt.

Hỏi người dùng một lượt (AskUserQuestion), vì bốn điều này đổi cả phim:

1. **Khung và độ dài**: ngang 2-3 phút cho khách hàng hay nội bộ (mặc định); dọc 45-90 giây cho mạng xã hội; cả hai thì làm bản ngang trước.
2. **Tiếng**: giữ giọng ai (người hướng dẫn, người tổ chức, đại diện khách hàng). Lời chia sẻ của người tham dự mặc định KHÔNG dùng khi buổi có nội dung riêng tư (vòng chia sẻ, chăm sóc tinh thần).
3. **Ai xem, phát hành ở đâu**: gửi riêng khách hàng hay đăng công khai. Quyết định có gói đăng tải không, có logo không, và mức đồng ý cần có của người lộ mặt (`references/danh-muc-quay.md` mục 3).
4. **Thẻ mở và kết**: tên chương trình, lời cảm ơn; logo và lời mời có hay không.

Hỏi thêm kịch bản hay chương trình buổi (tệp, Google Doc): đó là xương sống của mạch phim và nguồn trích dẫn chữ nổi. Chữ trên hình dùng NGÔN NGỮ CỦA CHƯƠNG TRÌNH: chương trình tiếng Anh thì toàn bộ thẻ, chữ nổi, tên chương bằng tiếng Anh (quy tắc chữ thuần Việt của xưởng áp cho chương trình tiếng Việt).

## Bước 1 - kiểm kê, đổi tên, khảo sát

```
python3 tools/recap.py kiem-ke "<thư mục nguồn>" --du-an "../Du an/<x>"
python3 tools/recap.py khao-sat --du-an "../Du an/<x>" --tieng      # chạy lặp tới khi báo XONG
```

- `kiem-ke` xếp clip theo giờ quay (tên tệp kiểu `VID_YYYYMMDD_HHMMSS`, rồi thẻ thời gian của máy, giờ UTC cộng `--lech-gio`), tách cụm theo khoảng nghỉ, gắn cờ HDR, VFR, khung dọc, 10-bit. Cụm thời gian thường trùng các phần của chương trình.
- `khao-sat` dựng `Du an/<x>/_kt/khao-sat/_tong-NN.jpg` (mỗi clip một ô, có số, giờ, độ dài) và bảng khung từng clip; clip dài thêm trang theo bước 20 giây. Đọc ảnh tổng quan trước, rồi mới mở bảng khung của clip cần chọn. Chỉ giải mã khung khoá nên 38 clip 4K xong trong khoảng hai phút.
- Điền `giai_doan` (theo pha của kịch bản: `don-khach`, `khai-mac`, `phan1-...`) và `mo_ta` (việc thấy trong hình) vào `Du an/<x>/recap/kiem-ke.json`. Mô tả suy từ hình thì ghi là suy đoán khi trình người dùng.
- Đổi tên khi người dùng muốn (hoặc đề nghị khi nguồn là tên máy khó đọc): `recap.py doi-ten` xem trước, `--ghi` đổi thật và để `DOI-TEN.md`, `DOI-TEN.json` trong thư mục nguồn, `--hoan-tac` trả lại. Không đổi tên bằng tay.
- Gỡ băng chỉ những clip có lời định dùng (khai mạc, hướng dẫn, đúc kết), theo skill phim-transcript; clip dài cắt thành khúc vài phút để mỗi lượt kịp 180 giây. Phòng đông, song ngữ, Whisper nhiễu: transcript chỉ để định vị câu, câu nào lên phim thì ghi vào danh sách người dùng nghe lại.

## Bước 2 - phương án cắt (chốt duyệt số 1)

Viết bảng cảnh theo thứ tự phim, ghi lên Project để người dùng duyệt: số cảnh, nguồn và giây trong clip, tiếng (giữ hay tắt), độ dài, việc của cảnh, chữ trên hình. Nguyên lý:

- **Mạch theo các phần của chương trình**, mỗi phần một chương: thiết lập (toàn cảnh căn phòng, người đến), hoạt động (trung cảnh, cận tay, chi tiết đồ vật), khoảnh khắc người (cười, ôm, nhìn nhau). Một thẻ chuyển phần ngắn cho mỗi phần lớn khi chương trình có cấu trúc rõ.
- **Lời nói là điểm neo, không là thân phim**: lời chào của người tổ chức, câu hướng dẫn mở hoạt động, một câu đúc kết. Mỗi đoạn lời 8-25 giây, vào và ra ở quãng lặng. Câu đúc kết đắt nhất của mỗi phần có thể lên chữ nổi, nguyên văn.
- **Nhịp cảnh câm**: 3-6 giây là điểm xuất phát (chi tiết 2-3 giây, toàn cảnh, khoảnh khắc cảm xúc 5-7 giây); đổi độ dài, không để cảnh nào cũng bằng nhau. Hai cảnh liền nhau đổi cỡ hoặc góc; chuỗi cùng góc chỉ khi có chủ đích (ba mốc của cùng một hoạt động cho thấy nó thành hình).
- **Mở và kết**: thẻ mở, rồi cảnh đẹp nhất của phần đón khách (hoặc một khoảnh khắc đắt đưa lên trước khi phim cần níu người lạ). Kết bằng cảnh chung cả nhóm hay ảnh chụp chung, mờ dần, rồi thẻ cảm ơn.
- **Ngân sách**: phim 3 phút khoảng 25-35 cảnh; ước tính và kiểm bằng `recap.py kiem --muc-tieu`.
- **Riêng tư ngay từ phương án**: cảnh người tham dự đang chia sẻ chỉ lấy hình, tắt tiếng; tránh cận mặt lúc xúc động; tắt tiếng nhạc phát trong phòng (nhạc có bản quyền).

Kèm danh sách "cần người dùng kiểm bằng tai, bằng mắt" (người nói có đúng là ai, câu trích có đúng không, mô tả suy từ hình). Nhạc là lựa chọn chủ quan nhất: trình hai phương án nhạc kèm bản nghe ngắn ngay ở chốt này (Bước 3).

## Bước 3 - nhạc

- **Chọn theo cảm xúc của buổi**: nhịp nhanh hay chậm đổi mức hưng phấn, giọng trưởng hay thứ đổi sắc cảm xúc (Husain, Thompson và Schellenberg, 2002). Buổi chăm sóc tinh thần, chữa lành: giọng trưởng, 60-80 nhịp, âm vực cao, giai điệu đơn giản dễ thương; tránh giọng thứ, nền pad điệu thức, tiếng ngân kéo dài (dễ nghe thành bí ẩn, u buồn). Hội nghị, ngày hội năng lượng: 100-130 nhịp.
- Nhóm A trước (`thu-vien/AM-THANH.md`); thư viện thiếu đúng màu cảm xúc thì soạn bản mới bằng `tools/soan-nhac.py` (thêm một hàm bản nhạc và một dòng `BAN`), đó vẫn là nhạc riêng, không lo Content ID.
- `python3 tools/recap.py nhac --du-an "../Du an/<x>" --nhac nhac-nen/<x>.mp3 [--bpm <nhịp>]` đo LUFS, dò nhịp và pha, ghi `Du an/<x>/recap/nhip.json` kèm `gainDb` gợi ý: recap ít lời để nhạc khoảng -20 LUFS trước chuẩn hoá (bản -15 LUFS thì khoảng -5); clip nói nhiều để nhạc khoảng -30 LUFS. Mode `full` + `duck`, `fadeIn` 2, `fadeOut` 4.

## Bước 4 - đồ họa

Theo skill phim-do-hoa, render ở sandbox. Mẫu job cho recap (props đã kiểm): `skills/phim-recap-su-kien/references/mau-bang-canh.md` mục 2. Điểm riêng của recap:

- Intro: tiêu đề là tên chương trình hay tên buổi, `subtitle` là chuỗi chương trình (FULL-CAP), `description` là đơn vị và dịp, `creditLines` là ngày. SectionTitle cho từng phần.
- Chữ nổi: Benefits một mục, `showIndex:false`, `wrap:true`, `position:'bottom'` (một mục không có `revealAt` tự hiện sau 0,3 giây theo `overlay.at`). Kiểm trên khung thật: pill nằm trên sàn, chân, mặt bàn, không trên mặt người.
- Outro cảm ơn: `headline` (xuống dòng bằng `\n`), `ctaLines: []`, `programName: ""`, `contactLines: []`, `showTagline: false`; không logo thì truyền `brand` có `logos: []`, `logoFile: null`. Để trống các trường này mà không ghi tường minh thì chữ mẫu của component lộ ra.
- Tên chương tiếng Anh: thêm `"chapterIntro": "Intro"` ở cấp cao nhất của timeline.

## Bước 5 - cắt, ráp, khớp phách, dựng

```
python3 tools/recap.py cat --du-an "../Du an/<x>"          # proxy 1080p theo recap/canh.json, chạy lặp tới XONG
python3 tools/recap.py timeline --du-an "../Du an/<x>" --intro do-hoa/ngang/intro.mp4 --outro do-hoa/ngang/outro.mp4 [--chuong-dau Intro]
python3 tools/recap.py kiem --du-an "../Du an/<x>" --muc-tieu 3:00
python3 tools/recap.py khop-nhip --du-an "../Du an/<x>" --ghi
python3 tools/assemble.py --project "../Du an/<x>" --kiem-tra
python3 tools/assemble.py --project "../Du an/<x>" --preview --out <tên>-ngang-nhap1
python3 tools/recap.py khop-nhip --du-an "../Du an/<x>" --map "../Du an/<x>/xuat-nhap/<tên>-ngang-nhap1.map.json" --ghi
python3 tools/assemble.py --project "../Du an/<x>" --out <tên>-ngang
python3 tools/nghiem-thu.py video "../Du an/<x>/xuat-nhap/<tên>-ngang.mp4" --khung ngang --anh
```

- Bảng cảnh `Du an/<x>/recap/canh.json` viết sau khi người dùng duyệt phương án (mẫu ở `references/mau-bang-canh.md` mục 1). `cat` cắt proxy có đệm 1 giây mỗi đầu, tự tonemap nguồn HDR, ép khung đều cho nguồn VFR, và sinh `transcript/<proxy>.silences.json` theo năng lượng cho cảnh giữ tiếng, nhờ vậy `snap` của assemble hút mép về quãng lặng. Sửa giây một cảnh rồi chạy lại: chỉ cảnh đó cắt lại.
- `khop-nhip` kéo mép cuối từng cảnh câm (trong phần đệm sẵn có) về phách gần nhất của nhạc, giữ nguyên cảnh có lời; chạy lần hai với `--map` của bản nháp vì `snap` làm độ dài đoạn lời đổi vài phần mười giây. Cắt trên phách nhưng không đều tăm tắp: lệnh báo khi nhiều cảnh liền nhau dài bằng nhau.
- `kiem` là kiểm giấy (thời lượng, tỉ lệ lời và cảnh câm, cảnh quá ngắn hay quá dài, cảnh có lời thiếu tệp khoảng lặng, chữ nổi dài quá cảnh, nhạc và gainDb, mép trúng phách); cổng thật vẫn là `nghiem-thu.py`.
- Người dùng có thể bỏ chốt nháp 480p (đã từng nói "dựng luôn bản full"): khi đó dựng thẳng bản chính, vẫn chạy `khop-nhip --map` trên `map.json` của chính bản chính rồi dựng lại (assemble dùng lại cache, chỉ ráp lại phần đổi).
- Cảnh báo "không đủ mốc" của phép đo đồng bộ so với nguồn là bình thường với phim toàn đoạn ngắn; chấp nhận khi assemble báo hình = tiếng ở từng part và thành phẩm.

## Bước 6 - báo, giao, dọn

- Báo người dùng: dòng "nghiệm thu máy: ĐẠT", thời lượng, nhạc gì và vì sao, các điểm cần nghe lại. Bản nghe thử gửi qua chat phải dưới 30 MiB (bản 640 px khoảng 11 MB là chắc ăn).
- Gói đăng tải (skill phim-dang-tai) chỉ khi phim đăng công khai; recap gửi riêng khách hàng thì bỏ và nói rõ, đề nghị làm khi người dùng muốn đăng. Nhạc nhóm A ghi `GHI-CONG.txt` "nhạc gốc của xưởng, không cần ghi công".
- Thành phẩm, giao và dọn theo cách xưởng gom thành phẩm và dọn nháp (CLAUDE.md, mục quy tắc về thành phẩm và xưởng sạch). Khi dọn giữ `Du an/<x>/recap/`, `timeline.json`, đồ họa, proxy đang dùng; bỏ `Du an/<x>/_kt/`, nháp, proxy không còn trong bảng cảnh (`cat` liệt kê). Nguồn thô đã ở ổ lưu trữ thì chỉ ghi `NGUON-O-DAU.md`.

## Quy tắc cứng

1. Lời chia sẻ của người tham dự không lên phim khi buổi có nội dung riêng tư: chỉ hình, tắt tiếng. Phim công khai cần sự đồng ý của người lộ mặt rõ; không chắc thì hỏi người dùng.
2. Chữ trên hình là lời thật (nguyên văn người nói hay kịch bản), đúng ngôn ngữ chương trình; không bịa trích dẫn, không gán lời cho người khác.
3. Không thẻ, pill, chữ nào che mặt người; kiểm trên khung thật của bản dựng.
4. Không dùng hình, clip do AI tạo thay cho hình thật của sự kiện.
5. Nguồn của người dùng chỉ đổi tên qua `recap.py doi-ten` (có sổ đổi ngược); không xoá, không ghi đè, không chép nguồn thô vào repo.
6. Nhạc riêng của xưởng trước (`tools/soan-nhac.py`), track bị cấm không dùng; tắt tiếng nhạc phát trong phòng.
7. Hai chốt duyệt và cổng `nghiem-thu.py` như mọi phim; người dùng bỏ chốt nháp thì ghi lại trong tiến độ.

<!-- ban-nguon: phim-recap-su-kien 2026-10-11 cee6a2c1 -->
