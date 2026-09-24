---
name: phim-bai-giang-slide
description: Dựng clip bài giảng ngang có SLIDE trong thư mục xưởng (gốc repo xuong-phim-claude): nhập slide (PPTX, PDF, bộ ảnh, quay màn hình), khớp từng slide với lời giảng, đề xuất dàn hình xen ba trạng thái mặt / slide toàn khung / cả hai theo nghiên cứu học tập đa phương tiện, dựng bằng assemble.py với trường layout và slide. Kích hoạt khi user nói "bài giảng có slide", "dựng clip có slide", "hiện slide", "picture in picture", "quay màn hình kèm mặt", hoặc nguon có file slide cạnh video quay mặt.
---

# Bài giảng có slide: mặt, slide, hay cả hai

Mở rộng của quy trình dựng bài (skill phim-dung-bai - vẫn áp dụng toàn bộ: Bước 0 nền tảng, transcript và cổng nghiệm thu transcript, phương án cắt, đồ họa, bản nháp, nghiệm thu máy bắt buộc). Skill này thêm đúng một lớp: quyết định người học NHÌN gì ở từng quãng lời giảng và dựng lớp hình đó. Chi tiết cơ sở nghiên cứu và bảng quy tắc đầy đủ ở `references/bo-cuc-slide.md` (bản gốc trong `skills-nguon/phim-bai-giang-slide/`).

Nguyên tắc rút từ nghiên cứu (Wang & Antonenko 2017; Polat 2022; Alemdag 2022; meta-analysis ánh nhìn 2023; Guo, Kim & Rubin 2014; Mayer 2020): mặt giảng viên không tự nâng kết quả học nhưng nâng kết nối và hài lòng; khi nội dung dày, mặt chia chú ý; xen kẽ mặt và slide giữ người xem lâu hơn; đổi trạng thái hình theo NỘI DUNG lời nói, không theo vị trí trong bài. Vì vậy: nói cái gì cần đọc thì cho slide đủ lớn; nói cái gì cần cảm thì cho mặt; slide đơn giản thì cả hai.

## Năm bố cục (khung ngang, toạ độ trong `do-hoa-chung/bo-cuc/bo-cuc.json`)

**Mặc định nghiêng về `ca-hai`, `slide` toàn khung là ngoại lệ phải có lý do cụ thể.** Che hết màn hình bằng slide xoá luôn người nói khỏi hình - đi ngược đúng phát hiện nghiên cứu ở `references/bo-cuc-slide.md` mục 1 (xen mặt với slide giữ người xem lâu hơn; hiện diện giảng viên nâng kết nối/hài lòng dù không tự nâng điểm ghi nhớ). Slide bài giảng thông thường (gạch đầu dòng, sơ đồ đơn, ảnh minh hoạ) gần như luôn đọc được ở 73% khung của `ca-hai` - dùng `ca-hai` trước, chỉ đổi sang `slide` toàn khung khi kiểm THẬT (thu ảnh `ca-hai` về 480 ngang như Bước 4 mục 1) cho thấy chữ/số liệu không đọc được, hoặc slide có nhiều animation/là quay màn hình. Ngưỡng số từ trong bảng dưới chỉ là ước lượng ban đầu để `slide-khop.py` chạy tự động, không phải căn cứ chốt.

| layout | Hình | Dùng khi |
|---|---|---|
| `mat` | mặt toàn khung | dẫn nhập, kể chuyện, chuyển ý, kết, lời mời - không có gì để đọc |
| `ca-hai` | slide chính 73% + mặt nhỏ 4:5 góc dưới phải | MẶC ĐỊNH cho mọi slide đọc được ở 73% khung - đa số slide bài giảng thông thường (gạch đầu dòng, sơ đồ đơn, số liệu vừa, trích dẫn dài); mặt giữ hiện diện, dải dưới trống cho pill |
| `slide` | slide toàn khung trên nền giấy | CHỈ khi đã thử `ca-hai` và kiểm đọc thật thất bại: bảng nhiều cột/hàng, sơ đồ dày chi tiết nhỏ, slide động/quay màn hình |
| `mat-chinh` | mặt toàn khung + slide thẻ nhỏ góc trên phải | slide < 12 từ: tên khung, trích dẫn ngắn, một ảnh - người nói là chính |
| `chia-doi` | mặt trái 816x900, slide phải 888x500 | cần thấy cử chỉ tay/biểu cảm cùng lúc với một hình đơn giản |

