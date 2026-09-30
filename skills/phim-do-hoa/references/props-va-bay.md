# Props chi tiết và các bẫy đã gặp (phim-do-hoa)

Tra khi soạn job JSON cho một composition cụ thể. Giá trị mặc định thật luôn kiểm được trong `studio/src/components/*.tsx`; InfoList, InfoSteps tự tính thời lượng theo số mục nếu không truyền `durationInSeconds`. Quy tắc chọn vị trí và không che mặt: `skills/_chung/overlay-va-the.md`.

## Intro

- `title`, `subtitle` (kicker phía trên title), `description` (một dòng mô tả phụ, cỡ `subtitleSize*0.92`), `creditLines` (mảng dòng credit như "Tác giả: ...", "Đơn vị xuất bản: ...", cỡ `subtitleSize*0.62`, mỗi dòng một FadeUp). Tách thông tin dài khỏi `title` để title không tự xuống dòng giữa cụm từ; quy tắc xuống dòng: `skills/phim-dung-bai/references/bien-tap.md` mục "Xuống dòng trong thẻ tiêu đề toàn màn hình". `subtitle` giữ xuống dòng theo `\n` (whiteSpace pre-line).
- **`subtitle` chỉ dùng khi clip thuộc một chuỗi chương trình ĐỊNH KỲ do chính người dùng vận hành, đặt tên.** Clip quay lại buổi dạy của người khác, hoặc không có chuỗi chương trình thật: PHẢI truyền tường minh `"subtitle": ""`; dùng `title` + `description` + `creditLines` cho đủ thông tin (tên bài, địa điểm, giảng viên, chương trình liên quan). Không điền placeholder hay suy diễn tên chương trình khi người dùng chưa xác nhận.
- **Bẫy đã xảy ra (một clip thực hành, 2026-09):** bỏ trống key `subtitle` KHÔNG ẩn được kicker, vì `defaultProps.subtitle = 'Tên chuỗi chương trình'`; placeholder lộ nguyên văn trên clip cuối, vượt qua mọi cổng máy. Quy tắc chung cho MỌI prop có default kiểu placeholder: kiểm `defaultProps` trước khi bỏ trống, đặt `""` tường minh; sau khi render trích một khung giữa đoạn Intro và xem bằng mắt.

## SectionTitle

`title` nhận chuỗi hoặc mảng dòng (mỗi phần tử một dòng cố định, `nowrap`) để tự quyết điểm xuống dòng, ví dụ `["HỌC CÁCH", "LẮNG NGHE"]`. Quy ước `kicker` + `title` + `showLogos`: `_chung/overlay-va-the.md` mục "Ba lớp đồ họa".

## Outro

- `headline` (thông điệp kết), `ctaLines`, `programName`, `contactLines`, `qrFile` + `qrCaption` (bỏ `qrFile` thì bố cục tự dồn giữa), `showTagline` (mặc định true). Preset và hướng dẫn tinh chỉnh: `do-hoa-chung/preset-intro-outro-<ngang|doc>.json`, `do-hoa-chung/GHI-CHU.md`.
- **`ctaLines`: mỗi phần tử là một dòng**; dòng dài tự xuống dòng và dễ để lại chữ mồ côi. Chia câu thành các dòng cân nhau, khoảng 30-40 ký tự mỗi dòng ở khung ngang, rồi xem khung outro trước khi dùng.

## Benefits (chữ, pill đè lên video thật mà vẫn giữ hình người nói)

- **Một mục** (`items` một phần tử, `showIndex:false`, `wrap:true`): một dòng chữ nổi bật trên thẻ bán trong suốt - tên chương trình, key message, câu hook, câu hỏi neo. Studio không có composition `Caption`; đây là cách làm thay.
- **Nhiều mục**: dải pill hiện dần từng mục đúng lúc lời nhắc tới; mỗi mục có `revealAt` (giây, tính từ mốc bắt đầu của overlay, cùng mốc 0 với `overlay.at`). Mục đã hiện thu nhỏ, mờ khi mục kế xuất hiện; mục vừa hiện tô đậm. Bỏ trống `revealAt` thì tự chia đều. Hợp 2-6 mục. Framework nhiều bước: đề xuất thêm một overlay tổng kết đặt đúng lúc người nói tự tổng kết (tra transcript, không đặt cứng theo số giây).
- `position`: `top` / `bottom` (mặc định) / `left` / `right` (cột dọc bám cạnh). `edgeInset` (0-1): khoảng neo tính theo phân số chiều cao khung (`top`/`bottom`) hoặc chiều rộng (`left`/`right`). `scale` (mặc định 1): nhân đều gap, padding, vòng số, cỡ chữ; đã dùng 1,1-1,15.
- Cỡ chữ nhãn khoảng `unit*4.5` (dọc) / `unit*4.0` (ngang); đã nâng hai lần sau góp ý đọc trên điện thoại, nhãn dài nhất vẫn không tràn khung dọc 1080 px. Component pill mới xuất phát từ cỡ này.
- Màu pill đang hiện lấy từ `palette.accent` của brand đang dùng.
- Clip thực hành không lời (khí công, yoga): mỗi động tác một webm riêng (một mục), gắn vào TỪNG segment tương ứng (chia video theo mốc chuyển động tác) để còn có `chapter` cho từng động tác; sửa tên một động tác chỉ cần render lại một webm.
- Nhiều pill rời trong cùng một đoạn: mỗi pill một webm ngắn chỉ hiện đúng một mục (các mục trước đặt `label:""`, `revealAt:9999` để ẩn), đặt ở các `overlay.at` khác nhau.

