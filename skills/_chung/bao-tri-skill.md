# Bảo trì skill phim-*

## Sửa ở đâu

1. Sửa ở `skills/<skill>/` (SKILL.md và references) trong thư mục xưởng trước. Đây là nguồn duy nhất.
2. Nếu có cài skill vào tài khoản Claude: đề xuất cập nhật ngay sau khi sửa (bản đề xuất thay toàn bộ SKILL.md). Skill tài khoản chỉ mang SKILL.md, nên mọi tham chiếu tới references và tới `_chung/` ghi đủ đường dẫn `skills/<skill>/references/<file>.md`, `skills/_chung/<file>.md`.
3. Sau khi sửa skill: `python3 tools/kiem-tai-lieu.py` phải ĐẠT (YAML của skill, đường dẫn, tên skill, kho ẩn dụ).
4. Thêm skill mới: thêm một dòng vào bảng "Việc nào, skill nào" của `CLAUDE.md` và bảng tài nguyên của `docs/QUY-TRINH-KY-THUAT.md`.

## Viết SKILL.md

- Skill chứa CÁCH LÀM của thể loại. Môi trường và lệnh chung ở QUY-TRINH, bài học ở BAI-HOC, chữ và chức danh ở PHONG-CACH, phần chung của mọi skill ở `_chung/`: chỉ trỏ tới, không chép lại.
- Bài học mới của một dự án: sửa thẳng vào đúng bước của skill (cách làm đúng từ nay), còn câu chuyện và nguồn thì vào BAI-HOC. Không để một mục "bài học từ dự án X" dài dần trong thân skill.
- Nội dung để chép ra (mẫu lệnh, mẫu hồ sơ, bảng props, checklist dài) đặt trong `references/`; SKILL.md giữ quy trình và quy tắc cứng.
- Mục "Quy tắc cứng" chỉ gồm bất biến kỹ thuật và giá trị (những điều không được vi phạm), 6-10 dòng, không lặp lại toàn bộ thân bài.
- Lựa chọn sáng tạo viết thành nguyên lý kèm lý do (vì người xem cần gì) và giá trị mặc định kèm khi nào nên khác; không viết thành luật cứng. Bài học từ một dự án là lý do để hiểu, không phải khuôn để lặp (`skills/_chung/van-hanh.md` mục "Nguyên lý trước khuôn mẫu").

## Trường description

- Là mô tả KÍCH HOẠT: khi nào dùng skill, những câu người dùng hay nói, và khi nào KHÔNG dùng (trỏ sang skill đúng). Không ghi changelog, ngày tháng, "đã sửa".
- Tối đa 1024 ký tự, bọc trong ngoặc kép, không chứa ngoặc nhọn.
- Không cần nêu tên tool hay tên file; nêu tên thể loại và tín hiệu nhận biết.
