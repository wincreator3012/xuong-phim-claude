# Xưởng phim Claude

**Dựng clip trình bày kiến thức bằng Claude Cowork, dành cho chuyên gia, giảng viên và nhà chuyên môn.** Bạn quay mình nói trước máy (có thể kèm slide), thả file vào một thư mục, nói yêu cầu bằng lời thường. Claude làm phần còn lại: gỡ băng, cắt gọn, chèn intro/outro và nhãn từ khoá, lồng nhạc đã kiểm định bản quyền, xuất bản ngang cho YouTube hoặc dọc cho Reels/Shorts, và tự kiểm chất lượng trước khi giao.

Repo này là một xưởng hoàn chỉnh đã chạy thật qua nhiều dự án, được gỡ phần riêng để ai cũng lấy về, thiết lập theo phong cách của mình và dùng ngay. Bạn không cần biết dựng phim, không cần biết lập trình, không cần cài phần mềm dựng.

## Bạn nhận được gì

- **Tám năng lực dựng phim** đóng thành quy trình chuẩn [skill] cho Claude: dựng bài giảng dài; bài giảng có slide (xen mặt, slide, hoặc cả hai theo nghiên cứu học tập đa phương tiện); clip ngắn dọc có phụ đề; podcast và buổi quay nhiều máy (tự đồng bộ bằng âm thanh, tự chuyển góc theo người nói); đồ họa động tối giản; gỡ băng tiếng Việt chạy ngay trên máy (video không rời máy bạn); tìm hình minh hoạ có kiểm định bản quyền; căn màu chỉ khi thật cần
- **Một bước thiết lập phong cách** khoảng 30 phút: Claude hỏi bạn là ai, dạy gì, cho ai, thích cảm giác nào (bốn mẫu để chọn hoặc mô tả riêng), rồi điền tên, chức danh, màu sắc, nhạc, thông điệp kết vào chỗ đã chừa sẵn. Mọi clip sau đó mang đúng dấu ấn của bạn và đổi được bằng một câu nói
- **Thư viện chất liệu sạch**: danh mục nhạc nền và hiệu ứng đã kiểm từng trang nguồn (dùng thương mại mọi nền tảng, không Content ID), tải về theo mẫu phong cách bạn chọn; danh mục nguồn hình miễn phí và quy tắc giấy phép
- **Cổng nghiệm thu tự động**: hình khớp tiếng tới 2 khung hình, âm lượng chuẩn -14 LUFS, không khoảng đen, không đứng hình. Claude không được nói "xong" khi máy chưa báo đạt
- **Hướng dẫn tận tình cho người mới**: `BAT-DAU.md` (cài lần đầu, từng bước), `HUONG-DAN.md` (cách đặt yêu cầu, ví dụ, xử lý sự cố)

## Bắt đầu trong ba bước

1. Tải repo này về máy (nút **Code → Download ZIP** rồi giải nén, hoặc `git clone`), đặt vào nơi bạn hay để tài liệu
2. Mở app **Claude** trên máy, vào **Cowork**, thêm thư mục vừa giải nén (nút "Add folder")
3. Nói với Claude: *"Đọc file CLAUDE.md trong thư mục này rồi thiết lập xưởng phim cho tôi."*

Claude sẽ tự cài môi trường (10-20 phút, cần mạng), hỏi bạn vài câu về phong cách, tải nhạc theo mẫu bạn chọn và render thử một intro để bạn duyệt. Chi tiết từng bước và những gì cần chuẩn bị: [BAT-DAU.md](BAT-DAU.md).

## Cấu trúc thư mục

```
xuong-phim-claude/
├── README.md              ← bạn đang đọc
├── BAT-DAU.md             ← cài lần đầu, từng bước, cho người mới
├── HUONG-DAN.md           ← cách đặt yêu cầu, ví dụ, sự cố thường gặp
├── CLAUDE.md              ← điểm vào cho Claude (đọc đầu mỗi phiên)
├── phong-cach/            ← PHONG-CACH.md: bản đồ phong cách của BẠN; mau/: 4 mẫu khởi đầu
├── brand/                 ← brand.json (tên, chức danh, bảng màu) + logo/ (thả logo vào đây)
├── skills/                ← 9 quy trình chuẩn cho Claude (thiết lập + 8 năng lực dựng phim)
├── docs/                  ← tài liệu kỹ thuật cho Claude: môi trường, bài học từ dự án thật
├── thu-vien/              ← danh mục nhạc/hiệu ứng/hình đã kiểm định (không chứa file, tải lúc cài)
├── nhac-nen/  hieu-ung/   ← file âm thanh tải về, theo nhóm công dụng
├── do-hoa-chung/          ← preset intro/outro dùng chung, bố cục slide
├── studio/                ← đồ họa động Remotion (Claude quản lý)
├── tools/                 ← công cụ pipeline + cài đặt (Claude quản lý)
└── du-an/                 ← mỗi clip một thư mục: nguon/ → xuat-hoan-chinh/
```

## Cách nó chạy (cho người tò mò)

Video của bạn được xử lý ngay trên máy bạn bằng ffmpeg trong máy ảo của Cowork; gỡ băng bằng Whisper chạy tại máy (sherpa-onnx), nên footage không rời máy. Đồ họa động (intro, outro, thẻ, nhãn từ khoá) là các thành phần Remotion tối giản, render trong sandbox của Claude rồi ghép về. Mọi bước nặng đều tự nối tiếp khi bị ngắt, mọi file trung gian đều được đo hình khớp tiếng, và một bộ bài học từ các dự án thật (`docs/BAI-HOC.md`) giúp Claude không lặp lại lỗi cũ.

## Yêu cầu

- App Claude trên máy tính với Cowork (Mac Apple Silicon chạy tốt nhất; máy ảo Cowork có sẵn ffmpeg, Python, Node)
- Khoảng 3 GB trống cho model nhận dạng giọng nói và thư viện
- Mạng lúc cài; sau đó gỡ băng và dựng đều chạy offline

## Giấy phép

Mã nguồn và tài liệu: MIT (xem `LICENSE`). Font Lora và Be Vietnam Pro: SIL Open Font License. Nhạc và hiệu ứng KHÔNG nằm trong repo; danh mục ghi rõ giấy phép từng track (Pixabay Content License, hoặc CC-BY 4.0 của Kevin MacLeod cần ghi công).

## Đóng góp

Bạn dựng được clip tốt hơn nhờ một quy tắc mới, hay bắt được một lỗi? Mở issue hoặc pull request: sửa `skills/<tên>/SKILL.md` cho quy trình, `docs/BAI-HOC.md` cho bài học, `thu-vien/am-thanh.json` cho track mới (nhớ kiểm Content ID). Repo được khởi tạo bởi Lương Dũng Nhân từ xưởng phim cá nhân đã vận hành thật cùng Claude.
