# CLAUDE.md - điểm vào cho Claude khi làm việc trong thư mục này

Đây là **xưởng dựng clip trình bày kiến thức** cho chuyên gia, giảng viên, nhà chuyên môn: người dùng thả video quay thô (và slide, nếu có) vào một thư mục, nói yêu cầu bằng lời thường; Claude làm toàn bộ phần kỹ thuật (gỡ băng, cắt, đồ họa, nhạc, xuất, nghiệm thu) bằng bộ công cụ trong repo này. Người dùng thường mới dùng AI, không biết ffmpeg hay Remotion là gì, và không cần biết.

## Thứ tự đọc ở đầu mỗi phiên

1. File này
2. `phong-cach/PHONG-CACH.md`: bản đồ phong cách của người dùng (tên, chức danh nguyên văn, mẫu màu, nhạc, quy tắc chữ, sổ tay góp ý). Còn dấu `[...]` chưa điền, hoặc chưa có `tools/.cai-dat.json` → chạy skill `skills/phim-thiet-lap/SKILL.md` trước mọi việc khác
3. `docs/QUY-TRINH-KY-THUAT.md`: môi trường, bản đồ tài nguyên, quy ước chất lượng, cổng nghiệm thu, hai hệ mốc thời gian
4. SKILL.md của việc đang làm (bảng dưới). Skill là quy trình chuẩn đã được kiểm chứng qua nhiều dự án thật; làm theo skill, không tự nghĩ lại quy trình. `docs/BAI-HOC.md` khi gặp tình huống lạ

## Việc nào, skill nào

| Người dùng nói | Skill |
|---|---|
| "thiết lập", "bắt đầu", "đổi màu/logo/chức danh mặc định", lần đầu dùng | `skills/phim-thiet-lap/` |
| "dựng bài giảng", "cắt bài này", "ghép intro outro", thả clip vào `nguon/` | `skills/phim-dung-bai/` (quy trình chủ lực; đọc cả `references/bien-tap.md`) |
| "infomotion", "làm video từ audio", "video hoạt hình giải thích", "explainer video", chỉ có file ghi âm không có video quay mặt | `skills/phim-infomotion/` (không có cảnh quay để cắt - hình tự nghĩ ra từ lời nói, dùng component `YNiem`/`YCanh`) |
| "bài giảng có slide", có PPTX/PDF/ảnh slide cạnh video | `skills/phim-bai-giang-slide/` |
| "cắt clip ngắn", "Reels", "Shorts", "TikTok", "teaser" | `skills/phim-clip-ngan/` |
| "podcast hai người", "nhiều góc quay", nguon có nhiều thư mục con | `skills/phim-multicam/` |
| "làm intro", "infographic", "bảng tên", "sửa đồ họa" | `skills/phim-do-hoa/` |
| "gỡ băng", "phụ đề", "transcript" | `skills/phim-transcript/` |
| "tìm hình minh hoạ", "cần ảnh cho đoạn này" | `skills/phim-tu-lieu/` |
| "màu bị bạc", "hai góc lệch màu", "da không đẹp" | `skills/phim-mau-sac/` |
| "phim tài liệu", "phóng sự phỏng vấn", "phim giới thiệu dự án/chương trình", "sắp có sự kiện muốn làm phim", "phỏng vấn ai, hỏi gì", "cần quay cảnh trám nào", nhiều file phỏng vấn nhiều người | `skills/phim-tai-lieu-phong-van/` (hai pha: Kế hoạch ghi hình trước quay, kịch bản thực tế sau quay; gọi phim-dung-bai/phim-do-hoa ở bước dựng) |

## Cách làm việc với người dùng mới

- Nói lời thường. Không nhắc ffmpeg, Remotion, LUFS, timeline, sandbox trừ khi người dùng hỏi. "Đang gỡ băng lời giảng", "đang dựng bản nháp", "đang kiểm hình có khớp tiếng không" là đủ
- Người dùng chỉ phải làm ba việc: thả file vào đúng thư mục, bấm link tải khi được nhờ, xem bản nháp và góp ý. Mọi lệnh Claude tự chạy
- Hỏi ít, mỗi lượt tối đa 4 câu, luôn có mặc định lấy từ PHONG-CACH.md. Hai chốt duyệt cố định: phương án cắt và overlay (trước khi dựng), bản nháp 480p (trước bản chính). Phim tài liệu phỏng vấn có thêm hai chốt trên giấy: Kế hoạch ghi hình (trước khi quay) và kịch bản thực tế có ước tính thời lượng (trước khi dựng). Người dùng vắng mặt: chọn mặc định, ghi rõ giả định, làm tiếp
- Báo tiến độ ngắn khi việc chạy lâu (gỡ băng bài dài, xuất bản chính), nói rõ đang chờ máy chứ không phải chờ người dùng
- Kết mỗi dự án bằng: file nằm ở `du-an/<tên>/xuat-hoan-chinh/`, thời lượng, dung lượng, dòng ghi công nhạc (nếu dùng track CC-BY), và câu "nghiệm thu máy: ĐẠT"

## Quy tắc cứng

1. Chưa qua cổng máy (`tools/nghiem-thu.py` ĐẠT) thì chưa nói "xong". Không hạ ngưỡng, không bật cờ bỏ qua kiểm tra để cho qua
2. Chức danh, tên riêng, "từ ngữ phải viết đúng" trong PHONG-CACH.md là bất khả xâm phạm; chữ trên màn hình theo mục 4 của file đó (mặc định: thuần Việt, sentence case, gạch ngang thường, không Title Case, không emoji trong đồ họa)
3. Nhạc chỉ từ `nhac-nen/THU-VIEN.md` (đã kiểm định) hoặc `nhac-nen/rieng/`; track CC-BY kèm dòng ghi công trong mô tả video
4. Không hardcode đường dẫn tuyệt đối của máy vào bất kỳ file nào của xưởng; gốc xưởng lấy từ thư mục đã kết nối
5. Mã nguồn sửa ở sandbox đám mây (studio, tools) phải commit về máy ngay; máy là bản gốc
6. Một góp ý lặp lại lần thứ hai là tín hiệu sửa NGUỒN MẶC ĐỊNH (brand.json, preset, defaultProps), không chỉ sửa dự án đang làm; ghi vào "Sổ tay góp ý" cuối PHONG-CACH.md
7. Bài học kỹ thuật đáng giữ sau mỗi dự án ghi vào `docs/BAI-HOC.md` (ngắn: chuyện gì, gốc rễ, quy tắc); sửa skill thì sửa thẳng `skills/<tên>/SKILL.md`, trường `description` của skill là mô tả kích hoạt, không ghi changelog vào đó
8. Footage của người dùng không rời máy họ, trừ vài khung hình để xem khi cần

## Kiểm nhanh trạng thái xưởng

`python3 tools/cai-dat.py --trang-thai` (máy người dùng). Chưa cài → phim-thiet-lap. Sau khi sửa bất kỳ tool nào → `python3 tools/kiem-tra-xuong.py --co-slide` phải ĐẠT.
