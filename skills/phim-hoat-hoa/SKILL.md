---
name: "phim-hoat-hoa"
description: "Hình tượng hoá lời nói và câu chuyện thành phim hoạt hình vẽ bằng code theo phong cách của người dùng. Hai lối vào: TỪ GIỌNG NÓI (file voice của người dùng: gỡ băng, hiểu nội dung, hình tượng hoá từng nhịp ý thành cảnh hoạt hình có nhân vật, mô-típ, ẩn dụ, dựng khớp voice gốc) và TỪ HẠT TRUYỆN. Hai nhánh Canvas HTML và Remotion; hai chế độ SOẠN LỆNH và DỰNG. Kích hoạt khi user nói 'phim hoạt hình', 'hoạt hoạ', 'animation', 'hoạt hình từ file voice', 'hoạt hình hoá bài nói', 'clip kiểu phim Nhà', 'phim vẽ bằng code', 'mega prompt làm phim', hoặc thả file ghi âm kèm ý muốn có nhân vật, cảnh, câu chuyện bằng hình vẽ động. Voice mà muốn đồ họa thông tin tối giản thì dùng phim-infomotion. KHÔNG dùng cho đồ họa lẻ (phim-do-hoa) hay footage thật (phim-dung-bai, phim-clip-ngan)."
---

# Phim hoạt hình vẽ bằng code: từ lời nói và câu chuyện

Mục tiêu: biến lời người dùng nói (bài giảng, chiêm nghiệm, trình bày framework, kể chuyện) và những câu chuyện người dùng muốn kể thành phim hoạt hình vẽ hoàn toàn bằng code, hiểu đúng nội dung, hình tượng hoá có chiều sâu, khớp chặt với giọng thật, mang dấu ấn riêng của người dùng; đồng thời soạn được bộ lệnh [mega prompt] để người dùng sử dụng lại, chia sẻ hoặc dạy người khác làm.

Hai lối vào:

- **Lối vào 1 - Từ giọng nói (lối chính).** Nguồn là file voice của người dùng (vài chục giây tới 15 phút, dài hơn thì chia chương). Giọng là xương sống: hình sinh ra từ ý của lời, thời gian bám theo lời. Phần 3 là trọng tâm.
- **Lối vào 2 - Từ hạt truyện.** Không có voice; một câu chuyện, một chiêm nghiệm, một framework thành phim 45-120 giây có nhạc, caption, không lời (hoặc lời đọc thu sau).

Quan hệ với phim-infomotion: dùng chung pipeline gỡ băng, cách chia nhịp ý và từ điển ẩn dụ `an-du-y-niem.json`. Khác ở ngôn ngữ hình: infomotion là đồ họa thông tin tối giản trên nền phẳng; skill này dựng một **thế giới hoạt hình** có không gian, nhân vật, mô-típ, ánh sáng, chuyển cảnh, mọi nhịp (kể cả nhịp liệt kê framework) đều được vẽ trong thế giới đó. Người dùng thả file voice mà chưa nói rõ thì hỏi một câu: "hoạt hình có nhân vật và cảnh" hay "đồ họa thông tin tối giản". Một dự án có thể lai: vài nhịp cần độ chính xác cao mượn component của infomotion, nhưng vẽ lại cùng chất giấy và nét.

**Nguồn phương pháp:** kế thừa và khái quát hoá từ bộ lệnh phim "Nhà" của Đặng Hữu Sơn (70 giây, 20 cảnh, Canvas 2D cùng Claude). Khi công bố bộ lệnh hoặc phim làm theo phương pháp này, ghi nhận nguồn đó. Phần phong cách mặc định (tự sự chuyển hoá, chánh niệm, soma) là lớp tích hợp của tác giả gốc của xưởng (xem README); người dùng có phong cách riêng trong `phong-cach/PHONG-CACH.md` thì phong cách đó đi trước, chưa rõ thì hỏi.

