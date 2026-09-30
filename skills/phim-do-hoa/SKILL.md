---
name: "phim-do-hoa"
description: "Tạo, chỉnh sửa và render đồ họa video Remotion minimalist cho người dùng - intro, outro, thẻ chuyển phần, infographic động (danh sách, trích dẫn, con số, các bước), bảng tên và chữ nổi nền trong suốt, hình ẩn dụ vẽ nét - từ studio trong thư mục \"xuong-phim-claude\". Kích hoạt khi user yêu cầu \"làm intro\", \"làm outro\", \"tạo infographic\", \"làm bảng tên\", \"thẻ chuyển phần\", \"render đồ họa\", \"đổi màu/font/brand đồ họa video\", \"thêm kiểu animation mới\", \"sửa template Remotion\", hoặc bất kỳ yêu cầu đồ họa chuyển động cho video nào - kể cả khi user chỉ mô tả \"cần cái hình động minh họa 4 bước cho đoạn này\". Cũng kích hoạt khi cần cập nhật logo hoặc brand.json cho hệ thống phim. KHÔNG dùng cho dựng video hoàn chỉnh (phim-dung-bai), video chỉ có giọng ghi âm (phim-infomotion), phim hoạt hình tự sự (phim-hoat-hoa) hay thiết kế tĩnh, poster (canvas-design)."
---

# Đồ họa Remotion minimalist

Studio nằm ở `studio/` trong thư mục xưởng (bản gốc trên máy của người dùng), render trong sandbox đám mây rồi commit về máy. Đọc trước: `skills/_chung/van-hanh.md` (hai nơi chạy lệnh, truyền file, chữ và chức danh) và `skills/_chung/overlay-va-the.md` (chọn loại đồ họa, vị trí, không che mặt); sandbox chưa dựng thì làm mục "Khởi động phiên mới" của `docs/QUY-TRINH-KY-THUAT.md`. Props chi tiết từng composition và các bẫy đã gặp: `skills/phim-do-hoa/references/props-va-bay.md`.

## Ngôn ngữ thiết kế (bất biến giữa các dự án)

Minimalist, tĩnh tại, "thở". Chi tiết tông, màu, chữ: `phong-cach/PHONG-CACH.md` mục 3-4; mã màu gốc trong `brand/brand.json`.

- Khoảng trắng rộng; mỗi khung hình một ý; không bao giờ nhồi.
- Chuyển động chậm và êm: fade + trồi nhẹ 20-30 px, easing bezier(0.22, 1, 0.36, 1), 24-34 frame mỗi chuyển động; không spring nảy, không hiệu ứng lòe loẹt, không emoji.
- Typography: Lora 500/600 cho tiêu đề, Be Vietnam Pro 400/500/600 cho nội dung; sentence case hoặc FULL-CAP cho kicker, không Title Case.
- Hai theme light, dark trong `brand.json`; mỗi dự án một theme, không pha.
- Đường nhấn mảnh 3 px là chữ ký thị giác; mọi thành phần mới nên có nó.

## Composition có sẵn

22 composition (11 loại, mỗi loại hai khung `-ngang` 1920x1080 và `-doc` 1080x1920, 30 fps). Danh sách thật lúc nào cũng kiểm được bằng `npx remotion compositions src/index.ts`.

| Loại | Dùng cho | Xuất |
|---|---|---|
| Intro, Outro | mở, kết từ preset `do-hoa-chung/preset-intro-outro-<ngang\|doc>.json` | mp4 |
| SectionTitle | thẻ chuyển hồi, chuyển phần | mp4 |
| InfoList, InfoSteps, InfoQuote, InfoStat | infographic toàn khung: liệt kê; tiến trình nhãn ngắn; câu đúc kết; một con số | mp4 |
| Benefits | chữ, pill đè lên hình thật (một mục = một dòng chữ nổi; nhiều mục = hiện dần theo lời) | webm alpha |
| LowerThird | bảng tên người nói | webm alpha |
| YNiem, YCanh | ẩn dụ vẽ nét (một khái niệm) và cảnh vẽ tay tám kỹ thuật chuyển động, chủ yếu cho infomotion; bản nổi mặc định canh giữa, khi dựng clip hỏi người dùng có muốn đổi vị trí không | mp4 toàn khung hoặc webm alpha nổi |

Studio KHÔNG có composition `Caption`. Đồ họa nổi (Benefits, LowerThird, YNiem/YCanh nổi) ghép bằng trường `overlay` của `tools/assemble.py`; đồ họa toàn khung bằng `insert` hoặc `broll` (xem `_chung/timeline-va-dung.md`).

## Render đồ họa (việc thường gặp nhất)

