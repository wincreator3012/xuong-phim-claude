# Hình tượng hoá lời nói - nền tảng nghiên cứu và heuristic (phim-infomotion)

Tài liệu này là phần "vì sao" của skill: nghiên cứu nào đứng sau từng quy tắc, heuristic chọn ẩn dụ, và đặc tả component `YNiem`.

## 1. Vì sao lời và hình phải khớp từng nhịp (Mayer, dual coding)

Mười hai nguyên tắc multimedia learning của Richard Mayer, dùng làm trần an toàn cho MỌI quyết định hình:

- **Coherence**: bỏ mọi hình, chữ, âm không phục vụ ý đang nói → hình nào cũng phải khớp đúng ý câu đang nói; nền trơn có ý đồ (ghi `Hình: KHÔNG - <lý do>`) vẫn là lựa chọn hợp lệ.
- **Signaling**: chỉ cần nhấn đúng chỗ (một đường nhấn, một chữ tô đậm) thay vì thêm hình.
- **Redundancy**: không hiện nguyên câu đang đọc thành chữ; chữ trên hình là nhãn ngắn, không phải phụ đề.
- **Temporal contiguity**: hình xuất hiện đúng lúc lời nói tới ý đó, không sớm để "đón", không trễ để "nhắc lại" → mốc từ transcript thật.
- **Segmenting**: chia chương, đổi trạng thái hình theo ranh giới ý.
- **Modality**: lời nói + hình, không phải chữ dày + hình.
- **Personalization / voice**: giọng thật của người dùng là tài sản; không thay bằng giọng máy.

Dual-coding (Paivio; Mayer & Anderson, "Animations Need Narrations"): hình và lời được mã hoá ở hai kênh và củng cố nhau CHỈ khi cùng nói một ý tại cùng một lúc. Nghiên cứu whiteboard animation (hai thí nghiệm với 133 học sinh, 2023): hình vẽ dần chỉ tăng ghi nhớ khi đi cùng tường thuật có mạch chuyện; tách rời thì không. Hệ quả cho skill: kịch bản viết ra cả lời lẫn hình trong cùng một khối, không có bước "chọn hình" riêng rẽ sau khi đã chốt chữ.

## 2. Từ trần mật độ đến phủ kín có ý đồ

Data Player (Shen và cộng sự, IEEE TVCG 2023) tự động ghép animation vào lời thuyết minh bằng LLM và constraint solver; kết quả được đánh giá ngang thiết kế tay, nhưng chính chuyên gia tham gia đánh giá than: "thuật toán tự động có xu hướng nhồi animation vào mọi câu". Xưởng đã gặp đúng lớp lỗi này ở dự án thật và một dự án khác (pill quá dày, che mặt, lệch chủ đề) - nhưng đó là phim CÓ người nói, nơi mỗi lớp đồ họa tranh chỗ với khuôn mặt. Bản đầu của skill vì vậy đặt trần 1 hình / 8-10 giây và 5 giây nền giữa hai hình toàn khung.

Dự án thật đầu tiên (2026-09) cho thấy với infomotion (không có mặt người, màn hình là toàn bộ câu chuyện), nền trơn kéo dài đọc thành "chết hình", và người dùng chỉ đạo: không có chỗ trống nào quá 1 giây trừ khi có ý đồ cụ thể. Từ 2026-09-30 đó là mặc định. Hai lời cảnh báo nghiên cứu vẫn giữ nguyên, chỉ chuyển chỗ đặt ranh giới: không còn đếm số hình, mà kiểm (1) mỗi hình khớp đúng ý câu đang nói [coherence, temporal contiguity], (2) mỗi nhịp một ý và một hình chính, hình nối tiếp liền mạch chứ không chồng lớp, (3) khoảng trống lấp bằng hình có chuyển động riêng từng nhịp, không bằng chữ thuần [redundancy, modality] và không lặp một khuôn. Trần cũ vẫn bật lại được (`uoc-luong.py --khoang-hinh 8`) khi người dùng muốn một video thưa hơn.

