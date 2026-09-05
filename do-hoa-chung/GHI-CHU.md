# Bộ intro/outro dùng chung - cách lấy về dự án và tinh chỉnh

Đây là preset intro/outro linh hoạt cho mọi dự án. Bốn file demo trong thư mục này chỉ để XEM cảm nhận chuyển động; mỗi dự án nên render bản riêng với chữ và lựa chọn của mình từ hai file preset JSON kèm theo (copy vào `du-an/<x>/do-hoa/`, sửa các giá trị PLACEHOLDER rồi nhờ Claude render - hoặc chỉ cần nói yêu cầu, Claude tự soạn).

## Chỗ nào tinh chỉnh được (props của Intro/Outro)

**Intro** (mặc định 6 giây):
- `title`: tên clip/bài giảng (placeholder chính)
- `subtitle`: tên chuỗi chương trình, hiện thành kicker phía trên
- `brand.logos`: hàng 1-3 logo (file nằm trong `brand/logo/` ở gốc, tự đồng bộ khi render); mỗi logo có thể là tên file hoặc `{"file": "...", "scale": 0.85}` khi cần chỉnh cỡ riêng
- `theme`: "light" / "dark"; theme tối tự chuyển logo về đơn sắc kem (`logoMono: false` nếu muốn giữ màu gốc)
- `showBrandName: true` khi logo không chứa tên người

**Outro** (mặc định 8 giây, có QR nên để 9-10 giây cho kịp quét):
- `headline`: thông điệp kết (placeholder chính)
- `ctaLines`: 1-2 dòng lời mời hành động
- `programName`: tên chương trình đang mở đăng ký (chữ nhấn màu accent)
- `contactLines`: web, email, điện thoại - mỗi mục một dòng
- `qrFile` + `qrCaption`: mã QR đăng ký (bỏ trống nếu không cần - bố cục tự dồn về giữa). QR theo dự án: đưa file PNG qua trường `"assets"` của job, hoặc đưa Claude đường link form để tạo QR tại chỗ
- `showTagline: false` để ẩn tagline dưới logo

## Quy tắc vị trí intro theo loại clip

- **Bài giảng dài**: intro đứng đầu như thông lệ (trường "intro" trong timeline)
- **Clip ngắn Reels/Shorts**: HOOK TRƯỚC, INTRO SAU - người lướt không chờ intro. Thứ tự: hook 3-10 giây (lời đắt nhất hoặc thẻ mở) → intro ngắn 2.5-4 giây (hoặc bỏ hẳn, dồn nhận diện về outro) → thân → outro. Kỹ thuật: không dùng trường "intro" của timeline, đưa file intro vào danh sách segments đứng sau segment hook

## Vì sao nên render riêng cho từng dự án thay vì tái dùng file demo

Render chỉ mất ~1 phút mỗi file và cho đúng tên bài, đúng chuỗi chương trình, đúng QR - trong khi file demo chứa chữ giả. Preset tồn tại để KHÔNG dự án nào phải thiết kế lại từ đầu, không phải để dùng nguyên xi.

## Gợi ý chữ ký âm thanh (khi dựng timeline)

- Intro: `hieu-ung/chuong-thien/chuong-xoay-go` vào đúng lúc đường nhấn xuất hiện (giây thứ ~1.6), hoặc `acoustic-stinger-30s` chạy trọn intro+outro
- Outro: nhạc bookends theo THU-VIEN-AM-THANH.md; chuông ngân dài cho video thiền
