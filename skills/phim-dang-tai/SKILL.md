---
name: "phim-dang-tai"
description: "Soạn gói đăng tải cho mỗi clip đã xuất hoàn chỉnh trong thư mục \"xuong-phim-claude\": ba phương án tiêu đề và mô tả YouTube chuẩn tìm kiếm (chương, thẻ, hashtag), status Facebook bằng giọng của người dùng, và ba phương án thumbnail dựng từ khung hình thật của clip, qua cổng kiểm máy. Tự chạy ngay khi một clip vừa qua nghiệm thu và vào xuat-hoan-chinh, không chờ người dùng nhắc. Cũng kích hoạt khi người dùng nói \"mô tả YouTube\", \"description\", \"SEO\", \"status Facebook\", \"caption đăng bài\", \"thumbnail\", \"ảnh bìa\", \"bìa Reels\", \"chuẩn bị đăng\", \"gói đăng tải\", hoặc nhờ làm những thứ đó cho một clip cũ. Không dùng để dựng clip (phim-dung-bai và các skill thể loại) hay làm đồ họa chạy trong video (phim-do-hoa)."
---

# Gói đăng tải: tiêu đề, mô tả YouTube, status Facebook, thumbnail

Trước khi bấm xem, người xem chỉ gặp ba thứ: thumbnail, tiêu đề, vài dòng đầu của mô tả hay status. Skill này soạn ba thứ đó cho từng clip, như bước cuối của mọi quy trình dựng. Nguyên lý xuyên suốt: **một lời hứa rõ ràng mà clip giữ được**. Đây vừa là giá trị của người dùng (chân thật, không giật tít, không khung sợ hãi) vừa là điều nền tảng thưởng: YouTube xếp hạng theo thời gian xem có giá trị [valued watch time] và khảo sát mức hài lòng, chọn thumbnail thắng trong thử nghiệm A/B bằng thời gian xem chứ không bằng lượt bấm; Meta hạ phân phối bài giật tít và mồi tương tác. Nền nghiên cứu và nguồn: `skills/phim-dang-tai/references/nghien-cuu-thumbnail.md`.

Kết quả của mỗi clip nằm trong `du-an/<tên>/dang-tai/<tên video>/`:

| Tệp | Là gì |
|---|---|
| `dang-tai.json` | nguồn chữ (Claude soạn): tiêu đề, mô tả, thẻ, status, bình luận đầu, ý đồ từng thumbnail, điều người dùng cần xem lại |
| `DANG-TAI.md` | bản chép-dán cho người dùng, do `tools/dang-tai.py kiem` sinh từ `dang-tai.json` |
| `thumb-1.jpg`, `thumb-2.jpg`, `thumb-3.jpg` | ba phương án 1920x1080 (clip dọc thêm `thumb-doc.jpg` 1080x1920) |
| `soi-thumbnail.jpg` | thumbnail ở cỡ thật trên bảng tin điện thoại, để nhìn trước khi báo |
| `khung/` | khung hình ứng viên, `khung.json`, bảng `ung-vien.jpg`, `quanh-kNN.jpg` |
| `thumbnail.json`, `thumbnail.job.json` | thiết kế thumbnail (Claude soạn) và job render sinh từ đó |

## Khi nào chạy

- **Tự chạy** ngay sau khi một clip có "nghiệm thu máy: ĐẠT" và đã copy sang `xuat-hoan-chinh/` (mọi skill dựng trỏ về đây ở bước giao). Người dùng không cần ra lệnh thêm; báo giao clip và gói đăng tải trong cùng một lượt.
- Nhiều clip một lượt (một buổi podcast ra hai clip, một loạt Reels): mỗi clip một gói, soạn chữ cho cả loạt cùng lúc để các tiêu đề không trùng ý.
- Clip cũ, clip không dựng trong xưởng: chạy độc lập theo đường dẫn video (`--video` thay cho `--map` ở bước chọn khung).
- Gói đăng tải là bản nháp để người dùng duyệt khi đăng, không có chốt duyệt chặn trước; Claude không tự đăng lên nền tảng nào.

## Bước 0 - nền tảng

