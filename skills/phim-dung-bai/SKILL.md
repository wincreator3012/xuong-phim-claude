---
name: "phim-dung-bai"
description: "Dựng bài giảng/clip giới thiệu hoàn chỉnh từ video talking-head quay thô trong thư mục \"xuong-phim-claude\" (transcript, phương án cắt và overlay, đồ họa, timeline.json, assemble.py, nghiệm thu tự động, xuat-hoan-chinh). Kích hoạt khi user nói \"dựng bài\", \"dựng video\", \"cắt bài giảng\", \"ghép intro outro\", \"chèn infographic\", \"xuất bản 16:9\" hoặc đưa clip quay thô vào thư mục nguon của dự án. Clip ngắn dùng phim-clip-ngan; bài giảng có slide dùng phim-bai-giang-slide; podcast hay nhiều góc máy dùng phim-multicam; phỏng vấn nhiều nhân vật dùng phim-tai-lieu-phong-van; chỉ có file ghi âm dùng phim-infomotion hoặc phim-hoat-hoa."
---

# Dựng bài giảng hoàn chỉnh từ quay thô

Quy trình chủ lực của xưởng phim: từ video talking-head quay liền mạch (có khoảng dừng giữa các nội dung, có thể nhiều góc máy và cảnh trám) ra thành phẩm 1080p chuẩn phát hành. Mục tiêu: người xem không nhận ra video từng bị cắt - mọi điểm cắt rơi vào khoảng lặng tự nhiên, nhịp gọn nhưng giữ trọn hơi thở sư phạm. **Mạch lạc tối đa là ưu tiên hàng đầu**: luôn chọn cách ít mối nối hơn - cần đổi hình (đồ họa, bảng tên, B-roll) trong lúc lời nói tiếp diễn thì chồng lớp (`overlay`) lên MỘT đoạn quay liên tục thay vì cắt rồi ghép.

**Nguyên tắc nghiệm thu (bài học 2026-09-05)**: máy đo những gì mắt không thấy (hình = tiếng, âm lượng, khớp thời lượng), mắt chỉ soi những gì máy không đo được. assemble.py tự kiểm bất biến "hình = tiếng" ở mọi bước; khi nó báo `[NGHIỆM THU] ... KHÔNG ĐẠT` thì DỪNG và tìm nguyên nhân, không hạ ngưỡng hay tìm đường vòng để cho qua. Chưa chạy `tools/nghiem-thu.py` đạt thì chưa được nói "xong".

## Bước 0 - nền tảng (bắt buộc)

Đọc `skills/_chung/van-hanh.md` (đọc gì trước, hai nơi chạy lệnh, truyền file, chữ và chức danh), `skills/_chung/timeline-va-dung.md`, `skills/_chung/overlay-va-the.md`, `skills/_chung/nghiem-thu-dung-y.md`. Phiên chưa dựng sandbox thì làm mục "Khởi động phiên mới" của `docs/QUY-TRINH-KY-THUAT.md` (nguồn sự thật về môi trường, lệnh, việc dài). Thư mục chưa kết nối thì dừng lại nhờ người dùng kết nối.

Đọc `skills/phim-dung-bai/references/bien-tap.md` trong thư mục xưởng trước khi lên phương án cắt (bản chuẩn, luôn mới nhất): tiêu chí biên tập, cách chọn `overlay` hay `broll`, cách tính thời lượng đồ họa theo nội dung, ba loại nội dung nên chủ động đề xuất overlay.

## Bước 1 - tiếp nhận và khảo sát

Tư liệu ở `du-an/<tên>/nguon/` (chưa có thì tạo theo `du-an/_mau/`). Chạy `python3 tools/mediainfo.py "du-an/<tên>/nguon"` (thời lượng, độ phân giải, fps, âm thanh). Khám màu mọi nguồn theo skill phim-mau-sac (`python3 tools/mau-sac.py kham "du-an/<tên>"`); footage HDR bắt buộc có đơn tonemap trong `mau-sac.json` trước khi dựng.

Làm rõ với user một lần, chỉ hỏi những gì `phong-cach/PHONG-CACH.md` chưa trả lời: ngang, dọc hay cả hai; độ dài; theme sáng/tối; nhạc nền nào trong `nhac-nen/`; đoạn phải giữ nguyên. User vắng mặt thì chọn mặc định (ngang, light, nhạc bookends) và ghi rõ giả định. Nguồn 25fps thì đặt `"fps": 25` trong timeline; mặc định 30.

## Bước 2 - transcript

