# Dự án mẫu: chỉ để tham khảo cấu trúc

Dự án thật tạo cạnh thư mục này, ví dụ `du-an/bai-1/`, chỉ cần có `nguon/` chứa video. Các thư mục còn lại Claude tạo khi làm: `transcript/`, `tu-lieu/`, `do-hoa/<ngang|doc>/`, `xuat-nhap/`, `xuat-hoan-chinh/`, và file `timeline.json`.

- `timeline.json` ở đây là ví dụ đầy đủ các trường hay dùng (schema chi tiết trong docstring `tools/assemble.py`)
- `do-hoa/job-do-hoa.json` là ví dụ job render đồ họa (intro/outro nên bắt đầu từ preset `do-hoa-chung/` thay vì file này)
- Hai hệ mốc thời gian: `in`/`out`/`broll.at` tính trong FILE NGUỒN; `overlay.at` tính từ ĐẦU ĐOẠN đã cắt