Nhịp: đổi tại điểm ngắt hơi (`snap: true`), mỗi trạng thái tối thiểu 6 giây, slide toàn khung ít nhất bằng thời gian đọc hết chữ (2,5 từ/giây) cộng 1-2 giây; sau quãng slide dày quay về `mat` ít nhất một câu. Tín hiệu: `slideZoom: [x, y, w, h]` (tỉ lệ 0-1, chọn vùng gần 16:9) khi lời giảng chỉ vào một phần của slide dày.

## Bước 1 - nhập slide

Slide user để trong `du-an/<tên>/nguon/` (PPTX, PDF, thư mục ảnh, hoặc video quay màn hình; Keynote thì nhờ user xuất PDF/PPTX). Chạy:

```
python3 tools/slide-nguon.py "du-an/<tên>/nguon/<slide>" --project "du-an/<tên>"
```

Ra `slide/slide-NN.png` (tối đa 1920 ngang) và `slide/slide.json` (chữ, ghi chú diễn giả, số từ, mốc `ts` nếu từ quay màn hình). Môi trường: PPTX cần LibreOffice (soffice), PDF cần poppler (pdftoppm) - VM trên MacBook Air đã có cả hai (kiểm 2026-09-05), sandbox đám mây cũng có; máy khác kiểm `which soffice pdftoppm` trước, thiếu thì chạy bước này ở đám mây rồi commit `slide/` về máy. Bộ ảnh và quay màn hình chạy ở đâu cũng được. Slide không có chữ (ảnh, quay màn hình): stage vài ảnh lên và ĐỌC để biết nội dung từng slide trước khi khớp.

## Bước 2 - khớp slide với lời giảng, đề xuất dàn hình (chốt duyệt cùng phương án cắt)

Cần transcript đã qua `nghiem-thu.py transcript`. Chạy:

```
python3 tools/slide-khop.py "du-an/<tên>" --clip "<tên file nguồn không đuôi>" [--lech <giây>] [--bo-qua 1,2]
```

- Không có mốc quay màn hình: khớp bằng quy hoạch động đơn điệu trên từ khoá (chữ slide + ghi chú vs câu transcript; cụm hai từ nặng hơn từ đơn; có "khoảng trống" để lời dẫn không bị nuốt vào slide). Slide tin cậy < 0.35 phải đọc transcript tự xác nhận.
- Có quay màn hình: dùng mốc `ts` + `--lech` (quay màn hình bắt đầu trễ bao nhiêu giây so với quay mặt; đo bằng tiếng vỗ tay/câu "bắt đầu" ở cả hai file).
- `--bo-qua`: slide bìa, cảm ơn, mục lục không dùng.

Ra `slide/DAN-HINH.md` (bảng: mốc nguồn, slide, bố cục đề xuất, tin cậy, lý do), `slide/slide-khop.json`, `slide/timeline-slide-nhap.json`. Bố cục đề xuất chỉ theo số từ - Claude ĐỌC lại từng khối theo ba câu hỏi (người học cần nhìn gì? slide có đơn giản đến mức mặt không tranh chú ý? có cần thấy cử chỉ không?) và sửa: ví dụ slide 15 từ nhưng là sơ đồ → `slide`; slide 30 từ nhưng đang kể chuyện cá nhân → `mat-chinh`; đoạn chuyển ý dài → `mat`. Trình bảng dàn hình CÙNG bảng phương án cắt và overlay của phim-dung-bai cho user duyệt một lần (SendUserMessage nếu đang giữa chuỗi tool). Ghi rõ slide nào không khớp được và đề xuất bỏ/đặt tay.