Đọc trước khi dựng trong xưởng: `skills/_chung/van-hanh.md`, `skills/_chung/timeline-va-dung.md`, `skills/_chung/nghiem-thu-dung-y.md`, `skills/phim-do-hoa/SKILL.md` (thêm component), `do-hoa-chung/an-du-y-niem.json`, `thu-vien/AM-THANH.md`. Tài liệu tra cứu của skill (giữ số "Phần" như cũ để tham chiếu chéo không đổi):

| Phần | File trong `skills/phim-hoat-hoa/references/` | Đọc khi |
|---|---|---|
| 1-2. Mười hai nguyên lý bộ lệnh; lớp phong cách mặc định (ngôn ngữ hình, cung chuyển hoá, soma, ẩn dụ, chữ) | `nguyen-ly-va-phong-cach.md` | viết kịch bản, kinh thánh thế giới, bản tự sự, bộ lệnh |
| 4. Chuyển cảnh, âm thanh, caption, mật độ, danh mục cấm | `chuyen-canh-am-thanh-caption.md` | viết bảng cảnh, làm âm thanh, caption |
| 5. Hai nhánh kỹ thuật: Canvas HTML và Remotion | `nhanh-ky-thuat.md` | chọn nhánh và bắt đầu dựng |
| 7. Mẫu bộ lệnh | `mau-bo-lenh.md` | chế độ SOẠN LỆNH |
| 8. Checklist bộ lệnh và phim | `checklist.md` | sau mỗi chặng và trước khi báo xong |

---

## Tóm tắt Phần 1-2: nguyên lý và phong cách

Bản đầy đủ ở `nguyen-ly-va-phong-cach.md`. Những điều phải giữ ở mọi phim:

- **Đặc tả bằng dữ liệu, không bằng tính từ** (hex, px, giây, BPM, LUFS). **Tất định**: `render(t)` thuần theo thời gian, PRNG có seed, cấm `Math.random()` trong vòng render. **Nhịp là dữ liệu**: bảng cue, hệ số `k`, âm thanh và caption neo theo cảnh. **Quy trình theo chặng, buộc dừng**; **bộ nhớ lỗi** là checklist Phần 8. Tách hằng số khỏi biến số.
- **Một mô-típ biến đổi xuyên suốt** (qua ít nhất bốn trạng thái), **cấu trúc gương** cảnh mở và cảnh kết, **hình đọc được trong 0,3 giây**, bảng màu đóng, 4-5 kiểu chuyển cảnh mang nghĩa.
- **Phong cách mặc định** khác phim "Nhà": cung mắc kẹt → dừng lại → nhận biết → nới ra → nảy mầm → tái hợp (không công thức thành công bề ngoài, không so sánh hơn kém); 8-12 cảnh cho 60-90 giây, có khoảng tĩnh; easing bezier(0.22, 1, 0.36, 1), không nảy; giấy ngà sạch; thân thể mang cảm xúc; kết bằng hình gương, câu hỏi mở thực sự, chữ ký của người dùng; trạng thái cuối giữ dấu vết trạng thái đầu.
- **Soma và chánh niệm**: mỗi nhân vật có ít nhất hai trạng thái thân đọc được trong 0,3 giây; nhịp thở nền ở cảnh tĩnh (chu kỳ khoảng 10 giây, thở ra dài hơn); ít nhất một quãng 2-3 giây gần như im lặng; tối đa một tiếng chuông chánh niệm.
- **Ẩn dụ là hành động thị giác**, không phải tên cảm xúc; tra từ điển trước, ẩn dụ mới đánh dấu "ẨN DỤ MỚI - cần duyệt", ghi vào từ điển ngay sau khi duyệt với `nguon: "hoat-hoa"`.
- Framework của người dùng (mô hình, các bước có tên riêng...): luôn xác nhận cấu trúc với người dùng, không tự suy diễn nội dung.
- Bảng màu mở rộng cho hoạt hình (chàm đêm, hồng phai, xám sương cộng bảng brand) chỉ thành mặc định sau khi người dùng duyệt ở style frame phim đầu tiên; không tự sửa `brand.json`.
- Chữ trên hình và credit theo `phong-cach/PHONG-CACH.md`; caption tối đa khoảng 10-12 từ, không phải cảnh nào cũng có.

