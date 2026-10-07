# Khuôn dự án: `tools/du-an-moi.py` chép từ đây

Dự án thật nằm NGOÀI repo, trong thư mục `Du an/` cạnh repo, ví dụ `Du an/2026-11 Bai 1/`; tạo bằng `python3 tools/du-an-moi.py "Bai 1"` (hoặc tự tạo thư mục), chỉ cần có `nguon/` chứa video. Các thư mục còn lại Claude tạo khi làm: `transcript/`, `tu-lieu/`, `do-hoa/<ngang|doc>/`, `xuat-nhap/`, `xuat-hoan-chinh/`, và file `timeline.json`.

- `timeline.json` ở đây là ví dụ đầy đủ các trường hay dùng (schema chi tiết trong docstring `tools/assemble.py`)
- `do-hoa/job-do-hoa.json` là ví dụ job render đồ họa (`@xuong/brand/brand.json` nghĩa là brand của xưởng, tính từ gốc repo) (intro/outro nên bắt đầu từ preset `do-hoa-chung/` thay vì file này)
- Hai hệ mốc thời gian: `in`/`out`/`broll.at` tính trong FILE NGUỒN; `overlay.at` tính từ ĐẦU ĐOẠN đã cắt
- Phim tài liệu phỏng vấn nhiều nhân vật có cấu trúc riêng (nguồn chia theo loại, năm file hồ sơ đi qua nhiều phiên): xem `tai-lieu-phong-van/GHI-CHU.md` cạnh đây
