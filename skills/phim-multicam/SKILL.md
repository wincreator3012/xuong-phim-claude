---
name: phim-multicam
description: Dựng clip ngang từ 2-3 góc quay của cùng một buổi trong thư mục xưởng (gốc repo xuong-phim-claude): đồng bộ các góc bằng đối chiếu âm thanh (multicam-khop.py), nhận diện người nói và đề xuất chuỗi chuyển góc theo thực hành podcast và multicam (multicam-dan.py), chia buổi dài thành session ngăn bằng thẻ chữ, dựng bằng assemble.py với audioSrc. Kích hoạt khi user nói "multicam", "nhiều góc quay", "podcast hai người", "góc cận góc toàn", "ghép các góc", "chuyển góc", hoặc nguon có nhiều thư mục con mỗi thư mục một máy quay.
---

# Multicam: khớp các góc rồi chuyển góc có chủ đích

Mở rộng của phim-dung-bai (áp dụng toàn bộ: Bước 0 nền tảng, transcript và cổng nghiệm thu transcript, đồ họa từ preset, bản nháp, nghiệm thu máy bắt buộc). Skill này thêm hai lớp: đặt mọi file của mọi góc lên MỘT trục thời gian chung bằng âm thanh, và quyết định người xem NHÌN góc nào ở từng quãng. Cơ sở và bảng luật đầy đủ ở `references/dan-goc-multicam.md` (bản gốc trong `skills-nguon/phim-multicam/`).

Hai dạng buổi:

- **Podcast / đối thoại**: mỗi người một máy cận (mic gần), thêm một máy toàn. Góc = người đang nói; xen phản ứng người nghe; hai người nói chồng thì về toàn.
- **Bài giảng một người nhiều góc**: góc chính thẳng mặt ~60%, góc phụ nghiêng ~30%, toàn ~10%; đổi góc tại ranh giới câu, mỗi góc giữ 12-25 giây; đổi cỡ cảnh theo hướng vào (toàn → cận) dễ chịu hơn hướng ra.

Nguyên tắc chung: tiếng là một dòng liên tục duy nhất (track chủ), hình đổi trên nền tiếng đó; mọi điểm cắt hút về khoảng lặng; giữ một góc tối thiểu 3 giây, tối đa ~30 giây; đổi góc vì nội dung (ai nói, phản ứng, nhấn ý), không đổi cho "đa dạng" vô cớ.

## Bước 0 - nguồn và cách quay

Cấu trúc bắt buộc: `du-an/<tên>/nguon/<góc>/<các file của máy đó>`. Tên thư mục quyết định loại: chứa `toan` là góc toàn; bắt đầu bằng `tieng` là file tiếng riêng (không hình); còn lại là góc cận và tên thư mục là tên người (podcast: `an`, `khach`, `minh`...; bài giảng: `chinh`, `nghieng`...). Một máy tự tách nhiều file (IMG_1, IMG_2) vẫn để chung một thư mục, tool tự xếp từng file lên trục chung kể cả khi có khoảng nghỉ giữa các file.

Nhắc user khi có dịp (ghi trong `references`): góc toàn quay liên tục không ngắt (làm trục chuẩn); mỗi máy tự thu tiếng (dù chỉ là tiếng scratch); vỗ tay một cái đầu buổi khi mọi máy đã chạy; podcast thì mic gần từng người và hai máy cận đặt đối xứng cùng tầm mắt; cùng cân bằng trắng và cùng 25/30 fps.

## Bước 1 - đồng bộ bằng âm thanh

```
python3 tools/multicam-khop.py "du-an/<tên>" [--chu toan] [--tron-tieng]
```

Ra `du-an/<tên>/multicam.json`: trục chuẩn, từng file mỗi góc có `offset` (mốc bắt đầu file trên trục chung), `dur`, `tin_cay` (đỉnh/đỉnh phụ), `khop_r` (Pearson đường bao), `drift_ppm`, `snr_db`; đoạn phủ và khoảng trống của mỗi góc; `tieng_chu_de_xuat` là góc có SNR cao nhất. `--tron-tieng` (podcast) trộn tiếng các mic gần đã căn offset thành `nguon/tieng-chu.wav` làm track chủ. Trục chuẩn mặc định là góc `toan` nếu chỉ một file, không thì góc ít file nhất; góc chuẩn có nhiều file bị xếp nối tiếp giả định không nghỉ (tool cảnh báo) nên luôn ưu tiên `--chu` là góc quay liên tục.