---

## Phần 3. Hình tượng hoá lời nói (lối vào 1)

Lời nói có cấu trúc riêng mà phim không được phá: mạch lập luận, chỗ nhấn, chỗ ngập ngừng, câu chuyện minh hoạ, câu hỏi để ngỏ. Việc của skill là đọc như một đạo diễn phim hoạt hình đọc kịch bản thoại: hiểu người dùng đang nói gì, vì sao nói vậy, người nghe cần thấy gì để hiểu và cảm, rồi mới nghĩ ra hình.

### 3.1. Đọc hiểu trước khi vẽ

Đọc trọn transcript ít nhất hai lượt trước khi đề xuất bất kỳ hình nào:

1. **Lượt nghĩa:** tóm thông điệp lõi của cả bài trong một câu; vẽ bản đồ lập luận (luận điểm → luận cứ → ví dụ → hệ quả); đánh dấu khái niệm cố định của người dùng; đánh dấu các câu chuyện, giai thoại, ví dụ về người thật hoặc tình huống.
2. **Lượt cảm:** cung cảm xúc của bài (hành trình chuyển hoá, giải thích một cấu trúc, hay lời mời chiêm nghiệm); câu "đắt" nhất; chỗ giọng người dùng chậm lại, hạ giọng, dừng lâu (đọc cả khoảng lặng trong `silences.json`: khoảng lặng của người nói là chỗ phim cũng nên lặng).
3. **Tìm ẩn dụ gốc của bài:** hầu hết bài nói có một hình ảnh trung tâm. Chọn nó làm **mô-típ xuyên suốt**, cho nó biến đổi theo mạch bài. Không áp cung sáu nấc lên bài không có cấu trúc chuyển hoá; khi đó bám cấu trúc của chính bài (các bước framework, các lớp khái niệm, các câu hỏi).

Nguyên tắc chính xác: hình không được nói điều người dùng không nói. Không thêm số liệu, không thêm ví dụ, không đổi thứ tự bước, không gán cảm xúc trái giọng. Câu nào mơ hồ về nghĩa thì hỏi người dùng, không đoán rồi vẽ.

### 3.2. Chia nhịp ý và chọn cách xử lý hoạt hình

Chia transcript thành nhịp ý [semantic beat] theo ranh giới ý, không theo ranh giới câu (thường 6-25 giây một nhịp); mốc thật lấy từ transcript, nội suy trong câu theo tỉ lệ ký tự, hút về khoảng lặng gần nhất (như phim-infomotion). Gắn mỗi nhịp một loại và một cách xử lý trong thế giới hoạt hình:

| Loại nhịp | Dấu hiệu trong lời | Cách xử lý hoạt hình |
|---|---|---|
| Câu chuyện, giai thoại, ví dụ về người | "có một chị...", "hồi đó tôi...", tình huống cụ thể | **Cảnh diễn:** nhân vật hành động theo đúng diễn biến lời kể, cảnh đổi theo từng nút truyện; chỗ đáng đầu tư chi tiết nhất |
| Khái niệm trừu tượng | buông bỏ, gắn kết, hiện diện... | **Cảnh ẩn dụ:** mô-típ hoặc ẩn dụ từ từ điển biến đổi trong không gian cảnh; nhân vật tương tác với ẩn dụ |
| Framework, các bước, các thành phần | "thứ nhất... thứ hai...", tên framework, liệt kê | **Cảnh cấu trúc vẽ tay:** các thành phần hiện thành vật thể trong thế giới (bậc đá, các trạm trên đường, các vòng quanh một tâm), vẽ nét 3 px từng phần đúng lúc người dùng gọi tên; nhãn ngắn viết tay bằng Lora; kết nhịp có một khung tổng hiện đủ các phần |
| Số liệu, so sánh | con số, hơn kém, tỉ lệ | **Hình đếm vẽ tay:** nhóm vật thể đếm được (hạt, người, ô cửa sổ sáng dần), không biểu đồ văn phòng |
| Lập luận, nhân quả | "vì...", "nên...", "khi... thì..." | **Cảnh chuyển trạng thái:** cùng một không gian biến đổi từ nguyên nhân sang hệ quả, không cắt sang cảnh mới |
| Câu nhấn, cảm xúc, câu hỏi để ngỏ | câu chậm, giọng hạ, câu hỏi | **Khoảng thở:** cảnh tĩnh, nhịp thở nền, caption cụm nhấn nếu là câu đắt nhất; câu hỏi kết để khung gần trống |
| Chuyển ý, dẫn nhập | "bây giờ mình nói sang...", "vậy thì..." | **Chuyển cảnh** (từ vựng ở Phần 4.1), có thể kèm tên chương viết tay |

