# Skill trong tài khoản AI: giải thích cho người dùng và cách lưu

Đọc ở Bước 5b của skill phim-thiet-lap, và mỗi khi người dùng hỏi "skill là gì", "lưu skill thế nào", "sao AI không nhận ra việc", "skill nào cần lưu lại". Người dùng thường chưa từng nghe chữ "skill": giải thích bằng lời thường, ví dụ gần đời, mỗi lượt một ý, kết bằng một câu hỏi.

## Bốn ý cần người dùng hiểu

**1. Skill là gì.** Một skill là bản quy trình chuẩn viết cho AI, giống cuốn sổ tay nghề của một người thợ lành nghề: khi nào dùng, làm từng bước ra sao, kiểm gì trước khi giao. Xưởng có mười lăm skill, mỗi loại việc một skill: dựng bài giảng, cắt clip ngắn, phim nhiều góc máy, gỡ băng, gói đăng tải... Nhờ skill, lần nào AI cũng làm theo cùng một cách đã kiểm chứng, chứ không mỗi lần nghĩ ra một kiểu.

**2. Skill sống ở hai nơi.** Bản gốc nằm trong thư mục xưởng (`skills/`): AI đọc và sửa bản này khi bạn góp ý, nó lớn lên theo bạn. Bản trong tài khoản AI là bản chép: nhờ nó, ở BẤT KỲ phiên làm việc nào, AI tự nhận ra việc bạn nhờ (bạn chỉ cần nói "cắt cho tôi vài clip dọc từ bài này") và mở đúng quy trình, không cần bạn nhắc tên skill hay nhắc đọc tài liệu.

**3. Tên mang dấu của bạn.** Trong tài khoản, mỗi skill mang tiền tố riêng của bạn (ví dụ `tma-phim-dung-bai`, `tma-phim-clip-ngan`): nhìn danh sách là biết skill nào của xưởng mình, và không trùng với skill người khác chia sẻ cho bạn.

**4. Skill cần xưởng.** Skill chỉ chứa CÁCH LÀM. Công cụ, phong cách, dự án nằm trong thư mục xưởng, nên mỗi phiên làm phim hãy thêm thư mục mẹ (chứa xưởng, `Du an`, `Thanh pham`) vào phiên làm việc. Skill không chứa video, phong cách hay thông tin riêng của bạn.

## Cách lưu (app Claude, giao diện tháng 10/2026; tên mục có thể đổi theo phiên bản app)

1. Bật một lần: Settings > Capabilities, bật "Code execution and file creation". Gói Team hoặc Enterprise: chủ tổ chức bật ở Organization settings.
2. Với mỗi tệp `.skill` AI gửi trong cuộc trò chuyện: bấm nút lưu skill trên thẻ tệp, nếu app có nút này.
3. Không có nút lưu: tải tệp về, vào Customize > Skills, bấm "+", chọn "Create skill", rồi "Upload a skill", chọn tệp. Hộp chọn tệp không nhận đuôi `.skill` thì đổi đuôi thành `.zip` (nội dung giống hệt).
4. Skill cùng tên đã có: chọn thay bản cũ. App tạo thành hai bản thì xoá bản cũ, để AI không bị hai quy trình lệch nhau.
5. Bật công tắc của skill trong danh sách. Lưu xong cả lượt, báo AI "đã lưu skill" để nó ghi sổ.

Cùng tài khoản đăng nhập Claude Code thì các skill đã bật cũng có mặt ở đó. Hướng dẫn chính thức: trang trợ giúp "Use skills in Claude" ở support.claude.com.

Trợ lý AI khác (Codex, ChatGPT, Antigravity...): lưu theo cách nền tảng đó hỗ trợ (thư mục skill, tệp hướng dẫn dự án như AGENTS.md, hướng dẫn tuỳ chỉnh). Nền tảng không có khái niệm skill thì bỏ qua: xưởng vẫn chạy vì `CLAUDE.md` và `AGENTS.md` trỏ thẳng tới `skills/` trong xưởng.

## Cách dùng sau khi lưu

- Nói việc bằng lời thường; AI tự chọn skill. Muốn chắc chắn thì gọi tên: "dùng skill tma-phim-clip-ngan cho dự án này".
- Góp ý xong mà muốn xưởng nhớ mãi, nói "từ nay luôn...". AI sửa bản gốc trong `skills/`, rồi đóng gói lại đúng những skill vừa đổi và gửi bạn lưu lại.
- Hỏi bất cứ lúc nào: "skill nào cần lưu lại?". AI chạy `python3 tools/dong-goi-skill.py` và trả lời.
- Tắt tạm một skill: gạt công tắc trong Customize > Skills. Xoá hẳn thì xưởng vẫn còn bản gốc, đóng gói lại lúc nào cũng được.

## Việc của AI (không đọc cho người dùng)

1. `python3 tools/dong-goi-skill.py --lam --tat-ca` (lần đầu) hoặc `--lam` (chỉ skill đã đổi so với lần lưu cuối). Tệp ra ở `Du an/_tam/goi-skill/<ngày giờ>/`, kèm `DOC-TRUOC.md` tóm tắt cách lưu.
2. Gửi tệp cho người dùng theo cách nền tảng cho phép (Cowork: gửi tệp vào cuộc trò chuyện, mỗi tệp một thẻ). Gửi theo nhóm, nói rõ còn bao nhiêu tệp.
3. Họ lưu xong: `python3 tools/dong-goi-skill.py --da-luu` (hoặc `--da-luu <tên> ...` nếu mới lưu một phần). Môi trường của bạn thấy được thư mục skill đã cài thì đối chiếu thẳng: `python3 tools/dong-goi-skill.py --so-voi <thư mục>`.
4. Mỗi lần sửa một SKILL.md hay tệp trong `references/`: sửa xong chạy `python3 tools/kiem-tai-lieu.py`, rồi `python3 tools/dong-goi-skill.py --lam` và nhờ người dùng lưu lại. Không để bản trong tài khoản cũ hơn bản gốc quá một phiên.
5. Đầu phiên, nếu `python3 tools/cai-dat.py --trang-thai` hay `python3 tools/dong-goi-skill.py` báo còn skill chưa lưu, nhắc người dùng một câu ở cuối câu trả lời đầu tiên, không chen vào giữa việc đang làm.
