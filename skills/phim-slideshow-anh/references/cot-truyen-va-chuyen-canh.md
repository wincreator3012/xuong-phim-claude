# Cốt truyện, nhịp và chuyển cảnh cho slideshow ảnh

Giá trị mặc định dưới đây là điểm xuất phát đã kiểm chứng ở một slideshow đám cưới 10 phút, 122 ảnh, im lặng, lặp; clip nào cần khác thì ứng biến và nói lý do với người dùng ở chốt duyệt.

## 1. Cốt truyện: người xem cần cảm gì ở từng đoạn

Người đứng xem giữa vòng lặp có thể vào ở bất cứ đâu, nên cốt truyện không cần dựa vào việc nhớ đoạn trước. Hai điều giữ cho mạch vẫn đẹp: mỗi chương có một chủ đề cảm xúc nhìn ra được từ ảnh đầu chương, và các đỉnh cảm xúc (khoảnh khắc hôn, ôm, cười lớn) rải đều chứ không dồn một chỗ.

- **Mở bằng thẻ chữ rồi chi tiết, không mở bằng đám đông.** Thẻ tên, ngày, nơi chốn, rồi ảnh vật (nhẫn, hoa, bàn tay, địa điểm). Người mới nhìn lên hiểu ngay đây là phim gì của ai.
- **Chương theo thời gian hay nơi chốn:** ví dụ chuẩn bị, gặp mặt, hai gia đình, chân dung ngoài trời, giờ vàng; rồi chương thứ hai ở nơi khác. Giữa phim đặt MỘT thẻ trích dẫn ngắn (8 đến 9 giây) làm điểm thở và ranh giới chương.
- **Gom theo khoảnh khắc, không theo thứ tự chụp.** Ảnh cùng một khoảnh khắc đứng cạnh nhau (đôi, ba hoặc lưới bốn) để người xem thấy trọn một đoạn, ví dụ tấm bay của tà váy hay bốn góc cùng hoàng hôn.
- **Đỉnh cảm xúc dùng chuyển cảnh riêng.** Khoảnh khắc hôn dùng `heart` (mống mắt hình trái tim mở từ chính hai gương mặt); không dùng quá ba lần cả phim, vì lặp nhiều thì mất ý.
- **Khép bằng ảnh chủ thể đẹp nhất, rồi thẻ cảm ơn.** Cuối phim đặt một ảnh của riêng cặp đôi hay chủ nhân (zoom chậm kiểu `hero`), sau đó thẻ cảm ơn 12,5 giây mờ về đúng khung nền của thẻ mở đầu để vòng lặp liền mạch.
- **Bỏ ảnh yếu thay vì nhồi.** Ảnh mờ, trùng ý, ảnh làm lộ ai đó kém đẹp: bỏ (khai báo trong `REMOVED`). Khi chủ nhân yêu cầu bỏ thêm sau khi duyệt, chạy lại `plan` rồi render lại toàn bộ.

## 2. Nhịp và thời lượng

Tổng thời lượng là mục tiêu (mặc định 600 giây). Mỗi cảnh ghi thời gian giữ "danh nghĩa" và `build_timeline` nhân một hệ số chung `f` để tổng đúng mục tiêu (thẻ chữ giữ nguyên). Ở dự án đầu `f` khoảng 1,19.

| Loại cảnh | Giữ danh nghĩa | Ghi chú |
|---|---|---|
| Ảnh đơn | 5,0 đến 5,6 giây | ảnh quan trọng 6,0 đến 7,0 (`kb='hero'`) |
| Ảnh đôi | 6,2 đến 6,6 giây | hai ảnh dọc cạnh nhau; ảnh thứ hai hiện sau 0,3 giây |
| Ảnh ba | 8,5 đến 9,0 giây | bộ ba cùng chủ đề |
| Lưới bốn | 8,0 đến 8,5 giây | bốn ảnh cùng khoảnh khắc; xếp lần lượt |
| Nhanh (`BURST`) | 3,6 đến 4,6 giây | chuỗi ảnh vui, dùng chuyển `quick` |
| Thẻ mở, trích dẫn, cảm ơn | 9,5, 8,5, 12,5 giây | |

Giữ hình rõ ngắn nhất (sau khi trừ nửa thời gian chuyển cảnh hai đầu) phải từ khoảng 2,5 giây trở lên (`plan` in số này): thấp hơn thì ảnh vụt qua, nhất là với người chỉ ngước nhìn.

Nếu phim phát KÈM NHẠC: nhịp nhanh hơn nhiều (khoảng 1,5 đến 3 giây mỗi ảnh, chuyển cảnh theo phách); xem `skills/phim-slideshow-anh/references/nghien-cuu-slideshow.md`. Động cơ vẫn dùng được, chỉ cần giảm thời gian giữ danh nghĩa và chọn chuyển `quick`, `dissolve`.

## 3. Bố cục ảnh

