# Nguyên lý bộ lệnh và lớp phong cách mặc định (phim-hoat-hoa)

Tài liệu tra cứu cho skill phim-hoat-hoa: mười hai nguyên lý viết bộ lệnh làm phim (rút từ bộ lệnh phim "Nhà" của Đặng Hữu Sơn) và lớp phong cách mặc định của skill (ngôn ngữ hình, cung tự sự chuyển hoá, trí tuệ soma, hệ ẩn dụ, chữ trên hình). SKILL.md giữ bản tóm tắt; đọc đầy đủ ở đây khi viết kịch bản, kinh thánh thế giới hoặc soạn bộ lệnh. Tên, chức danh và từ ngữ phải viết đúng: `phong-cach/PHONG-CACH.md`.

## Phần 1. Mười hai nguyên lý viết bộ lệnh làm phim

Đây là "ngữ pháp" rút ra từ bộ lệnh "Nhà". Mọi bộ lệnh skill này soạn phải đạt đủ mười hai điều.

1. **Vai trò kép.** Mở bằng vai "đạo diễn kiêm lập trình viên hình hoạ sáng tạo [creative coding]". Một vai lo cảm xúc và nhịp, một vai lo tính tất định và hiệu năng; thiếu vai nào phim hỏng theo kiểu của vai đó.
2. **Ràng buộc sinh phong cách.** "Chỉ code, không ảnh, không thư viện, không file âm thanh" không phải khó dễ kỹ thuật mà là cách ép phong cách nhất quán và chặn hình AI đại trà. Luôn nêu ngoại lệ tường minh (font Google Fonts, fallback khi mất mạng).
3. **Đặc tả bằng dữ liệu, không bằng tính từ.** Mã màu hex, số px, số giây, số pha, BPM, LUFS. "Ấm áp" là mơ hồ; "Fmaj7, 66 BPM, pad triangle lọc thấp" thì làm được.
4. **Tất định [determinism].** `render(t)` thuần theo thời gian, PRNG có seed, cấm `Math.random()` trong vòng render. Kèm phép kiểm: render cùng một `t` hai lần phải ra ảnh giống hệt. Không có điều này thì không tua, không xuất khung, không soát lỗi được.
5. **Nhịp là dữ liệu, không phải code.** Timeline là bảng cue `{scene, duration, k, tr, td, at}`, `start` tự cộng dồn; hệ số `k` kéo giãn thời gian bên trong cảnh để chỉnh nhịp mà không sửa hàm vẽ. Âm thanh và caption neo theo cảnh (`S(tên cảnh, u) = cue.start + u*k`), nên đổi nhịp thì tất cả tự khớp.
6. **Một mô-típ biến đổi xuyên suốt.** Máy bay giấy trong "Nhà" bay đi, gãy cánh, mở lại, nhân đôi, sinh thêm, bay vòng ôm gia đình. Mô-típ là sợi chỉ cảm xúc; mỗi trạng thái của nó là một nấc của hành trình.
7. **Cấu trúc gương [bookend].** Cảnh kết lặp bố cục cảnh mở nhưng đổi ánh sáng và đổi vai. Người xem cảm được sự chuyển hoá mà không cần lời giải thích.
8. **Hình đọc được trong 0,3 giây.** Mỗi cảnh một chủ thể, silhouette rõ, bảng màu đóng (khoảng 7 màu), không chữ trong hình trừ caption và chữ ký.
9. **Từ vựng chuyển cảnh đóng, mỗi loại mang nghĩa.** Chỉ 4-5 kiểu chuyển cảnh, cấm crossfade liên tục. Chuyển cảnh là dấu câu của tự sự.
10. **Âm thanh là ngữ nghĩa.** Hoà âm đi theo cung cảm xúc (trưởng ấm, rồi thứ tối, rồi sáng lại, ngân kết); SFX phân theo từng hồi; cấm thẳng lỗi mô hình hay mắc ("ting ting" chuông rải); SFX dưới nhạc; xuất stem riêng.
11. **Quy trình theo chặng, buộc dừng.** Không làm một phát cả phim. Mỗi chặng xuất contact sheet, tự soát, dừng cho người duyệt.
12. **Bộ nhớ lỗi.** Bộ lệnh mang theo checklist các lỗi đã từng gặp (thứ tự vẽ che khuất, tràn khung cửa sổ, caption che mặt...) và kiểm chứng đo được (khung nặng nhất dưới ~70 ms, LUFS, dung lượng). Checklist lớn dần qua từng phim.

