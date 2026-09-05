# Bốn mẫu phong cách để bắt đầu

Mỗi file JSON là một "bộ khởi đầu": bảng màu hai theme, nhóm nhạc ưu tiên, mức hiệu ứng, độ dài intro. Khi thiết lập, bạn chọn một mẫu (hoặc mô tả cảm giác riêng để Claude pha một bảng màu mới), Claude chép sang `brand/brand.json` và ghi vào `PHONG-CACH.md`. Font chữ (Lora cho tiêu đề, Be Vietnam Pro cho nội dung) và ngôn ngữ chuyển động (chậm, êm, không nảy) là phần nền dùng chung, không đổi theo mẫu, để mọi thứ luôn gọn và dễ đọc tiếng Việt có dấu.

| Mẫu | Cảm giác | Hợp với |
|---|---|---|
| `tinh-lang` | điềm tĩnh, sâu, sạch | tâm lý, chánh niệm, triết học, y khoa |
| `am-ap` | gần gũi, ấm, tin cậy | kỹ năng sống, nuôi dạy con, kể chuyện |
| `hien-dai` | rõ, sáng, năng động | công nghệ, kinh doanh, đào tạo doanh nghiệp |
| `hoc-thuat` | nghiêm túc, cổ điển, chắc | bài giảng đại học, hội thảo khoa học |

Muốn một mẫu riêng: chép một file, đổi tên và mã màu. Quy tắc để màu vẫn đọc tốt: `ink` trên `bg` phải đủ tương phản (chữ tối trên nền sáng hoặc ngược lại), `accent` là màu duy nhất "có cá tính", `line` chỉ nhạt hơn nền một chút.
