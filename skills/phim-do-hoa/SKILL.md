---
name: phim-do-hoa
description: Tạo, chỉnh sửa và render đồ họa video Remotion minimalist theo brand.json và phong cách của người dùng - intro, outro, thẻ chuyển phần, infographic động (danh sách, trích dẫn, con số, các bước), bảng tên nền trong suốt - từ studio trong thư mục xưởng (gốc repo xuong-phim-claude). Kích hoạt khi user yêu cầu "làm intro", "làm outro", "tạo infographic", "làm bảng tên", "thẻ chuyển phần", "render đồ họa", "đổi màu/font/brand đồ họa video", "thêm kiểu animation mới", "sửa template Remotion", hoặc bất kỳ yêu cầu đồ họa chuyển động cho video nào - kể cả khi user chỉ mô tả "cần cái hình động minh họa 4 bước cho đoạn này". Cũng kích hoạt khi cần cập nhật logo hoặc brand.json cho hệ thống phim. KHÔNG dùng cho dựng video hoàn chỉnh (skill phim-dung-bai) hay thiết kế tĩnh/poster (skill canvas-design).
---

# Đồ họa Remotion minimalist

Studio nằm ở `studio/` trong thư mục xưởng (bản gốc trên máy người dùng), render trong sandbox đám mây rồi commit về máy. Mọi chi tiết môi trường: `docs/QUY-TRINH-KY-THUAT.md` ở gốc thư mục - đọc trước, làm mục "Khởi động phiên mới" nếu đám mây chưa dựng.

## Ngôn ngữ thiết kế (bất biến giữa các dự án)

Minimalist, tĩnh tại, "thở" - để nội dung và người nói là trung tâm; bảng màu cụ thể lấy từ `brand/brand.json` (chép từ mẫu trong `phong-cach/mau/` lúc thiết lập):

- Khoảng trắng rộng; mỗi khung hình một ý; không bao giờ nhồi
- Chuyển động chậm và êm: fade + trồi nhẹ 20-30px, easing bezier(0.22, 1, 0.36, 1), 24-34 frame mỗi chuyển động; KHÔNG spring nảy, KHÔNG hiệu ứng lòe loẹt, không emoji trong đồ họa
- Typography: Lora 500/600 cho tiêu đề, Be Vietnam Pro 400/500/600 cho nội dung; sentence case hoặc FULL-CAP cho kicker, tuyệt đối không Title Case
- Hai theme trong `brand/brand.json` (light và dark, mỗi theme năm màu bg/ink/inkSoft/accent/line); mỗi dự án chọn một theme, không pha; không tự thêm màu ngoài palette
- Đường nhấn mảnh 3px là chữ ký thị giác; mọi thành phần mới nên có nó
- Ngôn ngữ chữ: theo mục 4 của `phong-cach/PHONG-CACH.md` (mặc định thuần Việt, sentence case, gạch ngang thường, thuật ngữ tiếng Anh trong ngoặc vuông); từ ngữ "phải viết đúng" trong đó là bất khả xâm phạm

## Render đồ họa có sẵn (việc thường gặp nhất)

18 composition: Intro, Outro, SectionTitle, InfoList, InfoQuote, InfoStat, InfoSteps, LowerThird, Benefits - mỗi cái hai khung `-ngang` (1920x1080) và `-doc` (1080x1920), 30fps. Props và thời lượng: xem defaults trong `studio/src/components/*.tsx`; InfoList/InfoSteps tự tính thời lượng theo số mục nếu không truyền durationInSeconds. `Intro` từ 2026-08-31 có thêm hai prop tùy chọn để tách nội dung dài khỏi `title` (tránh title tự xuống dòng giữa từ - xem `bien-tap.md` mục "Xuống dòng trong thẻ tiêu đề toàn màn hình"): `description` (một dòng mô tả phụ, cỡ chữ `subtitleSize*0.92`) và `creditLines` (mảng dòng credit như "Tác giả:...", "Đơn vị xuất bản:...", cỡ chữ `subtitleSize*0.62`, mỗi dòng một FadeUp riêng).