Và một nguyên lý đóng gói: **tách hằng số khỏi biến số.** Phần kỹ thuật, phong cách, âm thanh, xuất file là hằng số; phần câu chuyện, bảng cảnh, caption, credit là biến số. Ai dùng lại bộ lệnh chỉ cần sửa biến số.

## Phần 2. Lớp phong cách mặc định

Đây là phong cách mặc định do tác giả gốc của xưởng xây dựng (xem README) (tự sự chuyển hoá, chánh niệm, soma). `phong-cach/PHONG-CACH.md` của người dùng nói khác thì theo PHONG-CACH; chưa rõ thì hỏi người dùng có muốn dùng lớp này không.

"Nhà" là phim tốt, nhưng mang hai giả định khác phong cách mặc định này: công thức thành công bề ngoài (lên phố, thắng lợi, sân khấu, biểu đồ đi lên) và mật độ montage dày (20 cảnh / 70 giây). Bảng dưới là phép chuyển đổi.

| Trục | Phim "Nhà" | Phong cách mặc định |
|---|---|---|
| Cung tự sự | Nghèo khó → nỗ lực → thành công → về quê | Mắc kẹt → dừng lại → nhận biết → nới ra → nảy mầm → tái hợp |
| Thước đo "đến nơi" | Thành tựu nhìn thấy được | Trạng thái Tâm-Thể: thở được, hiện diện, kết nối |
| Mật độ | 20 cảnh / 70 giây, montage nhanh | 8-12 cảnh / 60-90 giây, có khoảng tĩnh |
| Chuyển động | easeBack nảy (pop-up), boil 8 lần/giây | bezier(0.22, 1, 0.36, 1), không nảy; boil 5-6 lần/giây biên độ nhỏ, đóng băng ở khoảnh khắc tĩnh |
| Chất giấy | Giấy cũ, vết loang, vignette nặng | Giấy ngà sạch, hạt mịn, vignette rất nhẹ |
| Nhân vật | Silhouette đặc | Silhouette hoặc người nét 3px; thân thể là nơi mang cảm xúc |
| Kết | Chữ ký "nhà" + credit | Hình gương + câu hỏi mở thực sự + chữ ký của người dùng |
| Chất bất toàn | Kết tròn trịa | Trạng thái cuối giữ dấu vết trạng thái đầu |

### 2.1. Ngôn ngữ hình ảnh

