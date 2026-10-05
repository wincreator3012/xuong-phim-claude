# BÀI HỌC CỦA XƯỞNG

Những bài học đã trả giá thật qua các dự án, chưng cất theo chủ đề để đọc nhanh trước mỗi khâu. Mỗi bài: điều cần làm hoặc tránh, lý do ngắn, và nguồn (dự án, ngày).

Bài học là lý do để hiểu vì sao một cách làm từng đúng với người xem của một clip, không phải khuôn để lặp ở mọi clip; con số trong đây là điểm xuất phát, chỉ các bất biến kỹ thuật mới giữ tuyệt đối. Nhãn **[máy]** nghĩa là bài học đã thành luật trong tool (script tự làm hoặc tự chặn), chỉ cần hiểu, không cần nhớ làm tay. Khi thêm bài mới: đặt đúng chủ đề, một đến ba dòng, có nguồn; bài học nào đổi môi trường, lệnh hay quy ước thì sửa luôn `docs/QUY-TRINH-KY-THUAT.md`. Góp ý phong cách của người dùng (chữ, cỡ, vị trí) ghi ở sổ tay góp ý của `phong-cach/PHONG-CACH.md`, không ghi ở đây.

## 1. Nguyên tắc gốc

- **Sai là dừng, không có nhánh sửa ngầm.** Một nhánh "tự encode lại khi lệch" từng che giấu lỗi lệch hình tiếng cộng dồn 4,5 giây suốt nhiều dự án. Mọi cách bù (khung đứng, mượn cảnh kề, hạ ngưỡng) phải thành lựa chọn của người dùng. (dự án thật, 2026-09-05) **[máy]**
- **Bất biến phải được đo ở mọi bước, không suy ra từ bước trước.** Hình = tiếng ở từng part, thân phim, thành phẩm. (dự án thật, 2026-09-05) **[máy]** `check_av()`
- **Kiểm "hiển thị đúng" và kiểm "đồng bộ đúng" là hai việc.** Trích một khung thấy chữ đúng chỉ chứng minh overlay render đúng; phải đối chiếu với câu transcript đang nói tại đúng khung đó. Hai pill từng lệch 85-93 giây mà vẫn qua kiểm khung. (dự án thật, 2026-09-01)
- **Sửa lỗi hiển thị thì kiểm bằng khung hình thật, không bằng suy luận "đã thêm đúng thuộc tính".** (dự án thật, 2026-08-31)
- **Góp ý lặp lần thứ hai là tín hiệu sửa nguồn mặc định** (brand.json, preset, defaultProps), không chỉ sửa job đang làm, nếu không dự án sau rơi lại lỗi cũ. (dự án thật, 2026-08-31)
- **Tách việc nghĩ và việc tính, kể cả trên giấy.** Con số trên kịch bản do script cộng (`uoc-luong.py`), mốc trên phim do `map.json`; cộng tay từng sinh bản nháp 9 phút so với mục tiêu 5-6 phút. (dự án thật, 2026-09-30) **[máy]**
- **Kiểm chứng dữ kiện là một cổng, không phải thói quen.** Con số, năm, trích dẫn lên hình phải có nguồn đối chiếu; lời nhân vật và giọng người dùng là chất liệu thật, không sửa. (dự án thật, 2026-09-30)
- **Qua 2-3 vòng suy luận vẫn sai thì đừng suy luận thêm:** nhờ người dùng xem bản render và cho mốc phút giây trực tiếp; mốc đo trên chính thành phẩm đáng tin hơn mọi suy luận ngược từ transcript. (dự án thật, 2026-09-30)
- **Học cơ chế, không học cách bù.** Từ dây chuyền tự động khác chỉ lấy cổng kiểm chứng, dòng "khi hỏng", bảng thời gian đo thật, hai làn song song; không lấy hình do AI tạo thay cảnh thật hay giọng máy thay giọng người. (dự án thật, 2026-09-30)
- **Chỉ đạo trực tiếp của người dùng trong một dự án thắng mặc định của skill;** chỉ đạo lặp lại thì thành mặc định mới. (dự án thật, 2026-09-22)
- **Đừng tự suy diễn ràng buộc không ai đặt ra.** Đồ họa nổi từng bị làm nhỏ vì tự cho là phải né người nói; người dùng xác nhận toàn khung là canvas. (dự án thật, 2026-09-22)
- **Mục tiêu thời lượng mâu thuẫn với đoạn người dùng đã chỉ định: giữ đúng đoạn người dùng chỉ định, báo số đo thật để người dùng quyết,** không tự cắt bớt câu. (dự án thật, 2026-09-21)
- **Người dùng nói "bản dài đã có đoạn cắt sẵn rồi": tái dùng NGUYÊN mốc `in`/`out`, B-roll, overlay của bản đã duyệt,** chỉ thay đồ họa cần sửa; không tự sáng tác lại cách cắt. (dự án thật, 2026-09-21)

## 2. Đồng bộ hình tiếng và assemble