Đọc `skills/_chung/van-hanh.md`, `phong-cach/PHONG-CACH.md` (mục 1 chức danh, mục 4 từ ngữ, mục 8 đăng tải), `skills/phim-dang-tai/references/mau-dang-tai.md` (schema, mẫu, giới hạn nền tảng). Lần đầu trong phiên, đọc `skills/phim-dang-tai/references/nghien-cuu-thumbnail.md`. 

## Bước 1 - hiểu clip như người sắp xem nó

Nguồn, theo thứ tự ưu tiên: transcript của chính bản đã dựng (thư mục `transcript/` của dự án, kể cả các mảnh trong `.tam/`); không có thì gỡ băng bản đã dựng bằng turbo trong VM (`tools/transcribe.py`, clip dưới 15 phút chạy được trong vài lượt gọi); kế hoạch overlay và pill (đó là các ý chính đã được người dùng duyệt); bảng nhân vật; `timeline.json` (nhạc nào, có cần ghi công CC-BY không); `tu-lieu/TU-LIEU.md` (dòng ghi công tư liệu).

Ghi ra (trong đầu hoặc nháp) bốn điều trước khi viết chữ nào:

1. Người xem nhận được gì sau clip, nói trong một câu.
2. Một hoặc hai cụm từ khoá chính, là cách một người Việt thật sự gõ tìm chủ đề này (không phải tên nội bộ của khung).
3. Những gì không được đưa lên chữ: tên người thứ ba được nhắc trong clip, số liệu chưa soát nguồn, chuyện kể lại chưa kiểm chứng, nhận định dễ gây hiểu lầm khi tách khỏi ngữ cảnh. Những điều này vào `ghi_chu_kiem`.
4. Chương: mốc lấy từ tool, không gõ tay. Clip một góc có chapter trong timeline: `<video>.chapters.txt` do assemble ghi. Clip multicam hay chương theo mốc nội dung: `tools/chuong-youtube.py --map ... --chuong <json> --ket "<tên chương outro>"` (mốc lấy thẳng từ kế hoạch pill). Clip dọc dưới 3 phút không cần chương.

## Bước 2 - chữ: `dang-tai.json`

Schema và mẫu đầy đủ ở `skills/phim-dang-tai/references/mau-dang-tai.md`. Nguyên lý:

- **Tiêu đề YouTube**: ba phương án khác nhau về cách vào (tóm ý, câu hỏi, cách làm), mỗi cái dưới 100 ký tự, từ khoá chính trong khoảng 60 ký tự đầu (điện thoại cắt sau đó), sentence case, không viết hoa toàn bộ, không emoji, không "!!". Tiêu đề tóm đúng nội dung thắng tiêu đề úp mở: người đọc thấy rõ mình sẽ nhận gì. Câu chủ mở bằng khái niệm hay ý chính người xem hiểu ngay và có thể đang tìm, lấy tên từ chính slide hay lời người nói; ẩn dụ chỉ làm câu phụ (một keynote từng bị chê "vé lên tàu" là khó hiểu khi không có ảnh nào hỗ trợ). Tiêu đề và chữ trên thumbnail bổ sung nhau, không lặp lại nhau.
- **Mô tả YouTube**: câu đầu tự đứng được và chứa từ khoá (chỉ vài dòng đầu hiện trước "Xem thêm"); hai ba đoạn ngắn nói ai nói gì, khung nào của ai (ghi tên tác giả mô hình, công cụ); chương; người trình bày với chức danh nguyên văn; lời mời của chương trình nếu có (một lần, không upsell lộ liễu); ghi công nhạc và tư liệu CC-BY; một câu hỏi mở thật mời người xem tự soi chiếu; 1-3 hashtag ở cuối.
- **Thẻ YouTube**: 5-12 thẻ, tổng dưới 500 ký tự; thẻ chỉ đóng vai trò nhỏ, dùng cho cách gõ khác của từ khoá chính (một dạng không dấu, một dạng tiếng Anh nếu người ta thật sự tìm bằng tiếng Anh) và tên người trình bày.
- **Status Facebook**: giọng người dùng, ngôi thứ nhất (xưng hô theo PHONG-CACH mục 8). Mở bằng một khoảnh khắc, một chi tiết thật trong clip (dòng đầu dưới khoảng 120 ký tự, vì điện thoại chỉ hiện hai ba dòng trước "Xem thêm"); thân hai đến bốn đoạn ngắn nói điều người xem nhận được, không tóm tắt cả clip; kết bằng một câu hỏi mở thật. Link YouTube và link chương trình để ở bình luận đầu; video tải thẳng lên Facebook; 0-3 hashtag. Clip dọc (Reels): status ba đến năm dòng.
- **Shorts, Reels**: tiêu đề tự đứng được; link trong mô tả Shorts không bấm được nên trỏ về bản dài bằng tính năng video liên quan, không bằng link.
- **Dữ kiện**: chỉ nói điều có trong clip. Số liệu chưa soát nguồn thì không đưa lên chữ; chuyện kể lại giữ đúng là "được nghe kể"; không nêu tên người thứ ba. Mọi điểm như vậy ghi vào `ghi_chu_kiem` để người dùng biết Claude đã tránh gì.
- **Rà chữ**: không cụm sáo mở bài, không từ phóng đại, không "hãy cùng", không "hành trình" khi không có chuyến đi thật, không cân bằng giả.