Kỹ thuật dùng lại từ Data Player: khớp ngữ nghĩa TRƯỚC, chọn hình SAU (không animate mù); mỗi hình neo vào mốc từ của lời và kéo dài đúng quãng ý đó; ba hành vi cơ bản của hình là xuất hiện, nhấn, rút lui - không cần nhiều hơn.

## 3. Heuristic chọn ẩn dụ (Conceptual Metaphor Theory)

Lakoff & Johnson: tư duy trừu tượng dựa trên các sơ đồ hình ảnh [image schema] có gốc cơ thể. Parsons ("Conceptual Metaphor Theory as a Foundation for Communicative Visualization Design") chuyển sang thiết kế visualization và thừa nhận: lý thuyết chỉ gợi HƯỚNG, không tự cho ra hình - phần dịch thành hình phải tự xây. Đó là việc của từ điển `an-du-y-niem.json`.

Khi gặp khái niệm chưa có trong từ điển, hỏi lần lượt:

| Khái niệm nói về... | Schema | Hình gốc tối giản (nét 3 px) |
|---|---|---|
| bị bao, bị giữ, thuộc về, ranh giới | chứa đựng | vòng/khung và cái bên trong; siết hay nở |
| tiến trình, hành trình, chuyển hoá | đường đi | một đường từ điểm này sang điểm kia, có chỗ rẽ |
| ổn định, nghiêng lệch, điều hoà | cân bằng | thanh ngang trên một điểm tựa |
| nhiều-ít, tốt-xấu, cao-thấp | trên-dưới | mũi/đường đi lên hoặc xuống |
| áp lực, kháng lại, buông | đẩy-kéo | mũi tên đối nhau, dây căng rồi chùng |
| sáng suốt, mờ mịt, tỏ ngộ | sáng-tối | điểm sáng nở ra, màn mờ tan |
| cốt lõi và lớp vỏ, bản chất và biểu hiện | trung tâm-ngoại vi | tâm và các vòng đồng tâm |
| lặp lại, thói quen, chu kỳ | vòng lặp | vòng khép kín, có điểm thoát |
| nền tảng, chồng lớp, mức độ | tầng lớp | các lớp xếp chồng, lớp dưới nâng lớp trên |

Ba phép thử trước khi đề xuất: (1) người xem Việt không cần giải thích vẫn đọc ra được; (2) vẽ được bằng vài nét, không cần hình vẽ minh hoạ phức tạp hay ảnh; (3) không trùng với ẩn dụ đã dùng cho khái niệm khác trong từ điển. Ẩn dụ quen thuộc (hơi thở, dòng sông, tấm gương, hạt-mầm) dễ hợp nhưng cũng dễ lặp: kiểm kỹ phép thử (3).

## 4. Đặc tả component `YNiem` và `YCanh`

Mục đích: một ẩn dụ vẽ nét dần + nhãn khái niệm, hai biến thể: toàn khung (nền brand, dùng như `broll`) và nổi (`alpha`, dùng như `overlay`, mặc định canh giữa `position:'center'`, xem mục 6).