- **`-itsoffset` + `overlay=eof_action=pass` làm hình dài hơn tiếng 0,3-0,4 giây mỗi đoạn có overlay.** Sửa bằng `-t` phía output. Mọi video có pill xuất trước 2026-09-05 có thể mang lỗi này. (dự án thật, 2026-09-05) **[máy]**
- **`concat -c copy` bỏ qua edit-list của AAC, lệch khoảng 21 ms và giật nhẹ ở MỌI mối nối,** kể cả đoạn không overlay. `-avoid_negative_ts make_zero` không sửa được. Nay ghép luôn giải mã rồi mã hoá lại. Mọi video dựng trước 2026-09-17 (có hay không có overlay) có thể mang lệch này; dựng lại bằng tool mới là hết. (dự án thật, 2026-09-17) **[máy]**
- **`check_av()` chỉ so thời lượng tổng;** lệch căn chỉnh cục bộ ở mối nối vẫn có thể ĐẠT. Khi nghi, rà khoảng cách gói `ffprobe -show_entries packet=pts_time` tại ranh giới đoạn. Nay có thêm hai công cụ đo tuyệt đối, xem ba mục ngay dưới. (dự án thật, 2026-09-17)
- **Lệch hình-tiếng CỘNG DỒN qua hàng trăm part, dù nguồn khớp và tổng thời lượng "đạt".** Nguyên nhân kép: (1) đoạn cắt bắt đầu giữa hai khung nguồn (nguồn 29.97 fps, mốc `in` lẻ) khiến ffmpeg chèn thêm một khung đầu đoạn, part hình dài hơn tiếng đúng 1 khung (33 ms) mà ngưỡng cũ 0,06 giây cho qua; (2) phần ghép dùng concat demuxer cùng `aresample=async=1` vốn tự chèn hay cắt tiếng để "vá" chênh thời lượng hình-tiếng của từng part, cộng thêm độ trễ mồi của AAC mã hoá từng part, nên sai số không bị chặn mà tích luỹ. Phim 44 phút 206 part lệch từ -111 đến +70 ms, rõ nhất ở các đoạn máy cận. Sửa (`assemble.py` r5, r6): mỗi part đúng n khung (`fps=N:start_time=0` + `tpad` + `trim=end_frame`) và đúng n×48000/fps mẫu (`atrim=end_sample`), tiếng trung gian PCM `-f mov`, ghép hình bằng copy, nối tiếng thô từng mẫu PCM, AAC mã hoá MỘT lần ở finalize; `check_av()` ngưỡng 4 ms cho part và thân phim (PCM), 60 ms chỉ cho thành phẩm AAC. (dự án thật, 2026-09-30) **[máy]** `kiem-dong-bo.py`, `do-dong-bo.py`
- **Cổng kiểm phải đo cái người xem thấy, không đo thay thế.** So thời lượng và dùng nguồn giả tiếng sine (không có mốc thời gian) không bao giờ bắt được lệch cục bộ. `tools/kiem-dong-bo.py` dựng nguồn giả có chớp trắng và tiếng click đúng cùng một khung, cắt tại mốc lẻ, rồi đo trực tiếp "tiếng - hình" từng sự kiện trên thành phẩm (đạt: mỗi cặp trong ±40 ms, trôi dưới 15 ms mỗi phút); chạy lại nó bằng bản `assemble.py` cũ cho KHÔNG ĐẠT, nên nó là bài kiểm hồi quy [regression]. `tools/do-dong-bo.py` đo trên phim thật, nghiệm thu gọi tự động. (dự án thật, 2026-09-30) **[máy]**
- **Công cụ đo tự viết phải được kiểm bằng nguồn biết trước đáp án trước khi tin.** Ba bẫy đã gặp: đo chớp-click với `-r 30000/1001` trên phim 30 fps cho lệch ảo tăng dần 0 đến 64 ms; so năng lượng chuyển động mà bỏ qua pts thật của khung đầu sau `-ss` (0 đến 33 ms) cho lệch ảo một khung; `map.json` làm tròn `dur` 3 chữ số cộng dồn lệch 0,3 ms mỗi part (69 ms sau 206 part), nay ghi 6 chữ số. Đo bằng pts thật của `ffprobe`/`showinfo`, không bằng `-r`. (dự án thật, 2026-09-30)
- **Nguồn 29.97 fps ra 30 fps: sai số hình còn trong nửa đến một khung (lượng tử hoá), tiếng khớp tuyệt đối.** Đo thật trên phim AIM Ngũ Tài: hình - tiếng trung bình +10 ms, khoảng [-7, +29] ms, không trôi. Muốn hết lượng tử: dựng đúng 29.97 (chưa thử; mẫu tiếng mỗi khung là 1601,6 nên phải tính lại). (dự án thật, 2026-09-30)
- **Sau bản dựng cuối, `.tam/` bị thu về 0 byte nên chạy lại `assemble.py` là dựng lại toàn bộ.** Cần sửa `map.json` hay chương thì viết script sửa thẳng file kết quả; nhớ đó cũng là lý do sửa mã ghi map mà không đổi được bản đã xuất. (dự án thật, 2026-09-30)
- **Khi nghi nguồn quay rớt khung, rà gói bằng `packet=...` (không giải mã, nhanh) chứ không `frame=...`;** trên ffprobe của VM, `frame=pts_time` không tồn tại và âm thầm trả dòng rỗng. `avg_frame_rate` lệch `r_frame_rate` thường chỉ là làm tròn metadata. (dự án thật, 2026-09-17)
- **Cache phải biết code đã đổi.** Chữ ký cũ chỉ hash tham số nên sửa code xong vẫn dùng lại part lỗi. Nay `.sig` gồm `TOOL_VERSION`; sửa logic encode thì đổi `TOOL_VERSION`. (dự án thật, 2026-09-05) **[máy]**
- **Thêm hay bớt segment làm dịch chỉ số part cache;** trước khi tin resume sau khi đổi cấu trúc timeline, chắc rằng cache cũ đã được thu về 0 byte hoặc `.sig` không khớp. (dự án thật, 2026-08-31)
- **Đồ họa Intro, Outro render ra có đuôi tiếng AAC dài hơn hình 0,05-0,06 giây,** đủ vượt ngưỡng nghiệm thu. Nay assemble tự cắt. (dự án thật, 2026-09-16) **[máy]**
- **Nhạc bookends từng giả định intro luôn đứng đầu,** nên khi hook đặt trước intro thì nhạc mở kêu ở giây 0. Nay dùng `"role": "intro"` trên insert. (dự án thật, 2026-09-22) **[máy]**
- **Đọc log snap sau khi dựng:** `snap:true` có thể dời mốc 70 ms so với số đã gõ; phụ đề hay overlay tính theo số cũ sẽ lệch. (dự án thật, 2026-08-30)
- **Mốc tuyệt đối cần tính trên thành phẩm thì cộng thời lượng ĐO THẬT của từng part,** không cộng số lý thuyết (out - in); nay dùng `map.json`. (dự án thật, 2026-08-29) **[máy]**
- **Ghép hoặc finalize không có resume;** khi một lượt 180 giây không đủ, chạy hai bước đó ở sandbox. Preset `ultrafast` thoát kẹt được nhưng file nặng gấp ba (430 MB lên 1,36 GB). (dự án thật, 2026-09-01)
- **Tự chạy lại một đoạn code của `assemble.py` bên ngoài `run()` thì chép CHÍNH XÁC từng cờ,** nhất là `-t <tổng thời lượng part>` phía output của bước ghép; thiếu cờ này hình tiếng lệch 0,068 giây và cổng nghiệm thu bắt đúng. (dự án thật, 2026-09-22)
- **Nguồn 4K 10-bit HEVC quá nặng để composite:** thay tạm `nguon/` bằng proxy 1080p H.264 CÙNG TÊN file (mọi mốc giữ nguyên), dựng, rồi khôi phục nguồn gốc. (dự án thật, 2026-09-22)
- **`render-do-hoa.mjs` gộp props kiểu shallow merge với defaultProps:** prop dạng object truyền vào thay thế toàn bộ object mặc định, không trộn từng khoá. (dự án thật, 2026-08-29)

- **Concat demuxer lấy thời lượng mỗi part từ mvhd làm tròn đến mili giây,** nên mối nối lệch +0,67 ms và cộng dồn thành vài ms trên phim 100 part. Nay `concat.txt` ghi dòng `duration` chính xác n/fps cho từng part (`CONCAT_REV` c7). (dự án thật, 2026-09-30) **[máy]**
- **Map thời gian phải ghi thời lượng frame-exact của insert, không phải số đo bằng ffprobe.** Thẻ chèn đo được 4,054 s nhưng part thật là 4,0667 s; qua 11 thẻ map trôi khoảng 89 ms, phim vẫn khớp nội bộ nhưng `do-dong-bo.py` (đo theo map) báo tiếng lệch +103 ms. Nay `insert_part` tính dur chính xác trước khi ghi map, và `write_time_map` dừng nếu tổng dur map lệch tổng part quá 5 ms (`CONCAT_REV` c8). Khi đo báo tiếng VÀ hình cùng trôi đều theo thời gian mà hình - tiếng ≈ 0, nghi map trước, không nghi phim. (dự án thật, 2026-09-30) **[máy]**
- **Cache đo loudness không được nhận kết quả lỗi.** Trễ mount làm `mix.wav` chưa thấy, lỗi "No such file" bị ghi vào `mix.wav.ln`, lượt sau đọc cache hỏng và lặng lẽ rơi về loudnorm một lượt: phim ra -15,2 và -16,3 LUFS, trượt cổng. Nay finalize chờ `mix.wav` sẵn sàng, chỉ cache khi có `input_i`, thử lại 5 lần và dừng nếu vẫn hỏng, không còn nhánh rơi về một lượt. (dự án thật, 2026-09-30) **[máy]**
- **Sửa map hay loudness của phim đã xong nghĩa là dựng lại toàn bộ** (`.tam/` đã về 0 byte). Phim 30 phút cần khoảng 8 lượt `timeout 170`; kiểm thử bản sửa `assemble.py` bằng `kiem-dong-bo.py` trước, rồi mới dựng thật. (dự án thật, 2026-09-30)

## 3. Mốc thời gian overlay và B-roll

- **`overlay.at` tương đối từ đầu đoạn; `broll.at` tuyệt đối trong file nguồn.** Đặt `broll.at: 21` với `in: 186.6` làm B-roll bật ngay đầu đoạn. Đây là chỗ nhầm kinh điển nhất. (dự án thật, 2026-08-29) **[máy]** `--kiem-tra`
- **Mốc overlay đồng bộ lời nói: neo theo tỷ lệ ký tự trong câu Whisper** (`frac = vị trí ký tự / độ dài câu`), rồi kiểm với transcript. Không tính bằng cộng dồn và hệ số kinh nghiệm. Công thức: `skills/phim-dung-bai/references/bien-tap.md`. (dự án thật, 2026-09-01)
- **Lấy mẫu khung để kiểm overlay thì cộng 0,7-1 giây vào mốc `at`:** `revealAt` nội bộ và hiệu ứng hiện dần làm chữ hiện trễ hơn mốc lý thuyết. (dự án thật, 2026-08-30)
- **`revealAt` bên trong Benefits dùng cùng mốc 0 với `overlay.at` của đoạn.** (dự án thật, 2026-08-29)
- **Overlay không có câu nói tương ứng (callout biên tập) không đặt đại vào khoảng lặng gần nhất;** đặt cạnh overlay cùng nhóm ý, trong vùng transcript đang bàn đúng chủ đề, và báo người dùng pill nào không có câu nói tương ứng. (dự án thật, 2026-09-30)
- **Thời lượng hiện overlay tính theo nội dung:** lấy lớn hơn giữa thời gian người nói bàn về ý đó và thời gian đọc chữ, cộng 1-2 giây. (dự án thật, 2026-08-29)

## 4. Overlay, pill và bố cục