User đã có transcript thì vẫn chạy bước khoảng lặng (silences.json). Chưa có: gỡ băng theo skill phim-transcript. Ưu tiên chạy trên Mac bằng large-v3 (khi máy là Mac thật và đã tải model này, xem `tools/models/TAI-MODEL.md`) (xếp việc bằng `python3 tools/hang-doi-go-bang.py them ...`, nhờ người dùng bấm đúp `Go bang tren Mac.command`); người dùng không ở máy hoặc cần ngay thì chạy trong VM (tự chọn turbo) và ghi rõ trong báo cáo. Sau đó luôn chạy:

```
python3 tools/nghiem-thu.py transcript "du-an/<tên>"
```

Lệnh này bắt quãng >8s có tiếng mà không có chữ (Whisper bỏ đoạn) và mốc đảo - KHÔNG ĐẠT thì nhận dạng lại quãng đó với cửa sổ rộng (skill phim-transcript) trước khi lên phương án cắt. Bài >90 phút: tách audio từng 30 phút, transcript từng phần, cộng offset. Việc chạy lâu: mục "Việc chạy dài hơn 180 giây" trong `docs/QUY-TRINH-KY-THUAT.md`.

## Bước 3 - phương án cắt VÀ phương án overlay (chốt duyệt số 1)

Đọc `transcript/<clip>.txt`, áp tiêu chí `bien-tap.md`, trình user MỘT bảng phương án cắt TRƯỚC KHI dựng: mốc nguồn | nội dung | giữ/bỏ | lý do.

Cùng lúc chủ động đề xuất overlay cho ba loại nội dung (không chờ user yêu cầu): (1) tên chương trình/chuyên đề/framework được xướng; (2) các bước quy trình hoặc cấu phần framework; (3) key message đáng trích riêng. Thêm một loại thứ tư: (4) đoạn người dùng GIẢI THÍCH một cơ chế, quy trình, so sánh, con số hay hướng dẫn một nhịp thực hành thì đề xuất một cảnh minh hoạ vẽ riêng theo skill phim-canh-minh-hoa, ghi kiểu chèn (toàn khung, nền là khung hình mờ, thẻ nổi cạnh người dùng, người dùng thu vào góc) và kịch bản cảnh bằng chữ (Thấy gì, các cảnh con có mốc, chữ ký chuyển động). Bảng overlay ghi: loại, mốc bắt đầu-kết thúc THEO LỜI NÓI, chữ dự kiến (trích từ transcript), composition (Benefits/InfoList/InfoSteps/InfoQuote/InfoStat/SectionTitle/LowerThird; một dòng chữ nổi bật = Benefits một mục `showIndex:false`, studio không có "Caption"). Kèm vị trí thẻ chuyển phần, B-roll, tổng thời lượng. Thẻ toàn màn hình phải cách nhau tối thiểu 5 giây cảnh quay chính; dày hơn thì đổi sang overlay bán trong suốt (Benefits, không tính vào quy tắc này). Gửi qua SendUserMessage nếu đang giữa chuỗi tool. Chờ user duyệt CẢ HAI bảng; user vắng lâu thì tiếp tục với phương án đã đề xuất và ghi rõ.

## Bước 4 - đồ họa và timeline

Đồ họa: intro/outro LUÔN từ preset `do-hoa-chung/preset-intro-outro-<ngang|doc>.json` (đủ placeholder, hàng 1-3 logo từ `brand/logo/`; tinh chỉnh theo `do-hoa-chung/GHI-CHU.md`). Đồ họa khác soạn job theo `du-an/_mau/do-hoa/`. Render bằng `node tools/render-do-hoa.mjs <job> --studio <studio-đám-mây>` - script tự đo từng file (thời lượng khớp `durationInSeconds`, fps, webm còn alpha), ghi `do-hoa-manifest.json`, thoát mã 1 là có file sai: sửa job, render lại, không đem file sai vào timeline. Commit về `du-an/<tên>/do-hoa/<ngang|doc>/`. Chi tiết: skill phim-do-hoa, `brand/brand.json`. Chữ trong đồ họa lấy từ chính lời giảng, không bịa thêm ý. Cảnh minh hoạ đã duyệt: viết, soi (`canh.mjs kiem`, `người dùng`), chụp theo skill phim-canh-minh-hoa; kiểu nền mờ cần một khung hình trích trên máy (`tools/canh-ghep.py khung`), kiểu thu vào góc ghép trên máy (`tools/canh-ghep.py pip`, `--at` bằng đúng `broll.at`); mẫu timeline bốn kiểu ở `skills/phim-canh-minh-hoa/references/viet-canh.md` mục 5.