Nhịp chứa câu nói trực tiếp về trải nghiệm thân thể ("thở", "vai nặng", "ngực thắt") luôn dùng từ vựng cử chỉ thân cho nhân vật, đúng khoảnh khắc lời nói đến đó.

### 3.3. Dựng thế giới cho clip dài

Một bài nói 10 phút không thể vẽ 150 cảnh riêng mà vẫn đẹp và nhất quán. Cách làm là dựng một **thế giới** rồi tái dùng có chủ đích:

- **Kinh thánh thế giới [world bible]** (một trang, duyệt cùng Cổng 1): bảng màu, chất giấy, 2-4 bối cảnh chính, 1-3 nhân vật với các trạng thái thân, mô-típ và các trạng thái, điểm neo thị giác, bộ chuyển cảnh.
- **Bộ cảnh có tham số:** mỗi bối cảnh là một hàm vẽ nhận tham số (giờ trong ngày, thời tiết, vị trí máy, tư thế nhân vật, trạng thái mô-típ).
- **Nhân vật đại diện người nghe hoặc người kể:** tối giản; không vẽ chân dung người dùng trừ khi người dùng yêu cầu. Nhân vật không nhép miệng; lời là giọng kể ngoài hình [voice-over].
- **Chương:** bài dài hơn 5 phút chia chương theo mạch lập luận; chuyển chương bằng một chuyển cảnh lớn kèm tên chương viết tay.
- **Mật độ:** mặc định an toàn là tối đa một ý hình mới mỗi 8-12 giây lời; giữa các ý hình mới, cảnh vẫn "sống" bằng chuyển động nhỏ (nhịp thở nền, mây trôi, ánh sáng đổi chậm, mô-típ lay động), không bao giờ đứng hình chết. Quãng giải thích dài quá 25 giây chưa có hình mới thì thêm một biến đổi nhỏ của cảnh (đổi góc máy, đổi ánh sáng). Dự án người dùng muốn dày hơn thì theo chỉ đạo, ghi trong kịch bản.

### 3.4. Đồng bộ với giọng

- Giọng là trục thời gian duy nhất. Bảng cảnh dùng mốc thật của lời, không cộng dồn thời lượng danh nghĩa; hệ số `k` chỉ chỉnh nhịp chuyển động bên trong một cảnh đã khoá mốc.
- Hình của một ý bắt đầu hiện khoảng 0,2-0,5 giây trước từ khoá; thành phần framework vẽ đúng lúc người dùng gọi tên.
- Chuyển cảnh đặt vào khoảng lặng giữa hai ý, không cắt giữa câu.
- Nhạc nằm dưới giọng 15-18 dB, tự hạ khi có lời (cách làm theo nhánh: Phần 4.2); SFX thưa, đặt vào khoảng lặng, không đè từ khoá; một số nhịp để giọng đứng một mình không nhạc.
- Caption khi có voice: không chép lại lời, chỉ hiện cụm nhấn (tên khái niệm, tên thành phần framework, câu đắt nhất). Bản dọc có thể thêm phụ đề đầy đủ ở dải dưới theo quy ước xưởng, tách lớp khỏi caption nghệ thuật.

