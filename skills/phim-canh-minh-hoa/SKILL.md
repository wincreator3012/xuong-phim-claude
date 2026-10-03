---
name: "phim-canh-minh-hoa"
description: "Vẽ riêng từng CẢNH MINH HOẠ giải thích (cơ chế, quy trình, so sánh, số liệu, mô phỏng, nhịp thực hành) bằng một trang web có thời gian ảo rồi chụp từng khung ra video, theo phong cách explainer: nhãn nhỏ, tiêu đề lớn có từ khoá tô màu, thẻ bo góc, sơ đồ lớn dần theo lời, màu theo vai. Dùng làm B-roll cho bài giảng quay mặt theo bốn kiểu chèn (toàn khung, nền là khung hình mờ, thẻ nổi cạnh người nói, người nói thu vào góc) hoặc làm giọng hình sơ đồ cho clip thuần minh hoạ từ file voice. Kích hoạt khi user nói \"cảnh minh hoạ\", \"minh hoạ động\", \"explainer\", \"làm hình động giải thích đoạn này\", \"render minh hoạ cho đoạn này\", \"dùng hình này làm nền mờ\", \"B-roll minh hoạ\", \"mô phỏng cơ chế\", \"sơ đồ động\", hoặc gửi hình mẫu explainer muốn làm theo. KHÔNG dùng cho intro, outro, bảng tên, pill chữ, infographic có tham số (phim-do-hoa), dựng cả bài (phim-dung-bai), kịch bản cả video từ file voice (phim-infomotion, skill đó gọi skill này cho từng nhịp), hoạt hình có nhân vật (phim-hoat-hoa)."
---

# Cảnh minh hoạ: từ trang web ra video

Mục tiêu: những đoạn người dùng GIẢI THÍCH (một cơ chế, một quy trình, một so sánh trước sau, một con số, một nhịp thực hành) có một cảnh minh hoạ vẽ riêng cho đúng ý đó, đẹp và rõ như một sơ đồ động, khớp từng nhịp với lời người dùng nói. Cảnh dùng được ở hai nơi: B-roll trong bài giảng quay mặt (skill phim-dung-bai), và giọng hình "sơ đồ" trong clip thuần minh hoạ từ file voice (skill phim-infomotion).

**Nguyên lý kỹ thuật.** Mỗi cảnh là một trang HTML có thời gian ẢO: mọi chuyển động là hàm của t (giây). Cùng một file vừa chạy trực tiếp trên trình duyệt (người dùng xem, tua, góp ý), vừa được `tools/canh.mjs` mở trong Chromium không giao diện, tua tới từng khung, chụp, ghép bằng ffmpeg. Máy chậm chỉ làm render lâu hơn, không bao giờ rớt khung. Đây cũng chính là nguyên lý của Remotion; khác ở chỗ cảnh được viết tự do theo nội dung thay vì chọn từ một bộ component có tham số.

**Ranh giới với studio Remotion.** Studio giữ đồ họa nhận diện dùng lại (intro, outro, bảng tên, pill Benefits, Info*, YNiem, YCanh). Cảnh minh hoạ là hình vẽ riêng cho một ý, không tái dùng nguyên khối; cái được tái dùng là bộ thiết kế (`do-hoa-chung/canh-kit/`) và các khuôn cảnh.

Đọc trước: `skills/_chung/van-hanh.md`, `skills/_chung/overlay-va-the.md`, `skills/_chung/nghiem-thu-dung-y.md`; nguyên lý thiết kế, mười một khuôn cảnh, bố cục, màu, chuyển động, danh sách cấm: `skills/phim-canh-minh-hoa/references/nguyen-ly-canh.md`; hợp đồng runtime, khung file, lệnh, bốn kiểu chèn kèm mẫu timeline: `skills/phim-canh-minh-hoa/references/viet-canh.md`. Hai cảnh mẫu đã kiểm: `do-hoa-chung/canh-kit/mau/cua-so-dung-nap.html` (sơ đồ toàn khung, có ô chừa góc) và `do-hoa-chung/canh-kit/mau/the-noi-tho-hop.html` (thẻ nổi nền trong suốt).

## Bốn nguyên tắc xuyên suốt

