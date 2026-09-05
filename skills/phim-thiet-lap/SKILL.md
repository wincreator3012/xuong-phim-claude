---
name: phim-thiet-lap
description: Thiết lập xưởng phim lần đầu cho một người dùng mới của repo xuong-phim-claude - cài môi trường và model bằng tools/cai-dat.py, phỏng vấn ngắn để điền phong-cach/PHONG-CACH.md và brand/brand.json theo một mẫu phong cách, tải nhạc và hiệu ứng theo mẫu, render thử intro/outro để duyệt. Kích hoạt khi user nói "thiết lập xưởng phim", "bắt đầu thiết lập", "cài đặt xưởng", "thiết lập phong cách", "cá nhân hoá xưởng phim", "đổi phong cách/màu/logo mặc định", hoặc khi thư mục xưởng chưa có tools/.cai-dat.json hay PHONG-CACH.md còn dấu [...] chưa điền.
---

# Thiết lập xưởng phim lần đầu

Mục tiêu: sau 30-45 phút, người dùng (thường là giảng viên, chuyên gia mới dùng AI) có một xưởng chạy được trên máy của họ, mang tên, chức danh, màu sắc và nhạc đúng ý họ, và biết câu đầu tiên cần nói để dựng clip. Nguyên tắc: hỏi ít, mỗi lượt tối đa 4 câu, luôn có phương án mặc định hợp lý, giải thích bằng lời thường, không bắt người dùng đọc tài liệu kỹ thuật. Người dùng vắng mặt thì chọn mặc định và ghi rõ giả định vào PHONG-CACH.md.

## Bước 0 - định vị

Đọc `CLAUDE.md` ở gốc xưởng (nếu chưa đọc trong phiên). Xác định: thư mục xưởng đã kết nối chưa (device tools) và lệnh chạy ở đâu (`device_bash` tại máy người dùng, `Bash` ở sandbox đám mây, hoặc chỉ có một nơi). Chưa kết nối thư mục thì dừng, hướng dẫn người dùng bấm "Add folder" trong app Claude và chọn thư mục xưởng.

Kiểm `tools/.cai-dat.json`: có và `dung_thu: true` thì bỏ qua Bước 1.

## Bước 1 - cài môi trường (máy người dùng)

Chạy từ gốc xưởng: `python3 tools/cai-dat.py`. Lệnh tự bỏ qua bước đã xong. Mã thoát 2 = model đang tải, chưa xong: chạy lại y nguyên lệnh tới khi thấy "✓ CÀI XONG" (mỗi lần tối đa ~150 giây, model ~560 MB nên thường 4-8 lần; báo tiến độ cho người dùng bằng lời thường, ví dụ "đang tải bộ nhận dạng giọng nói, được 40%"). Mạng không tải được: hướng dẫn tải tay theo `tools/models/TAI-MODEL.md`, hoặc tạm dùng `--model khong` và quay lại sau.

Nếu bước dựng thử báo KHÔNG ĐẠT: đọc chẩn đoán, sửa (thường là thiếu ffmpeg hoặc Pillow), chạy lại. Chưa đạt thì chưa sang bước 2 - xưởng chưa an toàn.

Song song, ở sandbox đám mây (nếu phiên có): dựng studio Remotion theo mục "Khởi động phiên" trong `docs/QUY-TRINH-KY-THUAT.md` (stage `studio/` lên, `npm install`, `npx remotion compositions src/index.ts` ra 18 composition). Cần cho Bước 4.

## Bước 2 - phỏng vấn phong cách (3 lượt, AskUserQuestion)

Đọc `phong-cach/PHONG-CACH.md` (mẫu có dấu `[...]`) và `phong-cach/mau/README.md` trước.

Lượt 1, về người dùng: tên hiển thị; chức danh đúng nguyên văn (nhấn mạnh sẽ hiện y như vậy trên mọi clip, hỏi lại chính tả nếu có chữ dễ nhầm); đơn vị hoặc chương trình; khán giả chính. Lĩnh vực chuyên môn hỏi luôn trong câu chức danh nếu chưa rõ.

Lượt 2, về sản phẩm và cảm giác: loại clip hay làm (đa chọn); khung mặc định và nơi đăng; mẫu phong cách - trình bốn mẫu bằng một câu cảm giác mỗi mẫu ("Tĩnh lặng: giấy ngà, mực than, một điểm lục trầm - điềm tĩnh và sâu"…) kèm lựa chọn "mô tả riêng"; theme sáng hay tối.

Lượt 3, về chữ, nhạc, kết clip: thuật ngữ tiếng Anh xử lý thế nào; từ ngữ phải viết đúng (tên chương trình, thuật ngữ nghề); nhạc chạy chỉ hai đầu hay suốt clip; hiệu ứng âm thanh mức nào; thông điệp kết, lời mời hành động, liên hệ, có QR không; có logo không (nếu có, nhờ thả vào `brand/logo/` ngay lúc này).