- **Ưu tiên overlay hơn broll hay insert khi lời cần liền mạch;** slide toàn màn hình từng cắt ngang mạch kể chuyện 3,5 phút, đổi thành pill thì đạt. Hỏi trước: đoạn này có phải cắt cảnh không. (dự án thật, 2026-08-30)
- **Giữa hai thẻ toàn màn hình có ít nhất 5 giây cảnh quay chính;** cần nhấn tiếp thì dùng overlay bán trong suốt. Không áp cho infomotion (không có mặt người để định hướng lại). (dự án thật, 2026-08-29)
- **Quy tắc 5 giây áp cả cho một lần lộ mặt ngắn xen giữa hai B-roll:** khe dưới một giây lộ mặt người nói giữa hai cảnh trám gây cú "lóe" giật mắt như hai thẻ dính nhau; nối liền B-roll phủ hết khe thay vì giữ khe. (dự án thật, 2026-09-30)
- **Chủ động rà ba loại nội dung để đề xuất overlay cùng phương án cắt:** tên chương trình hay framework, các bước hay cấu phần, key message. (dự án thật, 2026-08-29)
- **Không che mặt; kiểm ở trạng thái tích luỹ đầy đủ trên khung hình thật.** Pill 5 mục tích luỹ thành khối cao đè mặt dù khung đầu trông ổn. (dự án thật, 2026-09-09)
- **Người nói giữa khung và còn trống hai bên: tách list thành hai cột `left`/`right`, xen kẽ mục;** list 3-4 mục ở `top` dễ xuống hai hàng đè mặt. Xuất thử một khung trước khi chọn vị trí. (dự án thật, 2026-08-30)
- **Pill ở đáy khung dễ bị hiểu là phụ đề;** phỏng vấn ngồi thì `bottom` lại hợp nhất vì pill trên hay che đầu. Mặc định nay là `bottom`; chọn theo khung hình thật. (dự án thật, 2026-08-31)
- **LowerThird (thông tin về NGƯỜI) và Benefits (thông tin về Ý) là hai lớp, không thay nhau.** Phim tài liệu qua năm nháp không có thẻ tên nào vì không ai "chỉ" được chỗ thiếu; clip quảng bá phải có thẻ tên cho chính người dẫn. (dự án thật, 2026-09-20)
- **Câu hỏi neo, câu kết chiêm nghiệm: overlay Benefits một mục `wrap:true` đè lên cảnh thật,** không cắt sang thẻ riêng. (dự án thật, 2026-09-16)
- **Xuống dòng tiêu đề: kiểm soát chủ động bằng mảng dòng + `nowrap`,** không đoán bằng `\n`, giảm cỡ chữ hay `%`. Khi CSS ngắt không theo tính toán, vẽ border debug để thấy ranh giới thật. `Intro` có `description`, `creditLines` và `maxWidth` px thật; `SectionTitle.title` nhận mảng. (dự án thật, 2026-08-31)
- **Thẻ chuyển SectionTitle:** `kicker` là tên dự án viết hoa lặp xuyên suốt, `title` là tên hồi hoặc câu hỏi, `showLogos` ở ranh giới lớn. (dự án thật, 2026-09-20)
- **Kiểm có hay không một lớp phủ mà không xem ảnh:** đọc màu một điểm ảnh góc khung (nền kem `#FAF7F1` khác hẳn cảnh quay), hoặc tìm "cao nguyên" độ lệch so với khung tham chiếu. (dự án thật, 2026-08-30)

- **Tuyệt đối không để lớp phủ nào che mặt bất kỳ ai trong clip, kể cả người đứng ở nền hay người đang được gửi hình lên slide.** `mat-chinh` (slide thẻ góc trên phải) đã đè lên mặt người ngồi hàng sau ở ba chỗ trong nháp đầu của một keynote có slide (4:39, 3:53, 41:57). Cách xử lý: dùng `ca-hai` (slide ở khung riêng, mặt người nói ở ô riêng, không chồng lên cảnh) hoặc `mat` khi không cần slide; slide ít được nhắc (đội hình 7C ở cuối clip) thì bỏ hẳn. Nghiệm thu: trích khung tại MỌI mốc có lớp phủ (29 khung ở một keynote có slide) và nhìn từng khung, không chỉ vài mốc. (dự án thật, 2026-10-04)
- **Clip đăng YouTube: cắt bỏ phần mở đầu nói về cách dùng tài liệu/slide cho khán phòng tại chỗ,** người xem YouTube không cần; bắt đầu từ chỗ nội dung thật sự mở ra, kết ở câu chốt tự nhiên mà người dùng chỉ định. Khi người dùng chốt mốc vào/ra thì dùng đúng mốc đó. (dự án thật, 2026-10-04)

## 5. Khung dọc, cropFocus và cách kết

- **cropFocus đúng là giá trị giữ trọn cử chỉ tay,** không chỉ mặt giữa khung; chụp so sánh ở khung đang khoát tay. (dự án thật, 2026-09-09)
- **Đoạn dài có nhiều người trong khung rộng: kiểm 5-6 mốc trải khắp đoạn, ở mỗi mốc nhìn cả hai mép.** Ba vòng góp ý mới ra giá trị sạch (0,68, 0,64, rồi 0,60). (dự án thật, 2026-09-21)
- **Kết bằng thẻ tĩnh: mờ dần cả hình lẫn tiếng khoảng 1,5 giây;** chỉ `afade` vẫn thấy đột ngột vì sự đột ngột nằm ở hình. (dự án thật, 2026-09-21)
- **Mở phim tài liệu bằng chuỗi vài cảnh động ngắn** có nhịp sống hơn một cảnh kéo dài cùng thời lượng. (dự án thật, 2026-09-20)
- **cropFocus không phải hằng số của một file nguồn:** các đoạn cắt quay ở tư thế khác nhau cần giá trị riêng. Chỉnh theo góp ý "còn mất tay phía X": vẽ biên cửa sổ crop của nhiều giá trị lên khung CHƯA crop để thấy ngay hướng và biên độ cần pan. (dự án thật, 2026-09-21)
- **Bài giảng có slide: `ca-hai` là mặc định cho mọi slide còn đọc được ở 73% khung; `slide` toàn khung chỉ khi kiểm đọc thật thất bại** (người dùng thấy toàn khung "nhìn chán", muốn giữ người nói trên hình). `ca-hai` thành bố cục chủ đạo thì kiểm cropFocus rải đều trong từng đoạn. (dự án thật, 2026-09-22)

- **Điểm kết của short là chữ cuối của ý đã trọn, không phải mốc cuối của cue hay đoạn nhận dạng:** cue và Whisper kéo sang nửa câu kế tiếp, người dùng nghe ra "câu thừa" ngay còn máy không thấy. Chốt bằng đường bao năng lượng của chính thành phẩm (khoảng trũng 0,05-0,15 giây sau chữ cuối), fadeOut 0,05 giây; người dùng yêu cầu rút đuôi (7C bỏ "nhưng mà", Skill AI dừng sau "nhiều") thì đổi `out`, bớt phần giữ cuối của cảnh bằng `overlay.duration` kèm `giu`, sửa cue cuối, dựng, burn, nghiệm thu lại. (dự án thật, 2026-10-03)
- **Short cắt từ cuộc đối thoại phải tự đứng được:** bỏ câu nhắc "hồi nãy người dùng X nói" bằng cách vào sau câu đó; con số người nói ước lượng tại chỗ ("90-100%") giữ trong lời nhưng không lên hình, thumbnail, mô tả, và hỏi người dùng giữ hay cắt. (dự án thật, 2026-10-03)
- **Gọi short bằng slug và nội dung, không chỉ số thứ tự:** "S5" của người dùng là short thứ tư trong kế hoạch; hỏi một câu bằng nội dung thay vì đoán. (dự án thật, 2026-10-03)

## 6. Nhạc và âm thanh