- Props: `slug` (khoá trong bảng `SHAPES` của `studio/src/y-niem/index.ts` - mỗi hình là một mảng `path` SVG trong viewBox 0 0 100 100, vẽ nối tiếp; tuỳ chọn `travelDot` (chấm trôi dọc nét cuối) và `endArrow` (mũi tên ở điểm cuối); slug sẵn có: `duong-giam`, `dinh-roi-bang`, `duong-tang`, `goc-re-sau`), `label`, `sublabel?`, `theme`, `brand`, `drawSeconds` (mặc định 1,2), `labelAt` (giây nhãn xuất hiện, mặc định 2,0), `position?` cho biến thể nổi, `durationInSeconds`.
- Chuyển động: `stroke-dasharray/dashoffset` vẽ nét theo thứ tự đường (hiệu ứng "vẽ dần" - đúng yếu tố có bằng chứng trong nghiên cứu whiteboard), easing bezier(0.22, 1, 0.36, 1), nét 3 px màu `accent`, không spring, không tô màu đặc; nhãn `FadeUp` như các component khác; 18 khung cuối fade nhẹ.
- Đăng ký `YNiem-ngang`/`YNiem-doc` trong `Root.tsx`, defaults với một slug mẫu; `tsc --noEmit` sạch; still cả hai khung có chữ Việt có dấu; commit về máy ngay; ghi vào Bản đồ tài nguyên.
- Mỗi slug mới đi kèm một mục trong `an-du-y-niem.json`; không có slug "mồ côi".
- Thêm hình mới sau khi duyệt: YNiem thì thêm slug vào bảng `SHAPES` của `studio/src/y-niem/index.ts`; YCanh thì viết sub-component rồi đăng ký trong `YCanhVariant`, `VARIANT_LABEL_FRAME`, `VARIANT_LABEL_DURATION`, `yCanhSuggestedSeconds` và nhánh switch của `studio/src/components/YCanh.tsx` (hướng dẫn ở đầu file). Ghi mục từ điển tương ứng, rồi `npx tsc --noEmit`, still cả hai khung, `python3 tools/kiem-tai-lieu.py` (bắt slug, variant mồ côi hai chiều) và commit về máy ngay.
- `YCanh` (`studio/src/components/YCanh.tsx`): mỗi `variant` là một cảnh vẽ tay riêng với kỹ thuật chuyển động riêng, dùng cho chuỗi nhịp kể chuyện để không lặp khuôn. Tám variant đặt tên theo kỹ thuật: `hub-branches` (thân Y ba cụm chấm), `filling-grid` (lưới chấm lấp dần kèm số đếm), `radiant-sun` (mặt trời toả tia), `rising-moon` (trăng nhô lên, trang giấy hiện dòng), `growing-bars` (vạch mọc dần kèm số đếm), `tick-cluster` (chùm tick), `clock-sweep` (đồng hồ hở, kim quét), `growing-flame` (ngọn lửa lớn dần). Số đếm của `filling-grid` (108) và `growing-bars` (1.240) đang cố định trong code. Mốc hiện nhãn từng variant nằm trong `VARIANT_LABEL_FRAME`; thời lượng gợi ý trong `yCanhSuggestedSeconds`.

## 5. Cổng nghiệm thu đúng ý (mở rộng gói chống lỗi ngầm)

"Video as Code: Remotion and the Agent Feedback Gap" (2026): mã chạy được và render không lỗi chỉ chứng minh pipeline chạy, không chứng minh chuyển động đúng ý; máy render, người phán xét; kiểm bằng khung tĩnh ở đúng mốc chuyển đổi rẻ hơn nhiều so với render đầy đủ. Áp vào skill: still mẫu ở cổng 1; ở cổng 2, ngoài `nghiem-thu.py`, trích khung tại mốc mỗi hình (+1 giây) và ghép cặp với câu transcript đang nói - đây là bước đã cứu các dự án thật và một phim tài liệu phỏng vấn khỏi lỗi "render đúng nhưng sai ý".

## 6. Tạo hình đồ họa nổi: kích cỡ, chi tiết, vị trí, nhịp

Rút từ nhiều lượt góp ý trên dự án thật (2026-09-22). Ba trục duyệt độc lập với nhau và độc lập với nhịp, nội dung: đạt trục này không kéo theo trục kia, và lỗi ở ba trục này không lộ qua cổng máy.