- **Ảnh ngang (tỉ lệ từ 1,35 trở lên) mặc định là ảnh bìa tràn khung** với zoom hoặc pan chậm. Ảnh dọc và gần vuông mặc định vào khung có viền, trên nền là chính ảnh làm mờ (nên khung nào cũng có màu của ảnh, không bao giờ có dải đen).
- **Zoom và pan không bao giờ cắt mặt:** động cơ nội suy tâm và mức zoom giữa hai trạng thái, rồi ép hộp chủ thể (từ mặt nhận dạng, mở rộng) luôn nằm trong khung. Ảnh không nhận ra mặt cần `focus_override`.
- **Kiểu zoom `kb`:** `in`, `out`, `pan_r`, `pan_l`, `drift` (rất nhẹ), `burst` (gần như tĩnh), `hero` (vào chậm và sâu), `tile`/`tile_out` (trong khung). Mặc định xoay vòng `KB_CYCLE` để hai ảnh liền nhau không cùng hướng.
- **Nền đen trắng** (`mood='mono'`): đưa cả bộ ảnh đen trắng vào cùng một cảnh trên nền tối thay vì lẫn với ảnh màu.
- **Ảnh hạt nhiều (đen trắng ISO cao):** thêm vào `denoise`; động cơ khử nhiễu thay vì làm nét, vì làm nét làm hạt nổi lên.

## 4. Danh mục chuyển cảnh

Thời gian là mặc định (giây) của chuyển cảnh VÀO cảnh đang khai báo; chuyển cảnh chồng lên hai cảnh mỗi bên nửa thời gian.

| Tên | Giây | Cảm giác | Dùng khi | Tránh |
|---|---|---|---|---|
| `dissolve` | 1,5 | hoà tan mềm, nhẹ nhất | hai ảnh cùng không khí, nền của việc | ảnh bìa nối ảnh khung (nhìn như hai lớp chồng) |
| `quick` | 0,8 | hoà tan nhanh | chuỗi ảnh vui, `BURST` | đỉnh cảm xúc |
| `glow` | 2,1 | sáng ấm lên rồi hiện ảnh mới, hơi mờ | đổi không khí, vào chương, từ ảnh tĩnh sang đỉnh cảm xúc | dùng liên tục hai lần |
| `zoom` | 1,6 | ảnh cũ phóng ra, ảnh mới co vào | hai ảnh ngang cùng hướng nhìn | ảnh có mặt ở rìa |
| `push` | 1,3 | đẩy ngang có nhoè chuyển động, hướng đổi luân phiên | hai ảnh dọc, đổi nhịp, chuyển ý | ngay sau `push` khác (hướng sẽ đổi nhưng nhịp trùng) |
| `focus` | 1,8 | mờ nét rồi nét lại | chuyển sang ảnh chân dung, ảnh trầm, đen trắng | ảnh đã mờ sẵn |
| `doors` | 2,0 | hai cánh mở từ giữa, tối ở mép | bước vào một không gian mới (phòng, sảnh) | dùng giữa chương cùng chỗ |
| `heart` | 2,4 | mống mắt hình trái tim mở từ mặt chủ thể | khoảnh khắc hôn, đỉnh tình cảm; tối đa ba lần | cảnh không có mặt rõ |
| `lightleak` | 2,0 | quầng sáng ấm trôi qua | ảnh ngoài trời nắng, giờ vàng, hoàng hôn | cảnh trong nhà tối |
| `sweep` | 1,8 | vệt sáng quét chéo | nối ảnh bìa với ảnh khung hoặc ngược lại | |

Quy tắc chọn: chuyển cảnh nói điều gì đó về hai ảnh nó nối (cùng khoảnh khắc thì `dissolve`, sang không khí mới thì `glow`, bước vào không gian thì `doors`, đỉnh tình cảm thì `heart`). Giữ phần lớn chuyển cảnh ở nhóm nhẹ (`dissolve`, `glow`, `push`, `focus`), nhóm có hiệu ứng rõ (`doors`, `heart`, `lightleak`, `sweep`) chỉ để làm điểm nhấn. Chuyển cảnh gắt, xoay hay quay hình (như quay lật, xoáy) không có trong bộ vì không hợp không khí lễ cưới và làm sao nhãng khỏi ảnh.

## 5. Thẻ chữ

Mọi thẻ khai báo trong `slideshow.json` (`cards.<tên>`): `els` là danh sách dòng chữ (`font` là `caps`, `italic` hoặc `script`; `size`, `tracking` theo em, `y` là đường nền chữ tính theo pixel trong khung 1080, `color` là `gold` hay `ink`, `t0`-`t1` là giây hiện, `mode` là `fade` hay `wipe`); `line` là đường kẻ vàng có thoi ở giữa; `fade_out` là lúc cả thẻ mờ đi (chỉ thẻ cuối). Thẻ mở đầu và thẻ cuối dùng cùng nền ngà, khung vàng đôi, hạt vàng trôi: chính điều này làm vòng lặp liền mạch.

Khung chữ bố cục dọc (khung 1080): dòng phụ nhỏ cách nhau khoảng 60 điểm; tên viết tay đặt giữa (y khoảng 586 đến 625); đường kẻ cách tên khoảng 120 điểm; ngày và nơi chốn cách nhau 60 đến 70 điểm. Sau mỗi lần đổi, xem lại bằng `still` ở giây chữ đã hiện đủ.
