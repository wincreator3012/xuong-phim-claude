---
name: "phim-infomotion"
description: "Dựng video giải thích hoàn toàn bằng motion graphic [infomotion] từ MỘT nguồn duy nhất là giọng ghi âm trình bày của người dùng, không có cảnh quay người. Hai cổng: AI gỡ băng, chia lời thành nhịp ý, phân loại năm loại nhịp, tra từ điển ẩn dụ cá nhân (do-hoa-chung/an-du-y-niem.json, lớn dần qua từng dự án) hoặc đề xuất ẩn dụ mới, viết KỊCH BẢN HÌNH TƯỢNG HOÁ BẰNG CHỮ để user duyệt trước khi render (cổng 1); rồi tạo nền, render đồ họa, ghép khớp voiceover gốc bằng assemble.py, nghiệm thu đúng ý lẫn đúng thời lượng, user xem nháp góp ý (cổng 2). Kích hoạt khi user nói \"infomotion\", \"làm video từ file ghi âm\", \"chỉ có voice không có hình\", \"hình tượng hoá bài nói\", \"motion graphic minh hoạ bài giảng\", \"dựng clip từ voiceover\", hoặc thả file âm thanh vào nguon/ mà không có video. KHÔNG dùng khi có cảnh quay người (phim-dung-bai, phim-bai-giang-slide), đồ họa lẻ (phim-do-hoa), phỏng vấn (phim-tai-lieu-phong-van), hay hoạt hình có nhân vật, cảnh (phim-hoat-hoa)."
---

# Infomotion: từ giọng nói ra hình tượng hoá

Mục tiêu: từ một bản ghi âm người dùng trình bày (thường 3-15 phút, một framework hay một ý niệm), làm ra một video hoàn toàn bằng đồ họa động khớp chặt với voiceover gốc, chính xác về nội dung, dễ hiểu, hấp dẫn, và mang đặc trưng hình ảnh riêng của người dùng. Khác mọi skill khác trong xưởng: KHÔNG có cảnh quay để cắt, hình phải được nghĩ ra từ lời nói.

Ba nguyên tắc xuyên suốt (nền tảng nghiên cứu trong `skills/phim-infomotion/references/hinh-tuong-hoa.md`):

1. **Duyệt trên giấy trước, render sau.** Kịch bản hình tượng hoá viết bằng chữ là cổng duyệt 1. Không render video trước khi người dùng duyệt, trừ một khung tĩnh mẫu [style frame] cho loại hình lần đầu xuất hiện. Sai ẩn dụ hay sai cấu trúc là lỗi tốn kém nhất, phải chặn khi còn rẻ.
2. **Tra từ điển trước, sáng tạo sau.** Mọi khái niệm cố định của người dùng (tên framework, thuật ngữ riêng, các bước có tên...) tra `do-hoa-chung/an-du-y-niem.json` trước (dự án infomotion đầu tiên chưa có file: tạo theo schema ở `references/mau-kich-ban.md` mục 4); có thì dùng nguyên hình đã chốt; chưa có thì đề xuất và đánh dấu "ẨN DỤ MỚI" để người dùng duyệt, rồi ghi ngay vào từ điển. Hình nhất quán qua mọi video và chi phí sáng tạo giảm dần.
3. **Phủ kín có ý đồ, không nhồi.** Mặc định: không có khoảng nào quá 1 giây chỉ còn nền trơn, trừ nhịp đánh dấu `Hình: KHÔNG - <lý do>` (câu móc cần đứng một mình, khoảng lắng sau một hình nặng, câu hỏi kết để ngỏ). Mỗi nhịp một ý và một hình chính; các hình nối tiếp liền mạch thay vì chồng lớp; khoảng trống lấp bằng HÌNH có kỹ thuật chuyển động riêng từng nhịp, không bằng chữ thuần, không lặp một khuôn. Ranh giới nằm ở chỗ mỗi hình phải khớp ý câu đang nói, không ở số lượng hình (cảnh báo Data Player, TVCG 2023). Dự án người dùng muốn thưa hơn: ghi ở khung hình chung và chạy `uoc-luong.py --khoang-hinh 8`.

**Ranh giới với phim-hoat-hoa.** Cùng nguồn là file voice, cùng pipeline gỡ băng, chia nhịp ý và từ điển ẩn dụ, nhưng khác ngôn ngữ hình: skill này là đồ họa thông tin tối giản trên nền phẳng (nhãn, danh sách, con số, ẩn dụ nét đơn `YNiem`/`YCanh`); phim-hoat-hoa dựng một thế giới hoạt hình có bối cảnh, nhân vật, mô-típ. Người dùng thả file voice mà chưa nói rõ loại nào thì hỏi một câu trước Bước 1. Mục từ điển do phim-hoat-hoa thêm có trường `nguon: "hoat-hoa"`.

