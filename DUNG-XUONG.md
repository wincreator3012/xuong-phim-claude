# DỰNG XƯỞNG: hướng dẫn cho AI dựng một xưởng phim riêng từ bản thiết kế này

Tài liệu này viết cho trợ lý AI (Claude Cowork, Claude Code, Codex, ChatGPT, Antigravity...) mà một người dùng nhờ "dựng xưởng phim theo repo xuong-phim-claude". Đọc trọn một lượt trước khi ghi bất cứ tệp nào. Người dùng thường mới dùng AI: nói với họ bằng lời thường, hỏi ít, mỗi lượt tối đa bốn câu, luôn có phương án mặc định.

## Repo này là gì, và không phải là gì

Repo này là **bản thiết kế** [blueprint] của một xưởng dựng phim cùng AI đã vận hành thật qua nhiều dự án: cách làm (skill), tiêu chuẩn, công cụ, đồ họa, bài học. Việc của bạn là học bản thiết kế rồi dựng cho người dùng **một xưởng riêng** trên máy họ: mang tên họ, phong cách họ, và bộ skill có tiền tố riêng lưu trong tài khoản AI của họ.

Repo này **không phải** phần mềm để clone, fork, push hay pull:

- Không `git clone`, không fork, không tải ZIP vào thư mục của người dùng.
- Không tạo remote trỏ về repo này, không push, không pull, không mở issue hay pull request thay người dùng.
- Xưởng dựng xong không có liên kết git nào với repo này. Người dùng muốn quản lý phiên bản thì tự `git init` cho xưởng của họ, với repo riêng của họ.

Vì sao: xưởng sẽ lớn lên theo chính người dùng (phong cách, sổ tay góp ý, skill được tinh chỉnh sau mỗi dự án). Một bản clone sẽ xung đột hoặc bị ghi đè mỗi lần bản thiết kế đổi; một xưởng riêng thì tiếp nhận cái mới có chọn lọc, từng thay đổi do người dùng duyệt (mục cuối tài liệu này).

## Kết quả cần có khi xong

```
<thư mục mẹ, mặc định Documents/Xuong phim AI>/
├── <tên xưởng>/     ← xưởng riêng: công cụ, studio, skill, tài liệu, phong cách, thương hiệu (không có .git trỏ về đây)
├── Du an/           ← hồ sơ dự án, mỗi dự án một thư mục <năm-tháng tên>/
└── Thanh pham/      ← sản phẩm để đăng
```

Cùng với đó:

1. Môi trường đã cài và dựng thử ĐẠT; phong cách, thương hiệu, nhạc của người dùng đã điền.
2. Mười lăm skill của xưởng đã đóng gói thành tệp `.skill` mang tiền tố riêng (vd `tma-phim-dung-bai`), người dùng đã lưu vào tài khoản AI của họ, và hiểu skill là gì, gọi thế nào, khi nào cần lưu lại.
3. Người dùng được giới thiệu xưởng làm được gì và biết câu đầu tiên để làm clip.

## Bước 0: hiểu bản thiết kế (chỉ đọc)

Đọc trên GitHub, theo thứ tự: `README.md` (xưởng làm được gì), `CLAUDE.md` (cách xưởng vận hành, quy tắc cứng), `skills/phim-thiet-lap/SKILL.md` (thiết lập sau khi dựng), `skills/phim-thiet-lap/references/skill-trong-tai-khoan.md` (skill trong tài khoản), `docs/QUY-TRINH-KY-THUAT.md` (môi trường), `BAN-DO-TEP.json` (danh sách tệp). Địa chỉ đọc nguyên văn một tệp: `https://raw.githubusercontent.com/wincreator3012/xuong-phim-claude/main/<đường dẫn>`.

Kiểm môi trường của chính bạn:

- Có shell chạy trên máy người dùng không (Cowork: lệnh chạy trong thư mục đã kết nối). Nếu chưa có thư mục nào được kết nối, nhờ người dùng tạo thư mục mẹ và thêm vào (Cowork: nút "Add folder").
- Shell đó ra được GitHub không: thử lấy `https://raw.githubusercontent.com/wincreator3012/xuong-phim-claude/main/BAN-DO-TEP.json`.
- Có `python3` không (máy ảo Cowork có sẵn; Mac có sẵn từ bộ công cụ dòng lệnh).

