---
name: phim-infomotion
description: Làm video hoàn toàn bằng đồ hoạ động [motion graphics] khớp chặt với một bản ghi âm trình bày (thường 3-15 phút, một framework hay một ý niệm trừu tượng) - không có cảnh quay để cắt, hình phải được nghĩ ra từ lời nói. Kích hoạt khi user nói "infomotion", "làm video từ audio", "video hoạt hình giải thích", "explainer video", "video hoá bài giảng không quay hình", "dựng video chỉ từ file ghi âm", hoặc đưa một file âm thanh trình bày (không kèm video quay mặt) vào yêu cầu dựng. KHÔNG dùng khi đã có video quay mặt (phim-dung-bai) hay có slide làm nền (phim-bai-giang-slide) - hai skill đó xử lý lớp hình đã có sẵn, còn skill này tạo lớp hình từ đầu.
---

# Infomotion: từ giọng nói ra hình tượng hoá

Mục tiêu: từ một bản ghi âm trình bày (thường 3-15 phút, một framework hay một ý niệm), làm ra một video hoàn toàn bằng đồ hoạ động khớp chặt với voiceover gốc, chính xác về nội dung, dễ hiểu, hấp dẫn, và mang đúng đặc trưng hình ảnh của người dùng. Khác mọi skill khác trong xưởng: KHÔNG có cảnh quay để cắt, hình phải được nghĩ ra từ lời nói.

Ba nguyên tắc xuyên suốt:

1. **Duyệt trên giấy trước, render sau.** Kịch bản hình tượng hoá viết bằng chữ là cổng duyệt 1. Không render khung hình nào trước khi người dùng duyệt, trừ một khung tĩnh mẫu [style frame] cho loại hình lần đầu xuất hiện trong dự án. Lý do: sai ẩn dụ hay sai cấu trúc là lỗi tốn kém nhất, phải chặn khi còn rẻ.
2. **Tra từ điển trước, sáng tạo sau.** Mọi khái niệm cố định của người dùng (tên framework, thuật ngữ riêng, các bước có tên...) tra `do-hoa-chung/an-du-y-niem.json` trước; có thì dùng nguyên hình đã chốt; chưa có thì đề xuất và đánh dấu rõ "ẨN DỤ MỚI" để người dùng duyệt, rồi ghi ngay vào từ điển sau khi duyệt. Nhờ vậy hình nhất quán qua mọi video của cùng một người dùng, và chi phí sáng tạo giảm dần qua từng dự án. File từ điển CHƯA TỒN TẠI ở dự án infomotion đầu tiên của một người dùng - tạo mới dạng `{}` ngay khi có ẩn dụ đầu tiên được duyệt, không phải trước đó.
3. **Không phải câu nào cũng cần hình.** Trần mật độ: tối đa một hình mới mỗi 8-10 giây lời nói; nhịp "không cần hình" là lựa chọn hợp lệ, không phải thiếu sót. Thuật toán tự động có xu hướng nhồi animation vào mọi câu - đây là lỗi thật, không phải lý thuyết, và trùng lớp lỗi "quá tải overlay" xưởng từng gặp ở các skill khác.

Đọc trước: `docs/QUY-TRINH-KY-THUAT.md` ở gốc xưởng (môi trường, cổng nghiệm thu, hai hệ mốc thời gian), `skills/phim-do-hoa/SKILL.md` (ngôn ngữ thiết kế, cách render, cách thêm component mới), `phong-cach/PHONG-CACH.md` (chức danh nguyên văn, từ ngữ phải viết đúng, quy tắc chữ trên màn hình).

## Cấu trúc dự án

```
du-an/<tên>/
  nguon/voice.wav              giọng ghi âm gốc (chuẩn hoá 48 kHz; giữ file gốc cạnh đó)
  nguon/nen-<ngang|doc>.mp4    NỀN: video màu giấy brand có sẵn tiếng voice (Bước 2) - đây là "clip nguồn"
  transcript/                  transcript tạo từ nen-*.mp4 (một trục thời gian duy nhất, theo skill phim-transcript)
  KICH-BAN-INFOMOTION.md       kịch bản hình tượng hoá bằng chữ (Cổng duyệt 1)
  do-hoa/<ngang|doc>/ + do-hoa/job/   đồ hoạ render + job JSON gốc (giữ tới khi giao)
  timeline.json, SO-GOP-Y.md, xuat-nhap/, xuat-hoan-chinh/   như mọi dự án khác trong xưởng
do-hoa-chung/an-du-y-niem.json  TỪ ĐIỂN ẨN DỤ dùng chung mọi dự án của người dùng (không nằm trong du-an/)
```