## Bước 3 - thumbnail

### 3a. Chọn khung hình (máy lọc, mắt chọn)

```
python3 tools/chon-khung-thumbnail.py --map "du-an/<tên>/xuat-hoan-chinh/<video>.map.json"
```

Máy lấy mẫu mỗi 3 giây trong các đoạn cắt, dò mặt (YuNet), chấm cỡ mặt, độ chính diện, độ nét, độ sáng, xuất 12 ứng viên (và vài khung hai mặt cho podcast) từ file nguồn gốc, không dính pill hay phụ đề. Lượt gọi hết 180 giây thì gọi lại y nguyên, cache giữ phần đã chấm. Stage `khung/ung-vien.jpg` và NHÌN; chọn hai đến bốn ứng viên. Mặt đang nói đổi rất nhanh, nên tinh chỉnh quanh từng ứng viên:

```
python3 tools/chon-khung-thumbnail.py --map "<...>.map.json" --quanh k05 [--rong 1.5]
```

Stage `khung/quanh-k05.jpg` (cắt sát mặt, mỗi 0,25 giây) và chọn khung: mắt mở, nhìn thẳng (lời mời) hoặc nhìn về phía chữ; miệng khép hay cười thật, không khung đang nói dở miệng méo, không nháy mắt, không mờ vì chuyển động. Nét mặt ấm và điềm tĩnh, không diễn kinh ngạc. Không có ai trên hình (infomotion, hoạt hình): tool thoát mã 3, thumbnail dùng bố cục chữ làm chủ (`chu-chinh` không ảnh) hoặc một khung hình ẩn dụ trích từ chính clip.

**Clip giảng trên sân khấu hay bục giảng (người đứng, có màn hình hoặc slide phía sau):** ngoài ứng viên cận mặt, luôn trích thêm khung RỘNG [zoom out] có cả người và màn hình, tốt nhất ở đoạn người giảng đang nói về một khái niệm mà slide sau lưng ghi đúng chữ của khái niệm ấy (hình và chữ nói cùng một điều). Quét mặt theo giây trong quãng đã chọn: `python3 tools/quet-mat-theo-giay.py "<nguồn gốc>.mp4" --tu <s> --den <s> --buoc 1.5 --cat x:y:w:h --ra <thư mục tạm>`; NHÌN lưới `quet-mat.jpg` để chọn nét mặt, rồi cắt khung từ nguồn gốc 4K bằng ffmpeg (`-ss <giây> -vf crop=w:h:x:y`) và ghi vào `khung/khung.json` (`loai: "rong"`, toạ độ mặt theo tỉ lệ ảnh). Một lượt gọi 120 giây chỉ quét khoảng 25-30 mốc ở 4K nên chia quãng ra nhiều lượt.

### 3b. Thiết kế ba phương án

Ba phương án khác nhau ở **thông điệp**, không chỉ ở bố cục, để thử nghiệm A/B có nghĩa:

1. Câu hỏi soi chiếu, người xem nhận ra mình trong đó ("Bạn đang ở rổ nào?").
2. Khái niệm hay cách làm cốt lõi của clip ("Chia ra, rồi trừ bớt").
3. Điều đọng lại, bài học của câu chuyện ("Đặt tài năng đúng chỗ").

