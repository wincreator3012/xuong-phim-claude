# Mẫu dự án phim tài liệu phỏng vấn (skill phim-tai-lieu-phong-van)

Dự án thật tạo cạnh `du-an/_mau/`, ví dụ `du-an/phim-du-an-x/`. Khác dự án bài giảng ở hai điểm: nguồn chia theo loại, và có năm file hồ sơ đi qua nhiều phiên (chờ quay, chờ duyệt, chờ góp ý).

```
du-an/<tên phim>/
  HO-SO-PHIM.md          nguồn sự thật giữa các phiên (bối cảnh, khán giả, thông điệp, điều không nói, quyết định, trạng thái)
  KE-HOACH-GHI-HINH.md   Pha 1 - Cổng duyệt 1 (định hướng ba hồi, nhân vật + câu hỏi, danh mục cảnh trám, checklist ngày quay)
  nguon/phong-van/       mỗi file một nhân vật, tên = tên + vai
  nguon/canh-tram/       cảnh không lấy tiếng, tên mô tả nội dung
  nguon/su-kien/         ghi hình sự kiện có tiếng (nếu có)
  nguon/anh/             ảnh tĩnh
  transcript/            phim-transcript tạo
  KIEM-KE-NGUON.md       Pha 2 - kiểm kê và đối chiếu kế hoạch với thực tế
  KICH-BAN-THUC-TE.md    Pha 2 - Cổng duyệt 2 (paper edit có mốc, ước tính thời lượng, quyết định cần user)
  SO-GOP-Y.md            từng vòng nháp
  do-hoa/<ngang|doc>/    đồ họa render;  do-hoa/job/ giữ job JSON tới khi giao
  timeline.json, xuat-nhap/, xuat-hoan-chinh/
```

Mẫu điền sẵn của năm file hồ sơ và ngân hàng câu hỏi theo vai: `skills/phim-tai-lieu-phong-van/references/mau-ho-so.md`. Người dùng đã tự sắp nguồn theo cách khác thì giữ nguyên, ghi ánh xạ vào `HO-SO-PHIM.md`.
