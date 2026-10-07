---
name: "phim-ban-dung"
description: "Bàn dựng và Dựng bằng lời trong thư mục \"xuong-phim-claude\": để người dùng tự tay tinh chỉnh một clip đã có bản nháp (tỉa đầu cuối đoạn, tách, đổi thứ tự, dời và kéo dài thẻ đồ họa, B-roll, nhạc, bỏ chữ thừa bằng cách bôi đen trong lời), rồi Claude dựng lại và nghiệm thu. Kích hoạt khi người dùng nói \"mở bàn dựng\", \"người dùng tự chỉnh\", \"người dùng chỉnh tay xong\", \"người dùng chỉnh xong rồi\", \"dựng bằng lời\", \"bỏ chữ thừa trong lời\", \"timeline người dùng vừa sửa\", khi một timeline có trường _chinhTay, khi cần chuẩn bị mốc lời cho một dự án, hoặc khi phải sửa chính Bàn dựng (trang, máy chủ, quy tắc điểm cắt). Không dùng để dựng clip từ đầu (phim-dung-bai và các skill thể loại) hay làm đồ họa (phim-do-hoa)."
---

# Bàn dựng và Dựng bằng lời

Bàn dựng [timeline editor] là chỗ người dùng tự tay chỉnh nhỏ một clip đã có bản nháp, thay vì mô tả từng thay đổi cho Claude. Dựng bằng lời [text-based editing] là thẻ "Lời" trong Bàn dựng: bôi đen chữ thừa rồi bấm Delete, hình và tiếng được cắt đúng chỗ. Cả hai sửa thẳng `timeline.json`; bản dựng thật vẫn do `tools/assemble.py` làm và `tools/nghiem-thu.py` kiểm, nên mọi bất biến của xưởng giữ nguyên. Đặc tả, nền nghiên cứu và lý do từng lựa chọn: `skills/phim-ban-dung/references/kien-truc.md`.

Tinh thần: Bàn dựng trao lại cho người dùng quyền quyết những chỗ nhỏ mà mô tả bằng lời tốn hơn tự làm. Claude lo phần nền (mốc lời, dạng sóng, kiểm, dựng lại) và học từ cách người dùng chỉnh, không chỉnh đè lên.

## Bước 0 - nền tảng

Đọc `skills/_chung/van-hanh.md`, mục "Bàn dựng" trong `docs/QUY-TRINH-KY-THUAT.md`, chủ đề 17 của `docs/BAI-HOC.md`.

## Bước 1 - chuẩn bị một dự án cho người dùng chỉnh

Làm ngay khi gửi bản nháp đầu tiên (chốt duyệt số 2), để người dùng có thể chỉnh luôn nếu muốn:

1. `python3 tools/moc-tu.py "../Du an/<x>"` trong VM: chép nguyên văn từng âm tiết (giữ từ đệm) và mốc đầu-cuối, ra `transcript/<nguồn>.tu.json` và `<nguồn>.nang-luong.bin` cho mọi file tiếng mà timeline dùng. Bài dài chạy lặp đúng lệnh tới khi báo "✓ Xong" (bài 10 phút khoảng 2,5 phút; 1 giờ khoảng năm lượt). Thiếu bước này Bàn dựng vẫn mở được, nhưng không có dạng sóng, chữ trong khối và thẻ "Lời".
2. Nguồn là định dạng Chrome không giải mã (ProRes, HDR lạ): báo người dùng và đề xuất tạo proxy cùng trục thời gian; H.264, HEVC thì phát thẳng.
3. Báo người dùng một dòng: "Muốn tự chỉnh nhỏ thì bấm đúp `Mo ban dung.command`, mở <dự án>." Không giải thích kỹ thuật.

## Bước 2 - khi người dùng báo đã chỉnh xong