Giữ cùng một khuôn mặt (hoặc cùng cặp mặt) giữa các phương án khi muốn thử nghiệm đo đúng thông điệp. Riêng clip giảng trên sân khấu thì đổi cỡ khung giữa các phương án (cùng một người, khi cận khi xa; xem đoạn "Đa dạng cỡ khung" ngay dưới), thông điệp vẫn khác nhau ở chữ. Chữ: 2-5 từ, bổ sung cho tiêu đề chứ không lặp, xuống dòng chủ động theo cụm nghĩa bằng `\n`, mỗi dòng khoảng 10 ký tự, một cụm tô màu nhấn (`accent`). Kicker (tên chuỗi, FULL-CAP nhỏ) chỉ dùng khi clip thuộc chuỗi chương trình người dùng vận hành; logo nhỏ ở góc trái dưới, không ở góc phải dưới (YouTube đè nhãn thời lượng ở đó).

**Đa dạng cỡ khung, nhất là clip giảng trên sân khấu (người dùng chốt 2026-10-05 sau góp ý của người trình bày):** trong ba phương án có ít nhất một cận mặt (`faceScale` 0.30-0.34) và ít nhất một khung rộng zoom out (`toan-anh` khoảng 0.13; `chia-doi` hay ô vòm khoảng 0.15-0.16), phương án còn lại cỡ vừa. Ảnh phải HỖ TRỢ chữ: chữ là tên khái niệm người xem hiểu ngay, ưu tiên đúng chữ đang hiện trên slide sau lưng; một câu hỏi ẩn dụ ("Bạn có vé lên tàu?") mà ảnh bên cạnh không nói gì về nó thì khó hiểu. Dòng chữ 12 ký tự không đạt 110 px ở khung chia đôi: ngắt ba dòng, hoặc đặt `headlineSize` sau khi đã nhìn ảnh render và thấy chữ còn vừa ô.

Ba bố cục của composition `Thumbnail` (`studio/src/components/Thumbnail.tsx`), khung ngang 1920x1080 và dọc 1080x1920:

- `chia-doi`: chữ trên nền giấy một bên, ảnh một bên; hai ảnh thành hai ô (podcast hai người).
- `toan-anh`: ảnh phủ kín, một lớp nền giấy mờ dần phía chữ; tự đặt chữ về phía đối diện khuôn mặt.
- `chu-chinh`: chữ làm chủ, ảnh người trong một hay hai ô vòm nhỏ (tĩnh tại như khung cửa).
- Khung dọc (bìa Shorts, Reels): ảnh phía trên, chữ trong vùng an toàn giữa khung; `toan-anh` dọc cho cận mặt.

Brand theo dự án: mặc định `brand/brand.json` (giấy ngà, mực, lục trầm); dự án có nhận diện riêng thì một file `dang-tai/brand-<dự án>.json` chỉ ghi đè palette.

Soạn `thumbnail.json` (schema ở `skills/phim-dang-tai/references/mau-dang-tai.md` mục 2), rồi:

```
python3 tools/dang-tai.py job "du-an/<tên>/dang-tai/<video>/thumbnail.json"
```

Lệnh sinh `thumbnail.job.json` (ảnh khung khai báo trong "assets", tâm mặt chép từ `khung.json`) và ước cỡ chữ: chữ tiêu đề dưới 110 px trên khung 1920 (dưới 10 px khi YouTube hiện thumbnail rộng 168 px) thì báo lỗi, rút dòng dài nhất hoặc bớt chữ.

### 3c. Render ở sandbox

Stage các khung đã chọn, `khung/khung.json`, `thumbnail.json`, `thumbnail.job.json` (và file brand dự án nếu có) vào cây xưởng ở sandbox theo đúng đường dẫn tương đối, rồi:

```
node tools/render-do-hoa.mjs "<...>/thumbnail.job.json" --studio <studio-đám-mây> --lam-lai
```

Luôn `--lam-lai` với thumbnail: dấu vân tay props không đổi khi chỉ sửa code composition, nên không có cờ này script sẽ bỏ qua và giữ ảnh cũ. Script kiểm kích thước và giới hạn 2 MB từng ảnh. Commit `thumb-*.jpg`, `thumbnail.job.json`, `do-hoa-manifest.json` về đúng thư mục trên máy.

### 3d. Soi như người lướt bảng tin