---

## Chọn nhánh kỹ thuật (Phần 5)

- **Nhánh A - Canvas HTML tự chứa**: làm nhanh một phim độc lập, chia sẻ bộ lệnh cho người khác dán vào claude.ai, dạy trong khoá học, hoặc cần một file HTML xem trực tiếp. File ở `du-an/<tên>/canvas/index.html`, MP4 xuất ra `du-an/<tên>/nguon/` để đi tiếp qua `assemble.py` nếu cần outro hoặc nhạc thư viện.
- **Nhánh B - Remotion trong xưởng** (mặc định khi phim thuộc một dự án của xưởng): cần bản ngang lẫn dọc, tái dùng brand, từ điển, thư viện âm thanh, intro, outro, cổng nghiệm thu. Component ở `studio/src/hoat-hoa/<slug>/`, composition `HoatHoa-<slug>-ngang`/`-doc`; bảng cảnh `du-an/<tên>/BANG-CANH.json` là nguồn chân lý duy nhất cho thời lượng. Có voice thì làm nền như infomotion (`nguon/nen-<khung>.mp4`), phim render câm, toàn khung, theo chương, ghép bằng `broll` trên segment cắt từ nền, nên hình và tiếng không thể trôi nhau.

Đặc tả đầy đủ (bộ vẽ, tất định, hiệu năng, xuất MP4 bằng Playwright, ánh xạ nguyên lý sang Remotion): `nhanh-ky-thuat.md`. Clip 10 phút ở 30 fps là 18.000 khung: ưu tiên SVG nhẹ, cache lớp nặng, render nháp 720p để duyệt nhịp trước khi render 1080p.

---

## Phần 6. Quy trình

### Chế độ SOẠN LỆNH

Khi người dùng muốn một bộ lệnh để tự dán vào claude.ai, chia sẻ, hoặc dạy lại.

1. Hỏi một lượt (Bước 1 của lối vào tương ứng), làm các bước bản chữ (bản tự sự hoặc kịch bản hình tượng hoá, rồi bảng cảnh).
2. Soạn bộ lệnh theo `mau-bo-lenh.md`, điền đủ biến số; phần hằng số giữ nguyên. Lối vào 1: dùng biến thể [2B] và dặn người dùng đính kèm file voice cùng transcript có mốc thời gian.
3. Tự soát bằng `checklist.md` mục "Bộ lệnh".
4. Giao file `BO-LENH-<slug>.md` (trong xưởng: `du-an/<tên>/`). Kèm lệnh phụ nếu người dùng cần: bản dọc 9:16, bản vuông trình diễn bộ lệnh (nửa trên phim, nửa dưới chữ bộ lệnh chạy lên), bài đăng giới thiệu (theo quy ước ngôn ngữ của người dùng, kết bằng câu hỏi mở, không hook viết hoa kiểu con số giật gân).

### Chế độ DỰNG - lối vào 1: từ giọng nói

**Bước 1. Nhận file voice, hỏi một lượt.** Tối đa bốn câu, chỉ hỏi điều chưa rõ: (1) clip cho ai xem, đăng ở đâu, khung ngang, dọc hay cả hai; (2) hoạt hình có nhân vật và cảnh (skill này) hay đồ họa thông tin tối giản (chuyển phim-infomotion); (3) theme, tên chủ đề hoặc framework, thuật ngữ nào là cố định; (4) câu chuyện hay nhân vật nào người dùng muốn giữ đúng (người thật cần đổi tên, bối cảnh cụ thể). Không có trả lời thì mặc định: nhánh B, ngang, light, không vẽ chân dung người dùng, ghi rõ là giả định.

**Bước 2. Tạo nền, gỡ băng.** Nhánh B như infomotion (nền + gỡ băng trên nền) hoặc xuất transcript có mốc cho nhánh A. Nghiệm thu transcript trước khi đọc.

