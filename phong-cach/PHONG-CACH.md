# PHONG CÁCH CỦA TÔI

File này là "bản đồ phong cách" mà Claude đọc trước mỗi lần dựng clip cho bạn. Bạn không cần tự điền: trong buổi thiết lập đầu tiên, Claude sẽ hỏi bạn từng phần rồi điền vào đây (skill `phim-thiet-lap`). Sau đó bạn sửa tay bất cứ lúc nào, hoặc chỉ cần nói với Claude "từ nay đổi X thành Y" là Claude cập nhật.

Chỗ nào còn dấu `[...]` là chưa điền. Chỗ nào không áp dụng thì ghi "không".

## 1. Tôi là ai

- Tên hiển thị trên clip: `[Họ và tên hoặc tên thương hiệu]`
- Chức danh, đúng nguyên văn từng chữ (Claude không được rút gọn hay đổi chữ): `[ví dụ: Giảng viên Khoa Tâm lý học, Trường ...]`
- Học vị hoặc chứng chỉ muốn hiện kèm tên (bỏ trống nếu không): `[ví dụ: TS., M.Ed.]`
- Đơn vị hoặc chương trình hay xuất hiện cùng: `[...]`
- Lĩnh vực chuyên môn: `[...]`
- Khán giả chính của clip: `[ví dụ: sinh viên năm nhất; phụ huynh; đồng nghiệp cùng ngành]`

## 2. Tôi thường làm loại clip gì

Đánh dấu x vào loại hay làm, Claude sẽ ưu tiên hỏi ít hơn cho loại đó:

- [ ] Bài giảng dài, một người nói trước máy (10 phút tới vài giờ)
- [ ] Bài giảng có slide (tôi để slide PPTX/PDF cạnh video)
- [ ] Clip ngắn dọc cho Reels/Shorts/TikTok (30 tới 90 giây)
- [ ] Clip giới thiệu chương trình, khoá học, sách (2 tới 5 phút)
- [ ] Podcast hoặc buổi trò chuyện nhiều máy quay

Khung hình mặc định: `[ngang 16:9 | dọc 9:16 | cả hai]`
Nơi đăng chính: `[YouTube | Facebook | TikTok | LMS nội bộ | ...]`

## 3. Tông và cảm giác

Mẫu phong cách đang dùng (xem `phong-cach/mau/`): `[tinh-lang | am-ap | hien-dai | hoc-thuat | tự mô tả]`

Nếu tự mô tả, ba từ nói về cảm giác muốn người xem có: `[ví dụ: điềm tĩnh, gần gũi, đáng tin]`

Theme mặc định: `[sáng (light) | tối (dark)]`. Bảng màu cụ thể nằm trong `brand/brand.json` (Claude chép từ mẫu phong cách sang, bạn có thể đổi mã màu ở đó).

Hình ảnh nên tránh: `[ví dụ: không dùng ảnh stock có người lạ; không dùng hiệu ứng nảy]`

## 4. Chữ trên màn hình

- Kiểu viết hoa tiêu đề: `[sentence case (chỉ viết hoa chữ đầu) | FULL-CAP cho kicker ngắn]` - mặc định của xưởng là sentence case, không Title Case
- Dấu gạch: dùng gạch ngang thường (-), không dùng gạch dài (—)
- Thuật ngữ tiếng Anh: `[để trong ngoặc vuông sau từ Việt | giữ nguyên tiếng Anh | dịch hẳn]`
- Từ ngữ PHẢI viết đúng như sau (tên riêng, tên chương trình, thuật ngữ nghề): `[ví dụ: "Chánh niệm" không "Chính niệm"; tên framework viết là ...]`
- Từ ngữ KHÔNG dùng trên clip của tôi: `[...]`

## 5. Nhạc và hiệu ứng

- Nhóm nhạc nền ưa thích (xem `thu-vien/AM-THANH.md`): `[thien-ambient | piano-tinh-lang | acoustic-am | nang-luong-nhe]`
- Nhạc chạy: `[chỉ ở intro/outro (bookends) | suốt clip ở mức thấp, tự nhỏ khi tôi nói (full + duck)]`
- Hiệu ứng âm thanh (whoosh, chime): `[không | tiết chế, chỉ khi thẻ lớn xuất hiện | vừa]`
- Nhạc riêng của tôi (đã có quyền dùng): `[tên file trong nhac-nen/rieng/ hoặc "không"]`

## 6. Intro và outro mặc định

- Tên chuỗi chương trình hiện ở intro (kicker): `[...]`
- Intro dài: `[6 giây cho bài dài | 3 giây hoặc bỏ cho clip ngắn]` - mặc định của xưởng
- Thông điệp kết ở outro: `[ví dụ: Cảm ơn bạn đã cùng học]`
- Lời mời hành động: `[ví dụ: Đăng ký nhận bài giảng mới tại ...]`
- Liên hệ hiện ở outro (web, email, số điện thoại): `[...]`
- Mã QR: `[link form đăng ký hoặc "không"]`

## 7. Phụ đề

- Clip dọc: `[luôn burn phụ đề (mặc định) | không]`
- Clip ngang: `[không (mặc định) | có, file SRT rời | có, burn vào hình]`

## 8. Sổ tay góp ý (Claude ghi, bạn có thể sửa)

Mỗi lần bạn góp ý sửa một chỗ mà Claude có thể lặp lại ở clip sau, Claude ghi một dòng vào đây và sửa luôn nguồn mặc định (brand.json, preset) nếu cần. Một lỗi bị nhắc lần thứ hai là tín hiệu phải sửa tận gốc, không chỉ sửa ở dự án đang làm.

- `[ngày] - [điều đã góp ý] - [đã sửa ở đâu]`