- **`gainDb` theo từng track và từng chế độ** (full khác bookends) trong `thu-vien/AM-THANH.md`; `duck:true` là sidechain nên gainDb full có thể cao hơn trực giác. (dự án thật, 2026-08-31)
- **Mức tiếng nền cảnh thật (`volumeDb`) phụ thuộc độ ồn từng file;** nghe lại vòng sau vẫn có thể cần hạ thêm (-12 xuống -18). (dự án thật, 2026-09-20)
- **Ngưỡng `silencedetect` đặt theo sàn ồn đo được;** -38 dB không bắt được gì trên file có sàn -42 dB. (dự án thật, 2026-09-29)
- **Cắt ở chỗ không có khoảng lặng thật:** tính năng lượng ngắn hạn (cửa sổ 20 ms, `wave` + numpy) trên 4-6 giây quanh điểm nghi, cắt vào GIỮA khoảng trũng. Cắt giữa câu Whisper để né một cụm từ: ước lượng theo tỷ lệ ký tự, `silencedetect -30dB:d=0.1` trên cửa sổ 3-4 giây, đặt `snap:false`. (dự án thật, 2026-08-30)
- **True peak vượt khi LUFS đã đúng: chỉ thêm `alimiter` ở bước cuối** (`alimiter=limit=<hệ số>:attack=5:release=50:level=disabled`), dò hệ số qua vài lượt đo lại; không mix lại. (dự án thật, 2026-09-21)
- **Nghi "bụp" ở điểm cắt: đo RMS cửa sổ 10 ms quanh mốc cắt** (từng thấy vọt 0,08 lên 0,56); đoạn kết là B-roll cắt sang đồ họa sáng thì dùng `fadeOutAudio` (chỉ mờ tiếng) thay cho `fadeOut` (mờ cả hình về đen, sinh chớp đen). (dự án thật, 2026-09-21)
- **Tiếng gốc có crest khoảng 20 dB (đoạn to đoạn nhỏ chênh nhiều) làm chuẩn hoá -14 LUFS rơi -16 hoặc vượt true peak:** nén và giới hạn nhẹ trước thành `nguon/tieng-chu-nen.wav` rồi trỏ `audioSrc` vào đó. (dự án thật, 2026-10-01)
- **Nhãn "không đăng ký Content ID" của nhạc miễn phí chỉ đúng tại ngày nhìn, không bảo đảm gì:** một track Pixabay không nhãn bị đơn vị thứ ba đăng ký sau đó, Short dùng nó làm nhạc chạy suốt bị chặn toàn cầu dù nhạc nhỏ -23 dB. Content ID dò dấu vân âm thanh chứ không đọc giấy phép. Nhạc đảm bảo thật là nhạc xưởng tự tổng hợp (`tools/soan-nhac.py`, hậu tố `_xuong-rieng`); `nhac-nen/CAM-DUNG.json` làm `assemble.py` báo lỗi khi timeline dùng track đã bị cấm; nhạc ngoài chỉ dùng sau khi đăng bản riêng tư và xem mục Bản quyền của YouTube Studio sạch. Đổi nhạc là dựng lại từ timeline (sửa `music`), cắt và phụ đề giữ nguyên. (dự án thật, 2026-10-05)
- **Cache đo âm lượng `.tam/mix.wav.ln` có chữ ký không gồm nội dung tiếng:** đổi nguồn tiếng (hoặc nén lại) mà không làm rỗng file `.ln` thì bản ra lệch (-12,9 LUFS dù đã sửa); làm rỗng file đó rồi chạy lại. (dự án thật, 2026-10-01)

## 7. Gỡ băng

- **Câu lạc quẻ, nhắc kênh hay thương hiệu lạ ("hãy subscribe...") thường là hallucination do tạp âm,** không phải người nói lạc đề; ghi đúng lý do trong phương án cắt và hỏi người dùng khi cần. (dự án thật, 2026-08-29)
- **Cắt ngắn một cửa sổ để gỡ lại có thể CHÍNH LÀ nguyên nhân hallucination;** gỡ lại cửa sổ rộng 30-60 giây hoặc cả đoạn trước khi kết luận. (dự án thật, 2026-08-30)
- **Nhiều lần gỡ cùng đoạn ra kết quả khác hẳn nhau là bằng chứng mạnh của hallucination;** ưu tiên bản gỡ từ clip đã dựng xong và đối chiếu điều đã biết về người dùng (ví dụ tên tổ chức bị nghe thành một cụm tiếng Anh na ná). (dự án thật, 2026-09-03)
- **Whisper có thể rớt hẳn một cụm ở ranh giới lô khoảng 28 giây;** chốt điểm cắt gần ranh giới thì gỡ lại cửa sổ quanh đó để xác minh. (dự án thật, 2026-08-29) **[máy]** `nghiem-thu.py transcript` bắt quãng có tiếng dài hơn 8 giây không có chữ
- **large-v3 chết lặng trong VM 4 GB;** chạy large-v3 trên Mac qua hàng đợi, VM chỉ turbo. Lượt đầu sau khi máy khởi động chậm hẳn vì nạp 1,7 GB model. (dự án thật, 2026-09-21) **[máy]** `--model auto`

## 8. Phụ đề

- **Mốc phụ đề tự nhiên:** `silencedetect` ngưỡng lỏng (`-27dB:d=0.12`) trên chính thành phẩm lấy điểm ngắt hơi, chia câu theo tỷ lệ ký tự, mỗi câu tối thiểu khoảng 1,2 giây; câu Whisper quá dài không có dấu phẩy thì tách theo cụm khoảng 8 từ. (dự án thật, 2026-08-29)
- **Burn phụ đề bằng file `.ass` riêng có `PlayResX`/`PlayResY` đúng độ phân giải thật;** `force_style` nhiều key trên libass của VM không đáng tin. Đo MarginV bằng pixel trên khung trích, không nhìn ảnh thu nhỏ. (dự án thật, 2026-09-09)
- **Trích khung để kiểm phụ đề hay overlay thì `-ss` đặt SAU `-i`** (output-seek); đặt trước làm lệch PTS nên tưởng phụ đề không hiện. (dự án thật, 2026-08-29)
- **Font Be Vietnam Pro tải từ `raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro/`,** dùng `fontsdir=` trỏ tới file .ttf. (dự án thật, 2026-08-29) Cài font trên đúng VM của máy (nơi chạy `device_bash` và burn phụ đề), không phải sandbox. (dự án thật, 2026-08-29)
- **Tìm điểm ngắt hơi cho phụ đề trên audio GỐC (trước khi trộn nhạc)** khi `silencedetect` trên thành phẩm không đủ nhạy vì nhạc nền lấp khoảng lặng. (dự án thật, 2026-08-29)
- **Transcript thô trước khi lên phụ đề phải hiệu đính theo ngữ cảnh** ("di văn" là "di dân", "sân tồn" là "sinh tồn"); không burn nguyên văn máy nhận. (dự án thật, 2026-09-21)
- **Cue phụ đề trùng quá nửa thời gian với LowerThird hay pill thì cả cue dùng style nâng cao** (`Raised`), không cắt nhỏ cue cho khít. (dự án thật, 2026-09-21)
- **Font trong `.ass` bị rơi về DejaVu Sans** khi style xin weight 400 mà file chỉ có SemiBold: thêm file Regular/Bold thật hoặc khai đúng weight của file có sẵn; xem log `fontselect` khi burn. (dự án thật, 2026-09-21)

- **Cue theo hơi nói, nhóm cân bằng, khoảng 28 ký tự mỗi dòng trên điện thoại:** chia thuần theo tỉ lệ ký tự trong cụm dài lệch vài phần mười giây và để lẻ chữ; ASR file đã dựng lấy ranh giới cụm, nhóm cân bằng ưu tiên dấu câu, chữ soát tay. Burn và chuẩn hoá âm lượng trong cùng một lượt ffmpeg (acompressor, volume, alimiter); `volume` 2,5 dB cho -15,1 LUFS (không đạt), 3,7 dB cho -14,6; luôn đo lại. (dự án thật, 2026-10-03)

## 9. Đồ họa Remotion và render