1. **Cảnh lớn dần theo lời, không dồn ra đầu cảnh rồi đứng.** Mỗi cảnh là một chuỗi cảnh con, mỗi cảnh con mở đúng lúc lời người dùng nhắc tới phần đó (mốc lấy từ transcript). Lỗi làm cảnh giống slide là hiện hết trong một phần tư đầu rồi đứng yên. Hết ý thì giữ yên cho người xem đọc, không lắc lư cho có.
2. **Mỗi cảnh một chữ ký chuyển động.** Một khoảnh khắc sơ đồ tự "nói" ý chính (cửa sổ nới rộng, chấm sáng đi quanh hình vuông, hai làn so sánh cùng chạy rồi một làn rớt khung). Chọn khuôn cảnh trước, giữ chữ ký của khuôn, thay nội dung.
3. **Hình không nói điều người dùng không nói.** Chữ trên hình là cụm nhấn trích từ lời, không chép lại cả câu; dữ kiện có nguồn; mô hình của người khác ghi tên tác giả ngay trên cảnh.
4. **Khi lời là một lập luận hay quy trình, một chủ thể hình đi cùng lời và biến hình theo nó** (thẻ tự điền rồi đi qua AI rồi đóng gói; sân bóng sáng dần từng cầu thủ), thay vì chuỗi hình rời. Nội dung hình là đúng ví dụ người nói nêu, đúng thứ tự họ nhắc; khoảnh khắc khái quát là chữ ký của cảnh. Nguyên lý và ví dụ: `skills/phim-canh-minh-hoa/references/nguyen-ly-canh.md` mục 3 phần "Một chủ thể xuyên suốt".

## Quy trình

### Bước 1 - Chọn đoạn và kiểu chèn

Trong phương án overlay của bài giảng (phim-dung-bai Bước 3) hoặc kịch bản nhịp (phim-infomotion Bước 5), đánh dấu những đoạn đáng có cảnh minh hoạ: người dùng giải thích một cơ chế, quy trình, quan hệ nhân quả, so sánh, con số, hoặc hướng dẫn một nhịp thực hành. Không đặt cảnh vào lúc người dùng kể chuyện, giãi bày cảm xúc, hay đang nhìn thẳng người xem để kết nối: gương mặt người dùng lúc đó là thông điệp.

Mỗi cảnh chọn MỘT kiểu chèn (chi tiết lệnh và timeline ở `viet-canh.md` mục 5):

| Kiểu chèn | Hợp khi | Chụp | Ghép |
|---|---|---|---|
| Toàn khung thay hình | giải thích dài, sơ đồ cần cả khung; tiếng anh vẫn đi liền | `chup` ra mp4 | `broll` |
| Nền là khung hình mờ | như trên nhưng muốn người xem vẫn thấy đang ở trong phòng người dùng nói | `canh-ghep.py khung` lấy một khung, `chup --nen-anh` | `broll` |
| Thẻ nổi cạnh người nói | ý ngắn hay nhịp thực hành, gương mặt người dùng vẫn cần hiện | `chup --alpha` ra webm | `overlay` |
| Người nói thu vào góc | giải thích dài mà vẫn muốn giữ hiện diện của người dùng | `chup --pip`, rồi `canh-ghep.py pip` trên máy | `broll` |

Mật độ: bài giảng dài thường một cảnh mỗi 2-4 phút ở đúng những đoạn giải thích; clip ngắn một cảnh là đủ. Đây là điểm xuất phát, không phải trần: đoạn giải thích dày thì đề xuất dày hơn kèm lý do. Hai cảnh toàn khung liên tiếp cách nhau ít nhất 5 giây thấy mặt người dùng (`_chung/overlay-va-the.md`); thẻ nổi không tính.

### Bước 2 - Kịch bản cảnh bằng chữ (thuộc chốt duyệt 1)

Mỗi cảnh một khối trong phương án trình người dùng: mốc nguồn bắt đầu-kết thúc, lời nói (rút gọn), kiểu chèn, khuôn cảnh và chữ ký, dòng "Thấy gì:" tả người xem thấy gì bằng lời thường, chuỗi cảnh con với mốc (giây trong cảnh, lấy từ transcript), chữ trên hình, dòng "Kiểm chứng:" nếu có dữ kiện hay tác giả. Họ màu mặc định Đêm xanh (`phong-cach/PHONG-CACH.md` mục 3); cả dự án một họ màu.

Loại cảnh lần đầu xuất hiện trong dự án, hoặc người dùng muốn thấy chuyển động trước khi duyệt: dựng cảnh rồi đưa người dùng một trang phòng thử (`canh.mjs phong-thu`, đăng bằng Artifact) để người dùng xem chạy thật, đổi họ màu, khung, cách chèn, và góp ý theo số giây.

### Bước 3 - Viết file cảnh

`du-an/<x>/canh/NN-<ten>.html`, bắt đầu từ cảnh mẫu gần nhất. Mốc để ở MỘT đối tượng hằng số đầu script, tính `t trong cảnh = mốc nguồn - mốc bắt đầu cảnh`. Viết cả hai khung khi dự án có cả ngang lẫn dọc: dọc không phải bản cắt của ngang, là bố cục riêng (xếp chồng, chữ to hơn, trục toạ độ sơ đồ hẹp hơn). Theo luật tất định ở `viet-canh.md` mục 1. Chừa 1-2 giây giữ yên ở cuối cảnh để sau này rút đuôi thân vẫn không phải chụp lại.

### Bước 4 - Soi trước khi chụp

Trong sandbox (dựng theo mục "Khởi động phiên mới" của `docs/QUY-TRINH-KY-THUAT.md`, thêm `tools/canh.mjs`, `do-hoa-chung/canh-kit/` và `du-an/<x>/canh/`):