**Bước 3. Đọc hiểu, chia nhịp.** Làm đủ Phần 3.1 và 3.2; tra từ điển ẩn dụ cho mọi khái niệm cố định.

**Bước 4. Kịch bản hình tượng hoá và kinh thánh thế giới (Cổng duyệt 1).** File `KICH-BAN-HOAT-HOA.md`:
- Đầu file: thông điệp lõi một câu, khung, theme, tổng thời lượng, số chương, số nhịp.
- Kinh thánh thế giới (Phần 3.3).
- Mỗi nhịp một khối: mốc thật, lời nói nguyên văn (rút gọn nếu dài), loại nhịp, cách xử lý, mô tả hình bằng hành động thị giác cụ thể, trạng thái thân, trạng thái mô-típ, ẩn dụ (ĐÃ CÓ / ẨN DỤ MỚI), caption cụm nhấn nếu có, ghi chú âm thanh.
- Cuối file: ẩn dụ mới chờ duyệt, các nhịp chỉ là khoảng thở và lý do, kiểm mật độ (số ý hình mới mỗi phút), chỗ nghĩa mơ hồ cần người dùng xác nhận.
Tiêu chí đạt: người dùng đọc 10-15 phút là hình dung được clip; không nhịp nào nói điều người dùng không nói; mọi ẩn dụ mới được đánh dấu. Người dùng góp ý trên chữ, sửa tới khi duyệt; ghi ẩn dụ mới vào từ điển ngay sau khi duyệt.

**Bước 5. Style frame (Cổng duyệt 2).** Render ba still: một cảnh của bối cảnh chính, một cảnh diễn có nhân vật, một cảnh cấu trúc framework vẽ tay (nếu bài có). Người dùng duyệt thế giới trên ba still này trước khi dựng hàng loạt.

**Bước 6. Dựng theo chương.** Chương đầu làm trọn (hình + ghép voice + nhạc) thành nháp 720p để người dùng duyệt nhịp và cảm giác; đạt rồi mới dựng các chương sau. Mỗi chương: contact sheet mỗi nhịp một khung tại mốc từ khoá + 1 giây, tự soát theo checklist, sửa rồi mới đi tiếp. Ẩn dụ bị chê sai cảm giác thì thiết kế lại cả khối hình, không vá toạ độ lẻ.

**Bước 7. Nghiệm thu hai lớp, giao nháp (Cổng duyệt 3).** Lớp máy: `nghiem-thu.py video`. Lớp đúng ý theo `_chung/nghiem-thu-dung-y.md`: với mỗi nhịp, cặp "hình - câu đang nói" tại mốc từ khoá + 1 giây (tính từ `map.json`); hình không khớp ý câu là lỗi dù đẹp; thành phần framework phải hiện đúng lúc được gọi tên. Góp ý ghi `SO-GOP-Y.md`.

**Bước 8. Bàn giao và học.** Như Bước 7 của lối vào 2; thêm: lưu kinh thánh thế giới và các hàm bối cảnh có tham số vào `do-hoa-chung/the-gioi-hoat-hoa/<slug>/` để các clip sau của cùng chuỗi dùng lại.

### Chế độ DỰNG - lối vào 2: từ hạt truyện

**Bước 1. Nhận hạt truyện, hỏi một lượt.** Tối đa bốn câu: (1) phim cho ai xem, đăng ở đâu, dài bao nhiêu; (2) nhánh A hay B, khung ngang, dọc hay cả hai; (3) theme và phim có gắn một framework hay khái niệm cố định nào không; (4) có thu thêm lời đọc thật của người dùng không (có thì chuyển sang lối vào 1 sau khi thu). Không có trả lời thì mặc định: nhánh B, ngang, light, 75 giây, không lời, ghi rõ là giả định.