## Hai thành phần đồ hoạ dành riêng cho infomotion

Hai component Remotion `YNiem` và `YCanh` (trong `studio/src/components/`) là công cụ chính của skill này - không dùng ở skill nào khác trong xưởng vì chỉ infomotion mới cần "vẽ ra một ý niệm trừu tượng từ số không".

- **`YNiem`** - MỘT hình vẽ nét dần cho MỘT khái niệm đơn lẻ, dùng khuôn chung "vẽ nét rồi hiện nhãn chữ". Hình lấy từ kho `studio/src/y-niem/index.ts` theo `slug`; slug mới phải được duyệt và ghi vào `an-du-y-niem.json` (xem Bước 4). Có hai cờ tuỳ chọn trên mỗi hình trong kho, `travelDot`/`endArrow`, gợi ý một chuyển động CHƯA DỪNG dọc theo path cuối cùng của hình (một chấm trôi có nhịp chớp tắt, một mũi tên bật ra ở điểm cuối theo đúng tiếp tuyến) - dùng cho ý niệm kiểu "một xu hướng còn tiếp diễn", không dùng cho hình đã khép kín (như "rễ sâu").
- **`YCanh`** - một chuỗi CẢNH VẼ TAY riêng biệt, mỗi `variant` là một kỹ thuật chuyển động khác nhau (chấm bung theo cụm, lưới lấp dần kèm đếm số, mặt trời toả tia, trăng mọc rồi trang giấy hiện dần, vạch mọc dần kèm đếm số, chùm tick bật nhanh, kim đồng hồ quét, lửa lớn dần) - dùng khi một đoạn kể chuyện có NHIỀU nhịp liên tiếp cần mỗi nhịp một cảm giác riêng để không đơn điệu. Tám `variant` sẵn có (`hub-branches`, `filling-grid`, `radiant-sun`, `rising-moon`, `growing-bars`, `tick-cluster`, `clock-sweep`, `growing-flame`) là TÁM KỸ THUẬT chuyển động tổng quát - `label`/`sublabel` mới là nơi mang nội dung cụ thể của dự án, không sửa code cho từng dự án. Chọn variant theo ĐÚNG cảm giác của ý niệm (xem chú thích chọn dùng ở đầu mỗi variant trong `YCanh.tsx`), không theo variant còn "mới lạ chưa dùng".
- Cả hai đều nhận `floating` (true = nền trong suốt, dùng làm overlay nổi trên một cảnh khác hoặc trên nền màu của video) và `position` (`'center'` là mặc định khi `floating`, canh giữa cả hai trục - đã đổi từ mặc định cũ `'top'` sau một dự án thật bị góp ý "dồn hết lên nửa trên khung, nửa dưới trống"). Khi KHÔNG `floating`, cả hai tự vẽ nền toàn khung theo `Canvas` như một composition độc lập.
- Kích thước và mật độ đã canh chỉnh qua một dự án thật: icon `floating` chiếm khoảng `unit*58`, nhãn chữ `unit*6.0`/`unit*3.9` (label/sublabel) - đây là NGƯỠNG DƯỚI đã kiểm chứng bằng khung hình thật, component mới hay dự án mới không nên nhỏ hơn nếu không có lý do cụ thể. Một hình chỉ có 2-3 chi tiết trông "nghèo" ở kích thước lớn - đặt mục tiêu 5-10 chi tiết chuyển động cho một cảnh `YCanh` (nhiều điểm bật ra, nhiều tia, nhiều dòng...), không dừng ở một đường nét đơn.

## Quy trình

### Bước 1 - Nhận file, hỏi một lượt

Nhận file âm thanh, đọc `an-du-y-niem.json` nếu đã có và ghi chú dự án cũ nếu có. Hỏi MỘT lượt tối đa bốn câu, chỉ khi chưa rõ: (1) video cho ai xem và phát ở đâu (khung ngang mặc định; dọc khi người dùng nói rõ); (2) theme light hay dark; (3) tên chủ đề/framework và thuật ngữ nào là CỐ ĐỊNH (để tra từ điển đúng chỗ); (4) intro/outro dùng preset chuẩn hay có thông điệp kết riêng. Không có trả lời thì mặc định ngang, light, preset chuẩn, và ghi rõ là giả định.

