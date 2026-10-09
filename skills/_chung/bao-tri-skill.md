# Bảo trì skill phim-*

## Sửa ở đâu

1. Sửa ở `skills/<skill>/` (SKILL.md và references) trong thư mục xưởng trước. Đây là nguồn duy nhất.
2. Lưu skill vào tài khoản AI (nên làm, xem hướng dẫn giải thích cho người dùng ở skills/phim-thiet-lap/references/skill-trong-tai-khoan.md): sau mỗi lần sửa skill, chạy `python3 tools/dong-goi-skill.py --lam` để đóng gói lại đúng những skill đã đổi, gửi tệp .skill cho người dùng lưu, lưu xong chạy `python3 tools/dong-goi-skill.py --da-luu`. Tên trong tài khoản mang tiền tố riêng của người dùng (khoá tienToSkill trong cau-hinh.json). SKILL.md ghi đủ đường dẫn `skills/<skill>/references/<file>.md`, `skills/_chung/<file>.md` để skill trong tài khoản luôn đọc bản mới nhất trong thư mục xưởng.
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