Đọc trước: `skills/_chung/van-hanh.md` (đọc gì, hai nơi chạy lệnh, truyền file, chữ và chức danh), `skills/_chung/timeline-va-dung.md`, `skills/_chung/nghiem-thu-dung-y.md`, `skills/phim-do-hoa/SKILL.md` (render, thêm component), `docs/BAI-HOC.md` chủ đề "Infomotion và hình vẽ ẩn dụ". Mẫu kịch bản, timeline, job JSON, lệnh tạo nền và schema từ điển: `skills/phim-infomotion/references/mau-kich-ban.md`.

## Hai lối vào

- **Lối vào A - đã có bản ghi âm** (chuẩn): đi từ Bước 1.
- **Lối vào B - có bài viết hoặc dàn ý, chưa ghi âm**: chia nhịp và viết `KICH-BAN-INFOMOTION.md` ngay trên chữ, mốc tạm tính theo tốc độ nói thật của người dùng (số từ mỗi phút đo từ transcript một dự án cũ; chưa có thì 130 từ/phút, ghi là giả định), mọi mốc ghi "tạm". Duyệt ẩn dụ, cấu trúc, dữ kiện trên chữ (Cổng duyệt 1), rồi người dùng ghi âm theo kịch bản. Có file thật thì quay về Bước 2, thay mốc tạm bằng mốc thật và chạy lại kiểm giấy. Giọng đọc máy chỉ được làm bản giọng tạm để tự nghe nhịp hoặc dựng bản phác động [animatic] nội bộ; bản giao luôn là giọng thật của người dùng.

## Cấu trúc dự án

```
du-an/<tên>/
  nguon/voice.wav              giọng ghi âm gốc (chuẩn hoá 48 kHz; giữ file gốc cạnh đó)
  nguon/nen-<ngang|doc>.mp4    NỀN: video màu giấy brand có sẵn tiếng voice (Bước 2) - đây là "clip nguồn"
  transcript/                  phim-transcript tạo từ nen-*.mp4 (một trục thời gian duy nhất)
  KICH-BAN-INFOMOTION.md       kịch bản hình tượng hoá bằng chữ (Cổng duyệt 1)
  do-hoa/<ngang|doc>/ + do-hoa/job/   đồ họa render + job JSON gốc (giữ tới khi giao)
  timeline.json, SO-GOP-Y.md, xuat-nhap/, xuat-hoan-chinh/   như mọi dự án khác
do-hoa-chung/an-du-y-niem.json  TỪ ĐIỂN ẨN DỤ dùng chung mọi dự án (không nằm trong du-an/)
```

## Quy trình

### Bước 1 - Nhận file, hỏi một lượt

Nhận file âm thanh, đọc `an-du-y-niem.json` và ghi chú dự án nếu có. Hỏi MỘT lượt tối đa bốn câu, chỉ khi chưa rõ: (1) video cho ai xem và phát ở đâu (ngang mặc định; dọc khi người dùng nói rõ); (2) theme light hay dark; (3) tên chủ đề hay framework và thuật ngữ nào là CỐ ĐỊNH (để tra từ điển đúng chỗ); (4) intro, outro dùng preset chuẩn hay có thông điệp kết riêng. Không có trả lời thì mặc định ngang, light, preset chuẩn, ghi rõ là giả định.

### Bước 2 - Tạo nền và gỡ băng

Chuẩn hoá tiếng, tạo `nguon/nen-<khung>.mp4` bằng lệnh trong `mau-kich-ban.md` (nền màu `palettes.<theme>.bg`, 30 fps, tiếng = voice, `-shortest`). Từ đây nền là "clip nguồn" duy nhất: mọi `in/out`, `snap`, `silences.json`, `overlay.at`, `broll.at` tính trên trục của nó. Gỡ băng theo phim-transcript (large-v3 trên Mac là ưu tiên), qua `nghiem-thu.py transcript` trước khi lên kịch bản.

### Bước 3 - Đọc như biên tập viên motion graphic, chia nhịp

Đọc trọn transcript một lượt. Chia thành các **nhịp ý** [semantic beat] theo ranh giới Ý, không theo ranh giới câu (thường 6-25 giây; câu dài nhiều mệnh đề có thể là một nhịp; ba câu ngắn cùng một ý là một nhịp). Mốc thật lấy từ transcript, vị trí trong câu nội suy theo tỷ lệ ký tự, hút về khoảng lặng gần nhất.