### Bước 2 - Tạo nền và gỡ băng

Chuẩn hoá tiếng, tạo `nguon/nen-<khung>.mp4` (nền màu `palettes.<theme>.bg` của brand, 30 fps, tiếng = voice, `-shortest`). Từ đây nền là "clip nguồn" duy nhất: mọi `in/out`, `snap`, `silences.json`, `overlay.at`, `broll.at` đều tính trên trục của nó, không có trục thứ hai. Chạy skill `phim-transcript` trên nền; nghiệm thu `nghiem-thu.py transcript` bắt buộc trước khi lên kịch bản (Whisper có thể rớt cụm ở ranh giới lô 28 giây).

### Bước 3 - Đọc như biên tập viên motion graphic, chia nhịp

Đọc trọn transcript một lượt. Chia thành các **nhịp ý** [semantic beat] theo ranh giới Ý, không theo ranh giới câu (một nhịp thường 6-25 giây; câu dài nhiều mệnh đề có thể là một nhịp; ba câu ngắn cùng một ý là một nhịp). Mốc thật của nhịp lấy từ chunk transcript, vị trí trong chunk nội suy theo tỷ lệ ký tự, hút về khoảng lặng gần nhất.

Gắn cho mỗi nhịp MỘT trong năm loại (đọc hiểu nội dung, không bắt từ khoá máy móc):

| Loại | Dấu hiệu | Hình mặc định |
|---|---|---|
| Khái niệm trừu tượng | từ/cụm không có nghĩa đen | tra từ điển → `YNiem` (ẩn dụ vẽ nét dần) hoặc `Benefits` 1 mục `showIndex:false` |
| Thuật ngữ/định nghĩa cố định | tên framework, cấu phần được liệt kê | `InfoSteps` (nhãn ngắn có thứ tự) / `InfoList` (mệnh đề dài) / `Benefits` hiện dần theo lời |
| Bước/tiến trình | "đầu tiên... rồi... cuối cùng", nguyên nhân-kết quả | `InfoSteps`, hoặc `Benefits` với `revealAt` theo đúng lúc nói |
| Số liệu/so sánh | con số, phần trăm, hơn-kém | `InfoStat` (một con số) / `InfoList` (nhiều mục) |
| Chuỗi nhịp kể chuyện liên tiếp, mỗi nhịp cần cảm giác riêng | đoạn "Câu chuyện"/"Hành trình" nhiều nhịp ngắn nối tiếp | `YCanh`, mỗi nhịp một `variant` khác nhau |
| Câu nhấn / không cần hình | câu chuyển ý, cảm xúc, mở/kết, câu hỏi để ngỏ | nền trơn; câu đắt nhất mới dùng `InfoQuote`; câu hỏi kết để trống hình |

Lưu ý thực tế: studio KHÔNG có composition "Caption"; nhu cầu "một dòng chữ nổi" dùng `Benefits` 1 mục `showIndex:false`. `YNiem`/`YCanh` tạm dùng kho hình/variant sẵn có; component/variant mới chỉ khi có trường hợp thật không gì biểu đạt được (xem mục "Thêm hình/variant mới" bên dưới).

### Bước 4 - Tra từ điển, đề xuất ẩn dụ mới

Với mỗi nhịp loại "khái niệm trừu tượng" hoặc "thuật ngữ cố định": tra `an-du-y-niem.json` theo khoá slug không dấu của khái niệm (file chưa tồn tại ở dự án đầu tiên - coi như từ điển rỗng). Có → ghi "[ĐÃ CÓ]" và dùng nguyên `hinh-thuc`/`props`. Chưa có → chọn image schema gần nhất (chứa đựng, đường đi, cân bằng, trên-dưới, đẩy-kéo, sáng-tối, trung tâm-ngoại vi, vòng lặp, tầng lớp - xem chú thích các shape mẫu trong `studio/src/y-niem/index.ts`), đề xuất MỘT ẩn dụ tối giản vẽ được bằng đường nét 3 px (chữ ký thị giác của brand), ghi rõ "ẨN DỤ MỚI - cần duyệt". Không bao giờ tự coi ẩn dụ mới là đã chốt. Khái niệm chỉ xuất hiện một lần và không thuộc hệ thuật ngữ cố định của người dùng thì không cần vào từ điển.