Bước 4 sinh `soi-thumbnail.jpg`: mỗi phương án ở ba cỡ thật trên điện thoại (168, 246, 360 px), trên nền bảng tin sáng và tối, có nhãn thời lượng giả ở góc phải dưới. Stage và NHÌN: ở 168 px chữ còn đọc được không, gương mặt có nhận ra không, có gì quan trọng bị nhãn thời lượng đè không, ba phương án có thật sự khác nhau không. Chưa ổn thì sửa `thumbnail.json`, render lại.

## Bước 4 - cổng máy và báo

```
python3 tools/dang-tai.py kiem "du-an/<tên>/dang-tai/<video>"
```

Cổng kiểm: giới hạn YouTube (tiêu đề 100, mô tả 5000, thẻ 500, chương từ 0:00, tối thiểu ba chương, mỗi chương từ 10 giây, mốc khớp file chương của tool), từ khoá trong câu đầu, chức danh nguyên văn, ghi công nhạc CC-BY, câu hỏi mở ở cả mô tả lẫn status, từ ngữ phải viết đúng và gạch dài, emoji, Title Case, viết hoa toàn bộ, mồi tương tác và khung sợ hãi ("comment nếu", "tag bạn", "đừng bỏ lỡ", "bị bỏ lại"), link trong thân status, số hashtag, kích thước, tỉ lệ và dung lượng thumbnail. KHÔNG ĐẠT thì sửa `dang-tai.json` rồi chạy lại; không hạ ngưỡng, không sửa tay `DANG-TAI.md`.

Báo người dùng trong cùng lượt với báo giao clip: đường dẫn `DANG-TAI.md`, ảnh ghép ba thumbnail (gửi vào cuộc trò chuyện), các mục "cần người dùng xem lại", và cách đăng gọn (nhắc đăng bản riêng tư trước và đọc mục Bản quyền của YouTube Studio khi clip dùng nhạc không phải nhạc riêng của xưởng, nhất là short nhạc chạy suốt):

- YouTube: tiêu đề 1 và `thumb-1.jpg` làm mặc định; bật "Thử nghiệm và so sánh" [Test & Compare] trên máy tính với `thumb-2.jpg`, `thumb-3.jpg` (tối đa ba, chạy tới hai tuần, YouTube chọn theo tỉ lệ thời gian xem; kết quả "như nhau" cũng là câu trả lời). Thử nghiệm không áp dụng cho Shorts.
- Facebook: tải video thẳng lên, dán status, link ở bình luận đầu.

## Quy tắc cứng

1. Lời hứa của tiêu đề, thumbnail, mô tả là điều clip thật sự mang lại. Không giật tít, không mồi tương tác, không khung đua tranh, sợ hãi hay "bị bỏ lại", không upsell lộ liễu.
2. Thumbnail chỉ dùng khung hình thật của clip: không tách nền ghép cảnh, không hình do AI tạo thay người thật, không lật ảnh, không sửa nét mặt.
3. Chức danh, tên riêng, từ ngữ theo `phong-cach/PHONG-CACH.md` mục 1 và 4, nguyên văn.
4. Không nêu tên người thứ ba, không đưa số liệu chưa soát nguồn, chuyện kể lại giữ đúng là chuyện kể; mọi điều đã tránh ghi vào `ghi_chu_kiem`.
5. Mốc chương lấy từ tool, không gõ tay.
6. Chưa có `tools/dang-tai.py kiem` ĐẠT và chưa nhìn `soi-thumbnail.jpg` thì chưa báo gói đăng tải xong.
7. Claude soạn gói, không tự đăng.

## Khép việc

- Người dùng chọn phương án, sửa chữ, hay chê một kiểu thumbnail: một dòng vào sổ tay góp ý của `phong-cach/PHONG-CACH.md`; lặp lần hai thì sửa mặc định (PHONG-CACH mục 8, `thumbnailDefaults` trong `Thumbnail.tsx`, mẫu trong `references/mau-dang-tai.md`).
- Kết quả thử nghiệm A/B người dùng kể lại (phương án nào thắng, kiểu chữ nào): ghi vào `docs/BAI-HOC.md` chủ đề "Đăng tải" kèm tên clip; đủ nhiều thì chưng thành nguyên lý trong `references/nghien-cuu-thumbnail.md`.

<!-- ban-nguon: phim-dang-tai 2026-10-05 cd3ee6f6 -->