1. `node tools/canh.mjs kiem <cảnh>` phải báo "KIỂM TẤT ĐỊNH: ĐẠT".
2. `node tools/canh.mjs người dùng <cảnh> --t <các mốc cảnh con> --khung <khung đích>` rồi NHÌN contact sheet: chữ Việt đủ dấu, không tràn, không đè nhau, cỡ chữ đọc được trên điện thoại (khung dọc soi riêng).
3. Thẻ nổi: soi thêm trên khung hình thật bằng `--alpha --xem-tren <khung.jpg>` (khung trích từ nguồn trên máy), gương mặt người dùng phải trống hoàn toàn ở trạng thái đầy đủ nhất của thẻ. Nền trong suốt phải thử bằng khung ghép thật, vì theme có thể đè nền đặc lên (đã gặp).

### Bước 5 - Chụp và đưa về máy

Lệnh theo kiểu chèn ở `viet-canh.md` mục 4-5; ra `du-an/<x>/do-hoa/<khung>/canh-NN-<ten>.<mp4|webm>`, commit về máy theo `_chung/van-hanh.md` (kèm `do-hoa-manifest.json` và file cảnh `.html` nếu sửa ở sandbox). Thời lượng: `canh.mjs` tự đo và ghi manifest; lệch quá 0,1 giây là lỗi, chụp lại. Kiểu thu vào góc: chạy `canh-ghep.py pip` trên máy với nguồn thật (footage không rời máy).

### Bước 6 - Ghép, nghiệm thu

Vào timeline theo mẫu ở `viet-canh.md` mục 5 rồi đi tiếp quy trình của skill gọi (`assemble.py --kiem-tra`, nháp, bản chính). Nghiệm thu đúng ý theo `_chung/nghiem-thu-dung-y.md`: với mỗi cảnh, trích khung tại đầu mỗi cảnh con (+0,5 giây) trên bản dựng và ghép cặp với câu transcript đang nói; soi chỗ chuyển vào và ra cảnh (không giật, không lộ khung đen); thẻ nổi không che mặt trên khung hình thật.

Góp ý của người dùng ghi `SO-GOP-Y.md` theo mốc; góp ý về cả họ cảnh lặp lần hai thì sửa bộ thiết kế (`canh.css`, cảnh mẫu) và sổ tay góp ý của PHONG-CACH, không chỉ sửa cảnh đang làm. Khuôn cảnh mới thành công qua dự án thật thì thêm vào `nguyen-ly-canh.md` mục 4 và lưu một bản mẫu vào `do-hoa-chung/canh-kit/mau/`.

## Khi một khâu hỏng

- `kiem` KHÔNG ĐẠT: trạng thái đang phụ thuộc lịch sử tua (biến cộng dồn qua các khung, `Math.random`, `setTimeout`, CSS transition, video hay GIF tự chạy). Sửa thành hàm của t; không chụp cảnh chưa đạt.
- Chụp treo hay báo cảnh không sẵn sàng: mở `dong-goi` ra file rồi xem lỗi JavaScript trong log; font thiếu thì kiểm `do-hoa-chung/canh-kit/fonts/`.
- Một cảnh vẽ không ra sau hai lần sửa: báo người dùng, đề xuất đổi sang khuôn cảnh khác hoặc component studio có sẵn; đây là lựa chọn đưa người dùng duyệt lại.
- Ghép kiểu thu vào góc lệch ô: kiểm manifest có mục `pip` (chụp phải có `--pip`), hoặc truyền `--o` tường minh.

## Quy tắc cứng

- Mọi cảnh qua `canh.mjs kiem` ĐẠT trước khi chụp; không chụp tay, không quay màn hình.
- Hình không nói điều người dùng không nói; dữ kiện có "Kiểm chứng:"; mô hình, công cụ của người khác ghi tên tác giả trên cảnh.
- Chữ trên cảnh theo `phong-cach/PHONG-CACH.md` mục 4 (thuần Việt có ngoặc vuông [English], sentence case, không Title Case, gạch ngang thường, không emoji).
- Thẻ nổi và ô người nói không bao giờ che mặt; kiểm trên khung hình thật.
- Footage không rời máy: sandbox chỉ nhận vài khung hình tĩnh (nền mờ, soi thẻ nổi); ghép đoạn quay thật chạy trên máy bằng `canh-ghep.py`.
- Hình vẽ bằng code; không dùng ảnh hay clip AI tạo để thay hình thật về người, nơi chốn, sự kiện.
- Thời lượng cảnh khớp ô trong timeline, đo bằng manifest hay `ffprobe`; không kéo dài bằng khung đứng. Ô bị rút ngắn sau khi chụp thì bớt bằng `overlay.duration` kèm `giu`, không chạm hoạt cảnh.
- Chưa qua cổng nghiệm thu của skill gọi thì chưa báo "xong".

<!-- ban-nguon: phim-canh-minh-hoa 2026-10-03 5e71977b -->