- Kế thừa ngôn ngữ thiết kế của phim-do-hoa: khoảng trắng rộng, mỗi khung một ý, chuyển động chậm và êm (fade + trồi 20-30 px, easing bezier(0.22, 1, 0.36, 1), 24-34 khung mỗi chuyển động), không spring nảy, không emoji, đường nét 3 px là chữ ký thị giác.
- Font: Lora (500/600, có italic) cho caption và chữ ký, Be Vietnam Pro cho nhãn phụ. Cụm nhấn trong caption dùng Lora italic 600 màu nhấn kèm gạch chân 3 px vẽ dần, không dùng font viết tay hoa mỹ.
- Theme lấy từ `brand.json` (mã màu dưới là bảng mặc định; bảng người dùng chọn lúc thiết lập nằm trong `brand/brand.json`): light (giấy ngà `#FAF7F1`, mực `#23282D`, lục trầm `#2F5D50`) hoặc dark (than `#15181C`, kem `#F2EEE5`, đồng ấm `#C7A97B`). Mỗi phim một theme chủ đạo; phim có cung sáng-tối được phép đi từ tông tối sang tông sáng như một phần của chuyển hoá, nhưng vẫn trong cùng bảng màu.
- Hoạt hoạ tự sự cần nhiều màu hơn đồ họa thông tin. **Bảng mở rộng đề xuất (cần người dùng duyệt ở style frame phim đầu tiên, chưa phải mặc định):** giấy ngà `#FAF7F1` · mực `#23282D` · lục trầm `#2F5D50` · đồng ấm `#C7A97B` · chàm đêm `#1E2A38` · hồng phai `#C98E84` · xám sương `#9AA3A6`, cộng pha trộn giữa chúng. Sau khi người dùng duyệt, xin phép ghi vào `brand.json` dưới khoá `palettes.hoatHoa`; không tự sửa brand gốc.
- Silhouette đọc được trong 0,3 giây; đường chân trời thấp, trời chiếm khoảng 60-65% khung, để caption có chỗ thở.
- Một điểm neo thị giác cố định xuyên các cảnh (một chấm sáng, một vầng trăng, một vòng tròn nhỏ) giúp mắt người xem có chỗ tựa.

### 2.2. Cấu trúc tự sự chuyển hoá

Cung mặc định sáu nấc (mỗi nấc có thể là một hoặc vài cảnh):

1. **Mắc kẹt:** nhân vật vận hành theo khuôn mẫu; nhịp nhanh, khung chật, màu lạnh hoặc chói.
2. **Dừng lại:** một khoảnh khắc mọi thứ ngừng; cắt thẳng vào tĩnh lặng.
3. **Nhận biết:** nhân vật thấy điều đang siết mình (thấy vòng, thấy sợi dây); ánh nhìn chuyển vào trong.
4. **Nới ra:** thân thể mềm lại theo hơi thở; mô-típ bắt đầu gỡ.
5. **Nảy mầm:** điều mới mọc lên từ chính chỗ từng bị siết, không phải từ bên ngoài ban cho.
6. **Tái hợp:** trở về đời sống cũ (cảnh gương) với một cách hiện diện khác; kết nối với người khác hoặc với chính mình.

Ánh xạ khi phim nói về một framework của người dùng (luôn xác nhận với người dùng trước khi chốt, không tự suy diễn nội dung framework):

- Framework của người dùng: hỏi cấu trúc lõi và tên gọi từng phần, rồi ánh xạ vào cung sáu nấc hoặc giữ nguyên số bước của framework; nội dung từng phần lấy từ người dùng, không tự viết định nghĩa.

Quy tắc tự sự:

- Không công thức thành công bề ngoài, không so sánh hơn-kém, không framing đua tranh hay "bị bỏ lại".
- Không giảng đạo qua caption; hình tự nói, caption chỉ mở cửa.
- **Chất bất toàn:** trạng thái cuối giữ dấu vết trạng thái đầu (vòng tròn khép nhưng còn chỗ nối, chồi mọc từ vết gãy). Chuyển hoá không xoá quá khứ.
- Kết bằng một câu hỏi mở thực sự, không phải câu hỏi chọn A hay B để kéo tương tác.

### 2.3. Trí tuệ soma và chánh niệm

Thân thể là nơi mang cảm xúc; phim cho thấy trạng thái Tâm-Thể qua tư thế và nhịp, không qua lời.