### Bước 5 - Viết `KICH-BAN-INFOMOTION.md` (Cổng duyệt 1)

Đầu file: thông điệp lõi một câu, khung ngang/dọc, theme, tổng thời lượng và số nhịp. Rồi mỗi nhịp một khối: mốc thật, lời nói nguyên văn (rút gọn nếu dài), loại, ẩn dụ (đã có / mới), hình thức và props chính, ghi chú. Cuối file: danh sách ẨN DỤ MỚI chờ duyệt, danh sách nhịp không có hình và lý do, kiểm tra mật độ (số hình / tổng phút), và câu hỏi cần người dùng quyết định (tên video, câu kết, có QR không). Nội dung dài hơn 5 phút: chia chương, đề xuất `SectionTitle` giữa các chương và `chapter` trong timeline.

Tiêu chí bản kịch bản đạt: người dùng đọc 10-15 phút không cần mở gì khác là hình dung được video; mọi ẩn dụ mới đánh dấu rõ; không nhịp nào dày hơn 1 hình / 8 giây; mỗi khối có mốc thật (không phải ước lượng). Với loại hình lần đầu xuất hiện trong dự án, render MỘT still (`npx remotion still`) kèm theo để người dùng thấy dáng hình, không render video.

Người dùng góp ý trên chữ; sửa tới khi họ nói duyệt. Ngay sau khi duyệt: ghi mọi ẩn dụ mới vào `an-du-y-niem.json` (tạo file mới dạng `{}` nếu chưa có) TRƯỚC khi render, không để cuối dự án.

### Bước 6 - Render đồ hoạ, soạn timeline, dựng nháp

Job JSON theo mẫu của `phim-do-hoa`, mỗi nhịp một job với `durationInSeconds` = đúng độ dài nhịp (đo từ mốc thật, cộng đệm 0,5-1 giây nếu nhịp sau không có hình). Đồ hoạ toàn khung (InfoList/InfoSteps/InfoStat/InfoQuote/YNiem/YCanh toàn khung) render mp4 nền cùng màu nền; đồ hoạ nổi (Benefits, YNiem nổi, YCanh nổi) render webm `alpha: true`. Render trong sandbox, `render-do-hoa.mjs` tự đo thời lượng/alpha; kiểm ngay `ffprobe` hình = tiếng của từng file.

**Ngân sách khung khi một ô timeline có `durationInSeconds` LOCKED** (để giữ một lịch overlay không hở khung đã kiểm chứng trên timeline thật): góp ý kiểu "chậm nhịp vẽ lại" KHÔNG áp một hệ số chậm đồng nhất cho mọi cảnh - tính riêng từng cảnh theo đúng `budget = durationInFrames - 14 (dành cho fade-out) - biên an toàn`. Ô nào dư khung nhiều thì chậm gần trọn, ô nào eo hẹp thì chỉ chậm được một phần; mốc hiện nhãn chữ (`labelFrame`) và thời lượng `FadeUp` cũng phải tính lại theo đúng ngân sách còn lại của từng ô, không giữ nguyên một con số chung.

**"Đổi hẳn, không vá toạ độ"**: khi người dùng chê một ẩn dụ "hơi kỳ" hay hai yếu tố trong cùng cảnh chồng lên nhau (cả về không gian lẫn thời gian), sửa cả hai trục cùng lúc - đổi hẳn ý tưởng hình (không cố "sửa nhẹ" hình cũ) VÀ tách rõ vùng không gian lẫn mốc thời gian giữa các yếu tố (yếu tố B chỉ bắt đầu SAU KHI yếu tố A đã yên vị), thay vì chỉnh dần toạ độ từng chút một qua nhiều vòng góp ý.

Timeline (schema đầy đủ trong docstring `tools/assemble.py`): mỗi chương MỘT segment `type: video` cắt từ `nen-<khung>.mp4` (tiếng voice đi liền, không cần `audioSrc`); đồ hoạ toàn khung vào `broll` với `at` theo trục nguồn và `duration` đúng; đồ hoạ nổi vào `overlay` (list) với `at` TƯƠNG ĐỐI so với `in` của segment. Intro (`insert`) sau nhịp mở đầu nếu có câu móc, outro cuối. Nhạc nền `bookends` hoặc `full` gainDb theo `nhac-nen/THU-VIEN.md`. Chạy `assemble.py --kiem-tra` → `--preview` với `--out "<tên>-<khung>-nhap1"` tường minh.

