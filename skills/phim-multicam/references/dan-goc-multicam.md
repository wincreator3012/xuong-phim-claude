# Dàn góc multicam - cơ sở và bảng luật

Tài liệu tham chiếu cho skill phim-multicam. Đọc khi soạn hoặc sửa "dàn góc" [shot plan] cho một buổi quay nhiều máy. Mục tiêu: người xem theo được câu chuyện và cảm được mối quan hệ giữa những người đang nói, mà không nhận ra là mình đang bị cắt qua lại.

## 1. Vì sao khớp bằng âm thanh, và khớp thế nào

Mỗi máy quay là một đồng hồ riêng: bấm không cùng lúc, máy điện thoại tự tách file mỗi vài GB, và hai máy chạy lệch nhau vài phần triệu (drift). Âm thanh là thứ duy nhất mọi máy cùng nghe, nên nó là thước chung. `multicam-khop.py` rút tiếng mỗi file về 8 kHz mono, tính đường bao năng lượng log [log-energy envelope] 100 mẫu/giây có chuẩn hoá theo nền phòng, rồi tương quan chéo bằng FFT với đường bao của góc chuẩn; đường bao chịu được mic khác nhau, khoảng cách khác nhau và tạp âm, khác với so sóng thô. Sau đó tinh lại quanh đỉnh ở độ phân giải 1 ms, đo drift bằng ba đoạn đầu/giữa/cuối, và báo hai chỉ số tin cậy: đỉnh chia đỉnh phụ (cách hơn 1 giây) và Pearson r của đường bao tại lag tìm được. Đây cũng là cách các công cụ như PluralEyes, Premiere "Synchronize by audio", Descript và Eddie AI làm; điểm khác của xưởng là mọi mốc được ghi ra `multicam.json` để Claude và user kiểm được bằng mắt, không tin đen.

Tin cậy thấp thường do: hai máy quá xa nhau (tiếng vọng phòng át tiếng nói), một máy chỉ có tiếng nhạc nền, file bị cắt tiếng, hoặc góc chuẩn nhiều file bị xếp nối tiếp trong khi thật ra có nghỉ. Xử lý theo thứ tự: đổi `--chu` sang góc quay liên tục; kiểm bằng khung hình tại một khoảnh khắc có cử động rõ; cuối cùng mới soạn tay offset theo tiếng vỗ tay.

## 2. Nghiên cứu nói gì về cú cắt

