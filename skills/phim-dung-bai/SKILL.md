---
name: phim-dung-bai
description: Dựng bài giảng/clip giới thiệu hoàn chỉnh từ video talking-head quay thô trong thư mục xưởng (transcript, phương án cắt và overlay, đồ họa, timeline.json, assemble.py, nghiệm thu tự động, xuat-hoan-chinh). Kích hoạt khi user nói "dựng bài", "dựng video", "cắt bài giảng", "ghép intro outro", "chèn infographic", "xuất bản 16:9" hoặc đưa clip quay thô vào thư mục nguon của dự án. Clip ngắn dùng phim-clip-ngan.
---

# Dựng bài giảng hoàn chỉnh từ quay thô

Quy trình chủ lực của xưởng phim: từ video talking-head quay liền mạch (có khoảng dừng giữa các nội dung, có thể nhiều góc máy và cảnh trám) ra thành phẩm 1080p chuẩn phát hành. Mục tiêu: người xem không nhận ra video từng bị cắt - mọi điểm cắt rơi vào khoảng lặng tự nhiên, nhịp gọn nhưng giữ trọn hơi thở sư phạm. **Mạch lạc tối đa là ưu tiên hàng đầu**: luôn chọn cách ít mối nối hơn - cần đổi hình (đồ họa, bảng tên, B-roll) trong lúc lời nói tiếp diễn thì chồng lớp (`overlay`) lên MỘT đoạn quay liên tục thay vì cắt rồi ghép.

**Nguyên tắc nghiệm thu (bài học từ một lỗi lệch hình-tiếng cộng dồn từng lọt qua mắt người xem)**: máy đo những gì mắt không thấy (hình = tiếng, âm lượng, khớp thời lượng), mắt chỉ soi những gì máy không đo được. assemble.py tự kiểm bất biến "hình = tiếng" ở mọi bước; khi nó báo `[NGHIỆM THU] ... KHÔNG ĐẠT` thì DỪNG và tìm nguyên nhân, không dùng `--ep-encode-lai` hay hạ ngưỡng để cho qua. Chưa chạy `tools/nghiem-thu.py` đạt thì chưa được nói "xong".

## Bước 0 - nền tảng (bắt buộc)

Đọc `CLAUDE.md` và `docs/QUY-TRINH-KY-THUAT.md` ở gốc xưởng, đọc `phong-cach/PHONG-CACH.md` (phong cách, chức danh nguyên văn, từ ngữ phải viết đúng, nhạc ưa thích, sổ tay góp ý), làm mục "Khởi động phiên mới" (stage studio lên đám mây, npm install, kiểm composition, sherpa-onnx và model tại máy). File đó là nguồn sự thật về môi trường: egress allowlist, giới hạn device_bash, cách chạy việc dài, cách chuyển file (file >20MB phải split khi commit). Thư mục chưa kết nối thì dừng lại nhờ user kết nối.

Đọc `references/bien-tap.md` của skill này trước khi lên phương án cắt: tiêu chí biên tập, cách chọn `overlay` hay `broll`, cách tính thời lượng đồ họa theo nội dung, ba loại nội dung nên chủ động đề xuất overlay.

## Bước 1 - tiếp nhận và khảo sát

Tư liệu ở `du-an/<tên>/nguon/` (chưa có thì tạo theo `du-an/_mau/`). Chạy `python3 tools/mediainfo.py "du-an/<tên>/nguon"` (thời lượng, độ phân giải, fps, âm thanh). Khám màu mọi nguồn theo skill phim-mau-sac (`python3 tools/mau-sac.py kham "du-an/<tên>"`); footage HDR bắt buộc có đơn tonemap trong `mau-sac.json` trước khi dựng.

Làm rõ với user một lần, chỉ hỏi những gì `phong-cach/PHONG-CACH.md` chưa trả lời: ngang, dọc hay cả hai; độ dài; theme sáng/tối; nhạc nền nào trong `nhac-nen/THU-VIEN.md`; đoạn phải giữ nguyên. User vắng mặt thì lấy mặc định từ PHONG-CACH.md (không có thì ngang, light, nhạc bookends) và ghi rõ giả định. Nguồn 25fps thì đặt `"fps": 25` trong timeline; mặc định 30.

## Bước 2 - transcript

User đã có transcript thì vẫn chạy bước khoảng lặng (silences.json). Chưa có:

```
python3 tools/transcribe.py "du-an/<tên>/nguon/<clip>.mp4" --out-dir "du-an/<tên>/transcript"
python3 tools/nghiem-thu.py transcript "du-an/<tên>"
```

