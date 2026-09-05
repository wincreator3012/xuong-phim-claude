---
name: phim-tu-lieu
description: Nghiên cứu và thu thập tư liệu minh họa cho clip trình bày kiến thức - hình ảnh, video phụ trợ, số liệu trích dẫn - có kiểm định nội dung, nguồn gốc và bản quyền, tải về thư mục dự án trong xưởng kèm ghi chú TU-LIEU.md sẵn sàng cho bước dựng. Kích hoạt khi user yêu cầu "nghiên cứu tư liệu", "tìm tư liệu cho clip", "tìm hình minh họa", "chuẩn bị tư liệu", "clip này cần hình ảnh gì", "thu thập hình ảnh cho video", hoặc khi user mô tả một Ý TƯỞNG clip mới và muốn chuẩn bị tư liệu trước khi quay/dựng, hoặc khi user có clip quay thô và muốn tìm tư liệu minh họa cho nội dung đã nói. Cũng kích hoạt trong lúc dựng bài khi phát hiện các đoạn nói cần minh họa mà chưa có tư liệu. KHÔNG dùng cho tìm nhạc/hiệu ứng âm thanh (đã có thư viện nhac-nen/THU-VIEN.md), viết tổng quan học thuật (skill phd-literature-review), hay tạo đồ họa infographic (skill phim-do-hoa - nhưng skill này sẽ chỉ ra chỗ nào NÊN dùng infographic thay vì ảnh).
---

# Nghiên cứu tư liệu minh họa cho clip

Mục tiêu: mỗi phút clip nói về điều gì trừu tượng, xa lạ hay số liệu đều có thứ để NHÌN - đúng nội dung, sạch bản quyền, đủ chất lượng. Ba nguyên tắc xuyên suốt: không bao giờ dùng tư liệu chưa xác minh được nguồn gốc; ưu tiên tự dựng đồ họa hơn ảnh tải về khi minh họa khái niệm/số liệu (hợp brand minimalist, không rủi ro bản quyền); tư liệu thật của user (footage lớp học, hoạt động) luôn quý hơn ảnh stock - chỉ tìm ngoài những gì user không thể tự có.

Đọc trước: `docs/QUY-TRINH-KY-THUAT.md` ở gốc thư mục xưởng (môi trường, quy trình tải qua Chrome). Kết quả đặt tại `du-an/<tên>/tu-lieu/`.

## Lối vào A - user mới có ý tưởng

Hỏi gọn MỘT lượt (AskUserQuestion hoặc vài câu trong chat, không tra vấn dài) để nắm: thông điệp lõi của clip là gì; khán giả và nền tảng đăng; độ dài dự kiến; những khái niệm, mô hình, con số, địa danh, câu chuyện nào sẽ được nhắc tới; user đã có sẵn tư liệu gì của riêng mình (footage, ảnh hoạt động). Nếu ý tưởng thuộc mảng người dùng hay giảng (xem lĩnh vực chuyên môn trong phong-cach/PHONG-CACH.md), tự đề xuất thêm các điểm minh họa đắt giá từ hiểu biết về nội dung của user thay vì chỉ chờ liệt kê.

## Lối vào B - đã có clip quay thô

Lấy transcript theo skill phim-transcript (nếu chưa có). Đọc kỹ transcript và đánh dấu các "điểm minh họa" kèm mốc thời gian: khái niệm trừu tượng đang được giải thích; số liệu, nghiên cứu được trích; địa danh, tổ chức, nhân vật, sự kiện được nhắc; câu chuyện có bối cảnh cụ thể; đoạn nói dài quá 60-90 giây không có gì thay đổi trên hình (cần B-roll nghỉ mắt).

## Bản đề xuất tư liệu (chốt duyệt - BẮT BUỘC trước khi tải bất cứ gì)

Trình user bảng đề xuất, mỗi dòng một điểm minh họa:

| Mốc/đoạn | Nội dung đang nói | Loại tư liệu | Đề xuất cụ thể |
|---|---|---|---|
| 03:20 | Nhắc thí nghiệm kẹo dẻo Stanford | Ảnh thật + số liệu kiểm chứng | Ảnh Đại học Stanford (Wikimedia); số liệu follow-up làm InfoStat |
| 07:45 | Mô hình 3 vùng học tập | Infographic tự dựng | InfoSteps 3 bước, không cần ảnh ngoài |
| 12:10 | Kể chuyện lớp học ở Huế | Footage của user | Đề nghị user cung cấp ảnh/clip lớp đó |