## Bước 3 - timeline và dựng

Chép segments từ `timeline-slide-nhap.json` vào `timeline.json` sau khi chỉnh theo bảng đã duyệt; kiểm đuôi file nguồn (.mp4/.MP4/.MOV). Mỗi segment thêm `"layout"` và `"slide": "slide/slide-NN.png"` (bắt buộc khi layout khác `mat`), tùy chọn `"slideZoom"`; cấp cao nhất `"theme": "light"|"dark"` chọn nền khung. Overlay pill, fade, chapter, B-roll dùng như thường (B-roll bỏ qua layout trong quãng của nó). Intro/outro từ preset như mọi dự án; hook-trước-intro áp dụng như phim-dung-bai.

Kiểm rồi dựng: `python3 tools/assemble.py --project "du-an/<tên>" --kiem-tra` (bắt layout sai, thiếu slide, slideZoom sai, thiếu bo-cuc) → `--preview` → duyệt → bản chính. Bố cục ghép ở 1920x1080 rồi thu về preview nên bản nháp phản ánh đúng tỉ lệ. Thiếu `do-hoa-chung/bo-cuc/`: chạy `python3 tools/bo-cuc-slide.py`.

## Bước 4 - nghiệm thu

Như phim-dung-bai Bước 6 (cổng `nghiem-thu.py video` bắt buộc, ảnh lưới, mối nối theo `map.json`), thêm:

1. Trên ảnh lưới và 1 frame mỗi bố cục: chữ slide đọc được ở cỡ điện thoại (thu ảnh về 480 ngang và nhìn) - không đọc được thì đổi `ca-hai` sang `slide` hoặc dùng `slideZoom`
2. **Mặt trong ô nhỏ không cắt trán/cằm, đủ toàn thân khi có cử chỉ**: vì `ca-hai` giờ là bố cục mặc định (mục "Năm bố cục" trên), một dự án có thể có hàng chục đoạn `ca-hai` - kiểm `cropFocus` ở NHIỀU mốc rải đều trong TỪNG đoạn (không chỉ một khung đầu đoạn), nhìn cả hai mép trái-phải, đặc biệt khi người nói di chuyển/xoay người/đổi tư thế giữa đoạn. Kỹ thuật đo nhanh: trích khung hình CHƯA crop tại vài mốc trong đoạn, thử vài giá trị `cropFocus`, chọn giá trị giữ đủ người xuyên suốt; nếu người nói đổi vị trí lớn ngay trong một đoạn dài, tách thành nhiều segment `ca-hai` liên tiếp mỗi đoạn một `cropFocus` riêng thay vì ép một giá trị chung không sạch ở đâu cả
3. Slide đúng mốc lời nói: mở `map.json`, với 2-3 slide quan trọng trích frame tại `start` của part và đọc lại câu transcript bao quanh
4. Quãng `slide` đứng hình là cố ý (nghiem-thu đã bỏ cảnh báo theo `map.json`); quãng `mat`/`ca-hai` đứng hình là lỗi

Báo kết quả kèm số quãng theo từng bố cục (ví dụ "mặt 40%, slide 25%, cả hai 35%") để user cảm được nhịp, và dòng "nghiệm thu máy: ĐẠT".

## Ghi nhớ

- Đổi toạ độ/bo góc bố cục: sửa `tools/bo-cuc-slide.py`, chạy lại để sinh khung/mask, đổi `TOOL_VERSION` trong assemble.py nếu đổi logic ghép; commit cả `do-hoa-chung/bo-cuc/` về máy
- Slide chữ nhỏ hơn 24pt không nên vào `ca-hai`; nhắc user khi có dịp: một ý một slide, ít animation, có ghi chú diễn giả thì khớp chính xác hơn
- Khi user quay mặt và màn hình riêng, nhắc bắt đầu cả hai bằng một tín hiệu chung để đo `--lech`
- Khi đề xuất cập nhật skill, `description` là mô tả kích hoạt, không chứa dấu ngoặc nhọn, không ghi changelog