Sandbox render thường chỉ có 2 CPU: KHÔNG chạy nhiều job `render-do-hoa.mjs` song song. Gộp vào một job JSON (nội bộ tự tuần tự), hoặc nếu cần chạy nền trên `Bash` của sandbox đám mây thì dùng `nohup ... & disown` rồi `sleep`/`tail log` để theo dõi tiến độ (tiến trình nền của `Bash` sống qua nhiều lượt gọi tool; tiến trình nền chạy trên shell của MÁY người dùng thì KHÔNG - lệnh dài trên máy phải chạy đồng bộ trong một lượt gọi, dùng `timeout_ms` tối đa cho phép).

### Bước 7 - Nghiệm thu hai lớp, giao nháp (Cổng duyệt 2)

Lớp máy: `tools/nghiem-thu.py video` (hình = tiếng, LUFS, khung). Cảnh báo "hình đứng" ở quãng nền trơn là ĐÚNG THIẾT KẾ nếu quãng đó trùng một nhịp "không cần hình" trong kịch bản và không dài quá 20 giây; ngược lại là lỗi bố cục. Lớp đúng ý: từ `<thành phẩm>.map.json`, với MỖI hình trích khung tại mốc +1 giây (độ trễ hiện dần), đọc lại đúng câu transcript bao quanh, ghi vào báo cáo cặp "hình - câu đang nói"; hình nào không khớp ý câu là lỗi dù render đẹp. Hình nhiều mục (`Benefits` tích luỹ) kiểm ở trạng thái đầy đủ. Giao nháp preview cho người dùng xem, nhận góp ý theo mốc phút-giây, ghi `SO-GOP-Y.md`; góp ý lặp lần hai về cùng một kiểu lỗi → sửa mặc định trong component/từ điển, không chỉ sửa job.

### Bước 8 - Bản chính, bàn giao, cập nhật

Render 1080p với `--out "<tên>-<khung>-nhapN"` rồi copy bản đạt sang `xuat-hoan-chinh/`. Đề xuất bản dọc hoặc bản gọn 60-90 giây qua `phim-clip-ngan` nếu hợp. Cập nhật `an-du-y-niem.json` (số mục phải tăng nếu dự án có ẩn dụ mới). Ghi bài học kỹ thuật mới vào `docs/BAI-HOC.md` (mục "Về đồ hoạ" hoặc mở mục riêng nếu là bài học đặc thù infomotion); sửa quy trình thì sửa thẳng file này, `description` chỉ là mô tả kích hoạt, không ghi changelog vào đó. Giữ `do-hoa/job/*.json` tới khi giao xong.

## Thêm hình/variant mới

Component mới chỉ khi có trường hợp thật không gì biểu đạt được:

- **Thêm một hình vào `YNiem`**: thêm một entry `YNiemShape` vào `studio/src/y-niem/index.ts` (path dạng `"M x,y C x1,y1 x2,y2 x3,y3 C ..."` để dùng được với `travelDot`/`endArrow` nếu cần), chú thích ngắn khái niệm nó minh hoạ và image schema đang dùng. KHÔNG cần sửa `YNiem.tsx` - component đọc hình từ kho một cách tổng quát.
- **Thêm một variant vào `YCanh`**: viết một sub-component mới trong `YCanh.tsx` theo đúng khuôn các variant sẵn có (nhận `frame` + màu cần dùng từ `palette`, vẽ trong viewBox `0 0 100 100`, nét 3px qua `StrokePath`/`drawProgress`), đăng ký trong `YCanhVariant`, `VARIANT_LABEL_FRAME`, `VARIANT_LABEL_DURATION`, `yCanhSuggestedSeconds`, và nhánh `switch` của component chính.
- Cả hai trường hợp: làm theo 5 bước "Thêm component mới" của `skills/phim-do-hoa/SKILL.md` (đăng ký cả hai khung nếu có thay đổi ở `Root.tsx`, `tsc --noEmit` sạch, `npx remotion compositions` liệt kê đúng, render still tiếng Việt có dấu và NHÌN bằng mắt trước khi coi là xong, commit file nguồn về máy ngay).