1. **Soạn job JSON**: intro, outro bắt đầu từ preset (đủ placeholder; hướng dẫn tinh chỉnh `do-hoa-chung/GHI-CHU.md`); đồ họa khác theo mẫu `du-an/_mau/do-hoa/job-do-hoa.json`. `brandFile` trỏ `brand/brand.json`; đồ họa nổi đặt `"alpha": true`. File QR, hình riêng của dự án khai báo qua `"assets"` (đường dẫn tương đối so với file job); QR tạo ở sandbox bằng python `qrcode`. Prop có default kiểu placeholder (như `subtitle` của Intro) mà không dùng thì đặt `""` tường minh. Job JSON giữ trong `du-an/<x>/do-hoa/job/`.
2. **Still trước**: đồ họa mới hoặc props lạ thì render một still (`npx remotion still ... --frame=<giữa bài> --props=...`) và xem bằng Read: chữ Việt đủ dấu, không tràn khung, đúng theme. Job đổi sau still thì render lại still hoặc trích khung từ file cuối.
3. **Render ở sandbox**: `node tools/render-do-hoa.mjs <job.json> --studio <đường dẫn tuyệt đối>`. Nhiều đồ họa gộp một job để chạy tuần tự; không chạy song song; nhiều job thì `--gioi-han 150` và lặp đúng lệnh khi thoát mã 2. Script tự đồng bộ `brand/logo/`, tự đo thời lượng, bỏ qua job đã render đúng props.
4. **Commit** về `du-an/<x>/do-hoa/<ngang|doc>/` trên máy theo `_chung/van-hanh.md` (tên staged mới mỗi lần sửa, so md5, file lớn hơn 20 MB thì split).
5. **Soi chữ bằng mắt**: `nghiem-thu.py do-hoa` và cổng máy không đọc chữ trên hình. Sau MỖI lần sửa chữ (kể cả một chữ số), trích khung tại đúng mốc và xem bằng Read trước khi báo xong; đồ họa nổi kiểm thêm trên khung hình thật của video đã dựng.

## Thêm component mới, sửa component

1. Viết theo pattern có sẵn: `Canvas` (nền + fade biên), `FadeUp`, `AccentLine` từ `common.tsx`, palette qua `resolvePalette(theme, brand)` (bảng màu của người dùng chọn từ `phong-cach/mau/` lúc thiết lập, ghi vào `brand/brand.json`), kích thước qua `useLayout()` để một component chạy đúng cả hai khung.
2. Đăng ký trong `Root.tsx` cho CẢ HAI khung ngang, dọc, có defaults và calculateMetadata. Tránh default kiểu placeholder; nếu có thì ghi rõ trong `props-va-bay.md`.
3. Kiểm: `npx tsc --noEmit` sạch → `npx remotion compositions src/index.ts` liệt kê đủ → still cả ngang lẫn dọc với nội dung Việt CÓ DẤU dài thực tế và xem hình, chú ý tràn khung khi nhiều mục.
4. Commit file nguồn về máy NGAY (máy là bản gốc; sandbox mất khi hết phiên).
5. Cập nhật bảng composition ở trên, bảng tài nguyên của `docs/QUY-TRINH-KY-THUAT.md` và số composition ở khối "Khởi động phiên mới" nếu đổi.

Hình ẩn dụ mới cho YNiem (slug) hay YCanh (variant): kèm một mục trong `do-hoa-chung/an-du-y-niem.json` (chưa có file thì tạo theo schema ở `skills/phim-infomotion/references/mau-kich-ban.md`) sau khi người dùng duyệt, không để slug "mồ côi".

## Cập nhật brand và logo

- Logo dùng mảng `"logos"` trong `brand/brand.json` (1-3 logo từ `brand/logo/`, cách chuẩn bị logo ở `brand/logo/README.md`; chưa có logo thì để mảng rỗng và dùng tên thương hiệu chữ `showBrandName`); hàng logo tự chuẩn hoá chiều cao, có vạch ngăn. Logo mới: thả vào `brand/logo/`, render still xem cân đối rồi mới render loạt. Ghi đè theo dự án, brand riêng của chương trình, clip không mang thương hiệu của người dùng: `props-va-bay.md` mục "Brand riêng và logo".
- Đổi màu, tagline, social trong `brand/brand.json` ảnh hưởng mọi dự án về sau: xác nhận với người dùng trước; nhu cầu một dự án thì ghi đè trong job.
- Chức danh, tagline trên clip là chỗ hay bị góp ý lặp lại: nguồn chuẩn là `phong-cach/PHONG-CACH.md` mục 1. Góp ý sửa câu chữ lần thứ hai là tín hiệu sửa NGUỒN MẶC ĐỊNH (brand.json, defaultProps) và ghi vào sổ tay góp ý của PHONG-CACH, không chỉ sửa job đang làm.

<!-- ban-nguon: phim-do-hoa 2026-09-30 8d8e9d80 -->