Đọc kết quả trước khi đi tiếp: file có `tin_cay` < 1.1 hoặc `khop_r` < 0.2 là nghi ngờ (lời nói cùng phòng thường r 0.4-0.8); `drift_ppm` > 200 nghĩa là hai máy trôi rõ (tool đã hiệu chỉnh tại giữa mỗi segment nhưng segment > 60 giây nên tách đôi). Với file nghi ngờ, KIỂM BẰNG MẮT: trích một khung ở mốc trục chung T từ hai góc (`-ss` = T - offset của mỗi file) tại một khoảnh khắc có cử động rõ (vỗ tay, gật đầu, miệng mở) rồi ghép cạnh nhau và nhìn; hoặc cắt 3 giây tiếng của hai file tại cùng mốc trục, trộn và nghe xem có vọng đôi không. Sai thì soạn tay `multicam.json` (truyền `--cau-hinh`) hoặc bảo user báo mốc vỗ tay.

## Bước 2 - transcript của tiếng chủ

Chạy `transcribe.py` trên `nguon/tieng-chu.wav` (nếu đã trộn) hoặc file góc chuẩn, `--out-dir du-an/<tên>/transcript`, rồi `nghiem-thu.py transcript` như phim-dung-bai. Mốc transcript theo trục chung vì tiếng chủ chính là trục chung (tiếng trộn bắt đầu từ 0 của trục; nếu dùng `--tieng` là một file góc có offset khác 0 thì multicam-dan tự dời mốc transcript và `audioIn` theo).

## Bước 3 - dàn góc, chia session (chốt duyệt cùng phương án cắt)

```
python3 tools/multicam-dan.py "du-an/<tên>" --transcript "<tên transcript không đuôi>" \
    [--che-do auto|podcast|bai-giang] [--chinh <góc chính>] [--phut 8] [--khong-session]
```

`auto` chọn podcast khi có từ 2 góc cận trở lên: bài giảng một người nhiều góc PHẢI truyền `--che-do bai-giang --chinh <góc>`. Ra `du-an/<tên>/multicam/`: `nguoi-noi.json` (ai nói khi nào, từ so năng lượng mic gần), `session.json` (ranh giới, từ khoá, câu mở), `DAN-GOC.md` (bảng duyệt), `timeline-multicam-nhap.json`, `job-session.json`.

Việc của Claude trên bản nháp này, trước khi trình user:

1. Đặt TÊN từng session từ từ khoá và câu mở, đối chiếu transcript; tên là ý chính người nghe mang về, cỡ 3-7 từ, sentence case. Session dưới 3 phút gộp với session kề; buổi dưới 12 phút thường không cần session (`--khong-session`).
2. Đọc cột "Lý do" của chuỗi cắt và soi các chỗ tool không biết nội dung: lượt nói dài của một người mà có câu hỏi tu từ, kể chuyện xúc động, hay người nghe rõ ràng phản ứng (cười, "ồ") thì đặt phản ứng đúng chỗ đó thay cho chỗ tool đặt máy móc; đoạn cả hai cùng cười, cùng nói thì toàn; câu chốt của session để cận người nói, không để toàn.
3. Kiểm tỉ lệ góc ở đầu `DAN-GOC.md`: podcast cận host và cận khách nên gần cân xứng với thời gian nói của mỗi người, toàn 10-20%; bài giảng theo 60/30/10. Lệch nhiều thì sửa.
4. Chỗ góc bị trống (file máy đó ngắt) tool đã thay góc khác; kiểm cột "File góc" quanh ranh giới file.

Trình bảng dàn góc và tên session CÙNG bảng phương án cắt và overlay của phim-dung-bai cho user duyệt một lần (SendUserMessage nếu đang giữa chuỗi tool). Tối đa 2-3 cú cắt tay do user: dùng mốc trục chung, Claude quy về in/out của file góc bằng `offset` trong multicam.json.