## Bước 1: hỏi người dùng (một lượt)

1. **Thư mục mẹ** đặt xưởng: mặc định `Documents/Xuong phim AI`. Không đặt trong iCloud, Dropbox, OneDrive: video lớn làm kẹt đồng bộ.
2. **Tiền tố skill**: 2-6 chữ thường không dấu, mặc định chữ cái đầu họ tên (Trần Minh An thành `tma`). Giải thích một câu: mọi skill của xưởng khi lưu vào tài khoản sẽ mang tiền tố này (`tma-phim-dung-bai`), để họ nhận ra skill của mình và không trùng skill người khác.
3. **Tên xưởng** (tên thư mục): mặc định `xuong-phim-<tiền tố>`; không dấu, không khoảng trắng là tốt nhất.

Người dùng vắng mặt: dùng mặc định, ghi rõ giả định trong tin nhắn cuối.

## Bước 2: dựng khung và chép năng lực

1. Lấy mã commit mới nhất để mọi tệp cùng một phiên bản: `https://api.github.com/repos/wincreator3012/xuong-phim-claude/commits/main`, trường `sha`. Không gọi được thì dùng `main` và ghi rõ.
2. Đọc `BAN-DO-TEP.json` ở đúng mã đó. Với MỖI tệp có `"vai": "chep"`:
   - lấy nội dung theo mẫu địa chỉ `raw` (thay `{ref}` bằng mã commit, `{p}` bằng đường dẫn đã mã hoá URL, khoảng trắng thành `%20`), lấy theo byte. Không dùng công cụ "đọc trang web" có tóm tắt: nó không trả nguyên văn;
   - kiểm `sha`: sha1 của `blob <cỡ>\0` nối với nội dung (giống `git hash-object`). Lệch thì lấy lại; ba lần vẫn lệch thì dừng và báo người dùng;
   - ghi vào `<tên xưởng>/<đường dẫn>`, tạo thư mục cha nếu thiếu; tệp có `"chay": true` thì cấp quyền chạy.

   Cách gọn nhất: tự viết một vòng lặp ngắn bằng python (`urllib`, `hashlib`) chạy trong shell trên máy người dùng. Shell có giới hạn thời gian mỗi lệnh (Cowork: 180 giây) thì chia lượt: bỏ qua tệp đã có và đúng `sha`, chạy lại tới khi đủ.
3. Không chép tệp `"vai": "ban-mau"` (README, BAT-DAU, tài liệu này, nhật ký thay đổi, bản đồ tệp và công cụ lập bản đồ). Không tạo `.git`.
4. Kiểm: số tệp đã ghi bằng `so_tep_chep`, mọi `sha` khớp.

Vì sao chép nguyên văn phần công cụ mà không tự viết lại: công cụ, studio đồ họa và bộ thiết kế cảnh là mã đã kiểm chứng qua nhiều dự án thật, có cổng nghiệm thu đi kèm; viết lại từ đầu rất dễ sinh lỗi lệch hình với tiếng. Phần làm nên một xưởng RIÊNG nằm ở bước 3 đến 5: tên, phong cách, thương hiệu, nhạc, skill có tiền tố, sổ tay góp ý lớn dần theo từng dự án.

Shell trên máy người dùng không ra được GitHub: lấy tệp từ môi trường khác bạn có (ví dụ sandbox đám mây) rồi chuyển từng tệp vào thư mục người dùng bằng công cụ truyền tệp của nền tảng. Vẫn không được thì nói rõ với người dùng và xin phép phương án cuối: họ tải ZIP về một thư mục tạm NGOÀI thư mục mẹ, bạn chỉ đọc và chép theo bản đồ tệp, xong nhờ họ xoá ZIP và thư mục tạm.

## Bước 3: cá nhân hoá

Từ gốc xưởng mới:

```
python3 tools/cai-dat.py --dung-xuong --ten-xuong "<tên xưởng>" --tien-to <tiền tố> --ban-mau <mã commit>
```

Lệnh này bỏ các khối chỉ dành cho bản thiết kế trong `CLAUDE.md`, `AGENTS.md`; thay tên bản thiết kế bằng tên xưởng trong tài liệu, skill, công cụ; tạo `cau-hinh.json` (có `tienToSkill`), `README.md` của xưởng (kèm dòng ghi công bản thiết kế, giấy phép MIT), hai thư mục `Du an/`, `Thanh pham/` cạnh xưởng; ghi bản thiết kế đã dùng (repo, commit, ngày) vào `tools/.cai-dat.json`.

