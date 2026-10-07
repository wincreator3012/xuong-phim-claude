# Xưởng phim Claude

**Một xưởng dựng phim cùng AI ngay trên máy tính của bạn, dùng tốt nhất với Claude Cowork trên máy Mac chip Apple Silicon (với mô hình Claude mới nhất ở tầm trung như Sonnet là đủ, không cần dòng đỉnh cao như Opus).** Đây là repo tôi đóng gói các quy trình làm việc, tiêu chuẩn và bộ skill chuyên dụng để dựng clip trình bày kiến thức bằng Claude Cowork, thích hợp cho chuyên gia, giảng viên và nhà chuyên môn.

Nguyên liệu bạn cần là clip quay mình nói trước máy (có thể kèm slide), hoặc nếu không thích lên hình thì chỉ cần thu âm giọng trình bày. Thả file nguồn vào đúng thư mục trong xưởng, nói yêu cầu bằng lời thường, Claude làm phần còn lại: gỡ băng, cắt gọn, chèn intro/outro và nhãn từ khoá, lồng nhạc đã kiểm định bản quyền, xuất bản ngang cho YouTube hoặc dọc cho Reels/Shorts, và tự kiểm chất lượng trước khi bàn giao.

Repo này là một xưởng hoàn chỉnh đã chạy và rút kinh nghiệm qua nhiều dự án thật của tôi, được tinh gọn lại để bạn thiết lập theo phong cách riêng và dùng ngay. Bạn không cần biết dựng phim, không cần biết lập trình, không cần cài phần mềm dựng: Claude tự cài đặt các môi trường và công cụ cần thiết, gồm Remotion để dựng slide và đồ họa động, FFmpeg để cắt dựng, Whisper để gỡ băng lời nói.

Xưởng chạy êm nhất trên Mac chip Apple Silicon. Windows cũng dùng được, nhưng cần Claude rà soát kỹ hơn, tinh chỉnh lại và cài thêm vài thư viện tuỳ máy. Tôi thiết lập xưởng này trên Claude, nhưng bạn vẫn có thể nhờ những trợ lý AI khác như Codex, ChatGPT Work, Antigravity... đọc repo rồi tự tinh chỉnh, cài đặt để dùng.

Bản thân tôi không có nhu cầu với clip hình ảnh hay âm thanh do AI tạo ra nên không đưa năng lực đó vào xưởng; bạn tự bổ sung thêm nếu cần.

## Xưởng làm được gì cho bạn

Mười bốn năng lực dựng phim, mỗi năng lực là một quy trình chuẩn [skill] Claude làm theo. Bạn không cần nhớ tên chúng: nói bạn đang có gì và muốn gì, Claude chọn đúng quy trình.