Lệnh thứ hai bắt quãng >8s có tiếng mà không có chữ (Whisper bỏ đoạn) và mốc đảo - KHÔNG ĐẠT thì nhận dạng lại quãng đó với cửa sổ rộng (skill phim-transcript) trước khi lên phương án cắt. Model mặc định turbo; `--model small` khi gấp. Bài >90 phút: tách audio từng 30 phút, transcript từng phần, cộng offset. Việc chạy lâu: mục "Việc chạy dài" trong docs/QUY-TRINH-KY-THUAT.md.

## Bước 3 - phương án cắt VÀ phương án overlay (chốt duyệt số 1)

Đọc `transcript/<clip>.txt`, áp tiêu chí `bien-tap.md`, trình user MỘT bảng phương án cắt TRƯỚC KHI dựng: mốc nguồn | nội dung | giữ/bỏ | lý do.

Cùng lúc chủ động đề xuất overlay cho ba loại nội dung (không chờ user yêu cầu): (1) tên chương trình/chuyên đề/framework được xướng; (2) các bước quy trình hoặc cấu phần framework; (3) key message đáng trích riêng. Bảng overlay ghi: loại, mốc bắt đầu-kết thúc THEO LỜI NÓI, chữ dự kiến (trích từ transcript), composition (Caption/InfoList/InfoSteps/InfoQuote/SectionTitle/Benefits). Kèm vị trí thẻ chuyển phần, B-roll, tổng thời lượng. Thẻ toàn màn hình phải cách nhau tối thiểu 5 giây cảnh quay chính; dày hơn thì đổi sang overlay bán trong suốt (Caption/Benefits, không tính vào quy tắc này). Gửi qua SendUserMessage nếu đang giữa chuỗi tool. Chờ user duyệt CẢ HAI bảng; user vắng lâu thì tiếp tục với phương án đã đề xuất và ghi rõ.

## Bước 4 - đồ họa và timeline

Đồ họa: intro/outro LUÔN từ preset `do-hoa-chung/preset-intro-outro-<ngang|doc>.json` (đủ placeholder, hàng 1-3 logo từ `brand/logo/`; tinh chỉnh theo `do-hoa-chung/GHI-CHU.md`). Đồ họa khác soạn job theo `du-an/_mau/do-hoa/`. Render bằng `node tools/render-do-hoa.mjs <job> --studio <studio-đám-mây>` - script tự đo từng file (thời lượng khớp `durationInSeconds`, fps, webm còn alpha), ghi `do-hoa-manifest.json`, thoát mã 1 là có file sai: sửa job, render lại, không đem file sai vào timeline. Commit về `du-an/<tên>/do-hoa/<ngang|doc>/`. Chi tiết: skill phim-do-hoa, `brand/brand.json`. Chữ trong đồ họa lấy từ chính lời giảng, không bịa thêm ý.

Bài dài mặc định intro đứng đầu; NHƯNG nếu câu mở đầu tự nó là câu chốt mạnh thì áp quy tắc "hook trước, intro sau": Hook là segment ĐẦU TIÊN (snap đúng khoảng lặng), Intro là segment `type:"insert"` NGAY SAU (không dùng field `intro` cấp cao nhất vì nó luôn build trước mọi segment) - xem `bien-tap.md` mục "Hook trước Intro". Không chắc thì hỏi user.

Thời lượng overlay tính theo `bien-tap.md` (lớn hơn giữa thời lượng lời nói và thời gian đọc chữ, cộng đệm 1-2s), không đặt số tròn. Có `tu-lieu/TU-LIEU.md` (skill phim-tu-lieu) thì đọc khi soạn timeline; ảnh tĩnh chuyển Ken Burns theo lệnh trong đó; ghi công gom vào mô tả video.

Timeline `du-an/<tên>/timeline.json` theo schema trong docstring `tools/assemble.py`:
- `snap: true` cho mọi đoạn video
- Gộp nhiều nội dung liệt kê/nhấn mạnh vào MỘT đoạn quay liên tục bằng `overlay` dạng LIST (mỗi cái một `at` theo lời nói, không chồng lấn) thay vì tách segment hay dùng `broll`; chỉ tách segment khi cần BỎ nội dung ở giữa, và cắt vào khoảng lặng thật
- **Hai hệ mốc thời gian, dễ nhầm**: `in`/`out` và `broll[].at` là mốc TRONG FILE NGUỒN; `overlay[].at` TƯƠNG ĐỐI từ đầu đoạn (sau snap). Overlay muốn hiện lúc lời nói ở mốc nguồn T: `at = T - in`. Overlay chỉ phủ tới B-roll đầu tiên của đoạn
- Nhiều góc máy: đổi nguồn giữa các segment liên tiếp là đủ chuyển cảnh
- Gắn `chapter` cho các phần chính (chapters.txt cho YouTube)

