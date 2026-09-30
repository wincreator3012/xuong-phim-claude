# Checklist bộ lệnh và phim (phim-hoat-hoa)

Bộ nhớ lỗi của skill, lớn dần qua từng phim: thêm dòng khi gặp lỗi mới (theo `skills/_chung/bao-tri-skill.md`).

## Phần 8. Checklist

**Bộ lệnh** (trước khi giao ở chế độ SOẠN LỆNH):
- Đủ tám mục; hằng số và biến số tách rõ; mọi biến số đã điền (không còn ô dạng `{TÊN BIẾN}` hay `{mô tả}`; các cấu trúc dữ liệu như `{scene, duration, k...}` là đặc tả, giữ nguyên).
- Mọi yêu cầu đặc tả bằng số liệu; mỗi ràng buộc khó có ngoại lệ tường minh.
- Cung tự sự là cung chuyển hoá (hoặc bám đúng cấu trúc bài nói khi có voice), không phải cung thành công; có cảnh gương khi hợp; mô-típ qua ít nhất bốn trạng thái.
- Có khoảng lặng, có nhịp thở nền, có trạng thái thân ở từng cảnh, tối đa một chuông chánh niệm.
- Caption đúng quy ước ngôn ngữ; câu kết là câu hỏi mở thực sự; credit đúng chức danh (theo `phong-cach/PHONG-CACH.md` mục 1).
- Ghi nhận nguồn phương pháp khi bộ lệnh được chia sẻ công khai.

**Phim** (sau mỗi chặng và trước khi báo xong; lớn dần qua từng dự án):
- Thứ tự vẽ che khuất: vật tiền cảnh vẽ sau cỏ, lúa, đồi.
- Vật thể không tràn khung cửa sổ, khung tranh (clip).
- Tỉ lệ người ngồi, bàn ghế, cửa đúng.
- Caption không dài hơn cảnh (stagger tự co), không che mặt, không che bàn tay đang làm cử chỉ.
- Hai trạng thái thân của nhân vật khác nhau đọc được trong 0,3 giây.
- Khoảng lặng thật sự lặng (nhạc tắt, boil đóng băng).
- Không còn placeholder, không chữ lạ trong hình, chữ Việt đủ dấu.
- Không lỗi JS; render(t) lặp lại giống hệt; khung nặng nhất dưới ~70 ms.
- Hình = tiếng (ffprobe), LUFS đúng chuẩn, dung lượng đúng giới hạn nơi đăng.

**Clip có voice** (thêm vào danh sách trên):
- Mỗi nhịp có cặp "hình - câu đang nói" khớp ý; không hình nào thêm thông tin người dùng không nói.
- Thành phần framework hiện đúng lúc được gọi tên, đúng thứ tự, đúng tên gọi; khung tổng kết hiện đủ các phần.
- Không chuyển cảnh giữa câu; không SFX đè từ khoá; giọng luôn rõ trên nhạc.
- Không quãng nào đứng hình chết quá 25 giây; không nhịp nào dày hơn một ý hình mới mỗi 8-12 giây (mặc định an toàn; dự án người dùng muốn dày hơn thì theo chỉ đạo ghi trong kịch bản).
- Thế giới nhất quán qua các chương: cùng bảng màu, cùng nhân vật, cùng chất giấy và nét.
