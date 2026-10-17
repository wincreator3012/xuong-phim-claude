---
name: "phim-slideshow-anh"
description: "Dựng clip SLIDESHOW ẢNH từ một thư mục ảnh tĩnh trong thư mục \"xuong-phim-claude\": xếp cốt truyện theo chương, bố cục ảnh bìa, khung ảnh, ảnh đôi, ảnh ba, lưới bốn ảnh, chuyển cảnh mềm theo từng loại khoảnh khắc, thẻ chữ mở đầu, trích dẫn và cảm ơn, zoom chậm theo vị trí gương mặt, render chia đoạn, nghiệm thu và giao. Mặc định phim IM LẶNG, lặp liền mạch, để chiếu vòng quanh trong không gian sự kiện có nhạc sống hay nhạc của hội trường. Kích hoạt khi user nói \"slideshow ảnh\", \"slideshow đám cưới\", \"clip ảnh cưới\", \"ghép ảnh thành clip\", \"clip kỷ niệm từ ảnh\", \"photo montage\", \"chiếu ảnh lặp lại ở sảnh\", hoặc thả một thư mục ảnh và nhờ làm phim từ ảnh. KHÔNG dùng khi nguồn là clip quay (phim-recap-su-kien, phim-dung-bai), khi cần ảnh minh hoạ động chèn vào bài nói (phim-canh-minh-hoa), hay khi chỉ cần thiết kế một tấm ảnh tĩnh (không phải việc của skill phim)."
---

# Slideshow ảnh: phim từ ảnh tĩnh, im lặng, lặp liền mạch

Slideshow ở sự kiện được xem khác phim xem một mạch: khách đứng nói chuyện, ăn uống, đi ngang màn hình, ngước lên vài giây rồi quay đi, rồi lại ngước lên ở một chỗ khác của vòng lặp. Vì vậy mỗi khung phải đứng được một mình, nhịp phải thong thả (người xem có thời gian nhận ra mặt và cảm xúc), không cần nhạc, không cần đọc chữ, và điểm nối đầu-cuối phải mượt để vòng lặp không có "vết khâu". Phim hợp để chiếu liên tục vì cái người ta nhớ là cảm giác ấm áp và các khoảnh khắc đỉnh, không phải thứ tự từng tấm. Nghiên cứu nền và so sánh với cách làm theo nhạc: `skills/phim-slideshow-anh/references/nghien-cuu-slideshow.md`.

Động cơ dựng là code của xưởng (`tools/slideshow-anh/`): ảnh ra thẳng khung hình, không qua Remotion hay timeline video. Cốt truyện (tệp `spec.py`) và thẻ chữ (tệp `slideshow.json`) là hai tệp nhỏ trong thư mục `slideshow` của hồ sơ dự án, nên đổi một ảnh hay một dòng chữ chỉ cần render lại.

## Bước 0 - hỏi một lượt

Đọc `skills/_chung/van-hanh.md` (nguyên lý trước khuôn mẫu). Hỏi người dùng bằng AskUserQuestion những gì chưa có:

1. **Dịp và người xem**: đám cưới, kỷ niệm, lễ tri ân, tiệc công ty. Ai đứng xem và xem ở đâu (sảnh, trên sân khấu, trong bữa tiệc). Chữ trên hình dùng NGÔN NGỮ CỦA NGƯỜI XEM tại chỗ (đám cưới ở Mỹ thì thẻ chữ bằng tiếng Anh).
2. **Độ dài và cách phát**: mặc định im lặng, lặp, khoảng 10 phút cho vòng chiếu dài (khoảng 5 giây mỗi ảnh); nếu phát kèm nhạc thì nói rõ để theo `references/cot-truyen-va-chuyen-canh.md` mục nhịp theo nhạc.
3. **Nội dung thẻ chữ**: tên (đúng chính tả, đúng thứ tự), ngày, nơi chốn, một câu trích hay lời của chính chủ nhân (nếu có), dòng cảm ơn. Thiếu thì đề xuất mặc định rồi hỏi người dùng ở chốt duyệt.
4. **Ảnh nào không dùng và ảnh nào phải có**: người trong ảnh hay muốn bỏ một vài tấm (ví dụ chủ nhân góp ý "bỏ các tấm này"). Danh sách bỏ ghi vào `REMOVED` trong `spec.py`, không xoá ảnh gốc.
5. **Màu chủ đạo của thẻ**: mặc định ngà [ivory] và vàng đồng; đổi theo hoa, váy, bàn tiệc nếu chủ nhân có bảng màu.