Composition dùng khi cần đè chữ/nhãn lên video thật mà VẪN giữ hình người nói (không che hết khung, khác với InfoList/InfoQuote/InfoStat vốn full-screen). Không có composition "Caption" riêng: một câu caption nổi bật = `Benefits` với một mục, `showIndex:false`, `wrap:true`.
- **Benefits**: dải pill bán trong suốt, HIỆN DẦN TỪNG MỤC đúng lúc lời nói nhắc tới mục đó (không phải slide tĩnh hiện hết cùng lúc) - mỗi mục nhận prop `revealAt` (giây, tính từ mốc bắt đầu của overlay, khớp mốc `at` của assemble.py). Mục đã hiện tự thu nhỏ/mờ khi mục kế tiếp xuất hiện, mục vừa hiện được tô đậm - tạo cảm giác một chuỗi tiến trình đang được xây dần lên thay vì một slide chết. Layout hàng có tự xuống dòng (flex-wrap), canh giữa, đặt top hoặc bottom qua prop `position`; hợp cả liệt kê tĩnh (bỏ trống `revealAt` thì tự chia đều) lẫn tiến trình nhiều bước theo lời nói (2-6 mục). Cỡ chữ nhãn nên ở khoảng `unit * 4.5` (khung dọc) / `unit * 4.0` (khung ngang) - đủ đọc rõ khi lướt nhanh trên điện thoại, đừng để mặc định quá nhỏ (đã tăng hai lần sau góp ý thực tế - lần đầu từ `unit*3.0/2.7` lên `unit*3.6/3.2` vẫn còn bị chê nhỏ, lần hai lên hẳn `unit*4.5/4.0`; đã kiểm bằng đo biên nội dung qua alphaextract, nhãn dài nhất vẫn không tràn khung dọc 1080px) Prop `position` nhận `top`/`bottom`/`left`/`right` (từ 2026-08-30: `left`/`right` xếp cột dọc bám cạnh) - ưu tiên `left`/`right` khi khung hình còn khoảng trống hai bên (người nói không chiếm hết bề ngang) hoặc khi clip dài có NHIỀU pill liên tiếp, vì `position:'bottom'` dễ bị hiểu lầm là phụ đề (góp ý thực tế từ người dùng). Prop `scale` (mặc định 1, mới 2026-08-31) nhân đều gap/padding/cỡ vòng tròn số/cỡ chữ - dùng khi cần phóng to nguyên khối một pill mà không đổi bố cục (giá trị thực tế đã dùng: 1.1-1.15). Với framework nhiều bước, nên chủ động đề xuất thêm một overlay Benefits TỔNG KẾT cuối cùng (liệt kê lại đủ tên các thành phần + tên framework) đặt đúng vào lúc người nói tự nhiên tổng kết lại - đối chiếu transcript để tìm câu tổng kết, không đặt cứng theo số giây.

Benefits xuất webm alpha (`"alpha": true`), ghép vào video bằng trường `overlay` của `tools/assemble.py` - xem `phim-dung-bai/references/bien-tap.md` mục "Infographic/overlay" để biết khi nào dùng cái nào và cách tính thời lượng hiển thị theo nội dung (không phải số tròn tùy ý). `overlay` của một segment nhận cả list nhiều lớp chồng nối tiếp (nhiều Caption/Benefits/InfoList khác nhau trong CÙNG một đoạn quay liên tục), miễn khoảng hiển thị không chồng lấn thời gian.