- **File `.tsx` sửa ở sandbox phải commit về máy NGAY;** Benefits.tsx và Caption.tsx từng mất vì phiên trước không commit. (dự án thật, 2026-08-29)
- **Kiểm alpha của webm vp8 bằng ffmpeg tự soạn: đặt `-c:v libvpx` ngay trước `-i`;** không có cờ này ffmpeg âm thầm giải mã ra nền đen đục. `ffprobe` báo `yuv420p` dù alpha vẫn đúng. (dự án thật, 2026-08-29) **[máy]** trong `assemble.py`
- **Render alpha vp8 ở CRF mặc định của Remotion cực chậm;** nay đi đường PNG + libvpx và CRF 30. (dự án thật, 2026-09-22) **[máy]** `render-do-hoa.mjs`
- **File do một tiến trình mồ côi (sau lượt gọi bị timeout) tạo ra có thể bị cắt cụt mà kích thước vẫn hợp lý;** luôn `ffprobe` thời lượng trước khi dùng, sai thì render lại bằng lệnh sạch. Không `pkill -f <tên composition>` vì dễ giết nhầm tiến trình cha hợp lệ. (dự án thật, 2026-08-30)
- **Sửa nhiều cảnh cùng lúc: sửa xong mọi `.tsx` rồi `tsc` một lượt, render tuần tự, commit bằng `stagedPath`, dựng lại đồng bộ, soát bằng một contact sheet tại các mốc `part.start + overlay.at`.** (dự án thật, 2026-09-22)
- **Giữ job JSON đồ họa trong dự án (`du-an/<x>/do-hoa/job/`) tới khi giao xong;** job từng mất khỏi sandbox giữa hai vòng góp ý, sửa một trường `position` phải dựng lại job từ khung đã render. (dự án thật, 2026-09-30)
- **Cỡ chữ Benefits đã nâng hai lần** theo góp ý đọc trên điện thoại (nay `unit*4.5` dọc, `unit*4.0` ngang); component pill mới xuất phát từ cỡ này. (dự án thật, 2026-08-29)
- **Chrome Headless Shell của Remotion trên máy có thể mất và không tải lại được** (remotion.dev bị chặn): dấu hiệu là `render-do-hoa.mjs` treo 60-90 giây không có log, trong `studio/node_modules/.remotion/chrome-headless-shell/` chỉ còn `download.lock`. Render ở sandbox (Chromium có sẵn), commit kết quả về máy. (dự án thật, 2026-09-21)

## 10. Infomotion và hình vẽ ẩn dụ

- **Hai giọng hình, chọn theo nội dung:** cơ chế, số liệu, quy trình dùng cảnh minh hoạ sơ đồ (skill phim-canh-minh-hoa); ý niệm chiêm nghiệm giữ nét vẽ tối giản YNiem, YCanh và từ điển ẩn dụ; một video được trộn khi hợp. (dự án thật, 2026-10-01)
- **Phủ kín là mặc định:** không quá 1 giây nền trơn trừ nhịp có ý đồ; mốc kết thúc khối này bằng CHÍNH XÁC mốc bắt đầu khối sau, lấy thời lượng đo thật từ `ffprobe`. (dự án thật, 2026-09-22) **[máy]** `uoc-luong.py`
- **Lấp khoảng trống bằng chữ thuần là "chán";** lấp bằng hình, mỗi nhịp một kỹ thuật chuyển động riêng (cụm chấm nhiều màu, đếm số dồn, nét bút chạy, kim quét, lửa lớn dần), chung một họ easing và màu. (dự án thật, 2026-09-22)
- **Kích thước, độ giàu chi tiết và vị trí là ba trục duyệt độc lập,** đạt trục này không kéo theo trục kia: phóng to (toàn khung là canvas), làm giàu (5-6 tick thay vì 1, khoảng 10 dòng thay vì 1), canh giữa (`position:'center'`). Lỗi cỡ nhỏ không lộ qua cổng máy hay still riêng lẻ, chỉ lộ trên khung dọc thật. (dự án thật, 2026-09-22)
- **"Chậm lại 50%" trong ô timeline đã khoá thời lượng: tính ngân sách khung riêng từng cảnh,** chừa khoảng 14 khung cuối cho mờ dần; ô eo hẹp chỉ chậm được một phần. (dự án thật, 2026-09-22)
- **Ẩn dụ bị chê "hơi kỳ" hoặc hai chi tiết chồng nhau: thiết kế lại cả khối hình,** không vá toạ độ. Tách vùng theo cả không gian lẫn thời gian (trăng mọc xong rồi mới viết dòng); lớn dần từ điểm neo đáy; cảnh dài thì có chuyển động sống liên tục sau khi vẽ xong. (dự án thật, 2026-09-22)
- **Chỉ tổng quát hoá thành trường chung khi có trường hợp dùng thứ hai;** `travelDot`/`endArrow` bắt đầu là nhánh riêng của một slug rồi mới thành trường của `YNiemShape`. (dự án thật, 2026-09-22)
- **Từ điển ẩn dụ phải lớn lên qua dự án thật** (0 lên 12 mục sau dự án đầu); slug có hình mà không có mục từ điển, hoặc ngược lại, là lỗi. (dự án thật, 2026-09-22)

## 11. Phim tài liệu phỏng vấn

- **Dệt nhiều file phỏng vấn theo chủ đề dùng được timeline hiện có;** mỗi segment trỏ một file. Cầu nối B-roll 2-3 giây có fade khoảng 0,15 giây giữa hai nhân vật giảm cảm giác giật. (dự án thật, 2026-09-16)
- **Cắt câu là việc nhiều vòng;** nghe lại lần thứ sáu vẫn lộ phần dư ở những câu đã "đạt". (dự án thật, 2026-09-20)
- **Mốc phút giây không ổn định qua các nháp; góp ý theo nhãn đoạn A/B/T/M** giữ nguyên qua mọi nháp, `NHAN-DOAN.md` sinh lại sau mỗi render. (dự án thật, 2026-09-20) **[máy]** `nhan-doan.py`
- **Thiếu cảnh trám là lý do Pha 1 tồn tại:** một cảnh dùng được cho mỗi 20-30 giây phim, quay gấp 2-3 danh mục, giữ máy tối thiểu 10 giây, ba cỡ mỗi chủ thể, 30 giây tiếng môi trường mỗi bối cảnh. (dự án thật, 2026-09-17)
- **Người dùng có xuất hiện trong phim hay không là quyết định hỏi sớm** (mặc định không); cách kết theo `phong-cach/PHONG-CACH.md`. (dự án thật, 2026-09-17)

## 12. Multicam

- **Mọi góc cùng mang một tiếng thì so năng lượng mic ra "chồng" gần như toàn bộ;** chuyển sang so chuyển động mặt và tay ở góc cận (`--nguoi-noi hinh`). (dự án thật, 2026-09-29) **[máy]** `--nguoi-noi auto`
- **Lập kế hoạch pill và bảng tên TRƯỚC khi dàn góc** (`--khoa`), để điểm cắt tránh vùng overlay và bảng tên luôn nằm trên cận đúng người. (dự án thật, 2026-09-29) **[máy]**
- **Nguồn 4K nặng: làm proxy 1080p đã căn sẵn trước,** mọi phân tích chạy trên proxy. (dự án thật, 2026-09-29)
- **Một buổi quay có thể thành nhiều clip độc lập:** chia theo chủ đề trên transcript, mỗi clip dàn góc riêng trong cửa sổ của nó (`--cua-so`, `--hau-to`), có intro riêng, bảng tên hiện lại lần đầu mỗi người nói trong clip. (dự án thật, 2026-09-30)
- **Proxy 4K sang 1080p chạy cỡ 1x thời lượng mỗi khúc:** chia khúc khoảng 10 phút mỗi lượt gọi 180 giây; `--cau-hinh` dùng đường dẫn tuyệt đối khi nguồn ở ổ ngoài; `multicam-dan.py` đọc `--nguoi-noi`, `--khoa`, `--session-file` theo đường dẫn tương đối so với thư mục dự án. (dự án thật, 2026-10-01)
- **Nhận người nói bằng chuyển động hình sai khi người nghe cười hay gật nhiều:** sửa tay `luot-noi.json` đối chiếu cue trong transcript, rồi dàn lại; chuỗi pill khoá dài có thể để lại cú trên 40 giây nên thêm cú phản ứng người nghe vào khoảng trống. (dự án thật, 2026-10-01)

## 13. Truyền file và hạ tầng