1. **Kích cỡ.** Toàn khung là canvas: đồ họa nổi không cần né người nói (thể loại này không có người), đừng chọn cỡ dè dặt. Nhắm khoảng `unit*55-60` cho icon, `unit*6.0` cho nhãn chữ, `unit*3.9` cho phụ đề. Luôn kiểm bằng một khung trích từ bản render ở đúng tỉ lệ khung đích, không tin hằng số `unit*n` trên giấy và không tin still riêng lẻ.
2. **Độ giàu chi tiết.** Phóng to mà không làm giàu thì một nét đơn, một tick đơn trông thưa và thô. Mỗi hình cần khoảng 5-10 chi tiết chuyển động: cụm chấm nhiều màu, lưới điểm, nhiều vạch xen đậm nhạt, tick nhỏ bung quanh tick lớn, khoảng 10 dòng thay cho một dòng, số đếm dồn chạy song song. Cụm chấm cần phân biệt nhóm dùng ba tông phụ `#2F5D50` (xanh rêu), `#B0663F` (đất nung), `#B98A2E` (vàng đất) (hoặc ba tông phụ hợp bảng màu của người dùng trong `brand/brand.json`); giữ họ giấy mực, không dùng màu rực.
3. **Vị trí.** Mặc định canh giữa cả hai trục (`position:'center'`, là default của component từ 2026-09-30) để cân khoảng trống trên dưới; chỉ neo một cạnh khi có lý do cụ thể. Khi dựng clip, hỏi người dùng có muốn điều chỉnh không.
4. **Mỗi nhịp một kỹ thuật chuyển động.** Không lặp một khuôn "vẽ nét rồi hiện chữ" cho mọi nhịp; chung một họ easing và màu, khác kỹ thuật. Lấp khoảng trống bằng hình, không bằng chữ thuần.
5. **Làm chậm trong ô thời lượng đã khoá.** Khi được yêu cầu "chậm lại" cho nhiều cảnh nằm trong các ô `durationInSeconds` đã khoá (để giữ lịch nối liền), không áp một hệ số chung. Mỗi ô dành khoảng 10 khung đầu cho hiện dần và 14 khung cuối cho mờ dần; tính `ngân sách = durationInFrames - 14 - vài khung đệm` riêng từng cảnh rồi phân bổ mức chậm theo ngân sách đó. Ô rộng chậm được gần gấp đôi; ô eo hẹp chỉ chậm một phần và có thể phải rút thời lượng hiện chữ (`FadeUp duration`) xuống 14-20 khung (bảng `VARIANT_LABEL_DURATION`). Không đổi `durationInSeconds`/`at` của ô bên ngoài. Nhãn chữ chỉ hiện SAU khi phần hình chính vẽ xong (mốc trong `VARIANT_LABEL_FRAME` của YCanh), không đè lên lúc chấm hay nét còn đang bung; làm giàu chi tiết thì tính lại mốc này.
6. **Thiết kế lại thay vì vá.** Ẩn dụ bị chê "hơi kỳ", hoặc hai chi tiết chồng nhau: thiết kế lại cả khối hình (đổi hẳn kỹ thuật), không chỉnh toạ độ lẻ tẻ. Chồng lấn do cùng vùng không gian VÀ cùng lúc thì tách cả hai trục: vùng toạ độ riêng và mốc thời gian nối tiếp (phần tử sau chỉ bắt đầu khi phần tử trước đã vẽ xong). Hình lớn dần thì phóng quanh điểm neo đáy (`translate(px,py) scale(s) translate(-px,-py)`); cảnh dài thì có chuyển động sống liên tục (lung linh bằng `Math.sin`) sau khi vẽ xong để không "đứng hình".
7. **Tổng quát hoá khi có trường hợp thứ hai.** Hiệu ứng riêng của một slug làm thành nhánh riêng trước; chỉ khi slug thứ hai cần mới tách thành trường chung (như `travelDot`, `endArrow` của `YNiemShape`).

## 7. Nguồn

- Mayer, R. E., Multimedia Learning (các nguyên tắc coherence, signaling, redundancy, contiguity, segmenting, modality, personalization); Mayer & Anderson, "Animations Need Narrations: An Experimental Test of a Dual-Coding Hypothesis".
- Paivio, A., Dual Coding Theory.
- Lakoff, G. & Johnson, M., Metaphors We Live By; Parsons, P., "Conceptual Metaphor Theory as a Foundation for Communicative Visualization Design" (VisComm 2018).
- Shen, L. và cộng sự, "Data Player: Automatic Generation of Data Videos with Narration-Animation Interplay", IEEE TVCG 2023 (arXiv:2308.04703).
- "Paper2Video: Automatic Video Generation from Scientific Papers" (arXiv:2510.05096, 2025) - tách lớp trình bày/giọng/đồng bộ, định thời theo từ bằng forced alignment.
- "Successful learning with whiteboard animations - a question of their procedural character or narrative embedding?" (2023, PMC9898452).
- "Video as Code: Remotion and the Agent Feedback Gap" (Digital Applied, 2026).
- Quy trình sản xuất Kurzgesagt (tổng hợp 10.studio): thư viện tài sản module hoá, ẩn dụ hình ảnh, phong cách nhất quán ở quy mô lớn.