| Bạn đang có | Xưởng làm ra |
|---|---|
| Video bạn nói trước máy (bài giảng, chia sẻ, giới thiệu khoá học) | Clip ngang 16:9 hoàn chỉnh: cắt khoảng lặng và đoạn nói hỏng, intro và outro, nhãn từ khoá, nhạc, chương YouTube |
| Bài giảng kèm file slide, hoặc bài nói trên sân khấu có khán giả | Dàn hình xen mặt, slide hoặc cả hai theo từng đoạn lời, không bao giờ để chữ hay thẻ che mặt ai |
| Một bài dài, muốn clip ngắn cho mạng xã hội | Clip dọc 9:16 cho Reels, Shorts, TikTok: chọn đoạn có hook, phụ đề, bảng tên, cảnh minh hoạ khi ý cần hình |
| Podcast hoặc buổi quay nhiều máy | Tự đồng bộ các góc bằng âm thanh, chuyển góc theo người nói |
| Một đoạn giải thích cơ chế, quy trình, so sánh, số liệu | Cảnh minh hoạ động kiểu explainer vẽ riêng cho đoạn đó (sơ đồ lớn dần theo lời nói), chèn làm cảnh trám theo bốn kiểu: toàn khung, nền là khung hình mờ, thẻ nổi cạnh người nói, người nói thu vào góc |
| Chỉ có file ghi âm giọng nói | Video giải thích bằng đồ họa thông tin tối giản [infomotion], hoặc phim hoạt hình vẽ bằng code có nhân vật và cảnh (kèm bộ lệnh để tự làm hoặc chia sẻ) |
| Một dự án, chương trình, sự kiện cần phim giới thiệu | Phim tài liệu phỏng vấn nhiều nhân vật; Claude giúp lên kế hoạch ghi hình (phỏng vấn ai, hỏi gì, quay cảnh nào) trước khi quay, rồi viết kịch bản thực tế từ tư liệu thật và dựng |
| Cần chữ hoặc hình phụ trợ | Gỡ băng tiếng Việt ngay trên máy (video không rời máy bạn), hình minh hoạ đã kiểm bản quyền, căn chỉnh màu cơ bản khi thật cần, intro, outro, bảng tên, infographic động |
| Một clip đã dựng, sắp đăng | Gói đăng tải tự soạn sau mỗi clip: ba phương án tiêu đề, mô tả YouTube có chương, status Facebook bằng giọng của bạn, ba thumbnail dựng từ khung hình thật |
| Bản nháp chỉ còn vài chỗ nhỏ | Bàn dựng trên Chrome để tự tay chỉnh (kênh hình, tiếng, đồ họa, nhạc như phần mềm dựng), kèm Dựng bằng lời: bôi đen chữ thừa trong lời nói, hình và tiếng được cắt đúng chỗ |

Ngoài các năng lực trên, bạn nhận được:

- **Một bước thiết lập phong cách** khoảng 30 phút: Claude hỏi bạn là ai, dạy gì, cho ai, thích cảm giác nào (bốn mẫu để chọn hoặc mô tả riêng), rồi điền tên, chức danh, màu sắc, nhạc, thông điệp kết vào chỗ đã chừa sẵn. Mọi clip sau đó mang đúng dấu ấn của bạn và đổi được bằng một câu nói
- **Một buổi giới thiệu xưởng** khoảng 10 phút ngay sau thiết lập: Claude trình bày có hệ thống xưởng làm ra được gì cho bạn, một dự án chạy thế nào, những thói quen giúp dùng hiệu quả nhất, những gì xưởng chưa làm, rồi cùng bạn chọn bước đầu tiên. Gọi lại bất cứ lúc nào bằng câu "giới thiệu lại xưởng"
- **Thư viện chất liệu sạch**: danh mục nhạc nền và hiệu ứng đã kiểm từng trang nguồn (dùng thương mại mọi nền tảng, không Content ID), tải về theo mẫu phong cách bạn chọn; danh mục nguồn hình miễn phí và quy tắc giấy phép
- **Cổng nghiệm thu tự động**: hình khớp tiếng tới 2 khung hình, âm lượng chuẩn -14 LUFS, không khoảng đen, không đứng hình. Claude không được nói "xong" khi máy chưa báo đạt
- **Bài học từ các dự án thật**, ghi thành quy tắc cứng: chữ và thẻ không bao giờ che mặt bất kỳ ai, thumbnail xen cận mặt với khung rộng, chương YouTube đúng luật, và nhiều điều khác trong `docs/BAI-HOC.md`
- **Hướng dẫn tận tình cho người mới**: `BAT-DAU.md` (cài lần đầu, từng bước), `HUONG-DAN.md` (cách đặt yêu cầu, mười hai thói quen dùng hiệu quả, ví dụ, xử lý sự cố)

## Dùng sao cho hiệu quả nhất

Sáu điều đáng nhớ nhất, đầy đủ hơn ở `HUONG-DAN.md`:

1. Bắt đầu bằng một clip nhỏ có thật (3-10 phút), làm trọn một vòng từ nháp tới gói đăng tải.
2. Quay cho dễ dựng: ngừng một nhịp giữa các ý, đặt câu chốt mạnh nhất lên đầu, để mic gần.
3. Nói mục đích, người xem và nơi đăng trong một câu yêu cầu; chốt trước điểm vào, điểm ra nếu bạn đã biết.
4. Dành sức cho bảng phương án cắt: sửa ở đó chỉ mất một câu nói, sửa ở bản chính mất cả giờ.
5. Góp ý theo mốc thời gian, rồi dặn "từ nay luôn..." khi chê một điều, để Claude ghi vào sổ tay và các clip sau không lặp lại.
6. Tái dùng một buổi quay cho nhiều sản phẩm: bài đầy đủ, vài clip dọc, mỗi cái một gói đăng tải.

## Bắt đầu trong ba bước

1. Tạo một thư mục tên `Xuong phim AI` trong Documents. Tải repo này về (nút **Code → Download ZIP** rồi giải nén, hoặc `git clone`), đặt thư mục repo vào trong `Xuong phim AI` và giữ tên `xuong-phim-claude`
2. Mở app **Claude** trên máy, vào **Cowork**, thêm thư mục `Xuong phim AI` (nút "Add folder")
3. Nói với Claude: *"Đọc file CLAUDE.md trong thư mục xuong-phim-claude rồi thiết lập xưởng phim cho tôi."*

Claude sẽ tự cài môi trường (10-20 phút, cần mạng), hỏi bạn vài câu về phong cách, tải nhạc theo mẫu bạn chọn và render thử một intro để bạn duyệt. Cuối cùng Claude giới thiệu xưởng cho bạn một vòng (khoảng 10 phút) và cùng bạn chọn clip đầu tiên. Chi tiết từng bước và những gì cần chuẩn bị: [BAT-DAU.md](BAT-DAU.md).

## Cấu trúc thư mục

Repo chỉ chứa "năng lực" của xưởng (cách làm, công cụ, phong cách của bạn); dự án và thành phẩm nằm ở hai thư mục cạnh repo, nên cập nhật xưởng không bao giờ đụng tới video của bạn, và sao lưu một dự án chỉ cần dời một thư mục.

```
Xuong phim AI/
├── Du an/                 ← mỗi dự án một thư mục <năm-tháng tên>/: nguon/ (video bạn thả vào), nháp, file dựng
├── Thanh pham/            ← sản phẩm để đăng: <năm-tháng tên dự án>/00 Video day du/, Short 01 .../ (kèm gói đăng tải)
└── xuong-phim-claude/     ← repo này
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
└── tools/                 ← công cụ pipeline + cài đặt (Claude quản lý)
```

## Cách nó chạy (cho người tò mò)

Video của bạn được xử lý ngay trên máy bạn bằng ffmpeg trong máy ảo của Cowork; gỡ băng bằng Whisper chạy tại máy (sherpa-onnx: model turbo trong máy ảo, hoặc large-v3 trên Mac khi bạn bấm đúp `Go bang tren Mac.command`), nên footage không rời máy. Đồ họa động (intro, outro, thẻ, nhãn từ khoá) là các thành phần Remotion tối giản, render trong sandbox của Claude rồi ghép về. Cảnh minh hoạ là trang web có thời gian ảo: cùng một file vừa xem chạy trực tiếp trên trình duyệt để bạn duyệt chuyển động thật, vừa được tua tới từng khung trong Chromium không giao diện rồi ghép bằng ffmpeg, nên máy chậm chỉ làm render lâu hơn chứ không rớt khung. Kiểu chèn cần hình quay thật (nền mờ, người nói thu vào góc) được ghép ngay trên máy bạn. Mọi bước nặng đều tự nối tiếp khi bị ngắt, mọi file trung gian đều được đo hình khớp tiếng, và một bộ bài học từ các dự án thật (`docs/BAI-HOC.md`) giúp Claude không lặp lại lỗi cũ.

## Yêu cầu

- App Claude trên máy tính với Cowork, chọn mô hình Claude mới nhất ở tầm trung như Sonnet là đủ dùng, không cần dòng đỉnh cao như Opus (Mac Apple Silicon chạy êm nhất; máy ảo Cowork có sẵn ffmpeg, Python, Node)
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