Gắn cho mỗi nhịp MỘT trong năm loại (đọc hiểu nội dung, không bắt từ khoá máy móc):

| Loại | Dấu hiệu | Hình mặc định |
|---|---|---|
| Khái niệm trừu tượng | từ, cụm không có nghĩa đen (mắc kẹt, buông bỏ, gắn kết...) | tra từ điển → `YNiem` (một ẩn dụ vẽ nét) hoặc `YCanh` (cảnh vẽ tay riêng); `Benefits` 1 mục khi chỉ cần chữ |
| Thuật ngữ, định nghĩa cố định | tên framework, cấu phần được liệt kê (các bước, cấu phần có tên riêng...) | `InfoSteps` (nhãn ngắn có thứ tự) / `InfoList` (mệnh đề dài) / `Benefits` hiện dần theo lời |
| Bước, tiến trình | "đầu tiên... rồi... cuối cùng", nguyên nhân kết quả | `InfoSteps`, hoặc `Benefits` `revealAt` đúng lúc nói |
| Số liệu, so sánh | con số, phần trăm, hơn kém | `InfoStat` (một con số) / `InfoList` (nhiều mục); chart động chỉ tạo khi hai dự án cùng cần |
| Câu nhấn, chuyển ý | câu chuyển ý, cảm xúc, mở, kết, câu hỏi để ngỏ | giữ hình nhịp trước lắng lại (kéo dài ô), hoặc câu đắt nhất thành `InfoQuote`/`Benefits` 1 mục; nền trơn chỉ khi có ý đồ, ghi `Hình: KHÔNG - <lý do>` |

Kho hình có sẵn: `YNiem` tra hình theo `slug` trong `studio/src/y-niem/index.ts`; `YCanh` có tám variant đặt theo kỹ thuật chuyển động (`hub-branches`, `filling-grid`, `radiant-sun`, `rising-moon`, `growing-bars`, `tick-cluster`, `clock-sweep`, `growing-flame`); đặc tả ở `hinh-tuong-hoa.md` mục 4. Ẩn dụ đã duyệt dùng đúng như từ điển ghi; cần hình mới thì thêm variant hoặc slug theo mục "Thêm component mới" của phim-do-hoa và đưa người dùng duyệt như mọi ẩn dụ mới. Studio không có composition `Caption`.

### Bước 4 - Tra từ điển, đề xuất ẩn dụ mới

Với mỗi nhịp loại 1 và 2: tra `an-du-y-niem.json` theo khoá slug không dấu của khái niệm. Có → ghi "[ĐÃ CÓ]" và dùng nguyên `hinh-thuc`/`props`. Chưa có → chọn image schema gần nhất (chứa đựng, đường đi, cân bằng, trên dưới, đẩy kéo, sáng tối, trung tâm ngoại vi, vòng lặp, tầng lớp; heuristic ở `hinh-tuong-hoa.md` mục 3), đề xuất MỘT ẩn dụ tối giản vẽ được bằng nét 3 px, ghi rõ "ẨN DỤ MỚI - cần duyệt". Không bao giờ tự coi ẩn dụ mới là đã chốt. Khái niệm chỉ xuất hiện một lần và không thuộc hệ thuật ngữ của người dùng thì không cần vào từ điển.

### Bước 5 - Viết `KICH-BAN-INFOMOTION.md` (Cổng duyệt 1)

Theo mẫu trong `mau-kich-ban.md`: đầu file là thông điệp lõi một câu, khung, theme, tổng thời lượng, số nhịp; rồi mỗi nhịp một khối: mốc thật, lời nói nguyên văn (rút gọn nếu dài), loại, ẩn dụ (đã có / mới), hình thức và props chính, ghi chú. Cuối file: ẨN DỤ MỚI chờ duyệt, các nhịp `Hình: KHÔNG` và lý do, kiểm độ phủ, câu hỏi cần người dùng quyết (tên video, câu kết, QR). Nội dung dài hơn 5 phút: chia chương, `SectionTitle` giữa các chương và `chapter` trong timeline.

Ba thứ mọi kịch bản phải có thêm:

- **Khung hình chung** ở đầu file, chốt một lần ở Cổng duyệt 1: theme, màu nhấn chính, họ hình chủ đạo (vẽ nét `YNiem`, cảnh `YCanh`, infographic), nhịp chuyển động, vị trí đồ họa nổi (mặc định canh giữa; luôn hỏi người dùng có muốn điều chỉnh không). Nhịp nào lệch khung thì ghi lý do ngay ở nhịp đó.
- **Dòng "Thấy gì:"** cho mỗi nhịp có hình: một câu lời thường tả người xem thấy gì, không dùng tên component hay prop.
- **Dòng "Kiểm chứng:"** cho mỗi nhịp mà hình mang dữ kiện (con số, năm, tên nghiên cứu, tác giả, trích dẫn): nguồn đã tra được. Mô hình hay công cụ của người khác thì ghi tên tác giả trên hình. Lời trong bản ghi âm lệch với nguồn thì không sửa lời bằng chữ đè; đưa ba cách để người dùng chọn: (1) ghi âm lại riêng câu đó rồi thay vào đúng mốc; (2) giữ lời, hình không lặp dữ kiện; (3) cắt câu.

Trước khi trình, `python3 tools/uoc-luong.py "du-an/<x>/KICH-BAN-INFOMOTION.md"` phải báo "KIỂM GIẤY: ĐẠT", hoặc mỗi điểm "CẦN XEM" có lý do ghi trong kịch bản. Kịch bản đạt khi: người dùng đọc 10-15 phút không cần mở gì khác là hình dung được video; ẩn dụ mới đánh dấu rõ; hai nhịp liền nhau không dùng cùng một khuôn chuyển động; mọi mốc là mốc thật. Loại hình lần đầu xuất hiện: kèm MỘT still (`npx remotion still`).

Người dùng góp ý trên chữ; sửa tới khi người dùng nói duyệt. Ngay sau khi duyệt: ghi mọi ẩn dụ mới vào `an-du-y-niem.json` (kèm `duyet`, `du-an`) TRƯỚC khi render.

### Bước 6 - Render đồ họa, soạn timeline, dựng nháp

- **Job JSON** theo mẫu, mỗi nhịp một job, `durationInSeconds` = đúng độ dài nhịp (đo từ mốc thật; cộng đệm 0,5-1 giây nếu nhịp sau không có hình). Đồ họa toàn khung (InfoList, InfoSteps, InfoStat, InfoQuote, YNiem toàn khung) render mp4 nền cùng màu nền; đồ họa nổi (Benefits, YNiem nổi, YCanh nổi) render webm `alpha: true`. Nhiều job gộp chung một job JSON để chạy tuần tự.
- **Render** `node tools/render-do-hoa.mjs <job.json> --studio <đường dẫn tuyệt đối>`; đo ngay thời lượng thật từng file bằng `ffprobe`. Lịch đồ họa nối liền dựa trên số đo này, không dựa trên `durationInSeconds` danh nghĩa.
- **Tạo hình**: đồ họa nổi canh giữa (mặc định của component), lấp phần lớn khung, giàu chi tiết (5-10 chi tiết chuyển động mỗi hình), mỗi nhịp một kỹ thuật chuyển động. Làm chậm trong ô đã khoá thì tính ngân sách khung riêng từng cảnh; ẩn dụ bị chê hay chồng lấn thì thiết kế lại cả khối. Chi tiết và con số: `hinh-tuong-hoa.md` mục 6.
- **Timeline** (mẫu trong references): mỗi chương MỘT segment `type: video` cắt từ `nen-<khung>.mp4` (tiếng voice đi liền); đồ họa toàn khung vào `broll` với `at` theo trục nguồn và `duration` đúng; đồ họa nổi vào `overlay` (list) với `at` TƯƠNG ĐỐI so với `in`. Overlay chỉ hiện ở quãng TRƯỚC B-roll đầu tiên của segment (`--kiem-tra` cảnh báo khi vi phạm): chương có đồ họa nổi xen sau đồ họa toàn khung thì tách chương thành nhiều sub-segment liền mạch tại điểm kết thúc mỗi đồ họa toàn khung (`out` đoạn trước = `in` đoạn sau), overlay tính `at` từ `in` của sub-segment chứa nó. Mốc kết thúc khối trước bằng đúng mốc bắt đầu khối sau. Hai đồ họa toàn khung liên tiếp chuyển liền mạch trên cùng màu nền (quy tắc 5 giây của phim có người nói không áp ở đây). Intro (`insert`, `"role": "intro"`) sau nhịp mở đầu nếu có câu móc, outro cuối. Nhạc theo `_chung/timeline-va-dung.md`.
- **Dựng**: `assemble.py --kiem-tra` → `--preview --out "<tên>-<khung>-nhap1"`.