- **Từ vựng cử chỉ thân:** vai nhô và co, ngực khép, hàm cứng, bàn tay nắm → dừng lại → bàn tay đặt lên ngực, vai hạ, ngực mở, cằm ngẩng, ánh mắt chạm ánh mắt. Mỗi nhân vật có ít nhất hai trạng thái thân rõ rệt, khác nhau đọc được trong 0,3 giây.
- **Nhịp thở nền:** ở cảnh tĩnh, một dao động rất nhẹ (tỉ lệ khung 1-1,5%, độ sáng, độ mở mô-típ) chạy theo chu kỳ khoảng 10 giây (quanh 6 nhịp thở/phút), pha thở ra dài hơn pha hít vào khoảng 1,5 lần. Ở cảnh mắc kẹt, nhịp nông và nhanh (chu kỳ 2-3 giây). Người xem thở theo phim mà không biết.
- **Ngôn ngữ trạng thái**, gợi cảm hứng từ lý thuyết đa phế vị [Polyvagal Theory] của Porges (là heuristic thiết kế, không phải tuyên bố lâm sàng): huy động (nhanh, sắc, tương phản gắt), đóng băng hoặc sụp (tối, chậm, xám, âm trầm thưa), an toàn và kết nối (ấm, mềm, nhịp dài, có sự hiện diện của người khác).
- **Khoảng lặng là chất liệu:** mỗi phim có ít nhất một quãng 2-3 giây gần như im lặng tuyệt đối (chỉ tiếng phòng hoặc tiếng thở) và đóng băng boil. Tổng thời lượng không có caption tối thiểu 30%.
- **Chuông chánh niệm:** tối đa một tiếng trong cả phim, ngân dài từ 6 giây, đặt đúng nấc "nhận biết". Đây là ngoại lệ có chủ ý của luật "tránh ting ting", không được nhân lên.

### 2.4. Hệ khái niệm và ẩn dụ

- Mọi khái niệm cố định của người dùng (thuật ngữ, tên mô hình riêng...) tra `do-hoa-chung/an-du-y-niem.json` trước. Có thì dùng nguyên hình đã chốt; chưa có thì đề xuất một ẩn dụ vẽ được bằng nét 3 px, đánh dấu **ẨN DỤ MỚI - cần duyệt**, ghi vào từ điển ngay sau khi duyệt (cùng schema phim-infomotion, thêm trường `nguon: "hoat-hoa"`).
- Chọn ẩn dụ từ lược đồ hình ảnh [image schema]: chứa đựng, đường đi, cân bằng, trên-dưới, đẩy-kéo, sáng-tối, trung tâm-ngoại vi, vòng lặp, tầng lớp, gốc-ngọn.
- Ẩn dụ phải là **hành động thị giác**, không phải tên cảm xúc: không viết "nhân vật thấy nhẹ lòng", viết "sợi nét quấn ngực nới một vòng theo mỗi lần thở ra, rơi xuống thành đường chân trời".
- **Ngân hàng mô-típ gợi ý** (chọn một làm mô-típ xuyên suốt, tránh dùng lặp giữa các phim gần nhau): sợi nét 3 px (rối → gỡ → thành chân trời), vòng tròn chưa khép, hạt mầm, ngọn đèn, chiếc lá, thuyền giấy, giọt nước lan, cánh cửa. Mô-típ phải qua ít nhất bốn trạng thái theo cung tự sự.

### 2.5. Ngôn ngữ chữ trên hình

- Theo `phong-cach/PHONG-CACH.md` mục 4: thuần Việt, thuật ngữ tiếng Anh trong ngoặc vuông khi thật cần, sentence case, gạch ngang thường, từ ngữ phải viết đúng.
- Caption tối đa khoảng 10-12 từ, không phải cảnh nào cũng có caption. Không cụm sáo, không rule of three cứng, không signposting.
- Credit mặc định: dòng 1 "Thiết kế và tạo bởi <tên người dùng>", dòng 2 chức danh nguyên văn theo `phong-cach/PHONG-CACH.md` mục 1, dòng 3 tuỳ chọn "Cùng trí tuệ nhân tạo Claude của Anthropic". Chữ ký dùng logo của người dùng trong `brand/logo/` (nét đơn sắc) hoặc tên viết từng nét.
