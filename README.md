# Xưởng phim Claude

**Một xưởng dựng phim cùng AI ngay trên máy tính của bạn, dùng tốt nhất với Claude Cowork trên máy Mac chip Apple Silicon (mô hình Sonnet 5).** Đây là repo tôi đóng gói các quy trình làm việc, tiêu chuẩn và bộ skill chuyên dụng để dựng clip trình bày kiến thức bằng Claude Cowork, thích hợp cho chuyên gia, giảng viên và nhà chuyên môn.

Nguyên liệu bạn cần là clip quay mình nói trước máy (có thể kèm slide), hoặc nếu không thích lên hình thì chỉ cần thu âm giọng trình bày. Thả file nguồn vào đúng thư mục trong xưởng, nói yêu cầu bằng lời thường, Claude làm phần còn lại: gỡ băng, cắt gọn, chèn intro/outro và nhãn từ khoá, lồng nhạc đã kiểm định bản quyền, xuất bản ngang cho YouTube hoặc dọc cho Reels/Shorts, và tự kiểm chất lượng trước khi bàn giao.

Repo này là một xưởng hoàn chỉnh đã chạy và rút kinh nghiệm qua nhiều dự án thật của tôi, được tinh gọn lại để bạn thiết lập theo phong cách riêng và dùng ngay. Bạn không cần biết dựng phim, không cần biết lập trình, không cần cài phần mềm dựng: Claude tự cài đặt các môi trường và công cụ cần thiết, gồm Remotion để dựng slide và đồ họa động, FFmpeg để cắt dựng, Whisper để gỡ băng lời nói.

Xưởng chạy êm nhất trên Mac chip Apple Silicon. Windows cũng dùng được, nhưng cần Claude rà soát kỹ hơn, tinh chỉnh lại và cài thêm vài thư viện tuỳ máy. Tôi thiết lập xưởng này trên Claude, nhưng bạn vẫn có thể nhờ những trợ lý AI khác như Codex, ChatGPT Work, Antigravity... đọc repo rồi tự tinh chỉnh, cài đặt để dùng.

Bản thân tôi không có nhu cầu với clip hình ảnh hay âm thanh do AI tạo ra nên không đưa năng lực đó vào xưởng; bạn tự bổ sung thêm nếu cần.

## Bạn nhận được gì