Bài dài mặc định intro đứng đầu; NHƯNG nếu câu mở đầu tự nó là câu chốt mạnh thì áp quy tắc "hook trước, intro sau": Hook là segment ĐẦU TIÊN (snap đúng khoảng lặng), Intro là segment `type:"insert"` NGAY SAU, đánh dấu `"role": "intro"` để nhạc bookends bám đúng thẻ intro (không dùng field `intro` cấp cao nhất vì nó luôn build trước mọi segment; thiếu `role` thì `--kiem-tra` cảnh báo) - xem `bien-tap.md` mục "Hook trước Intro". Không chắc thì hỏi user.

Thời lượng overlay tính theo `bien-tap.md` (lớn hơn giữa thời lượng lời nói và thời gian đọc chữ, cộng đệm 1-2s), không đặt số tròn. Có `tu-lieu/TU-LIEU.md` (skill phim-tu-lieu) thì đọc khi soạn timeline; ảnh tĩnh chuyển Ken Burns theo lệnh trong đó; ghi công gom vào mô tả video.

Timeline `du-an/<tên>/timeline.json` theo schema trong docstring `tools/assemble.py`:
- `snap: true` cho mọi đoạn video
- Gộp nhiều nội dung liệt kê/nhấn mạnh vào MỘT đoạn quay liên tục bằng `overlay` dạng LIST (mỗi cái một `at` theo lời nói, không chồng lấn) thay vì tách segment hay dùng `broll`; chỉ tách segment khi cần BỎ nội dung ở giữa, và cắt vào khoảng lặng thật
- **Hai hệ mốc thời gian, dễ nhầm**: `in`/`out` và `broll[].at` là mốc TRONG FILE NGUỒN; `overlay[].at` TƯƠNG ĐỐI từ đầu đoạn (sau snap). Overlay muốn hiện lúc lời nói ở mốc nguồn T: `at = T - in`. Overlay chỉ phủ tới B-roll đầu tiên của đoạn
- Nhiều góc máy: đổi nguồn giữa các segment liên tiếp là đủ chuyển cảnh
- Gắn `chapter` cho các phần chính (chapters.txt cho YouTube)
- Kết bài: đoạn nội dung cuối đặt `fadeOut` 0,4-0,6 giây; chỉ muốn tiếng tắt dần thì `fadeOutAudio`; outro tĩnh thì mờ cả hình lẫn tiếng khoảng 1,5 giây (`_chung/timeline-va-dung.md` mục "Điểm cắt, fade, kết")

Soạn xong, kiểm ngay: `python3 tools/assemble.py --project "du-an/<tên>" --kiem-tra` - bắt file thiếu, `out` vượt nguồn, `overlay.at` vượt đoạn, `broll.at` ngoài đoạn, B-roll chồng nhau, cảnh báo overlay bị cắt cụt. Hết lỗi rồi mới dựng.

## Bước 5 - bản nháp (chốt duyệt số 2)

```
python3 tools/assemble.py --project "du-an/<tên>" --preview --out "<tên>-<aspect>-nhap1"
```

Bản 480p. LUÔN truyền `--out` tường minh có số nháp (`-nhap1`, `-nhap2`...): không truyền thì mọi vòng dùng chung tên `<tên>-<aspect>-nhap.mp4` và vòng sau lặng lẽ ghi đè vòng trước (đã xảy ra thật). Tên kết thúc bằng `-nhapN` thì script không nối thêm `-nhap`. Lệnh bị ngắt thì gọi lại y nguyên, assemble tự resume (cache tự vô hiệu khi đổi code, tham số hay file nguồn). Cuối lượt assemble in dòng `NGHIỆM THU: hình = tiếng = tổng N part` và ghi `<file>.map.json` (mốc nguồn sang mốc thành phẩm từng part) cùng `<file>.nghiem-thu.json`. Báo user mở `xuat-nhap/<tên>-<aspect>-nhapN.mp4` xem trên máy. Lặp nháp tới khi ưng, mỗi vòng tăng số.

Assemble dừng với `[NGHIỆM THU] KHÔNG ĐẠT`: đọc bảng chẩn đoán, xử lý đúng part đó (truncate part + .sig rồi chạy lại; kiểm nguồn cắt cụt, overlay/B-roll vượt đoạn); tuyệt đối không hạ ngưỡng. Đồ họa chèn mang đuôi tiếng thừa 0,02-0,06s thì assemble.py tự cắt về bằng hình và in một dòng thông báo, không cần xử lý tay. User báo chỗ nghe/nhìn bất thường: đối chiếu vị trí mối nối trong `map.json` trước, mối nối là nguồn giật phổ biến nhất (xem `bien-tap.md`).

## Bước 6 - bản chính và nghiệm thu

Chạy assemble không `--preview` cho từng aspect với `--out "<tên>-<aspect>"` (gọi lại y nguyên nếu bị ngắt). Nghiệm thu, không bỏ mục nào:

1. **Cổng máy đo, chạy trước mọi thứ**: `python3 tools/nghiem-thu.py video "du-an/<tên>/xuat-nhap/<file>.mp4" --khung <ngang|doc> --anh` phải ĐẠT (mã thoát 0): hình = tiếng trong 0.06s, khớp tổng part, đồng bộ hình-tiếng so với NGUỒN tại 10 mốc (cổng tự gọi `tools/do-dong-bo.py`: tiếng phải khớp nguồn trong ±25 ms, hình - tiếng trong ±50 ms, không trôi quá 15 ms mỗi phút), khung/fps/codec, -14±1 LUFS và true peak, im lặng dài, hình đứng, quãng đen, còn HDR không; xuất `<file>.luoi.jpg` 12 khung có mốc giờ
2. Stage `<file>.luoi.jpg` và NHÌN: intro/outro đúng chỗ, bảng tên hiện, không khung đen, không lệch crop, chữ không tràn
3. Kiểm TỪNG mối nối bằng `silencedetect`/`volumedetect` quanh mốc `start`/`end` của từng part trong `map.json` (không tính tay)
4. Mỗi overlay: mốc thành phẩm = `start` của part + `at`, khớp bảng Bước 3; chưa chắc thì xuất 1 frame xem
5. Nghe điểm vào/ra nhạc (xuất 5s audio quanh mốc nếu cần)
6. chapters.txt khớp `map.json` nếu có chapter
7. Phim nhiều part (multicam, phim tài liệu, trên 40 part) hay có lời than "hình lệch tiếng": chạy thêm `python3 tools/do-dong-bo.py "<file>.mp4" --mau 24` và đọc từng dòng (mốc dày hơn, thấy cả lệch cục bộ lẫn trôi dần). Lệch xuất hiện ở đầu ra mà tiếng đúng 0 ms thì nghi nguồn (tiếng từng máy so với tiếng chủ, hình cận so với hình toàn), không nghi bước dựng

Đạt rồi mới COPY sang `du-an/<tên>/xuat-hoan-chinh/<tên>-<aspect>.mp4` (bỏ `-nhap`) và báo: tên file, thời lượng, dung lượng, chapters, kèm dòng "nghiệm thu máy: ĐẠT (hình = tiếng, -14 LUFS)". Thành phẩm đã ở máy user, không cần commit.

## Bước 7 - gói đăng tải (tự làm, không chờ nhắc)

Ngay sau khi giao, làm gói đăng tải theo skill phim-dang-tai: ba phương án tiêu đề, mô tả YouTube có chương (lấy từ `<video>.chapters.txt` hoặc `tools/chuong-youtube.py`), status Facebook, ba thumbnail từ khung hình thật của clip, qua cổng `tools/dang-tai.py kiem`. Báo cùng lượt với báo giao.

## Ghi nhớ vận hành

- `.tam/` sau khi dựng bị truncate còn 0 byte nhưng tên còn - bình thường
- Sửa script/studio ở đám mây phải commit về máy ngay (máy là bản gốc). Sửa logic cắt, ghép hay finalize trong `assemble.py` thì đổi `TOOL_VERSION`, rồi chạy `python3 tools/kiem-tra-xuong.py` (gồm `kiem-dong-bo.py`, dựng thử chớp/click đo tiếng - hình từng sự kiện) và chỉ dựng thật khi cả hai ĐẠT
- **Lớp lỗi "bất biến bị vi phạm nhưng không ai kiểm"**: mọi file trung gian phải hình = tiếng; bước sau chỉ đi tiếp khi bước trước đo đạt; không để nhánh "sửa ngầm" (encode lại, hạ ngưỡng, bắt ngoại lệ rồi bỏ qua) che dấu vết; con số khớp "gần đúng" khó hiểu là dấu hiệu, không phải may mắn. Bất biến hình = tiếng phải được đo cả SO VỚI NGUỒN (ngưỡng chặt 4 ms ở part và thân phim, không dùng chung ngưỡng 0,06 s của AAC); một công cụ đo tự viết phải thử trên nguồn biết trước đáp án trước khi tin
- Kết thúc dự án đáng nhớ: bài học kỹ thuật vào `docs/BAI-HOC.md` đúng chủ đề; tiêu chí biên tập mới vào `skills/phim-dung-bai/references/bien-tap.md`; góp ý phong cách vào sổ tay góp ý của `phong-cach/PHONG-CACH.md`. Sửa skill theo `skills/_chung/bao-tri-skill.md`

<!-- ban-nguon: phim-dung-bai 2026-09-30 46aeeb9a -->