### Bước 7 - Nghiệm thu hai lớp, giao nháp (Cổng duyệt 2)

Lớp máy: `tools/nghiem-thu.py video`. Cảnh báo "hình đứng" ở quãng nền trơn chỉ đúng thiết kế khi trùng một nhịp `Hình: KHÔNG - <lý do>` và không dài quá 20 giây; ngược lại là lỗi độ phủ hoặc bố cục. Lớp đúng ý theo `_chung/nghiem-thu-dung-y.md`: với MỖI hình, cặp "hình - câu đang nói" tại mốc `part.start + overlay.at` (+1 giây); contact sheet cho đoạn nhiều overlay nối tiếp để soát lịch nối liền và nhiều điểm góp ý cùng lúc; Benefits tích luỹ kiểm ở trạng thái đầy đủ.

Giao nháp cho người dùng xem trên máy, nhận góp ý theo mốc phút giây, ghi `SO-GOP-Y.md`; góp ý lặp lần hai về cùng một kiểu lỗi → sửa mặc định trong component hoặc từ điển, không chỉ sửa job.

### Bước 8 - Bản chính, bàn giao, cập nhật

Render 1080p với `--out "<tên>-<khung>"`, nghiệm thu, copy bản đạt sang `xuat-hoan-chinh/`. Đề xuất bản dọc hoặc bản gọn 60-90 giây qua phim-clip-ngan nếu hợp. Cập nhật `an-du-y-niem.json` (số mục phải tăng nếu dự án có ẩn dụ mới); bài học kỹ thuật mới vào `docs/BAI-HOC.md` chủ đề "Infomotion và hình vẽ ẩn dụ"; cách làm đổi thì sửa skill theo `_chung/bao-tri-skill.md`. Giữ `do-hoa/job/*.json` tới khi giao xong.

## Khi một khâu hỏng

Nguyên tắc chung ở `_chung/van-hanh.md` và bảng từng khâu ở QUY-TRINH. Riêng thể loại này:

- Transcript trên nền không qua `nghiem-thu.py transcript`: gỡ lại cửa sổ rộng quanh chỗ hỏng; chưa có transcript đạt thì chưa lên kịch bản, vì mọi mốc dựa vào nó.
- Một hình mới không vẽ được sau một lần sửa (still lỗi, `tsc` không sạch): dừng riêng nhịp đó, báo người dùng, đề xuất thay bằng một hình đã có trong kho hoặc `Benefits` nhãn chữ. Đây là lựa chọn đưa người dùng duyệt lại, không tự thay sau khi kịch bản đã duyệt.
- Một job render lỗi hoặc ra file ngắn hơn nhịp: không kéo dài bằng khung đứng, không đẩy file ngắn vào timeline; render lại đúng `durationInSeconds`, các job khác vẫn chạy.
- Dựng không qua `check_av()` hoặc `nghiem-thu.py video`: dừng, đọc bảng chẩn đoán, không giao nháp lỗi.

## Quy tắc cứng

- Không render video trước Cổng duyệt 1; still mẫu được phép. Kiểm giấy bằng `uoc-luong.py` trước khi trình.
- Tra từ điển trước khi sáng tạo; ẩn dụ mới luôn đánh dấu; ghi vào từ điển ngay sau khi duyệt.
- Mỗi hình khớp ý câu đang nói; không hình nào nói điều người dùng không nói. Phủ kín là mặc định của skill (không quá 1 giây nền trơn trừ nhịp `Hình: KHÔNG - <lý do>`); clip nào cần thưa hơn hay nhịp khác vì trải nghiệm người xem thì đề xuất kèm lý do ở Cổng duyệt 1.
- Mốc từ transcript thật và thời lượng đo bằng `ffprobe`; không cộng dồn số danh nghĩa.
- Tái dùng component có sẵn trước; component mới theo phim-do-hoa (cả hai khung, `tsc` sạch, still tiếng Việt có dấu, commit về máy ngay).
- Mọi hình mang dữ kiện có dòng "Kiểm chứng:"; lời lệch nguồn không sửa bằng chữ đè, người dùng chọn một trong ba cách.
- Hình vẽ bằng code theo brand; không dùng ảnh hay clip do AI tạo. Giọng máy chỉ làm bản tạm ở Lối vào B, không bao giờ vào bản giao.
- Nghiệm thu máy VÀ cặp "hình - câu đang nói" là bắt buộc trước khi báo "xong".

<!-- ban-nguon: phim-infomotion 2026-09-30 3735b26d -->
