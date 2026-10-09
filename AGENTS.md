# AGENTS.md - điểm vào cho mọi trợ lý AI (Codex, ChatGPT, Antigravity, Gemini, Claude...)

<!-- BAN-MAU -->
## Bạn đang đọc một BẢN THIẾT KẾ, không phải phần mềm để clone

Repo `wincreator3012/xuong-phim-claude` là bản thiết kế của một xưởng dựng phim cùng AI. Người dùng nhờ bạn đọc nó để **dựng một xưởng riêng trên máy của họ**, không phải để lấy repo về dùng nguyên.

- Không `git clone`, không fork, không tải ZIP vào thư mục của người dùng, không tạo remote trỏ về đây.
- Không push, không pull, không mở issue hay pull request thay người dùng.
- Làm theo `DUNG-XUONG.md`: học bản thiết kế, chép phần năng lực đã kiểm chứng theo `BAN-DO-TEP.json` vào thư mục người dùng chọn, cá nhân hoá (tên xưởng, tiền tố skill), cài môi trường, thiết lập phong cách, đóng gói skill cho người dùng lưu vào tài khoản AI của họ, rồi giới thiệu xưởng.
<!-- /BAN-MAU -->

## Xưởng này vận hành thế nào

Sách vận hành của xưởng là `CLAUDE.md`: áp dụng cho mọi trợ lý AI, không riêng Claude. Đọc nó đầu mỗi phiên, rồi `phong-cach/PHONG-CACH.md`, `docs/QUY-TRINH-KY-THUAT.md`, và SKILL.md của việc đang làm trong `skills/` (bảng "Việc nào, skill nào" trong `CLAUDE.md`).

- Skill là quy trình chuẩn của từng loại việc; làm theo skill, không tự nghĩ lại quy trình. Nền tảng của bạn có khái niệm skill thì có thể nạp các tệp do `python3 tools/dong-goi-skill.py --lam` đóng gói (tên mang tiền tố riêng của người dùng).
- Lệnh trong tài liệu chạy từ gốc xưởng. Dự án và thành phẩm nằm NGOÀI xưởng: `../Du an/`, `../Thanh pham/`.
- Môi trường gốc của xưởng là Claude Cowork (lệnh chạy trên máy người dùng, đồ họa render trong sandbox đám mây). Môi trường khác: đọc `docs/QUY-TRINH-KY-THUAT.md` mục "Môi trường" rồi tự điều chỉnh nơi chạy lệnh; giữ nguyên các cổng nghiệm thu và quy tắc cứng.
