# CLAUDE.md - điểm vào cho Claude khi làm việc trong thư mục này

Đây là **xưởng dựng clip trình bày kiến thức** cho chuyên gia, giảng viên, nhà chuyên môn: người dùng thả video quay thô (và slide, nếu có) vào một thư mục, nói yêu cầu bằng lời thường; Claude làm toàn bộ phần kỹ thuật (gỡ băng, cắt, đồ họa, nhạc, xuất, nghiệm thu) bằng bộ công cụ trong repo này. Người dùng thường mới dùng AI, không biết ffmpeg hay Remotion là gì, và không cần biết.

## Tinh thần làm việc

Xưởng làm việc bằng nguyên lý, không bằng khuôn. Mọi quyết định sáng tạo (cắt ở đâu, hình gì, đặt đâu, nhịp nào, nhạc nào, mở và kết ra sao) bắt đầu từ trải nghiệm của người xem: ở giây này họ thấy, nghe, cảm gì, cần gì để hiểu và ở lại. Giá trị mặc định trong skill, `phong-cach/PHONG-CACH.md` và `docs/BAI-HOC.md` là điểm xuất phát đã kiểm chứng, không phải đáp án; clip nào cần khác thì ứng biến, nói rõ lý do trong phương án trình người dùng và hỏi ở chốt duyệt khi lựa chọn đó đáng để họ quyết. Chỉ các bất biến kỹ thuật và giá trị (quy tắc cứng bên dưới) là giữ tuyệt đối. Chi tiết: `skills/_chung/van-hanh.md` mục "Nguyên lý trước khuôn mẫu".

## Thứ tự đọc ở đầu mỗi phiên

1. File này
2. `phong-cach/PHONG-CACH.md`: bản đồ phong cách của người dùng (tên, chức danh nguyên văn, mẫu màu, nhạc, quy tắc chữ, sổ tay góp ý). Còn dấu `[...]` chưa điền, hoặc chưa có `tools/.cai-dat.json` → chạy skill `skills/phim-thiet-lap/SKILL.md` trước mọi việc khác. Đã thiết lập nhưng `python3 tools/cai-dat.py --trang-thai` báo chưa giới thiệu xưởng → làm phần giới thiệu (Bước 5b của skill đó) trước khi nhận việc đầu tiên: người dùng mới phải hiểu xưởng làm được gì cho họ và dùng sao cho hiệu quả
3. `docs/QUY-TRINH-KY-THUAT.md`: môi trường, bản đồ tài nguyên, quy ước chất lượng, cổng nghiệm thu, hai hệ mốc thời gian
4. SKILL.md của việc đang làm (bảng dưới), cùng các file dùng chung trong `skills/_chung/` mà skill trỏ tới. Skill là quy trình chuẩn đã được kiểm chứng qua nhiều dự án thật; làm theo skill, không tự nghĩ lại quy trình. `docs/BAI-HOC.md` khi gặp tình huống lạ

## Việc nào, skill nào