## Bước 4 - đồ họa session và timeline

Điền tên session vào `multicam/job-session.json` (mỗi job là một SectionTitle 4 giây, `subtitle` "Phần N" hoặc bỏ), render bằng `node tools/render-do-hoa.mjs multicam/job-session.json --studio <studio>` như phim-do-hoa (script tự đo file, thoát mã 1 là có file sai), commit về `du-an/<tên>/do-hoa/ngang/session-NN.mp4`. Buổi không chia session thì bỏ bước này và bỏ các `insert` trong bản nháp.

Ghép `timeline.json`: segments từ `timeline-multicam-nhap.json` sau khi chỉnh theo bảng đã duyệt, giữ nguyên `audioSrc`/`audioIn` (tiếng chủ theo trục chung) và `snap: false` (điểm cắt đã hút về khoảng lặng; bật snap sẽ làm hình và tiếng lệch nhau vì snap chỉ dịch `in`/`out` của hình). Các khoá `_goc`, `_ly_do`, `_truc` chỉ để đọc, assemble bỏ qua. Thêm intro/outro từ preset, hook trước intro nếu có, overlay pill và chapter như phim-dung-bai; B-roll đè lên quãng nào thì tiếng chủ vẫn chạy. Cắt bỏ một quãng lời (ậm ừ, lạc đề) thì cắt cả hình và tiếng: bỏ hẳn quãng đó khỏi trục, tức tách segment và dịch `audioIn` theo, không chỉ dịch hình.

Yêu cầu: `assemble.py` đã có trường `audioSrc`/`audioIn` (bản trong repo đã có; `--kiem-tra` báo "audioSrc" không hợp lệ nghĩa là assemble.py bị thay bằng bản cũ, lấy lại từ repo). Kiểm rồi dựng: `--kiem-tra` → `--preview` → duyệt → bản chính.

## Bước 5 - nghiệm thu

Như phim-dung-bai Bước 6 (cổng `nghiem-thu.py video` bắt buộc, ảnh lưới, mối nối theo `map.json`), thêm ba kiểm riêng của multicam:

1. **Khớp hình-tiếng qua góc**: chọn 3 cú cắt xa nhau (đầu, giữa, cuối, ưu tiên cú cắt sang file thứ hai của một góc), trích 1 khung ngay sau cắt và nghe 2 giây tiếng quanh đó; miệng mở đúng lúc có tiếng, không có cảm giác tiếng trước hình. Nếu lệch một phía cố định → offset file đó sai; lệch tăng dần về cuối → drift, tách segment ngắn hơn.
2. **Nhịp cắt**: đọc `map.json`, không có part hình < 3 giây trừ khi cố ý (phản ứng 2.5-3.5 giây), không có part > 35 giây trong podcast; mở mỗi session bằng toàn.
3. **Thẻ session**: đúng tên đã duyệt, đủ 4 giây (manifest đồ họa), chapter khớp mốc.

Báo kết quả kèm tỉ lệ góc (ví dụ "cận người dẫn 47%, cận khách 38%, toàn 15%, 42 cú cắt, trung bình 18 giây/cú") và dòng "nghiệm thu máy: ĐẠT".

## Ghi nhớ

- Đổi luật cắt (ngưỡng lượt nói, khoảng giữ, tần suất phản ứng): sửa hằng trong `plan_podcast`/`plan_lecture` của `tools/multicam-dan.py`; đổi thuật toán khớp: `tools/multicam-khop.py`; mọi mốc đều trên trục chung, chỉ `to_segments` mới quy về file góc.
- Podcast có 3 người trở lên vẫn chạy: mỗi người một thư mục cận; góc toàn càng cần khi nhiều người chồng lời.
- Clip ngắn dọc cắt từ buổi multicam: dùng phim-clip-ngan với `src` là góc cận người nói và `audioSrc` tiếng chủ như trên, `cropFocus` theo người.
- Khi đề xuất cập nhật skill, `description` là mô tả kích hoạt, không chứa dấu ngoặc nhọn, không ghi changelog.
