---
name: "phim-duyet"
description: "Khi người dùng nói \"duyệt\" sau khi xong các clip thành phẩm của một dự án phim trong xuong-phim-claude: chuyển thành phẩm sang thư mục giao của máy đang dùng kèm bộ đăng tải và transcript, rồi dọn nháp cho trống ổ."
---

# Duyệt: chuyển thành phẩm và dọn nháp

Kích hoạt khi người dùng nói "duyệt" (hoặc "duyệt dự án này", "chuyển thành phẩm") sau khi các clip của một dự án đã qua nghiệm thu máy và có gói đăng tải. Chưa nghe chữ "duyệt" thì chỉ chạy bước xem kế hoạch, không chép, không xoá.

Không cố định tên hay đường dẫn thư mục nào trong skill này: người dùng hay dùng cùng một tài khoản trên nhiều máy, mỗi máy có thư mục giao (nơi để thành phẩm đã duyệt) tên và vị trí riêng. Luôn đọc cấu hình của máy đang dùng trước.

Công cụ nằm trong thư mục xưởng `xuong-phim-claude` (chạy từ đó; trong VM Cowork nó nằm dưới `$HOME/mnt/<tên thư mục xưởng đã gắn>/xuong-phim-claude`). Quy ước đầy đủ: `CLAUDE.md`. Nếu máy chưa có `tools/duyet.py` thì báo người dùng cần cập nhật repo xưởng trước (kéo bản mới từ git), không tự dựng lại.

## Quy trình

1. Xem cấu hình máy: `python3 tools/cau_hinh.py`. Dòng "Du an", "Thanh pham" là nơi làm việc và thành phẩm chưa duyệt; dòng "Giao" là thư mục giao.
2. Xác định thư mục giao của máy này:
   - "Giao" đã trỏ tới một thư mục tồn tại: dùng luôn, nói cho người dùng biết tên thư mục đó ở câu báo.
   - Chưa đặt, hoặc trỏ tới thư mục không còn: hỏi người dùng một lần (AskUserQuestion) thư mục giao trên máy này tên gì, ở đâu (gợi ý các thư mục người dùng cấp qua `get_device_info` và thư mục nhà). Thư mục chưa gắn vào phiên thì `device_request_folder_access`. Rồi `python3 tools/duyet.py --dat-dich "<đường dẫn>"` để ghi vào `cau-hinh.json` của máy (chỉ dùng một lần thì truyền `--dich "<đường dẫn>"` cho từng lệnh).
   - Thư mục giao đã đặt nhưng phiên chưa gắn: `device_request_folder_access` cho thư mục đó.
3. Xác định dự án: tên thư mục dự án trong thư mục Thành phẩm (trùng tên hồ sơ trong Du an), ví dụ `2026-10 một clip giới thiệu chương trình.0 MC1 Dinh vi ban than`. Dự án đang làm trong phiên là mặc định; có nhiều dự án mà chưa rõ thì hỏi người dùng một lần.
4. Xem kế hoạch: `python3 tools/duyet.py "<dự án>"`. Đọc nhóm H (video không trùng đâu, có thể là bản dựng duy nhất): nhóm H luôn hỏi người dùng, không tự xoá.
5. Chuyển: `python3 tools/duyet.py "<dự án>" chuyen`. Ghi dấu duyệt `NGUON-O-DAU.md` trong hồ sơ dự án, chép sang `<thư mục giao>/<dự án>/`, đối chiếu cỡ mọi tệp và mã băm mẫu mọi video. Thoát mã 75 hoặc in CON-VIEC thì gọi lại y nguyên lệnh (mỗi lượt tối đa khoảng 150 giây) cho tới XONG-CHUYEN.
6. Xin quyền xoá một lần bằng `device_request_delete_permission` cho thư mục xưởng (người dùng đã dặn cứ xin, người dùng cấp). Quyền chỉ có hiệu lực trong phiên đó.
7. Dọn: `python3 tools/duyet.py "<dự án>" don` để xem, rồi `... don --ghi`. Công cụ đối chiếu lại rồi mới xoá bản trong thư mục Thành phẩm, sau đó dọn rác (R) và nháp (N: `.tam`, bản trung gian và bản trùng trong `xuat-nhap/` và `xuat-hoan-chinh/`, ảnh lưới, ảnh thử, log, `_khuc`, `_to_delete`, việc tạm trong `Du-an/_tam`). Kết thúc bằng dòng XONG-DON kèm dung lượng giải phóng.
8. Chạy `python3 tools/kiem-sach.py` cho tới ĐẠT (còn nháp lạc trong repo thì `--xoa`).
9. Báo người dùng: dự án nằm ở đâu (tên thư mục giao), số thư mục con và số video, dung lượng giải phóng, và những gì cố ý giữ lại.

## Kết quả trong thư mục giao

Một thư mục cho mỗi dự án; bên trong thư mục con đánh số (`00 Video day du`, `Short NN <slug>`), mỗi thư mục con tự đủ: video, `nghiem-thu.json`, `dang-tai/` (tiêu đề, mô tả, status, thumbnail), `transcript/` (short: `phu-de.srt`, `loi-noi.txt`, `trich-nguon.txt`; video dài: gỡ băng cả buổi). Ngoài ra có `MUC-LUC.md` trong thư mục dự án và `SO-LUU-TRU.json`, `MUC-LUC-LUU-TRU.md` ở gốc thư mục giao.

## Giữ lại, không bao giờ tự xoá

Nguồn quay thô (`Du-an/<dự án>/nguon/`, nhất là bản ghi Zoom chỉ có một bản), timeline, gỡ băng, đồ hoạ, cảnh, nhạc, `dang-tai/` làm việc, `NGUON-O-DAU.md`, và mọi video thuộc nhóm H.

## Lưu ý

- `rm` bị chặn cho tới khi người dùng cấp quyền xoá; hết phiên là mất quyền, nên mỗi phiên xin lại.
- `thuMucGiao` trong `cau-hinh.json` là một đường dẫn hoặc danh sách (lấy cái tồn tại đầu tiên); VM Cowork thấy thư mục ở `$HOME/mnt/<tên>`, Mac thật thấy đường dẫn của Mac. `--dat-dich` tự lưu dạng bền qua các phiên (tương đối so với thư mục xưởng, hoặc `~/...`), không ghi đường dẫn tạm của phiên.
- Công cụ chép bằng tệp tạm rồi đổi tên và chạy lặp được, nên bị ngắt giữa chừng thì gọi lại y nguyên.

<!-- ban-nguon: phim-duyet 2026-11-03 1deb4a7a -->