Mỗi lượt xong, ghi ngay vào `PHONG-CACH.md` (thay đúng dấu `[...]` tương ứng, giữ cấu trúc file) rồi mới hỏi lượt kế - không gom tới cuối. Người dùng chọn "mô tả riêng": pha một bảng màu mới theo quy tắc trong `phong-cach/mau/README.md` (ink tương phản đủ với bg, một accent, line nhạt hơn nền), ghi thành `phong-cach/mau/<tên-riêng>.json`.

Điền `brand/brand.json`: `name`, `credentials`, `tagline` (chức danh nguyên văn), `contactLines`, `palettes` chép từ mẫu đã chọn, `logos` theo file người dùng thả (tối đa 3). Xoá trường `_huong_dan` không cần thiết. Nếu chưa có logo: để `logos: []`, ghi chú trong PHONG-CACH.md rằng intro dùng `showBrandName: true`.

Cập nhật hai preset `do-hoa-chung/preset-intro-outro-<ngang|doc>.json`: thay PLACEHOLDER của outro (headline, ctaLines, programName, contactLines) bằng giá trị mặc định người dùng vừa cho; title/subtitle của intro giữ PLACEHOLDER vì đổi theo từng clip. Sinh lại bố cục slide cho khớp màu: `python3 tools/bo-cuc-slide.py`.

## Bước 3 - chất liệu theo mẫu

`python3 tools/tai-chat-lieu.py --mau <mẫu>`: tải thẳng những gì được (Kevin MacLeod), in danh sách còn lại cần trình duyệt. Với danh sách đó:

- Có Claude in Chrome hoặc trình duyệt tích hợp: mở từng trang, bấm "Free download" (Pixabay) hoặc nút tải MP3 (incompetech), chờ 6-8 giây trước khi sang trang kế (điều hướng sớm huỷ lượt tải). Pixabay có thể yêu cầu đăng nhập cho một số track - hỏi người dùng đăng nhập giúp một lần
- Không có trình duyệt: gửi người dùng danh sách link (SendUserMessage), nhờ bấm từng link, file về Downloads

Rồi `python3 tools/nhap-am-thanh.py --tu ~/Downloads` (trên máy người dùng, Downloads có thể cần xin quyền thư mục một lần) và kiểm `nhac-nen/THU-VIEN.md`. Hai track đúng mẫu là đủ để bắt đầu; không kéo dài bước này quá 10 phút, phần còn lại tải dần khi dựng clip thật. Nhạc riêng của người dùng: thả vào `nhac-nen/rieng/`, chạy `nhap-am-thanh.py --tu <thư mục> --nhom rieng`.

Hình minh hoạ không tải lúc này (theo từng dự án, skill phim-tu-lieu).

## Bước 4 - render thử intro/outro để duyệt bằng mắt

Ở nơi có studio: copy preset ngang vào `du-an/_thiet-lap/do-hoa/`, điền title "Tên bài giảng mẫu", subtitle tên chuỗi chương trình thật, render `node tools/render-do-hoa.mjs <job> --studio <studio>`; xuất một khung giữa intro và một khung giữa outro (ffmpeg -ss), đưa người dùng xem (SendUserFile). Hỏi đúng ba điều: màu có đúng cảm giác không, chữ và chức danh đúng chưa, logo cân đối chưa. Sửa brand.json/preset theo góp ý, render lại tới khi gật. Mỗi góp ý về chữ/chức danh ghi vào "Sổ tay góp ý" của PHONG-CACH.md.

Không có studio ở đâu cả (không sandbox, máy không có node): bỏ qua, ghi chú trong PHONG-CACH.md "chưa duyệt đồ họa thử", sẽ duyệt ở dự án đầu tiên.

## Bước 5 - bàn giao

Tóm tắt cho người dùng bằng 5-7 câu: đã cài gì, mẫu phong cách nào, nhạc nào đã có, cái gì còn treo (logo, track chưa tải). Kết bằng câu đầu tiên họ có thể nói để làm clip thật, ví dụ: "Tạo thư mục du-an/bai-1, tôi sẽ thả clip quay vào nguon, rồi dựng bài giảng ngang cho tôi". Nhắc: mọi thứ vừa chọn đều đổi được sau bằng một câu nói.

## Khi người dùng muốn đổi phong cách về sau

Đọc PHONG-CACH.md hiện tại, chỉ hỏi về phần muốn đổi, sửa PHONG-CACH.md + brand.json + preset, sinh lại bố cục slide, render thử một intro để xác nhận. Không hỏi lại từ đầu.