Loại tư liệu chọn theo thứ tự ưu tiên: (1) tư liệu riêng của user, (2) infographic tự dựng bằng skill phim-do-hoa (mọi khái niệm, mô hình, số liệu), (3) ảnh/video thật từ nguồn mở đã kiểm định (địa danh, sự kiện, chân dung nhân vật lịch sử, bối cảnh không thể tự quay). Ghi rõ trong bảng cột nào cần user duyệt/cung cấp. Chờ duyệt xong mới sang bước tìm.

## Tìm và xác minh (ba lớp, không bỏ lớp nào)

Nguồn và quy tắc giấy phép chi tiết: đọc `thu-vien/HINH-ANH.md` ở gốc xưởng (bản sao trong `references/nguon-tu-lieu.md` của skill này chỉ để dùng khi skill được cài rời khỏi repo).

1. **Đúng nội dung**: đọc trang nguồn và caption gốc của ảnh - ảnh phải đúng đối tượng, đúng sự kiện, đúng thời điểm được nói tới (ảnh "một giảng đường bất kỳ" không được chú thích thành Harvard). Số liệu: truy về nguồn sơ cấp [primary source] bằng WebSearch/WebFetch, ghi lại citation đầy đủ; số không xác minh được thì báo user, không đưa vào clip
2. **Sạch bản quyền**: đọc giấy phép TỪNG FILE (Wikimedia mỗi file một giấy phép khác nhau); chỉ nhận public domain, CC0, CC-BY/CC-BY-SA (ghi công đúng chuẩn), hoặc giấy phép nền tảng cho phép thương mại (Pexels, Unsplash, Pixabay). Ảnh có người nhận diện rõ: tránh dùng trong clip quảng bá thương mại (giấy phép stock không bảo đảm quyền hình ảnh cá nhân [model release]); clip bài giảng giáo dục thì chấp nhận được với nguồn chuẩn
3. **Đủ chất lượng**: ảnh ≥1920px chiều rộng cho khung ngang (≥1080px chiều rộng nếu chỉ dùng khung dọc), không watermark, không ảnh AI trừ khi user chủ động muốn; video phụ trợ ≥1080p; ưu tiên tông màu trầm ấm hợp brand

## Tải về và ghi chú

Tải qua trình duyệt theo đúng quy trình trong thu-vien/AM-THANH.md mục "Quy tắc bổ sung thư viện" (click nút tải trên trang nguồn, chờ 6-8 giây mỗi lượt, file về Downloads rồi copy vào dự án). Wikimedia: tải bản "Original file" độ phân giải gốc.

- Đặt tên: `<mo-ta-ngan>_<nguon>-<id>.<ext>` vào `du-an/<tên>/tu-lieu/`
- Ghi `du-an/<tên>/tu-lieu/TU-LIEU.md`: mỗi file một mục gồm mô tả, dùng cho đoạn nào (mốc transcript), URL nguồn, tác giả, giấy phép, dòng ghi công nếu CC-BY (mẫu: `Ảnh: <tên> - <tác giả>, CC BY 4.0`), kích thước; thêm mục "Số liệu đã kiểm chứng" liệt kê từng con số với citation và câu chữ đề xuất cho InfoStat/InfoQuote; cuối file: mục "Chưa tìm được / cần user cung cấp"
- Dòng ghi công gom lại để phiên dựng chèn vào mô tả video (giống nhạc MacLeod)

## Bàn giao cho bước dựng

Ảnh tĩnh vào clip qua hiệu ứng Ken Burns nhẹ (chậm rãi, hợp nhịp thở của brand) - phiên dựng chuyển ảnh thành video rồi dùng như insert/B-roll trong timeline:

```
ffmpeg -loop 1 -i tu-lieu/anh.jpg -t 6 -vf "scale=2400:-2,zoompan=z='min(1.10,1+0.0006*on)':x='(iw-iw/zoom)/2':y='(ih-ih/zoom)/2':d=1:s=1920x1080:fps=30,format=yuv420p" -c:v libx264 -crf 18 -an tu-lieu/anh-kb.mp4
```

Kết thúc: báo user số tư liệu đã thu thập, những gì cần họ cung cấp thêm, và TU-LIEU.md đã sẵn sàng để skill phim-dung-bai hoặc phim-clip-ngan dùng khi soạn timeline.