- **Commit lại cùng một `stagedPath` từng ghi bản CŨ;** mỗi lần commit bản sửa dùng tên staged mới và so md5 hai phía. (dự án thật, 2026-09-29)
- **mp4 và ảnh qua `outputs/` có thể được gắn hộp `uuid` (manifest nguồn gốc):** md5 và dung lượng khác dù hình tiếng giữ nguyên; so bằng `ffprobe`. (dự án thật, 2026-09-30)
- **File hơn 20 MB: `split`, commit từng phần, `cat` trên máy, kiểm `sha256sum` hai đầu.** Chunk đầu chứa header `ftyp` từng bị chèn thêm byte; chèn một chuỗi byte rác vào đầu chunk đầu rồi `tail -c +<n+1>` cắt bỏ trên máy. (dự án thật, 2026-09-22)
- **Dấu tiếng Việt có thể mất khi script tạo qua heredoc thường;** luôn dùng `python3 <<'PYEOF'` đọc sửa ghi và đọc lại giá trị đã ghi (`repr`) sau khi chạy. (dự án thật, 2026-09-22)
- **Khung kiểm tra, ảnh tạm để trong thư mục nhà của VM,** không để trong thư mục của người dùng (không xoá được); lỡ tạo thì chuyển vào `_to_delete/`. (dự án thật, 2026-09-29)
- **`git status` trong VM để lại `.git/index.lock` rỗng không xoá được** (thư mục của người dùng cấm xoá mặc định), làm lần commit sau của người dùng bị git chặn. Chỉ đọc trạng thái repo bằng `GIT_OPTIONAL_LOCKS=0 git status`; lỡ để lại khoá thì xin quyền xoá đúng file đó. (dự án thật, 2026-09-30)
- **Không chạy lệnh git trong VM trên repo của người dùng:** `git status` tạo tệp khoá index.lock trong thư mục .git mà VM không xoá được (cấm xoá), lock rỗng sẽ chặn lần commit của người dùng. Lỡ tạo thì đổi tên tệp khoá ngay trong thư mục .git (`mv -n`, git bỏ qua tên lạ), rồi báo người dùng. Muốn biết tệp nào đổi thì đọc kết quả `dong-bo-repo.py`. (dự án thật, 2026-10-01)

- **Dựng clip dài (hơn 35 phút, hàng trăm đoạn `ca-hai`) trên VM 4 nhân, mỗi lệnh gọi bị chặn khoảng 120 giây và tiến trình nền bị giết khi lệnh kết thúc:** (1) mã hoá song song 4 worker, mỗi đoạn `ca-hai` cắt nhỏ khoảng 13 giây để vừa một lượt gọi; (2) `ca-hai` nướng sẵn [bake] khung nền và slide thành một PNG, chỉ overlay ô mặt, nhanh gấp khoảng 3 lần mà hình tương đương (PSNR Y 43,5 dB); (3) chia việc theo ngân sách thời gian từng lượt gọi, mọi bước đều phải resume được qua cache (`.sig`, dấu hoàn thành); (4) ghép cuối `fin.py` làm từng chặng nhỏ có đánh dấu (v.ok, raw.ok, mux.ok), bỏ bước `+faststart` nếu không kịp. Sau khi finalize, các `.tam/part-*.mp4` bị truncate về 0 byte nên đổi bất kỳ tham số nào (kể cả đỉnh tiếng [true peak]) là phải mã hoá lại từ đầu: chốt thông số âm thanh trước khi bấm bản chính. Không dùng `pkill -f ffmpeg` (giết luôn shell của chính mình, mã 143). (dự án thật, 2026-10-04)

## 15. Đăng tải

- **Mặt đang nói đổi rất nhanh:** trong cùng một giây có khung cười thật và khung miệng méo, mắt liếc; máy lọc ứng viên theo cỡ mặt, độ chính diện, độ nét, còn nét mặt thì phải nhìn bảng `quanh-kNN.jpg` (mỗi 0,25 giây, cắt sát mặt) rồi mới chọn. (dự án thật, 2026-10-01)
- **`render-do-hoa.mjs` bỏ qua job khi props không đổi, kể cả khi code composition đã đổi:** thumbnail luôn render với `--lam-lai`, nếu không sẽ giữ ảnh cũ mà vẫn báo xong. (dự án thật, 2026-10-01)
- **Ước bề rộng chữ 0,56 em làm dòng xuống chủ động bị ngắt thêm** ("sang nhân" rớt thành hai dòng); `Thumbnail.tsx` và `dang-tai.py job` cùng dùng 0,6 em. (dự án thật, 2026-10-01)
- **Chữ tiêu đề dưới 110 px trên khung 1920 gần như không đọc được ở bề ngang 168 px của YouTube trên điện thoại:** `dang-tai.py job` chặn; cách sửa là rút dòng dài nhất còn khoảng 10 ký tự, không phải thu nhỏ ảnh. (dự án thật, 2026-10-01)
- **Cảnh toàn podcast hai người không hợp bố cục toàn ảnh có chữ một bên:** hai mặt cách nhau quá xa, không chừa được chỗ cho chữ; dùng cận từng người (chia đôi, ô vòm). Mặt lệch trái trong khung gốc thì đặt chữ bên phải thay vì phóng ảnh rất lớn. (dự án thật, 2026-10-01)
- **Transcript đầy đủ của bản đã dựng là nguyên liệu của bước đăng tải:** dự án thật chỉ còn các mảnh trong `transcript/.tam/`; giữ lại transcript của bản đã dựng tới khi đăng xong. (dự án thật, 2026-10-01)
- **Cache ghi dở khi lượt gọi bị ngắt để lại JSON hỏng mà VM không xoá được:** ghi ra tệp tạm rồi `os.replace`, đọc hỏng thì chấm lại từ đầu. (dự án thật, 2026-10-01)
- **Nhạc Pixabay không bắt buộc ghi công;** chỉ track CC-BY (MacLeod) mới đặt `nhac_ccby`. Dòng ghi công cho track Pixabay chỉ là tự nguyện. Cổng sentence case chặn cả tên clip người dùng đặt ("Hành trình" viết hoa): đổi chữ thường và ghi vào `ghi_chu_kiem`. (dự án thật, 2026-10-01)

- **Short khái niệm: thumbnail dùng chính thuật ngữ người nói** ("Skill AI là gì?", "Khung chuyên môn từ phía AI", "Đóng gói tiêu chuẩn của bạn"), cùng một khuôn mặt cho ba phương án để thử nghiệm đo đúng thông điệp; dòng dài nhất 8-10 ký tự (ba dòng cũng được khi ý cần). Tiêu đề đặt từ khoá trong khoảng 60-70 ký tự đầu. Clip cắt lại sau khi đã có gói: sửa độ dài trong `ghi_chu_kiem`, chạy `dang-tai.py kiem` lại. (dự án thật, 2026-10-03)

- **Chương YouTube: chương đầu `Mở đầu` chỉ dài 6 giây thì cổng kiểm báo ngắn hơn 10 giây;** áp luật của `chuong-youtube.py` (gộp chương sát chương trước), chương `Mở đầu` kéo dài tới chương nội dung đầu tiên. Tên clip người dùng đặt có viết hoa từng từ cũng bị cổng sentence case chặn: tiêu đề đăng viết sentence case và ghi vào `ghi_chu_kiem`. (dự án thật, 2026-10-04)

- **Thumbnail clip giảng sân khấu: xen cận mặt với khung rộng zoom out, chữ khớp thứ thấy trong ảnh.** Ẩn dụ ("vé lên tàu") kèm ảnh cận mặt bị người trình bày chê khó hiểu; khung rộng có slide "Bản đồ khuyến khích" sau lưng thì chữ và hình hỗ trợ nhau. Quét mặt theo giây bằng `tools/quet-mat-theo-giay.py`, cắt khung từ 4K; `faceScale` 0.13 cho toàn ảnh rộng; chữ 12 ký tự không đạt 110 px thì ngắt ba dòng. (dự án thật, 2026-10-05)

## 14. Màu

- **Số liệu lệch kênh phụ thuộc bối cảnh, mắt quyết:** "trội kênh G" trên năm clip hoá ra là cây cỏ trong khung; so chéo lệch màu giữa các nguồn chỉ đáng xử lý khi chúng cắt qua lại cùng cảnh. Đa số clip đạt không chỉnh; HDR bắt buộc tonemap, kiểm từng file bằng `color_transfer`, không đoán theo thiết bị. (nghiệm thu màu, 2026-08)
- **Đa góc: cảnh toàn tối hơn hai cảnh cận dù cùng sắc (tường p50 196 so với 222-224):** khám phải so p50 tường giữa các góc trước khi dựng, vì `mau-sac.py kham` chỉ quét file nằm thẳng trong `nguon/` chứ không quét thư mục con từng góc. Đơn bậc 2 riêng cho `toan.mp4`: `curves=master='0/0 0.25/0.32 0.5/0.61 0.77/0.87 1/1',eq=saturation=1.04`; thêm `colorbalance` ấm làm áo khoác xám của người nói ngả nâu nên bỏ. Mức nâng vượt trần gamma của skill nhưng người dùng yêu cầu rõ và khung toàn không cháy. (dự án thật, 2026-10-01)

## 16. Cảnh minh hoạ HTML