1. Soạn job JSON: intro/outro bắt đầu từ preset `do-hoa-chung/preset-intro-outro-<ngang|doc>.json` (đủ placeholder: title/subtitle; outro: headline thông điệp kết, ctaLines, programName, contactLines, qrFile+qrCaption - bỏ qrFile thì bố cục tự dồn giữa; hướng dẫn tinh chỉnh: `do-hoa-chung/GHI-CHU.md`); đồ họa khác theo mẫu `du-an/_mau/do-hoa/job-do-hoa.json`. brandFile trỏ `brand/brand.json`; LowerThird đặt `"alpha": true` để ra webm nền trong suốt. File QR/hình riêng của dự án: khai báo qua trường `"assets"` (đường dẫn tương đối so với file job) - script tự copy vào studio; QR tạo tại đám mây bằng python qrcode từ link user đưa
2. Chạy ở đám mây: `node tools/render-do-hoa.mjs <job.json> --studio <studio-đám-mây>`
3. TRƯỚC khi render video, với đồ họa mới hoặc props lạ: render 1 still (`npx remotion still ... --frame=<giữa bài> --props=...`) và XEM HÌNH bằng Read - chữ Việt đủ dấu, không tràn khung, đúng theme
4. Commit kết quả về `du-an/<x>/do-hoa/<ngang|doc>/` trên máy (file >20MB: split 19m, commit từng phần, cat nối lại trong device_bash)

## Thêm component mới / sửa component

1. Viết theo pattern có sẵn: dùng `Canvas` (nền + fade biên), `FadeUp`, `AccentLine` từ `common.tsx`, palette qua `resolvePalette(theme, brand)`, kích thước qua `useLayout()` để một component tự chạy đúng cả hai khung
2. Đăng ký trong `Root.tsx` cho CẢ HAI khung ngang/dọc, có defaults và calculateMetadata
3. Kiểm tra: `npx tsc --noEmit` sạch → `npx remotion compositions src/index.ts` liệt kê đủ → render still cả ngang lẫn dọc với nội dung Việt CÓ DẤU dài thực tế (không "abc test") và xem hình - chú ý tràn khung khi danh sách/bước nhiều mục
4. Commit file nguồn đã sửa về máy NGAY (máy là bản gốc; đám mây mất khi hết phiên)
5. Component mới nên nêu trong docs/QUY-TRINH-KY-THUAT.md (bản đồ tài nguyên) nếu nó thêm khả năng mới cho hệ thống

## Cập nhật brand và logo

- Logo dùng mảng `"logos"` trong `brand/brand.json` (1-3 logo, file nằm trong `brand/logo/` do người dùng thả vào lúc thiết lập); mỗi phần tử là tên file hoặc `{"file": "...", "scale": 0.85}` khi cần chỉnh cỡ riêng; hàng logo tự chuẩn hóa chiều cao và có vạch ngăn. `render-do-hoa.mjs` TỰ đồng bộ `brand/logo/` vào studio - không cần copy tay. Theme tối tự chuyển logo về đơn sắc kem (prop `logoMono: false` để giữ màu gốc). Ghi đè logos theo dự án: đặt trong props của job thay vì sửa brand gốc. Logo mới: thả file vào `brand/logo/`, render still xem cân đối rồi mới render loạt
- Đổi màu/tagline/social: sửa `brand/brand.json` - ảnh hưởng mọi dự án từ đó về sau, xác nhận với user trước khi đổi giá trị mặc định; nhu cầu một dự án riêng thì ghi đè palettes trong job JSON của dự án đó thay vì sửa brand gốc
- **Chức danh/tagline hiển thị trên clip là chỗ hay bị góp ý sửa LẶP LẠI qua nhiều dự án** (ví dụ một chức danh dài từng bị rút gọn sai ở `brand.json` `tagline` và giá trị mặc định `role` của `LowerThird.tsx`; chức danh nguyên văn nằm ở mục 1 của `phong-cach/PHONG-CACH.md`). Khi user góp ý sửa một câu chữ/chi tiết LẦN THỨ HAI trở lên, đó là tín hiệu phải sửa NGUỒN MẶC ĐỊNH (brand.json, defaultProps trong component) ngay, không chỉ sửa trong job JSON của dự án đang làm - nếu không, dự án kế tiếp lại rơi về giá trị cũ và lặp lỗi lần ba.
