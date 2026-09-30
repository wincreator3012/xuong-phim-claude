# Mẫu gói đăng tải: schema, khuôn chữ, giới hạn nền tảng

Tệp để chép ra khi soạn gói đăng tải (skill phim-dang-tai). Khuôn chữ là điểm xuất phát; clip nào cần khác thì viết khác, miễn qua được `tools/dang-tai.py kiem`.

## 1. `dang-tai.json`

```json
{
 "ten": "<tên hiển thị của clip>",
 "video": "du-an/<tên>/xuat-hoan-chinh/<video>.mp4",
 "tu_khoa": ["<cụm từ khoá chính>", "<cụm thứ hai nếu có>"],
 "chuong_file": "du-an/<tên>/xuat-hoan-chinh/<video>.chuong.txt",
 "chuc_danh": ["<chức danh nguyên văn người 1, đúng như trong mô tả>"],
 "chuc_danh_fb": [],
 "nhac_ccby": null,
 "ghi_chu_kiem": ["<điều người dùng cần xem lại: câu thuật lời, tên người thứ ba đã tránh, số liệu chưa soát...>"],
 "youtube": {
  "tieu_de": ["<phương án 1>", "<phương án 2>", "<phương án 3>"],
  "mo_ta": "<toàn văn mô tả, xuống dòng bằng \n>",
  "the": ["<thẻ 1>", "<thẻ 2>"]
 },
 "facebook": {
  "status": "<toàn văn status>",
  "binh_luan_dau": "<link YouTube, link chương trình>",
  "goi_y": ["<gợi ý cách đăng riêng cho clip này>"]
 },
 "thumbnail": [
  {"file": "thumb-1.jpg", "y_do": "<thông điệp và lý do chọn>"},
  {"file": "thumb-doc.jpg", "khung": "doc", "y_do": "<bìa Reels, Shorts>"}
 ]
}
```

- `tu_khoa`: cổng máy đòi ít nhất một cụm nằm trong câu đầu của mô tả; nhắc nếu không nằm trong 70 ký tự đầu của tiêu đề.
- `chuong_file`: có thì cổng máy đòi các mốc trong mô tả khớp từng dòng với tệp này (mốc phải lấy từ tool). Clip không có chương thì bỏ trường này.
- `chuc_danh`: mỗi chuỗi phải có nguyên văn trong mô tả (lấy từ `phong-cach/PHONG-CACH.md` mục 1 hoặc bảng nhân vật của dự án). `chuc_danh_fb` tương tự cho status (thường để trống: status là giọng người dùng).
- `nhac_ccby`: dòng ghi công nhạc nguyên văn (mẫu trong `thu-vien/AM-THANH.md`) khi dùng track CC-BY; `null` khi nhạc không cần ghi công.
- Clip chỉ đăng Facebook, Reels: bỏ khối `youtube`. Clip chỉ đăng YouTube: bỏ khối `facebook`.

## 2. `thumbnail.json`

```json
{
 "theme": "light",
 "brandFile": "../brand-<dự án>.json",
 "kicker": "<TÊN CHUỖI, để trống nếu không thuộc chuỗi>",
 "logo": "<tên file trong brand/logo, tuỳ chọn>",
 "ban": [
  {"out": "thumb-1.jpg", "layout": "chia-doi", "headline": "<dòng 1>\n<dòng 2>", "accent": "<cụm tô màu>",
   "người dùng": ["k05c", "k04"]},
  {"out": "thumb-2.jpg", "layout": "toan-anh", "headline": "...", "accent": "...", "người dùng": ["k05c"]},
  {"out": "thumb-3.jpg", "layout": "chu-chinh", "headline": "...", "accent": "...", "người dùng": ["k09e"]},
  {"out": "thumb-doc.jpg", "aspect": "doc", "layout": "chia-doi", "headline": "...", "người dùng": ["k09e"]}
 ]
}
```