- **"Render trang web ra video" chính là nguyên lý của Remotion** (trang web, Chrome không giao diện, tua từng khung, ffmpeg ghép); cái làm hình mẫu explainer đẹp hơn đồ họa có tham số là mỗi cảnh được vẽ riêng theo ý, lớn dần theo lời, màu theo vai. Xưởng giữ Remotion cho đồ họa nhận diện dùng lại, thêm `do-hoa-chung/canh-kit/` cho cảnh vẽ riêng. (dự án thật, 2026-10-01)
- **Chữ đang chuyển động nằm trên lớp compositing riêng nên khử răng cưa khác chữ tĩnh:** cùng một mốc, tua thẳng và chạy tuần tự lệch nhau vài điểm ảnh (khoảng 44 dB). `hien()` trả phần tử về trạng thái tĩnh khi đã lắng (bỏ transform, opacity) để hai đường ra cùng điểm ảnh; `canh.mjs kiem` coi lệch từ 40 dB trở lên là khử răng cưa, dưới 40 dB là trạng thái phụ thuộc lịch sử tua (lỗi thật). (dự án thật, 2026-10-01) **[máy]** `canh.mjs kiem`
- **Chụp nền đặc bằng JPEG chất lượng 95 nhanh gần gấp đôi PNG** (15 giây 1080p: 80 giây xuống 34 giây, 2 luồng), sau H.264 CRF 17 mắt không phân biệt; nền trong suốt vẫn phải PNG. (dự án thật, 2026-10-01) **[máy]** `canh.mjs chup`
- **Ghép người nói vào ô của cảnh chạy trên máy, không ở sandbox:** footage không rời máy; sandbox chụp cảnh có ô `.o-pip` và ghi toạ độ ô vào manifest, `canh-ghep.py pip` trên máy cắt, bo góc, đặt nguồn thật vào đúng ô (ffmpeg 4.4 của VM chạy được, 6 giây mất khoảng 1 giây). (dự án thật, 2026-10-01) **[máy]** `kiem-tra-xuong.py` dựng thử một B-roll kiểu này

- **Cảnh minh hoạ trong short hay nhất khi là một chủ thể xuyên suốt biến hình theo lời** (sân bóng sáng dần, hai cột rồi bảy vị trí, thẻ khung đi qua AI ra slide rồi đóng gói), nội dung lấy đúng ví dụ người nói nêu, khoảnh khắc khái quát đặt đúng lúc lời nói ý chính; người dùng khen cách làm này ở cả ba short. Hàm dựng khối phải trả đủ trường mà `ve()` dùng (thiếu `tick`/`tLab` gây NaN), cỡ lớn từ đầu (bản đầu thẻ nhỏ lọt thỏm phải làm lại), chừa 1-2 giây giữ cuối cảnh. Nguyên lý: `skills/phim-canh-minh-hoa/references/nguyen-ly-canh.md` mục 3; clip có minh hoạ: `skills/phim-clip-ngan/references/clip-co-minh-hoa.md`. (dự án thật, 2026-10-03)

- Phỏng vấn người dùng Trung (dự án thật, 2026-10-05): thẻ nổi bên trái người nói, chữ tiếng Việt rớt dòng tách cụm từ ghép ("chi / phí", "nhân / tạo") hoặc để một từ lẻ ở dòng cuối. Gốc rễ: trình duyệt ngắt theo khoảng trắng, không biết cụm nghĩa. Quy tắc: dùng khoảng trắng không ngắt [NBSP] cho cụm từ ghép, nội dung trong [..] ngắn và hai từ cuối của mỗi khối, cộng `text-wrap: pretty` (`balance` cho tiêu đề); cụm trong [..] dài thì không nối hết (tràn khung). Chữ trên thẻ Remotion không có pre-line thì cũng dùng NBSP, và đặt `\n` tay cho tiêu đề nhiều dòng. Sau khi đổi chữ, chụp ảnh trước và sau ở trạng thái đầy đủ rồi so điểm ảnh: chỉ cảnh nào đổi mới phải chụp lại cả video. Cỡ thẻ câu hỏi chuyển đoạn: 5,5 giây là vừa đọc.

## 17. Bàn dựng và dựng bằng lời

- **Lớp chữ để dựng bằng lời phải là lớp nguyên văn, không lấy chữ whisper:** clip "một dự án bài giảng" 10 phút, whisper large-v3 ghi 2.157 âm tiết và 4 từ đệm, zipformer tiếng Việt ghi 2.579 âm tiết và 39 từ đệm ("ờ", "á", "à", "ạ"), tức đúng những chữ người dùng muốn cắt; whisper còn bỏ "cái", "thì". large-v3 vẫn giữ cho phụ đề. (dự án thật, 2026-10-01) **[máy]** `moc-tu.py`
- **Mốc token của zipformer (transducer) không dùng để cắt được:** token đầu khúc luôn rơi vào khung 0, token sau trôi tới 0,36 s tuỳ điểm bắt đầu khúc. Căn khớp CTC (omnilingual 300M) chữ của zipformer vào tiếng: 73% điểm vào lời sau khoảng lặng lệch không quá 40 ms so với năng lượng tiếng, 86% không quá 80 ms; chạy lại với khúc dịch 0,3 s cho mốc y hệt. (dự án thật, 2026-10-01) **[máy]** `moc-tu.py`
- **Đỉnh CTC của nguyên âm kéo dài ("thì ờờờ") nằm bất kỳ đâu trong nguyên âm,** nên điểm cắt tìm trong khe giữa đầu âm tiết trái và đầu âm tiết phải, theo năng lượng tiếng (dải lặng, hoặc thung sâu từ 10 dB), không theo mốc cuối CTC. Âm tiết không có thân tiếng riêng giữa hai khe là âm tiết dính (thường "á", "ờ" kéo liền chữ trước): không tách riêng được, phải bỏ cả cụm. Trong clip thử: 42% ranh giới trong khúc có dải lặng, 24% thung sâu, 34% dính liền. (dự án thật, 2026-10-01) **[máy]** `ban_dung_loi.py`
- **Chữ nhiều âm (tên nước ngoài như "vitoling") có khe lặng bên trong do âm tắc,** nên vùng tìm điểm cắt sau một chữ bắt đầu từ mốc cuối CTC của chữ trừ 0,06 s, không từ đầu chữ; tìm từ đầu chữ đã cắt lẹm "-ling" (người dùng chấm "Lẹm chữ", điểm cắt sai 0,8 s). Nghe thử 16 điểm cắt: 15 sạch, mục lẹm đã sửa, 15 mục còn lại không đổi. (dự án thật, 2026-10-01) **[máy]** `ban_dung_loi.py`
- **HuggingFace bị chặn ở cả VM lẫn sandbox; GitHub releases của sherpa-onnx thì tải được:** chọn mô hình có bản phát hành trên đó (zipformer tiếng Việt, omnilingual CTC, đều Apache 2.0). Các wav2vec2 tiếng Việt trên HuggingFace vừa không tải được vừa là giấy phép phi thương mại. (dự án thật, 2026-10-01)
- **Chrome trên máy Mac chính tua video gốc HEVC 2688x1512 (4 GB) trung bình 29 ms, chậm nhất 39 ms:** Bàn dựng phát thẳng file nguồn, chỉ tạo proxy khi nguồn là định dạng Chrome không giải mã (ProRes, HDR lạ) hoặc máy yếu hơn đo thấy chậm. (dự án thật, 2026-10-01)
- **Kiểm Bàn dựng ở sandbox phải dùng WebM:** Chromium của Playwright không giải mã H.264/AAC (`canPlayType` rỗng), nên thời lượng ra NaN và không phát; dự án thử chuyển sang VP9 + Opus. Chrome thật trên Mac thì phát cả H.264 lẫn HEVC. (dự án thật, 2026-10-01)
- **Thẻ video dùng chung cho mỗi file nguồn** là cách gọn nhất để xem trước liền mạch: đoạn tách chỉ để gắn overlay phát nối tiếp không tua; chỉ tua khi đổi file hoặc nhảy mốc. Bỏ Remotion Player vì mỗi Sequence tạo một thẻ video riêng và tua lại ở mỗi mối nối. (dự án thật, 2026-10-01)
- **`volumeDb` của đoạn có trong tài liệu và skill phim tài liệu nhưng `assemble.py` chưa từng đọc** (không bản sao lưu nào có): mọi mức hạ tiếng nền từng ghi đều không tác dụng, kể cả lần "nghe thấy cần hạ thêm" ở phim tài liệu. Sửa ở r7; bài học: trường mới ghi vào tài liệu phải kèm kiểm trên thành phẩm, không chỉ kiểm cú pháp. (dự án thật, 2026-10-01) **[máy]** `kiem-tra-xuong.py` đo chênh mức đoạn -6 dB
- **Đoạn multicam có B-roll từng lặp tiếng:** `cut_part` nhận cùng `audioIn` cho mọi quãng con, quãng sau B-roll phát lại từ đầu đoạn. r7 truyền `audioIn + (đầu quãng - in)`. (dự án thật, 2026-10-01) **[máy]** `kiem-tra-xuong.py` đọc `map.json`
- **Kéo dài thẻ đồ họa không cần render lại:** ffmpeg tách thẻ tại giữa file (chỗ thẻ đứng yên), `tpad=stop_mode=clone` giữ khung, rồi nối phần kết; giữ nguyên kênh trong suốt VP9/VP8 vì giải mã bằng libvpx. Rút ngắn thì bỏ quãng giữa, không lấn hoạt cảnh kết. (dự án thật, 2026-10-01) **[máy]** `kiem-tra-xuong.py` đo ô thẻ sau mốc file gốc hết
- **Vi mờ 5 ms chỉ đặt ở mối nối tiếng không liền** (cắt bỏ một quãng, đổi file, giáp đồ họa chèn); mối tách đoạn, B-roll, đổi góc multicam cùng tiếng chủ giữ nguyên. Trước r8, 1 ms sát mối nối có năng lượng bằng 1,05 lần phần bên cạnh (cắt cụt sóng); sau r8 dưới 0,5 lần. (dự án thật, 2026-10-01) **[máy]** `kiem-tra-xuong.py` đo 22 mép mối nối
- **Đầu vùng tìm khe phải lùi vào trong chữ đủ sâu:** lấy đầu chữ + 0,04 s (làm tròn xuống khung) thì rơi đúng chỗ tiếng "hôm" vừa nhú, năng lượng còn thấp, bị nhận là khe; kéo theo luật "âm tiết dính" đánh dấu nhầm "ờ hôm" là dính liền. Sửa: đầu chữ + 0,08 s, làm tròn lên. 16 điểm đã nghe thử không đổi; người dùng nghe lại cả 16: 16/16 sạch. (dự án thật, 2026-10-01) **[máy]** `kiem-tra-xuong.py` kiểm điểm cắt trên lời tổng hợp
- **Chữ mờ, chữ gạch chỉ hiện khi chưa đoạn nào dùng:** thứ tự đoạn có thể khác thứ tự file (đoạn multicam đứng giữa, đoạn đảo chỗ); hiện chữ đã có ở đoạn khác thì "khôi phục" sẽ thành lặp lời. (dự án thật, 2026-10-01)