## LowerThird

`name`, `role`, `alpha: true` (webm nền trong suốt). Tên và chức danh theo `_chung/van-hanh.md` mục "Chữ và chức danh"; không lấy từ `Intro.props.subtitle`.

## YNiem và YCanh

`YNiem`: `slug` (tra trong `studio/src/y-niem/index.ts`), `label`, `sublabel`, `theme`, `brand`, `drawSeconds`, `labelAt`, `floating`, `position`, `durationInSeconds`. `YCanh`: `variant` (tám kỹ thuật chuyển động), `label`, `sublabel`, `floating`, `position`. Cả hai nổi thì `alpha: true`; `position` mặc định `'center'`. Khi dựng clip, hỏi người dùng có muốn đặt khác không (neo một cạnh khi cần né chi tiết quan trọng hoặc khi bố cục cả video cần). Đặc tả: `skills/phim-infomotion/references/hinh-tuong-hoa.md` mục 4 và 6; ẩn dụ đã duyệt: `do-hoa-chung/an-du-y-niem.json`.

## Brand riêng và logo

- Ghi đè logo theo dự án: đặt `logos` trong props của job, không sửa brand gốc. Mỗi phần tử là tên file trong `brand/logo/` hoặc `{"file": "...", "scale": 0.85}`. Theme tối tự chuyển logo về đơn sắc kem (`logoMono: false` để giữ màu gốc).
- Chương trình có bộ nhận diện riêng: đặt `props.brand` (palettes, logos) trong từng job.
- Clip KHÔNG mang thương hiệu cá nhân của người dùng: ghi đè `brand` trong props của job Intro, Outro bằng object rỗng (`name/tagline/logoFile: ""/null`, `logos: []`, `contactLines: []`); object này THAY THẾ HOÀN TOÀN brand cấp job, không cần copy `palettes` (`resolvePalette` tự dùng palette mặc định của theme). Đặt thêm `showTagline: false` ở Outro.
- Logo trên theme sáng: bản có nền màu riêng (dạng huy hiệu) đọc rõ hơn bản trong suốt chữ trắng; xem still trước khi render loạt.

## Bẫy kỹ thuật khi render và kiểm

- **Đuôi tiếng AAC của mp4 Intro, Outro dài hơn hình khoảng 0,06 giây** dù im lặng: không xử lý tay, `assemble.py` tự cắt ở bước chèn và in dòng thông báo.
- **Đường render alpha**: mặc định chuỗi PNG rồi ffmpeg libvpx (vp8 + yuva420p), nhanh khoảng sáu lần encoder vp8 của Remotion (bảng tên 4,5 giây: khoảng 15 giây thay vì 90 giây trên sandbox 2 lõi); `--alpha-remotion` quay về encoder cũ. Job đã render đúng props được bỏ qua (propsHash trong `do-hoa-manifest.json`); nhiều job thì `--gioi-han 150` và lặp đúng lệnh khi thoát mã 2; `--lam-lai` để ép render lại.
- **Không chạy hai lệnh render song song** trên sandbox 2 lõi: hai tiến trình vp8 kẹt nhau, file đứng ở 0 byte hàng chục phút.
- **Tự ghép thử một webm alpha bằng ffmpeg**: đặt `-c:v libvpx` (vp9: `-c:v libvpx-vp9`) NGAY TRƯỚC `-i` của file đó, nếu không ffmpeg âm thầm giải mã như hình không có alpha. `assemble.py` đã làm đúng.
- **Kiểm nhanh một loạt pill**: chồng từng webm lên nền xám bằng `-c:v libvpx -i`, trích một khung ở trạng thái tích luỹ đủ; rồi kiểm lại trên khung hình thật của video đã dựng (không che mặt).
- **Commit lại cùng đường dẫn**: chép sang tên staged mới (ví dụ `ten.v2.webm`) trước khi commit và so md5 hai phía.