- `brandFile` tương đối so với `thumbnail.json`; bỏ trường này thì dùng brand mặc định của studio (giấy ngà, mực, lục trầm). File brand dự án chỉ cần `palettes.light` (hoặc `dark`) ghi đè.
- `người dùng`: mã khung trong `khung/khung.json`; "k12#1" là mặt thứ hai của khung k12 (khung nhiều mặt).
- Tuỳ chọn từng bản: `photoSide` ("left", "right"), `faceScale` (chiều cao mặt so với chiều cao ô ảnh; mặc định 0.34 chia đôi một ảnh, 0.30 hai ảnh, 0.30 toàn ảnh, 0.26 ô vòm), `headlineSize` (px, chỉ khi ước lượng tự động sai), `theme`, `logo`, `chinh_anh` ({"k05c": {"focusX": 0.4, "focusY": 0.45, "faceScale": 0.3}}).
- Ngưỡng chữ: lệnh `job` báo lỗi khi chữ tiêu đề ước dưới 110 px (khung ngang) hay 95 px (khung dọc).

## 3. Khuôn mô tả YouTube

```
<Câu 1: từ khoá chính + người xem nhận được gì, tự đứng được, khoảng 150 ký tự.>

<Đoạn 2: ai trò chuyện, bối cảnh (chuỗi chương trình), khái niệm chính, tên tác giả của khung hay công cụ được nhắc.>

<Đoạn 3: cách clip đi (ví dụ, câu chuyện, cách làm), không kể hết.>

Chương:
0:00 Mở đầu
<mốc từ tool>

Người trình bày:
<chức danh nguyên văn>

<Lời mời của chương trình, một lần, kèm link.>

<Ghi công nhạc, tư liệu CC-BY nếu có.>

<Một câu hỏi mở thật, gắn với đời sống người xem.>

#<hashtag1> #<hashtag2> #<hashtag3>
```

Câu hỏi kết: hỏi về đời sống của người xem, không hỏi "bạn thấy video thế nào", không đòi họ gõ một chữ cho trước. Ví dụ tốt: "Nếu xếp những việc bạn làm trong tuần qua vào bốn rổ, rổ nào đang chiếm nhiều thời gian nhất, và đó có phải là rổ bạn muốn nuôi lớn?"

## 4. Khuôn status Facebook

```
<Dòng mở: một khoảnh khắc, chi tiết thật trong clip, ngôi thứ nhất, dưới 120 ký tự.>
<(tuỳ chọn) một câu tiếp nối chi tiết đó.>

<Đoạn 2: điều chi tiết ấy mở ra, bằng lời của người dùng.>

<Đoạn 3: clip là gì (tên tập, ai cùng trò chuyện, khung chính), một hai câu.>

<Câu người dùng muốn giữ lại, hoặc câu hỏi người dùng đang sống cùng.>

<Câu hỏi mở thật cho người đọc.>
```

Bình luận đầu: "Bản đầy đủ <N> phút trên YouTube: [dán link YouTube sau khi đăng]" và link chương trình nếu có. Không đặt link trong thân status.

Clip dọc (Reels): dòng mở, hai câu thân, câu hỏi; tối đa năm dòng.

## 5. Giới hạn cổng máy kiểm (`tools/dang-tai.py kiem`)

| Mục | Chặn (KHÔNG ĐẠT) | Nhắc (lưu ý) |
|---|---|---|
| Tiêu đề | trên 100 ký tự; Title Case; viết hoa toàn bộ; emoji; "!!"; dấu < >; gạch dài; từ ngữ sai quy ước; mồi tương tác | trên 70 ký tự; từ khoá ngoài 70 ký tự đầu; cụm sáo |
| Mô tả | trên 5000 ký tự; câu đầu thiếu từ khoá; chương sai luật hay lệch file chương; thiếu câu hỏi mở; thiếu chức danh nguyên văn; thiếu ghi công CC-BY; emoji; mồi tương tác | trên 5000 byte; không có chương; hơn 3 hashtag; cụm sáo |
| Thẻ | tổng trên 500 ký tự | hơn 15 thẻ |
| Status | thiếu câu hỏi mở ở cuối; hơn 3 hashtag; emoji; mồi tương tác; từ ngữ sai quy ước | có link trong thân; dòng đầu trên 140 ký tự |
| Thumbnail | thiếu tệp; sai tỉ lệ; ngang dưới 1280 px; trên 2 MB; chưa có bản ngang cho YouTube | |

Mồi tương tác và khung sợ hãi bị chặn: "comment/bình luận/gõ... nếu", "nếu... thì share", "tag/gắn thẻ bạn bè", "share ngay", "đừng bỏ lỡ", "bị bỏ lại (phía sau)", "tụt hậu", "sốc", "không thể tin", "xem ngay".