1. Đọc dòng cuối `Du an/<x>/ke-hoach-dung/_ban-dung/nhat-ky.jsonl`: danh sách thay đổi và đường dẫn bản cũ (thư mục `Du an/<x>/ke-hoach-dung/_phien-ban/`). Đọc thay đổi như đọc góp ý của người dùng.
2. `python3 tools/assemble.py --project "../Du an/<x>" --timeline <file> --kiem-tra`. Lỗi thì báo đúng chỗ và hỏi người dùng, không tự sửa ngược ý người dùng.
3. Dựng nháp với `--out` tường minh (số nháp kế tiếp), nghiệm thu, gửi người dùng như mọi vòng. Bản đạt mới sang bản chính.
4. Nhìn lại thay đổi: một kiểu chỉnh lặp lần thứ hai (ví dụ luôn cho bảng tên hiện muộn hơn, luôn hạ nhạc) là góp ý lặp, sửa nguồn mặc định và ghi sổ tay góp ý của `phong-cach/PHONG-CACH.md` theo quy tắc cứng 6 của `CLAUDE.md`.

## Bước 3 - sửa timeline khi người dùng đã chỉnh tay

Timeline có `_chinhTay` là nguồn sự thật (quy tắc cứng 9 của `CLAUDE.md`). Claude sửa thẳng file đó bằng đọc-sửa-ghi, giữ nguyên chỉnh tay; không sinh lại từ `plan.py`, kịch bản hay phương án cũ. Cần làm lại hẳn một phần thì nói rõ với người dùng phần nào sẽ mất chỉnh tay trước khi làm. Mỗi lần Claude sửa, người dùng mở lại Bàn dựng sẽ thấy bản mới; nếu người dùng đang mở dở, trang tự hỏi nạp bản mới hay ghi đè.

## Bước 4 - sửa chính Bàn dựng

Bản đồ tệp, mô hình dữ liệu, quy tắc điểm cắt và cách kiểm ở `skills/phim-ban-dung/references/kien-truc.md`. Nguyên tắc:

- Bố cục trên trang phải khớp đúng cách `tools/assemble.py` dựng (snap, overlay tương đối, B-roll theo mốc nguồn, nhạc bookends, `overlay.duration`). Thêm trường mới vào assemble thì thêm cả vào `tools/ban-dung/js/mo-hinh.js`.
- Điểm cắt theo lời chỉ có một nơi tính: `tools/ban_dung_loi.py` (máy chủ gọi qua `/api/cat`). Không chép logic sang trình duyệt.
- Sửa quy tắc điểm cắt: chạy lại phòng nghe thử 16 điểm (`Du an/<x>/_ban-dung-thu/`) và so mốc cũ; `kiem-tra-xuong.py` có phần kiểm điểm cắt trên lời tổng hợp.
- Kiểm trang ở sandbox bằng Playwright với dự án thử WebM (Chromium của sandbox không giải mã H.264), rồi commit về máy. Máy chủ giữ module đã nạp: người dùng phải đóng và mở lại Bàn dựng sau khi sửa phần Python.

## Quy tắc cứng

1. `timeline.json` là nguồn sự thật duy nhất; Bàn dựng không bao giờ tự nói "xong". Chỉ cổng `nghiem-thu.py` ĐẠT mới là xong.
2. Timeline có `_chinhTay`: không sinh lại, không ghi đè chỉnh tay của người dùng.
3. Không bao giờ sửa bản gỡ băng hay mốc lời để "cho khớp"; Dựng bằng lời chỉ đổi `in`, `out` và cấu trúc đoạn.
4. Chỉ cắt trong khe giữa hai âm tiết; ranh giới dính liền thì hỏi người dùng, không tự cắt.
5. Footage không rời máy: máy chủ chạy trên Mac, chỉ nghe 127.0.0.1.
6. Bản cũ mỗi lần lưu luôn được cất; không xoá `Du an/<x>/ke-hoach-dung/_phien-ban/`.
7. Đổi logic encode của `assemble.py` vì Bàn dựng cần thì đổi `TOOL_VERSION` và chạy `kiem-tra-xuong.py --co-slide` ĐẠT trước khi dựng thật.

## Khép việc

- Bài học kỹ thuật mới (một kiểu cắt hỏng, một định dạng không phát) vào chủ đề 17 của `docs/BAI-HOC.md`; đổi thao tác, lệnh thì sửa mục "Bàn dựng" của `docs/QUY-TRINH-KY-THUAT.md` và `HUONG-DAN.md`.
- Góp ý về chính Bàn dựng (thiếu thao tác, khó dùng): ghi vào tài liệu "ban-dung-dac-ta" trong Project, làm theo từng đợt có chốt duyệt.

<!-- ban-nguon: phim-ban-dung 2026-10-07 3b767ef5 -->