Từ đây `CLAUDE.md` trong xưởng mới là sách vận hành. Đọc lại nó trước khi làm tiếp.

## Bước 4: cài môi trường và thiết lập phong cách

Làm theo skill `skills/phim-thiet-lap/SKILL.md` của xưởng mới, từ Bước 1: cài môi trường (`python3 tools/cai-dat.py`, chạy lại tới khi "✓ CÀI XONG"), phỏng vấn phong cách, tải chất liệu, render thử intro để người dùng duyệt.

## Bước 5: skill vào tài khoản của người dùng

Theo Bước 5b của skill phim-thiet-lap:

1. `python3 tools/dong-goi-skill.py --lam --tat-ca`: mười lăm tệp `<tiền tố>-phim-*.skill` ở `Du an/_tam/goi-skill/<ngày giờ>/`.
2. Giải thích cho người dùng skill là gì, vì sao nên lưu vào tài khoản, cách lưu và cách dùng, theo `skills/phim-thiet-lap/references/skill-trong-tai-khoan.md`. Gửi từng tệp để họ lưu.
3. Họ báo đã lưu xong: `python3 tools/dong-goi-skill.py --da-luu --tat-ca`.

Bạn không phải Claude, hoặc nền tảng không có khái niệm skill: đặt skill theo cách nền tảng đó hỗ trợ (thư mục skill, tệp hướng dẫn dự án). Không có cách nào thì bỏ bước này: xưởng vẫn chạy, vì `CLAUDE.md` trỏ thẳng tới `skills/` trong xưởng.

## Bước 6: nghiệm thu việc dựng xưởng

- `python3 tools/kiem-tai-lieu.py` ĐẠT; `python3 tools/kiem-sach.py` ĐẠT; dựng thử trong `cai-dat.py` ĐẠT.
- `python3 tools/cai-dat.py --trang-thai` có dòng "bản thiết kế" với đúng mã commit; `python3 tools/dong-goi-skill.py` báo mọi skill đã lưu.
- Trong xưởng không còn `.git` trỏ về repo bản thiết kế.
- Làm buổi giới thiệu xưởng (Bước 5c của skill phim-thiet-lap), rồi báo người dùng: xưởng ở đâu, skill nào đã lưu, câu đầu tiên để làm clip.

## Về sau: tiếp nhận cái mới từ bản thiết kế

Người dùng nói "xem bản thiết kế có gì mới" (hoặc tương tự):

1. Đọc `THAY-DOI.md` trên GitHub, lấy các mục sau ngày `ban_mau.ngay` trong `tools/.cai-dat.json` của xưởng.
2. Với mỗi thay đổi, tìm các tệp liên quan; so tệp trong xưởng với bản thiết kế CŨ (ở mã `ban_mau.commit`, áp lại phép thay tên của bước 3). Giống nhau: người dùng chưa sửa, lấy bản mới được. Khác: người dùng hoặc AI của họ đã tinh chỉnh, phải hợp nhất có chọn lọc.
3. Trình người dùng danh sách: lấy gì, vì sao đáng lấy, ảnh hưởng gì tới thói quen hiện tại. Họ duyệt rồi mới ghi.
4. Không bao giờ ghi đè: `phong-cach/`, `brand/`, nhạc và hiệu ứng, hai preset intro/outro đã sửa, từ điển ẩn dụ, hình vẽ riêng trong `studio/src/y-niem/` và `studio/src/hoat-hoa/`, skill người dùng đã tinh chỉnh.
5. Ghi xong: chạy lại `python3 tools/cai-dat.py --dung-xuong --ten-xuong "<tên xưởng>" --tien-to <tiền tố> --ban-mau <mã mới>` (an toàn khi chạy lại: áp phép thay tên cho tệp mới, cập nhật `ban_mau`, không đụng `README.md` và `cau-hinh.json` đã có), rồi `python3 tools/kiem-tai-lieu.py`, `python3 tools/kiem-tra-xuong.py --co-slide` (khi có đổi công cụ), và `python3 tools/dong-goi-skill.py --lam` để người dùng lưu lại những skill đã đổi.