- **Mười bốn năng lực dựng phim** đóng thành quy trình chuẩn [skill] cho Claude: dựng bài giảng chuyên gia trình bày trước máy quay; bài giảng có slide (xen mặt, slide, hoặc cả hai theo bố cục tối ưu); clip ngắn dọc có phụ đề; podcast và buổi quay nhiều máy (tự đồng bộ bằng âm thanh, tự chuyển góc theo người nói); đồ họa động tối giản; cảnh minh hoạ giải thích kiểu explainer (sơ đồ cơ chế, quy trình, so sánh, số liệu lớn dần theo lời nói, Claude vẽ riêng từng cảnh như một trang web chuyển động rồi chụp từng khung ra video), chèn làm cảnh trám cho bài giảng theo bốn kiểu: toàn khung, nền là khung hình mờ của chính đoạn quay, thẻ nổi cạnh người nói, người nói thu vào góc; video giải thích bằng đồ họa thông tin [infomotion] chỉ từ một file ghi âm, không cần lên hình; phim hoạt hình vẽ bằng code có nhân vật và cảnh, hình tượng hoá lời nói hay một câu chuyện (kèm bộ lệnh để tự làm hoặc chia sẻ, phương pháp kế thừa từ bộ lệnh phim "Nhà" của Đặng Hữu Sơn); gỡ băng tiếng Việt chạy ngay trên máy (video không rời máy bạn); tìm hình và tư liệu minh hoạ phù hợp nội dung, đã kiểm định bản quyền; căn chỉnh màu cơ bản khi thật cần; phim tài liệu phỏng vấn nhiều nhân vật giới thiệu một dự án hay sự kiện (Claude giúp lên kế hoạch ghi hình - phỏng vấn ai, hỏi gì, quay cảnh trám nào - trước khi quay, rồi viết kịch bản thực tế từ tư liệu thật và dựng); gói đăng tải tự soạn sau mỗi clip (ba phương án tiêu đề, mô tả YouTube có chương, status Facebook bằng giọng của bạn, ba thumbnail dựng từ khung hình thật của clip); Bàn dựng để bạn tự tay chỉnh nhỏ một bản nháp trên Chrome (kênh hình, tiếng, đồ họa, nhạc như phần mềm dựng) kèm Dựng bằng lời: bôi đen chữ thừa trong lời bạn nói, hình và tiếng được cắt đúng chỗ
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
├── Go bang tren Mac.command ← bấm đúp để gỡ băng large-v3 trên Mac (khi Claude nhờ)
├── phong-cach/            ← PHONG-CACH.md: bản đồ phong cách của BẠN; mau/: 4 mẫu khởi đầu
├── brand/                 ← brand.json (tên, chức danh, bảng màu) + logo/ (thả logo vào đây)
├── Mo ban dung.command   ← bấm đúp để mở Bàn dựng (tự chỉnh nhỏ bản nháp trên Chrome)
├── skills/                ← 15 quy trình chuẩn cho Claude (thiết lập + 14 năng lực dựng phim)
├── docs/                  ← tài liệu kỹ thuật cho Claude: môi trường, bài học từ dự án thật
├── thu-vien/              ← danh mục nhạc/hiệu ứng/hình đã kiểm định (không chứa file, tải lúc cài)
├── nhac-nen/  hieu-ung/   ← file âm thanh tải về, theo nhóm công dụng
├── do-hoa-chung/          ← preset intro/outro dùng chung, bố cục slide, canh-kit/ (bộ thiết kế cảnh minh hoạ)
├── studio/                ← đồ họa động Remotion (Claude quản lý)
├── tools/                 ← công cụ pipeline + cài đặt (Claude quản lý)
└── du-an/                 ← mỗi clip một thư mục: nguon/ → xuat-hoan-chinh/
```

## Cách nó chạy (cho người tò mò)

Video của bạn được xử lý ngay trên máy bạn bằng ffmpeg trong máy ảo của Cowork; gỡ băng bằng Whisper chạy tại máy (sherpa-onnx: model turbo trong máy ảo, hoặc large-v3 trên Mac khi bạn bấm đúp `Go bang tren Mac.command`), nên footage không rời máy. Đồ họa động (intro, outro, thẻ, nhãn từ khoá) là các thành phần Remotion tối giản, render trong sandbox của Claude rồi ghép về. Cảnh minh hoạ là trang web có thời gian ảo: cùng một file vừa xem chạy trực tiếp trên trình duyệt để bạn duyệt chuyển động thật, vừa được tua tới từng khung trong Chromium không giao diện rồi ghép bằng ffmpeg, nên máy chậm chỉ làm render lâu hơn chứ không rớt khung. Kiểu chèn cần hình quay thật (nền mờ, người nói thu vào góc) được ghép ngay trên máy bạn. Mọi bước nặng đều tự nối tiếp khi bị ngắt, mọi file trung gian đều được đo hình khớp tiếng, và một bộ bài học từ các dự án thật (`docs/BAI-HOC.md`) giúp Claude không lặp lại lỗi cũ.

## Yêu cầu

- App Claude trên máy tính với Cowork, dùng tốt nhất với mô hình Sonnet 5 (Mac Apple Silicon chạy êm nhất; máy ảo Cowork có sẵn ffmpeg, Python, Node)
- Windows dùng được, nhưng cần Claude rà soát kỹ hơn và tinh chỉnh, cài thêm vài thư viện tuỳ máy
- Khoảng 3 GB trống cho model nhận dạng giọng nói và thư viện (thêm khoảng 2 GB nếu muốn dùng large-v3 trên Mac)
- Mạng lúc cài và lần đầu gỡ băng trên Mac; sau đó gỡ băng và dựng đều chạy offline
- Muốn dùng trợ lý AI khác ngoài Claude (Codex, ChatGPT Work, Antigravity...): nhờ trợ lý đó đọc `CLAUDE.md` rồi tự tinh chỉnh, cài đặt cho phù hợp với máy và công cụ của nó

## Giấy phép

Mã nguồn và tài liệu: MIT (xem `LICENSE`). Font Lora, Be Vietnam Pro và JetBrains Mono: SIL Open Font License (bản nhúng cho cảnh minh hoạ nằm trong `do-hoa-chung/canh-kit/fonts/` kèm giấy phép). Phần nguyên lý thiết kế cảnh minh hoạ có tham khảo bộ skill "faceless explainer" của HyperFrames (HeyGen, Apache 2.0); xưởng không dùng mã của dự án đó. Nhạc và hiệu ứng KHÔNG nằm trong repo; danh mục ghi rõ giấy phép từng track (Pixabay Content License, hoặc CC-BY 4.0 của Kevin MacLeod cần ghi công).

## Tác giả

Xưởng phim này do tôi, **Lương Dũng Nhân** (M.Ed, PCC, Humanistic AI Practitioner), xây dựng từ xưởng phim cá nhân đã vận hành thật, và gửi tặng lại hoàn toàn miễn phí để cộng đồng giáo dục cùng dùng. Website: [ldn.edu.vn](https://ldn.edu.vn). Email: hello@ldn.edu.vn.

Nếu bạn dùng, chia sẻ lại hoặc giới thiệu repo này (bài viết, video, fork công khai...), một dòng ghi công dẫn về tác giả và nguồn gốc trên sẽ rất được trân trọng.

## Đóng góp

Bạn dựng được clip tốt hơn nhờ một quy tắc mới, hay bắt được một lỗi? Mở issue hoặc pull request. Skill, `docs/`, `tools/` và `studio/` được đồng bộ tự động từ xưởng gốc của tác giả, nên thay đổi ở đó sẽ được chép về bản gốc trước rồi mới vào repo; `thu-vien/am-thanh.json` cho track mới thì sửa thẳng (nhớ kiểm Content ID). Trước khi gửi, chạy `python3 tools/kiem-tai-lieu.py` phải ĐẠT.