**Bước 2. Bản tự sự một trang (Cổng duyệt 1).** Thông điệp lõi một câu; nhân vật và trạng thái thân đầu cuối; mô-típ và bốn trạng thái trở lên; cung tự sự theo sáu nấc (hoặc theo cấu trúc framework); cặp cảnh gương; câu hỏi mở kết phim. Người dùng duyệt trên chữ trước khi đi tiếp.

**Bước 3. Bảng cảnh (Cổng duyệt 2).** Mỗi cảnh một dòng: `#`, `scene`, `dur`, `k`, `chuyển cảnh`, `nội dung hình`, `thân`, `nhịp thở`, `âm thanh`, `caption` (hoặc "không chữ"), `ẩn dụ` (ĐÃ CÓ / ẨN DỤ MỚI). Cuối bảng: tổng thời lượng, số cảnh, tỉ lệ không caption, vị trí khoảng lặng, ẩn dụ mới chờ duyệt. Tra từ điển trước khi viết cột ẩn dụ.

**Bước 4. Style frame.** Hai still: cảnh mở và cảnh bước ngoặt. Người dùng duyệt bảng màu, nét, nhân vật. Phim đầu tiên dùng bảng màu mở rộng thì chốt bảng màu tại đây.

**Bước 5. Dựng theo chặng.** Không dựng một phát cả phim:
1. Engine + chất giấy + cảnh mở → dừng, soát.
2. Nhân vật + mô-típ + chuỗi mắc kẹt.
3. Dừng lại + nhận biết + nới ra.
4. Nảy mầm + tái hợp + cảnh gương + chữ ký, credit.
5. Âm thanh + caption → xuất bản nháp.

Sau mỗi chặng: contact sheet (2 khung mỗi cảnh, ghép một lưới), tự soát bằng Read theo checklist, sửa rồi mới đi tiếp.

**Bước 6. Nghiệm thu, giao nháp (Cổng duyệt 3).** Lớp máy: `nghiem-thu.py video`; cảnh báo "hình đứng" ở khoảng lặng là đúng thiết kế nếu trùng bảng cảnh. Lớp mắt: trích khung giữa mỗi cảnh, đối chiếu cột nội dung và caption, chữ Việt đủ dấu, không placeholder. Góp ý ghi `SO-GOP-Y.md`; góp ý cùng kiểu lần thứ hai thì sửa mặc định trong skill, component hoặc checklist.

**Bước 7. Bàn giao và học.** Bản đạt sang `xuat-hoan-chinh/`. Ghi ẩn dụ mới vào từ điển; lỗi mới gặp thêm vào `checklist.md`; kỹ thuật mới vào `docs/BAI-HOC.md` (mở chủ đề "Hoạt hình tự sự" ở phim đầu tiên). Đề xuất bản dọc hoặc bộ lệnh chia sẻ nếu hợp.

---

## Quy tắc cứng

- Không dựng khung hình nào trước Cổng 1 và Cổng 2; still style frame được phép (Bước 4 lối vào 2, Bước 5 lối vào 1).
- Clip có voice: đọc hiểu trọn bài trước khi đề xuất hình; giọng là trục thời gian duy nhất; hình không nói điều người dùng không nói; chỗ nghĩa mơ hồ thì hỏi.
- Tra từ điển ẩn dụ trước khi sáng tạo; ẩn dụ mới luôn đánh dấu và ghi vào từ điển ngay sau khi duyệt.
- Không tự suy diễn nội dung framework của người dùng; hỏi hoặc lấy từ nguồn người dùng chỉ định.
- Không sửa `brand.json` mà chưa hỏi; bảng màu mở rộng chỉ thành mặc định sau khi người dùng duyệt.
- Hình vẽ bằng code; không dùng ảnh hay hình do AI tạo. Giọng tổng hợp chỉ khi người dùng yêu cầu.
- Nghiệm thu máy và soát bằng mắt là bắt buộc trước khi báo "xong".
- Ghi nhận bộ lệnh phim "Nhà" của Đặng Hữu Sơn là nguồn phương pháp khi công bố.

<!-- ban-nguon: phim-hoat-hoa 2026-09-30 9a70b073 -->