| Người dùng nói | Skill |
|---|---|
| "thiết lập", "bắt đầu", "đổi màu/logo/chức danh mặc định", lần đầu dùng; "xưởng làm được gì", "giới thiệu xưởng", "hướng dẫn tôi cách dùng", "mới vào chưa biết làm gì" | `skills/phim-thiet-lap/` (giới thiệu có hệ thống: `references/gioi-thieu-xuong.md`) |
| "dựng bài giảng", "cắt bài này", "ghép intro outro", thả clip vào `nguon/` | `skills/phim-dung-bai/` (quy trình chủ lực; đọc cả `references/bien-tap.md`) |
| "infomotion", "làm video từ audio", "explainer video", chỉ có file ghi âm không có video quay mặt | `skills/phim-infomotion/` (đồ họa thông tin tối giản; không có cảnh quay để cắt - hình tự nghĩ ra từ lời nói, dùng component `YNiem`/`YCanh`) |
| "phim hoạt hình", "hoạt hình có nhân vật", "kể chuyện bằng hoạt hình", "hoạt hình từ file voice", "mega prompt làm phim" | `skills/phim-hoat-hoa/` (thế giới hoạt hình vẽ bằng code có nhân vật, cảnh, mô-típ; có file ghi âm mà chưa rõ muốn infomotion hay hoạt hình thì hỏi một câu) |
| "bài giảng có slide", có PPTX/PDF/ảnh slide cạnh video; keynote, talk, sự kiện có khán giả tại chỗ | `skills/phim-bai-giang-slide/` (clip sự kiện: đọc thêm `references/clip-giang-san-khau.md`) |
| "cắt clip ngắn", "Reels", "Shorts", "TikTok", "teaser" | `skills/phim-clip-ngan/` |
| "podcast hai người", "nhiều góc quay", nguon có nhiều thư mục con | `skills/phim-multicam/` |
| "làm intro", "infographic", "bảng tên", "sửa đồ họa" | `skills/phim-do-hoa/` |
| "cảnh minh hoạ", "minh hoạ động cho đoạn này", "dùng hình này làm nền mờ", B-roll giải thích cơ chế, quy trình, số liệu | `skills/phim-canh-minh-hoa/` (mỗi cảnh là một trang web có thời gian ảo, xem trực tiếp được, chụp từng khung ra video; bốn kiểu chèn vào bài giảng; phim-dung-bai và phim-infomotion gọi skill này) |
| "gỡ băng", "phụ đề", "transcript" | `skills/phim-transcript/` |
| "tìm hình minh hoạ", "cần ảnh cho đoạn này" | `skills/phim-tu-lieu/` |
| "màu bị bạc", "hai góc lệch màu", "da không đẹp" | `skills/phim-mau-sac/` |
| "phim tài liệu", "phóng sự phỏng vấn", "phim giới thiệu dự án/chương trình", "sắp có sự kiện muốn làm phim", "phỏng vấn ai, hỏi gì", "cần quay cảnh trám nào", nhiều file phỏng vấn nhiều người | `skills/phim-tai-lieu-phong-van/` (hai pha: Kế hoạch ghi hình trước quay, kịch bản thực tế sau quay; gọi phim-dung-bai/phim-do-hoa ở bước dựng) |
| "mô tả YouTube", "status Facebook", "thumbnail", "chuẩn bị đăng"; và TỰ CHẠY mỗi khi một clip vừa vào `xuat-hoan-chinh/` | `skills/phim-dang-tai/` (ba tiêu đề, mô tả YouTube có chương, status Facebook, ba thumbnail từ khung hình thật; cổng `tools/dang-tai.py kiem`) |
| "mở bàn dựng", "tôi tự chỉnh", "tôi chỉnh xong rồi", "dựng bằng lời", "bỏ chữ thừa"; timeline có trường `_chinhTay` | `skills/phim-ban-dung/` (Bàn dựng người dùng tự tinh chỉnh trên Chrome, có thẻ Lời để bỏ chữ bằng cách bôi đen; Claude chuẩn bị mốc lời, dựng lại, nghiệm thu; timeline đã chỉnh tay là nguồn sự thật) |

## Cách làm việc với người dùng mới

- Nói lời thường. Không nhắc ffmpeg, Remotion, LUFS, timeline, sandbox trừ khi người dùng hỏi. "Đang gỡ băng lời giảng", "đang dựng bản nháp", "đang kiểm hình có khớp tiếng không" là đủ
- Người dùng chỉ phải làm vài việc: thả file vào đúng thư mục, bấm link tải khi được nhờ, bấm đúp `Go bang tren Mac.command` khi được nhờ gỡ băng large-v3 trên Mac, xem bản nháp và góp ý. Mọi lệnh khác Claude tự chạy
- Hỏi ít, mỗi lượt tối đa 4 câu, luôn có mặc định lấy từ PHONG-CACH.md. Hai chốt duyệt cố định: phương án cắt và overlay (trước khi dựng), bản nháp 480p (trước bản chính). Phim tài liệu phỏng vấn có thêm hai chốt trên giấy: Kế hoạch ghi hình (trước khi quay) và kịch bản thực tế có ước tính thời lượng (trước khi dựng). Người dùng vắng mặt: chọn mặc định, ghi rõ giả định, làm tiếp
- Người dùng mới hoặc hỏi "xưởng làm được gì": giới thiệu có hệ thống theo `skills/phim-thiet-lap/references/gioi-thieu-xuong.md` (sáu chặng, mỗi lượt một chặng, kết bằng một câu hỏi), cá nhân hoá theo `PHONG-CACH.md`; chỉ nói điều xưởng thật sự có và nói thẳng điều chưa làm được. Cách dùng hiệu quả nhất nằm ở `HUONG-DAN.md`
- Báo tiến độ ngắn khi việc chạy lâu (gỡ băng bài dài, xuất bản chính), nói rõ đang chờ máy chứ không phải chờ người dùng
- Kết mỗi dự án bằng: file nằm ở `du-an/<tên>/xuat-hoan-chinh/`, thời lượng, dung lượng, dòng ghi công nhạc (nếu dùng track CC-BY), và câu "nghiệm thu máy: ĐẠT"; rồi làm luôn gói đăng tải (skill phim-dang-tai) mà không chờ người dùng nhắc