Soạn xong, kiểm ngay: `python3 tools/assemble.py --project "du-an/<tên>" --kiem-tra` - bắt file thiếu, `out` vượt nguồn, `overlay.at` vượt đoạn, `broll.at` ngoài đoạn, B-roll chồng nhau, cảnh báo overlay bị cắt cụt. Hết lỗi rồi mới dựng.

## Bước 5 - bản nháp (chốt duyệt số 2)

```
python3 tools/assemble.py --project "du-an/<tên>" --preview
```

Bản 480p, KHÔNG truyền `--out` (script tự đặt `<tên>-<aspect>-nhap.mp4`); lệnh bị ngắt thì gọi lại y nguyên, assemble tự resume (cache tự vô hiệu khi đổi code, tham số hay file nguồn). Cuối lượt assemble in dòng `NGHIỆM THU: hình = tiếng = tổng N part` và ghi `<file>.map.json` (mốc nguồn sang mốc thành phẩm từng part) cùng `<file>.nghiem-thu.json`. Báo user mở `xuat-nhap/<tên>-<aspect>-nhap.mp4` xem trên máy. Lặp nháp tới khi ưng.

Assemble dừng với `[NGHIỆM THU] KHÔNG ĐẠT`: đọc bảng chẩn đoán, xử lý đúng part đó (truncate part + .sig rồi chạy lại; kiểm nguồn cắt cụt, overlay/B-roll vượt đoạn); tuyệt đối không hạ ngưỡng, không bật `--ep-encode-lai`. User báo chỗ nghe/nhìn bất thường: đối chiếu vị trí mối nối trong `map.json` trước, mối nối là nguồn giật phổ biến nhất (xem `bien-tap.md`).

## Bước 6 - bản chính và nghiệm thu

Chạy assemble không `--preview` cho từng aspect (không `--out`, gọi lại y nguyên nếu bị ngắt). Nghiệm thu, không bỏ mục nào:

1. **Cổng máy đo, chạy trước mọi thứ**: `python3 tools/nghiem-thu.py video "du-an/<tên>/xuat-nhap/<file>.mp4" --khung <ngang|doc> --anh` phải ĐẠT (mã thoát 0): hình = tiếng trong 0.06s (không còn 0.3s như trước 2026-09-05), khớp tổng part, khung/fps/codec, -14±1 LUFS và true peak, im lặng dài, hình đứng, quãng đen, còn HDR không; xuất `<file>.luoi.jpg` 12 khung có mốc giờ
2. Stage `<file>.luoi.jpg` và NHÌN: intro/outro đúng chỗ, bảng tên hiện, không khung đen, không lệch crop, chữ không tràn
3. Kiểm TỪNG mối nối bằng `silencedetect`/`volumedetect` quanh mốc `start`/`end` của từng part trong `map.json` (không tính tay)
4. Mỗi overlay: mốc thành phẩm = `start` của part + `at`, khớp bảng Bước 3; chưa chắc thì xuất 1 frame xem
5. Nghe điểm vào/ra nhạc (xuất 5s audio quanh mốc nếu cần)
6. chapters.txt khớp `map.json` nếu có chapter

Đạt rồi mới COPY sang `du-an/<tên>/xuat-hoan-chinh/<tên>-<aspect>.mp4` (bỏ `-nhap`) và báo: tên file, thời lượng, dung lượng, chapters, kèm dòng "nghiệm thu máy: ĐẠT (hình = tiếng, -14 LUFS)". Thành phẩm đã ở máy user, không cần commit.

## Ghi nhớ vận hành

- `.tam/` sau khi dựng bị truncate còn 0 byte nhưng tên còn - bình thường
- Sửa script/studio ở đám mây phải commit về máy ngay (máy là bản gốc). Sửa logic encode trong `assemble.py` thì đổi `TOOL_VERSION` và dựng lại một dự án nhỏ qua cổng nghiệm thu trước khi dùng thật
- **Lớp lỗi "bất biến bị vi phạm nhưng không ai kiểm"**: mọi file trung gian phải hình = tiếng; bước sau chỉ đi tiếp khi bước trước đo đạt; không để nhánh "sửa ngầm" (encode lại, hạ ngưỡng, bắt ngoại lệ rồi bỏ qua) che dấu vết; con số khớp "gần đúng" khó hiểu là dấu hiệu, không phải may mắn
- Kết thúc dự án đáng nhớ: ghi bài học chung vào `docs/BAI-HOC.md`, góp ý riêng của người dùng vào "Sổ tay góp ý" trong `phong-cach/PHONG-CACH.md`; sửa nguồn mặc định (brand.json, preset) ngay khi một góp ý lặp lại lần thứ hai. Khi đề xuất cập nhật skill, `description` là mô tả KÍCH HOẠT, không ghi changelog vào đó