## Bước 1 - khảo sát ảnh

```
python3 -I tools/slideshow-anh/run.py "../Du an/<x>" init "<thư mục ảnh>"    # tạo <x>/slideshow/spec.py và slideshow.json từ mẫu
python3 -I tools/slideshow-anh/run.py "../Du an/<x>" faces                    # nhận dạng mặt (YuNet) -> .tam/faces.json
python3 -I tools/slideshow-anh/run.py "../Du an/<x>" sheets                   # bảng ảnh đánh số -> .tam/sheets/
```

Ảnh nguồn để nguyên chỗ người dùng đặt (không chép vào hồ sơ). Mở từng bảng ảnh (stage rồi Read) và ghi lại cho mỗi ảnh: người, khoảnh khắc, ngang hay dọc, ảnh nào gần giống nhau, ảnh nào là đỉnh cảm xúc. `faces` in ra các ảnh không thấy mặt: nếu chủ thể nằm lệch hay là bàn tay, chi tiết, thì đặt `focus_override` trong `slideshow.json` (tâm, nửa rộng, nửa cao theo tỉ lệ ảnh) để zoom không cắt mất chủ thể. Ảnh đen trắng nhiều hạt thêm vào `denoise`.

Ảnh gọi bằng số thứ tự trên bảng ảnh (nhanh) hoặc bằng tên tệp (bền khi thư mục còn thêm bớt ảnh, vì số thứ tự dịch theo). Thêm hay bớt ảnh sau này thì chạy lại `faces`.

## Bước 2 - cốt truyện (chốt duyệt số 1)

Viết `SEQ` trong `spec.py` của thư mục `slideshow` theo `skills/phim-slideshow-anh/references/cot-truyen-va-chuyen-canh.md`: chương, nhịp, gom ảnh (đơn, đôi, ba, lưới bốn), chọn chuyển cảnh theo loại khoảnh khắc, thẻ chữ ở đầu, giữa, cuối. Mỗi ảnh dùng đúng một lần; `plan` báo ảnh thiếu, ảnh trùng và thời gian giữ hình rõ ngắn nhất.

```
python3 -I tools/slideshow-anh/run.py "../Du an/<x>" plan
```

Trình người dùng danh sách chương và vài điểm đáng quyết (ảnh mở, ảnh khép, thẻ trích dẫn đặt đâu, ảnh nào làm trung tâm) trước khi render cả phim. Bản nháp tự động của mẫu (`auto_seq`) chỉ để chạy thử; phim thật cần cốt truyện viết tay.

## Bước 3 - xem trên khung thật

```
... still 7.4 120 454          # ảnh thử 1280x720 tại các mốc giây
... strip <k>                   # sáu khung của chuyển cảnh vào cảnh thứ k
... review                      # mỗi cảnh một khung, 12 cảnh một bảng -> .tam/review/
```

Stage rồi nhìn từng bảng duyệt: mặt có bị cắt không, chữ có chạm viền khung không, chuyển cảnh nào gắt (thường là ảnh bìa nối ảnh khung bằng dissolve hay zoom, đổi sang sweep, focus, lightleak hay glow). Thẻ chữ xem tại các mốc chữ đã hiện đủ (khoảng giây 7 của thẻ mở đầu). Sửa `slideshow.json` (chữ, vị trí y, thời điểm) hay `spec.py` rồi chạy lại `still`.

## Bước 4 - render, ghép, nghiệm thu