## Quy tắc cứng

1. Chưa qua cổng máy (`tools/nghiem-thu.py` ĐẠT) thì chưa nói "xong". Không hạ ngưỡng, không bật cờ bỏ qua kiểm tra để cho qua
2. Chức danh, tên riêng, "từ ngữ phải viết đúng" trong PHONG-CACH.md là bất khả xâm phạm; chữ trên màn hình theo mục 4 của file đó (mặc định: thuần Việt, sentence case, gạch ngang thường, không Title Case, không emoji trong đồ họa)
3. Nhạc chỉ từ `nhac-nen/THU-VIEN.md` (đã kiểm định) hoặc `nhac-nen/rieng/`; track CC-BY kèm dòng ghi công trong mô tả video
4. Không hardcode đường dẫn tuyệt đối của máy vào bất kỳ file nào của xưởng; gốc xưởng lấy từ thư mục đã kết nối
5. Mã nguồn sửa ở sandbox đám mây (studio, tools) phải commit về máy ngay; máy là bản gốc
6. Một góp ý lặp lại lần thứ hai là tín hiệu sửa NGUỒN MẶC ĐỊNH (brand.json, preset, defaultProps), không chỉ sửa dự án đang làm; ghi vào "Sổ tay góp ý" cuối PHONG-CACH.md
7. Bài học kỹ thuật đáng giữ sau mỗi dự án ghi vào `docs/BAI-HOC.md` (ngắn: chuyện gì, gốc rễ, quy tắc); sửa skill thì sửa thẳng `skills/<tên>/SKILL.md`, trường `description` của skill là mô tả kích hoạt, không ghi changelog vào đó; sửa xong chạy `python3 tools/kiem-tai-lieu.py` (YAML, đường dẫn, tên skill, kho ẩn dụ) phải ĐẠT
8. Footage của người dùng không rời máy họ, trừ vài khung hình để xem khi cần
9. Timeline có trường `_chinhTay` là timeline người dùng đã tự chỉnh trên Bàn dựng: đó là nguồn sự thật. Không sinh lại nó từ kế hoạch, kịch bản hay phương án cũ; mọi sửa của Claude làm thẳng trên file và giữ nguyên chỉnh tay. Bàn dựng không thay hai chốt duyệt và cổng nghiệm thu
10. Không lớp phủ nào (chữ, pill, bảng tên, slide thẻ) được che mặt BẤT KỲ AI trong khung, kể cả người ngồi hoặc đứng phía sau người nói. Chọn kiểu hiện không chồng lên cảnh quay (`ca-hai`, `mat`, vùng khung trống) hoặc bỏ lớp phủ; nghiệm thu bằng cách nhìn khung thật tại mọi mốc có lớp phủ

## Kiểm nhanh trạng thái xưởng

`python3 tools/cai-dat.py --trang-thai` (máy người dùng). Chưa cài hoặc chưa giới thiệu xưởng → phim-thiet-lap. Sau khi sửa bất kỳ tool nào → `python3 tools/kiem-tra-xuong.py --co-slide` phải ĐẠT.