## Ghi chú vận hành kỹ thuật (pipeline đám mây - máy)

- **`device_bash` (lệnh chạy trên máy người dùng) KHÔNG giữ tiến trình nền qua các lượt gọi tool khác nhau** (khác với `Bash` của sandbox đám mây, tiến trình nền của nó sống qua nhiều lượt gọi). Lệnh dài chạy trên máy (assemble.py, transcribe) phải chạy ĐỒNG BỘ trong một lượt gọi `device_bash`, dùng `timeout_ms` tối đa cho phép.
- **`device_commit_files` dùng được trực tiếp với `stagedPath`** dưới `/mnt/user-data/outputs/<file>` (sau khi `cp`/`Write` file vào đó) mà KHÔNG cần gọi `SendUserFile` trước để lấy `file_uuid` - nhanh hơn khi commit nhiều file cùng lúc và không cần thẻ file hiện trong khung chat.
- **Bẫy dấu tiếng Việt khi ghi file bằng heredoc hai bước** (`cat > file << 'EOF' ... EOF` rồi mới chạy): có thể lặng lẽ làm phẳng/mất dấu tiếng Việt ở bước THỰC THI dù nội dung đọc lại từ nguồn trông đúng. Cách an toàn: ghi file một bước bằng `python3 <<'PYEOF' ... PYEOF` hoặc dùng công cụ `Write`/`Edit`, mở file bằng `io.open(path, 'a', encoding='utf-8')` khi cần nối thêm - và LUÔN đọc lại nội dung vừa ghi để xác nhận dấu còn nguyên trước khi coi là xong.
- Ngân sách khung, mật độ chi tiết tối thiểu (5-10 chi tiết chuyển động một cảnh `YCanh`), và kích thước `floating` (`unit*58`/`unit*6.0`/`unit*3.9`) trong mục "Hai thành phần đồ hoạ" ở trên là kết quả một dự án thật đã qua nhiều vòng góp ý - không hạ xuống dưới các mốc đó khi bắt đầu dự án mới trừ khi người dùng chủ động yêu cầu.

## Quy tắc cứng

- Không render video trước cổng 1; still mẫu được phép.
- Tra từ điển là bước bắt buộc trước sáng tạo; ẩn dụ mới luôn đánh dấu; ghi vào từ điển ngay sau duyệt.
- Trần mật độ 1 hình / 8-10 giây; nhịp không hình hợp lệ; câu hỏi kết để trống hình.
- Tái dùng hình/variant có sẵn trong `YNiem`/`YCanh` trước; hình/variant mới chỉ khi có trường hợp thật không gì biểu đạt được, và làm theo `skills/phim-do-hoa/SKILL.md` (đăng ký cả hai khung, tsc sạch, still tiếng Việt có dấu, commit về máy ngay).
- Overlay nổi (`floating: true`) mặc định `position: 'center'`, kích thước không nhỏ hơn ngưỡng đã kiểm chứng (`unit*58` icon, `unit*6.0`/`unit*3.9` label/sublabel), tối thiểu 5-10 chi tiết chuyển động cho một cảnh `YCanh`.
- Ô timeline có `durationInSeconds` LOCKED (giữ lịch overlay đã kiểm chứng): "chậm nhịp" tính ngân sách khung RIÊNG từng cảnh, không dùng một hệ số chung.
- Góp ý "hình hơi kỳ" hoặc hai yếu tố chồng nhau: đổi hẳn ý tưởng hình VÀ tách cả không gian lẫn thời gian, không vá toạ độ từng chút.
- Mốc từ transcript thật, hút về khoảng lặng; không cộng dồn thời lượng danh nghĩa.
- Đồ hoạ nổi không che nhau về thời gian trong cùng segment; hai đồ hoạ toàn khung liên tiếp cách nhau tối thiểu 5 giây nền hoặc gộp thành một.
- Nghiệm thu máy VÀ đọc lại transcript quanh mốc là bắt buộc trước khi báo "xong"; `--out` tường minh từ nháp đầu.
- `device_bash` trên máy người dùng chạy đồng bộ, không có tiến trình nền qua nhiều lượt gọi; sandbox đám mây chỉ 2 CPU nên không render đồ hoạ song song nhiều job.