```
timeout 112 python3 -I tools/slideshow-anh/run.py "../Du an/<x>" render 4 95       # lặp lại tới khi in XONG-RENDER
python3 -I tools/slideshow-anh/run.py "../Du an/<x>" concat "../Thanh pham/<YYYY-MM tên>/<tên>-1080p.mp4"
python3 -I tools/slideshow-anh/run.py "../Du an/<x>" qc "../Thanh pham/<YYYY-MM tên>/<tên>-1080p.mp4"
```

`render` chia phim thành đoạn 10 giây, chạy bốn tiến trình song song, bỏ qua đoạn đã có nên gọi lại y nguyên được; máy ảo chỉ cho 180 giây mỗi lượt và không giữ tiến trình nền, nên đặt ngân sách 95 giây và `timeout 112`. Phim 10 phút khoảng 8 lượt. Nhìn bảng khung mẫu của `qc` (`.tam/qc/qc.jpg`, gồm khung ở các mốc nối đoạn) bằng mắt, không chỉ tin chữ ĐẠT. Cổng `qc` kiểm: kích thước 1920x1080, đúng số khung và thời lượng của kế hoạch, không có luồng tiếng, khung đầu và khung cuối khớp (vòng lặp). `tools/nghiem-thu.py` thiên về tiếng nói nên không dùng cho phim im lặng này.

Sau khi đã render mà người dùng bỏ hay thêm ảnh: thời gian giữ của mọi ảnh co giãn theo (tổng luôn đúng mục tiêu), nên MỌI đoạn đã render đều hết giá trị. Chuyển `.tam/chunks` sang `.tam/old/` rồi render lại.

## Bước 5 - giao

Thả phim vào `Thanh pham/<YYYY-MM tên dự án>/`, trình người dùng bản đã qua `qc` kèm: số cảnh, số ảnh dùng và ảnh bỏ, thẻ chữ đã đặt, cách phát lặp (VLC chế độ lặp, hoặc trình phát của hội trường), và nhắc thử trên máy chiếu hay màn hình thật của nơi chiếu trước ngày. Người dùng nói "duyệt" thì theo `tools/duyet.py` (CLAUDE.md quy tắc 18).

## Quy tắc cứng

1. Mọi ảnh trong danh sách phải xuất hiện đúng một lần, trừ ảnh nằm trong `REMOVED`; `plan` không báo THIẾU hay TRÙNG thì mới render.
2. Không cắt mặt: zoom và pan luôn giữ khung chủ thể trong hình (động cơ tự giữ); ảnh `faces` không thấy mặt phải có `focus_override` hoặc được xem bằng mắt.
3. Phim im lặng thì không có luồng tiếng; khung đầu và khung cuối phải khớp để lặp liền mạch (`qc` ĐẠT).
4. Tên người, ngày, nơi chốn và câu trích trên thẻ phải được người dùng hay chủ nhân xác nhận; câu trích của người khác ghi đúng tác giả.
5. Ảnh nguồn thuộc về chủ nhân: không xoá, không sửa, không đưa lên dịch vụ ngoài; hồ sơ dự án chỉ giữ cấu hình và tệp nhỏ.
6. Thay đổi ảnh sau khi render là render lại toàn bộ (mục Bước 4); không ghép đoạn cũ với đoạn mới.
7. Không tự commit git (CLAUDE.md quy tắc 7); thành phẩm và nháp ở ngoài repo.

## Nơi tra thêm

- `skills/phim-slideshow-anh/references/cot-truyen-va-chuyen-canh.md`: cách xếp chương, gom ảnh, nhịp, danh mục chuyển cảnh và khi nào dùng.
- `skills/phim-slideshow-anh/references/ky-thuat-dong-co.md`: cấu hình, bố cục, giới hạn máy, lỗi thường gặp, cách thêm hiệu ứng mới.
- `skills/phim-slideshow-anh/references/nghien-cuu-slideshow.md`: nguồn nghiên cứu và khác biệt giữa phim chiếu lặp im lặng và slideshow theo nhạc.
- `docs/BAI-HOC.md` mục 28 (bài học của dự án slideshow đầu tiên).

<!-- ban-nguon: phim-slideshow-anh 2026-10-17 0cf71bba -->