**Người xem không thấy phần lớn các cú cắt nếu cắt đúng lúc.** Nghiên cứu "edit blindness" của Smith và Henderson: khi cú cắt rơi vào lúc chú ý đang bị kéo bởi hành động hoặc lời nói, người xem bỏ lỡ tới một phần ba số cú cắt; cắt lệch khỏi dòng hành động thì bị nhận ra ngay. Sau mỗi cú cắt, mắt của mọi người xem hội tụ về cùng một điểm (đồng bộ chú ý [attentional synchrony]) rồi tản ra dần; vì vậy chỗ mắt hội tụ ngay sau cắt phải là điểm có ý nghĩa (mặt người nói, bàn tay đang chỉ). Nguồn: [Smith & Henderson, Edit Blindness, JEMR 2008](https://www.mdpi.com/1995-8692/2/2/11); [Match-Action: motion and audio in change blindness, Media Psychology 2017](https://www.tandfonline.com/doi/abs/10.1080/15213269.2016.1160789).

**Đổi cỡ cảnh dễ chịu hơn đổi góc lệch; đổi theo hướng vào tự nhiên hơn hướng ra.** Đo điện não khi xem các cú cắt nối tiếp: cắt đổi cỡ cảnh (toàn → trung → cận) gây phản ứng nhỏ, não xử lý như một lần "nhìn kỹ hơn"; cắt đổi góc mạnh nhưng cùng cỡ, hoặc vượt trục, gây phản ứng lớn hơn và người xem nhận ra vết nối. Nguồn: [Cinematographic continuity edits across shot scales and camera angles: an ERP analysis, Frontiers in Neuroscience 2023](https://www.frontiersin.org/journals/neuroscience/articles/10.3389/fnins.2023.1173704/full). Suy ra: hai máy cận trong podcast đặt đối xứng cùng tầm mắt, cùng tiêu cự; bài giảng một người thì góc phụ nên khác cỡ cảnh (trung hoặc cận hơn) chứ không chỉ khác góc.

**Tiếng dẫn hình.** Cắt "nguội" đúng lúc người mới bắt đầu nói tạo cảm giác bóng bàn; cho tiếng của người sắp nói vào trước hình một nhịp ngắn (J-cut) hoặc giữ hình người nghe khi người kia đã nói (L-cut, chính là cú phản ứng) làm dòng hội thoại liền mạch hơn; lệch quá xa lại thành cảm giác hình tiếng không khớp. Kiểm bằng cách nghe lại bản dựng không nhìn hình ("ears-only pass"). Nguồn: [Finchley, Video execution of a professional podcast: editing considerations](https://www.finchley.co.uk/finchley-learning/visual-podcast/video-execution-of-a-professional-podcast-the-post-production-guide-editing-considerations).

**Công cụ tự động làm gì.** Descript Automatic Multicam: cắt theo người đang nói, khi hội thoại nhanh thì hiện nhiều người, khi độc thoại thì chèn cảnh cắt xen [cutaway] với nhịp người dùng chọn: "occasional" mỗi 30 giây, "frequent" mỗi 10 giây ([Descript Help](https://help.descript.com/hc/en-us/articles/28736507904525-Automatic-multicam)). Eddie AI: tối đa 6 góc cộng một file tiếng riêng, mỗi máy cần ít nhất tiếng scratch để khớp, chọn góc theo người đang nói và không cho chỉnh nhịp cắt hay chèn phản ứng theo yêu cầu ([Eddie AI Help](https://help.heyeddie.ai/en/articles/10548843-multicam-podcasts-the-correct-angle-chosen-for-the-correct-speaker)). Xưởng lấy nhịp xen của Descript làm khung (mặc định ~24 giây, giữa hai mức) nhưng đặt cú xen tại chỗ ngắt hơi và để Claude dời nó theo nội dung, là điểm các công cụ này không làm.

**Chia khúc buổi dài.** Nguyên lý phân đoạn [segmenting] của Mayer (xem `references/bo-cuc-slide.md` của skill bài giảng): người học tiếp thu tốt hơn khi nội dung được chia thành khúc có tên. Phân tích 6,9 triệu lượt xem MOOC của Guo, Kim & Rubin 2014 cho thấy thời gian xem thực rơi mạnh sau 6-9 phút liên tục; thẻ session không làm video ngắn hơn nhưng cho người xem điểm tựa để dừng và quay lại, và chapter trên YouTube nhờ đó có nghĩa.

## 3. Bảng luật cắt (mặc định trong multicam-dan.py)

| Tình huống | Góc | Vì sao |
|---|---|---|
| Mở session | toàn 4-6 giây | thiết lập không gian và số người; người xem định vị trước khi vào cận |
| Một người nói (podcast) | cận người đó | mặc định; mắt người xem tìm miệng đang nói |
| Lượt nói dưới 1,5 giây ("vâng", "đúng rồi") | không đổi góc | đổi góc cho lời đệm gây bóng bàn; phản ứng ngắn không cần hình |
| Người mới bắt đầu nói | cắt 0,4 giây SAU khi họ bắt đầu | tiếng dẫn hình (J-cut); người xem nghe rồi mới thấy, tự nhiên như quay đầu |
| Một người nói liền hơn 25-30 giây | xen cận người nghe 2,5-3,5 giây tại chỗ ngắt hơi (mỗi ~24 giây), hoặc toàn | phản ứng người nghe là cách người xem biết "nên cảm gì"; đồng thời tránh một khung tĩnh quá lâu |
| Hai người nói chồng hơn 1,5 giây, cùng cười | toàn | không chọn được ai; toàn cho thấy quan hệ giữa hai người |
| Câu chốt, câu xúc động | cận người nói, giữ đến hết câu | không cắt qua điểm cảm xúc |
| Đóng session | toàn 3 giây | thở ra trước thẻ chuyển |
| Bài giảng một người: mặc định | góc chính ~60% | ánh nhìn thẳng máy quay giữ kết nối |
| Bài giảng: ý mới sau ngắt hơi ≥ 0,6 giây | đổi sang góc phụ, giữ 12-25 giây | đổi góc đánh dấu ý mới, không đổi giữa ý |
| Bài giảng: ví dụ, kể chuyện, cử chỉ tay rộng | toàn ~10% | thấy cơ thể; đổi cỡ cảnh hướng ra ít dùng, nên ngắn |
| Mọi cú cắt | hút về khoảng lặng của tiếng chủ (±0,6 giây) | cắt giữa từ là vết nối lộ nhất |
| Giữ một góc | tối thiểu 3 giây, tối đa ~30 giây | dưới 3 giây là nháy; trên 30 giây là tĩnh |

Claude sửa bản nháp theo nội dung thật, ưu tiên: (1) đặt phản ứng đúng chỗ có phản ứng thật (cười, gật, "ồ") thay vì chỗ tool đặt theo đồng hồ; (2) không để cú cắt rơi vào giữa một câu quan trọng; (3) tỉ lệ góc phản ánh vai: host dẫn ít nói thì cận host ít hơn, nhưng đừng để một người "biến mất" hơn 60 giây khi vẫn đang ngồi đó.

## 4. Chia session theo transcript

`multicam-dan.py` chấm điểm mỗi khoảng ngắt dài (≥ 0,8 giây) bằng ba dấu hiệu: độ dài khoảng ngắt, độ khác từ khoá giữa 60 giây trước và 60 giây sau (Jaccard), và cụm chuyển ý ("tiếp theo", "chuyển sang", "câu hỏi tiếp", "tóm lại", "cuối cùng"...). Rồi chọn tham lam các ranh giới sao cho session gần độ dài mục tiêu (`--phut`, mặc định 8). Tool KHÔNG đặt tên: nó chỉ đưa từ khoá và câu mở; Claude đặt tên theo ý người nghe mang về, user duyệt. Buổi dưới 12 phút hoặc một mạch không nên chia (`--khong-session`). Podcast phỏng vấn thì ranh giới tự nhiên là câu hỏi mới của host; thêm cụm đặc thù của user vào danh sách `CUE` trong tool nếu user hay dùng một câu chuyển riêng.

## 5. Kỹ thuật (tóm tắt)

Trục chung = đồng hồ của góc chuẩn (mốc 0 là đầu file đầu của góc chuẩn). Mỗi file góc có `offset`: mốc trục chung nơi file bắt đầu; `in`/`out` trong timeline theo file góc = mốc trục − offset (đã cộng hiệu chỉnh drift tại giữa segment); `audioSrc`/`audioIn` trỏ vào tiếng chủ theo trục chung nên tiếng chạy liền qua mọi cú cắt. Tiếng chủ là `nguon/tieng-chu.wav` (amix mic gần đã căn, có dynaudnorm) hoặc file góc SNR cao nhất. Nhận diện người nói: năng lượng 0,1 giây của từng mic gần trừ nền riêng của mic đó, người nói = mic cao nhất và cao hơn mic nhì ≥ 3 dB; chồng lời khi hai mic gần nhau và cả hai cao; làm mượt 0,7 giây, gộp lượt ngắn dưới 1 giây. assemble.py nhận `audioSrc` từ bản vá slide (2026-09-05); cổng nghiệm thu bắt hình = tiếng trong 0,06 giây như mọi dự án.

## 6. Lưu ý khi quay

- Góc toàn quay liên tục cả buổi; các máy cận có thể tách file, tool ghép được.
- Mỗi máy tự thu tiếng (scratch cũng được) để khớp; tiếng sạch thì dùng mic gần từng người hoặc recorder riêng bỏ vào `nguon/tieng/`.
- Vỗ tay một cái sau khi mọi máy đã chạy: vừa là mốc kiểm tay, vừa là đỉnh tương quan rất sắc.
- Hai máy cận đối xứng, cùng tầm mắt, cùng tiêu cự, cùng cân bằng trắng, cùng fps; đặt máy toàn ở giữa hai người để không vượt trục.
- Podcast: người nghe không nhìn xuống điện thoại; phản ứng của người nghe là nguyên liệu dựng.