## 18. Clip panel hai khách mời (dự án thật, 2026-10-05)

- **Dựng proxy 4 góc chạy bằng hàng đợi Mac (`"loai": "proxy"` trong `hang-doi-go-bang.py`, chạy `proxy-mac.py`):** Mac có ffmpeg nhưng KHÔNG có ffprobe, đo độ dài mảnh bằng `ffmpeg -i` đọc dòng Duration. Khoảng trống giữa hai file nguồn dưới 0,3 s (DJI hở 0,004 s) phải được bỏ qua, nếu không công việc dừng với "Khoảng trống nguồn". **[máy]** `proxy-mac.py`
- **`-t` phải đặt TRƯỚC `-i` khi một lệnh ffmpeg ra nhiều đầu ra:** đặt sau `-i` chỉ giới hạn đầu ra đầu tiên, các góc còn lại ra mảnh dài hàng nghìn giây (khoảng 1 GB mỗi mảnh). Mảnh sai độ dài phải bị nhận ra và làm lại (`chunk_ok` so Duration với độ dài mong đợi).
- **Công việc Mac chết giữa chừng để lại tiến trình ffmpeg mồ côi** vẫn ghi mảnh sai độ dài và đổi tên thành mảnh hoàn chỉnh sau khi lần chạy mới đã kiểm xong; thấy file ghép bị cụt (ở đây 21 phút thay vì 44:51) thì dời mảnh sai sang `_to_delete` rồi xếp lại việc. Dặn người dùng đóng Terminal cũ trước khi bấm đúp lại.
- **`snap()` trong `build.py` chỉ hút điểm cắt vào quãng lặng khi có quãng lặng trong ±0,35 s; không có thì giữ nguyên mốc,** tức cắt giữa lời mà không báo. Ba mối nối của bản nháp 1 (kết đoạn C "nhưng bây giờ quan trọng hơn", vào đoạn D giữa câu, kết đoạn F kèm lời dặn người chỉnh màn hình) lọt qua nghiệm thu vì máy chỉ đo đồng bộ. Cách bắt: chạy nhận dạng zipformer trên cửa sổ 6 giây trước và sau từng mối nối lớn của bản nháp, đọc cả hai nửa câu; sửa bằng mốc tìm từ đường bao năng lượng 20 ms (chỗ trũng sau chữ cuối hoặc quãng lặng trước chữ đầu). **[máy]** đọc nửa câu ở mọi mối nối lớn trước khi trình Chốt 2
- **`do-dong-bo.py` với cửa sổ 6 giây cho mốc lệch giả +55-76 ms ở các góc toàn và góc chính ít chuyển động** (độ tin cậy hình q 0,5-0,87), trong khi mọi mốc q trên 0,9 trong ±14 ms và độ trôi 0. Cửa sổ 14 giây cho 24 mốc trong ±20 ms. `nghiem-thu.py` nay gọi `do-dong-bo.py --mau 12 --cua-so 14` (cửa sổ dài chính xác hơn, không nới ngưỡng ±50 ms).
- **Giọng trong clip nhiều người nói: xác định người nói bằng giọng liền mạch trong gỡ băng, không đoán theo vị trí đoạn** (đoạn C ban đầu để "chưa rõ người nói" nên chiếu góc rộng; thực ra là người kia, bảng tên chuyển về đúng chỗ người dùng lần đầu nói).
- **Mảnh proxy 60 giây phải có ĐÚNG 1800 khung (`-frames:v`), không chỉ "gần 60 giây":** `-t 60` ở 30 fps cho 1801 đến 1802 khung (60,03 đến 60,07 s); ghép 45 mảnh thì hình dài hơn tiếng chủ khoảng 1,2 đến 1,9 s ở cuối clip, tức hình đi sau tiếng càng về sau càng nhiều (người dùng nghe thấy ở nửa sau nháp 2). Mọi cổng máy đều ĐẠT vì `do-dong-bo.py` và `nghiem-thu.py` so thành phẩm với proxy, không so với wav tiếng chủ. Sửa: `proxy-mac.py` tính số khung của từng mảnh theo mốc làm tròn (`round((t+d)*30) - round(t*30)`), thêm `-frames:v`, `chunk_ok` chặn độ lệch trên 0,02 s; sau khi chạy kiểm tra `ffmpeg -i x.mp4 -map 0:v -c copy -f null -` phải ra đúng 80700 khung cho 44:50. Bài học chung: sau khi ghép nhiều mảnh, đối chiếu tổng số khung với độ dài tiếng chủ, đừng chỉ tin cổng đo từ proxy. (dự án thật, 2026-10-05)
- **Bù độ trôi đồng hồ máy quay chính (`drift_ppm` trong job proxy) là nguyên nhân phụ, chỉ khoảng 50-80 ms ở cuối clip:** công thức mốc trong file = (T - offset) x (1 + drift_ppm x 1e-6); các góc DJI trôi 0. Nguyên nhân chính là số khung mỗi mảnh ở trên.
- **Mỗi lần xếp lại việc proxy cho Mac đều phải nhờ người dùng bấm đúp "Go bang tren Mac.command" (đóng Terminal cũ trước)**; hẹn việc tự quay lại sau 20 đến 25 phút và báo rõ lý do cần người dùng bấm.
- **Chương YouTube có mốc cách nhau dưới 10 giây thì công cụ gộp vào chương trước;** tên chương dài bằng tiếng Anh xen lẫn nên viết thuần Việt, từ gốc để trong ngoặc vuông ("kiến tạo ý nghĩa [sense-making]").
- **Tên clip người dùng đặt vượt 100 ký tự thì tiêu đề YouTube bỏ tiền tố (ngày, tên chương trình), giữ câu hỏi;** nói rõ trong `ghi_chu_kiem`.
