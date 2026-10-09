# THAY ĐỔI: nhật ký bản thiết kế

Tệp này dành cho AI đang chăm một xưởng đã dựng từ bản thiết kế: khi người dùng nói "xem bản thiết kế có gì mới", đọc các mục SAU ngày `ban_mau.ngay` trong `tools/.cai-dat.json` của xưởng, rồi làm theo mục cuối của `DUNG-XUONG.md` (đề xuất từng thay đổi, người dùng duyệt rồi mới ghi, không ghi đè phần riêng của họ). Mỗi mục ghi: điều gì đổi, vì sao đáng lấy, tệp chính bị ảnh hưởng. Mục mới ở trên cùng.

## 2026-10-10: loạt short dọc "mặt trên, cảnh dưới"

- Bố cục `mat-tren` trong `tools/assemble.py` (r10, r11): khung dọc chia hai ô, mặt người nói ở ô trên (`cropFocus`, `cropFocusY`, `cropZoom`, `paneH`), nền giấy phía dưới cho cảnh minh hoạ chuyển động. `tools/kiem-tra-xuong.py` có thêm bước kiểm bố cục này.
- Bộ công cụ làm cả loạt short từ một buổi giảng dài của một người nói: `tools/short-dung.py` (chốt mép cắt theo âm tiết, timeline, phụ đề), `tools/short-soi.py` (soi âm tiết, quãng lặng, độ khớp chữ), `tools/short-canh.py` với khung `do-hoa-chung/canh-kit/mau/canh-short.html` (cảnh viết bằng dữ liệu), `tools/short-render-canh.sh`, `tools/short-xuat.sh`, `tools/short-khung.sh`, `tools/short-chot.sh`.
- Quy trình, thông số và các bẫy đã gặp: `skills/phim-clip-ngan/references/short-mat-tren.md` và mục 25 của `docs/BAI-HOC.md`. Gói đăng tải: chữ thumbnail ngang chia ba dòng ngắn để qua cổng 110 px; chữ công khai tránh ngày, giá, thương hiệu, mốc thời gian tương đối (`skills/phim-dang-tai/SKILL.md`).
- Nếu xưởng của người dùng đã có `assemble.py` cũ hơn r10: đề xuất lấy bản mới (đổi `TOOL_VERSION`, chạy `tools/kiem-tra-xuong.py` trước khi dựng thật).

## 2026-10-09: bản thiết kế và skill trong tài khoản

- Repo chuyển hẳn thành bản thiết kế: AI của người dùng đọc trên GitHub và dựng xưởng riêng, không clone, không tải ZIP, không push hay pull. Hướng dẫn cho AI: `DUNG-XUONG.md`; điểm vào cho mọi trợ lý: `AGENTS.md`; bản đồ tệp có mã kiểm: `BAN-DO-TEP.json` (lập bằng `tools/lap-ban-do-tep.py`).
- `tools/cai-dat.py --dung-xuong`: cá nhân hoá xưởng vừa dựng (tên xưởng, tiền tố skill, README ghi công, ghi bản thiết kế đã dùng vào `tools/.cai-dat.json`). Xưởng dựng trước ngày này: chạy lệnh này tại chỗ để chuyển thành xưởng riêng (HUONG-DAN mục "Cập nhật xưởng").
- `tools/dong-goi-skill.py` (mới): đóng gói skill thành tệp `.skill` mang tiền tố riêng của người dùng để lưu vào tài khoản AI, sổ ghi bản đã lưu, báo skill nào trong tài khoản cũ hơn bản gốc. Khoá mới `tienToSkill` trong `cau-hinh.mau.json`.
- Skill phim-thiet-lap: Bước 0 nhận biết xưởng chưa dựng xong; Bước 5 tách ba phần (tóm tắt, lưu skill vào tài khoản, giới thiệu xưởng); tài liệu mới `skills/phim-thiet-lap/references/skill-trong-tai-khoan.md` giải thích skill cho người mới.
- `CLAUDE.md` quy tắc 12 (xưởng riêng, không push pull về bản thiết kế); quy tắc 7 thêm bước đóng gói lại skill sau khi sửa. `HUONG-DAN.md`: mục "Skill trong tài khoản", mục "Cập nhật xưởng" viết lại.
- Cùng đợt (từ xưởng gốc): rà màn hình chia sẻ trước khi dựng (`skills/phim-bai-giang-slide/references/demo-man-hinh.md`, `tools/xem-khung.sh`), dựng phim dài theo giai đoạn (`tools/dung-dai.py`), giao trọn gói thành phẩm sang thư mục đồng bộ (`tools/giao-thanh-pham.py`, khoá `thuMucGiao`).

## 2026-10-07: dự án và thành phẩm nằm ngoài xưởng

- Bố cục `Xuong phim AI/{<xưởng>, Du an, Thanh pham}`: xưởng chỉ chứa năng lực; dự án tạo bằng `tools/du-an-moi.py`; cấu hình đường dẫn `cau-hinh.json`, đọc qua `tools/cau_hinh.py`; cổng `tools/kiem-sach.py` giữ xưởng sạch.
- Thành phẩm gom một thư mục mẹ theo dự án, thư mục con đánh số (`00 Video day du`, `Short NN <slug>`), mỗi thư mục tự đủ (phim, nghiệm thu, gói đăng tải).
- Tiền tố `@xuong/` cho tài nguyên dùng chung trong job đồ họa.

## 2026-10-05: clip sân khấu, buổi giới thiệu xưởng

- Quy tắc cứng: không lớp phủ nào che mặt bất kỳ ai. Cách dựng clip giảng trên sân khấu: `skills/phim-bai-giang-slide/references/clip-giang-san-khau.md`; quét mặt theo giây.
- Buổi giới thiệu xưởng sáu chặng cho người mới (`skills/phim-thiet-lap/references/gioi-thieu-xuong.md`); thumbnail xen cận mặt với khung rộng.
- Thư viện nhạc: rà Content ID, nhạc riêng soạn bằng `tools/soan-nhac.py`.

## 2026-09-29 đến 2026-10-03: mở rộng năng lực

- Multicam và podcast (khớp góc bằng âm thanh, proxy, nhận diện người nói, chương YouTube); Bàn dựng và Dựng bằng lời; gói đăng tải tự soạn sau mỗi clip; cảnh minh hoạ động (`do-hoa-chung/canh-kit/`); phim hoạt hình vẽ bằng code; hệ thống hoá skill và phần dùng chung `skills/_chung/`.

## 2026-09-05 đến 2026-09-24: khởi tạo

- Bản đầu: dựng bài giảng, clip ngắn, đồ họa, gỡ băng, tư liệu, màu sắc, bài giảng có slide, multicam; cổng nghiệm thu chống lệch hình tiếng; thư viện âm thanh đã kiểm định; phim tài liệu phỏng vấn (2026-09-20).
