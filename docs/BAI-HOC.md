# BÀI HỌC TỪ CÁC DỰ ÁN THẬT - dành cho Claude, đọc khi gặp tình huống tương tự

Xưởng này được rút ra từ hơn một tháng dựng clip thật (bài giảng dài, clip dọc, clip giới thiệu sách, bài giảng có slide, multicam) và sửa lỗi qua nhiều vòng góp ý. Những bài học dưới đây không gắn với một người dùng cụ thể; chúng là lý do nhiều quy tắc trong `docs/QUY-TRINH-KY-THUAT.md` và các skill tồn tại. Mỗi dự án mới có bài học đáng giữ, thêm vào đây bằng một đoạn ngắn: chuyện gì xảy ra, gốc rễ, quy tắc rút ra.

## Về nghiệm thu

**Máy đo những gì mắt không thấy; mắt chỉ soi những gì máy không đo được.** Một lỗi lệch hình-tiếng 0.3 giây mỗi đoạn có overlay đã lọt qua bốn vòng nghiệm thu bằng mắt vì mỗi vòng chỉ "xem vài khung hình". Người dùng cảm nhận "càng về sau càng lệch" trước khi có phép đo nào bắt được. Từ đó: hình = tiếng phải được đo ở từng file trung gian; cổng `nghiem-thu.py` bắt buộc trước khi nói "xong".

**Frame-check chỉ xác nhận overlay RENDER đúng, không xác nhận nó ĐỒNG BỘ đúng với lời nói.** Trích một khung hình thấy chữ hiện đúng là chưa đủ; phải đọc lại đúng đoạn transcript bao quanh khung hình đó để chắc chữ khớp ý đang nói. Hai việc khác nhau, trước đây bị nhầm là một.

**Contact sheet dày đặc đáng tin hơn vài điểm rời rạc.** Khi nghi thứ tự hay vị trí đồ họa sai, trích một khung mỗi 2 giây xuyên suốt đoạn nghi ngờ, ghép lưới có nhãn thời gian, đọc một lần; lộ ngay thứ tự thật thay vì tin phép tính.

**Khi đã qua 2-3 vòng suy luận vẫn sai, đừng suy luận thêm.** Để người dùng xem bản render và cho mốc phút-giây trực tiếp; mốc đo trên chính output đáng tin hơn mọi suy luận ngược từ transcript.

**File do một tiến trình "sống sót" qua lần gọi bị timeout tạo ra có thể bị cắt cụt** dù kích thước khác 0. Luôn `ffprobe` thời lượng thật trước khi dùng tiếp.

**Con số khớp "gần đúng" một cách khó hiểu là dấu hiệu, không phải may mắn.** Nhánh concat tự encode lại khi lệch quá dung sai từng che mất lỗi thật trong nhiều dự án.

## Về mốc thời gian

**Hai hệ mốc trong timeline là bẫy kinh điển**: `overlay.at` tương đối từ đầu đoạn, `broll.at` tuyệt đối trong file nguồn. Đã gây sai ở cả hai chiều trong hai dự án khác nhau. `assemble.py --kiem-tra` giờ bắt được phần lớn; vẫn phải nhớ khi soạn.

**Mốc overlay đồng bộ lời nói phải tra trực tiếp trong transcript**, neo theo tỷ lệ ký tự trong chunk Whisper chứa cụm từ đó, không cộng dồn thời lượng danh nghĩa các đoạn trước rồi ước lượng. Cách cộng dồn đã cho hai pill lệch 85-93 giây.

**Overlay không có câu nói literal (callout biên tập) không được đặt vào khoảng lặng gần nhất bất kể chủ đề**; phải đặt cạnh một overlay cùng nhóm ý, trong vùng transcript đang bàn đúng chủ đề, và báo cho người dùng biết pill nào không có câu nói tương ứng.

**Khi mốc mới khiến overlay tràn qua ranh giới segment kế tiếp, dời ranh giới segment** (nếu hai segment vốn liền mạch cùng cảnh quay) thay vì ép file đồ họa.

**Chèn thêm segment vào giữa timeline dịch lại mọi mốc phía sau**: phụ đề, chapter tính lại từ `.map.json`, không cộng trừ tay.

## Về transcript

**Whisper có thể hallucinate khi có tạp âm** (ra câu quảng cáo kênh lạ) và **có thể làm rớt hẳn một cụm từ đúng ranh giới lô 28 giây**. Đoạn nghe lạc quẻ: cân nhắc lỗi nhận dạng trước khi kết luận người nói lỡ lời; điểm cắt gần ranh giới lô thì transcript lại một cửa sổ rộng quanh đó.

**Cắt ngắn một đoạn để transcript lại riêng có thể tự gây hallucination** vì mất ngữ cảnh. Ưu tiên transcript lại đoạn dài hơn hoặc cả file đã dựng. Khi nhiều lần thử ra kết quả khác hẳn nhau, bản thân sự không ổn định là bằng chứng của hallucination; chọn bản khớp ngữ cảnh đã biết về người dùng.

**Khoảng lặng kỹ thuật không phải hơi thở thật.** Dấu phẩy trong văn viết không có nghĩa người nói ngừng hơi. Khi VAD báo liên tục mà vẫn cần tách, tính RMS 20ms trên đoạn audio ngắn để tìm khoảng trũng nhỏ, cắt vào giữa khoảng trũng.

**silencedetect trên file đã trộn nhạc kém nhạy**; chạy trên audio gốc tại đúng khung `[in, out]` để lấy điểm ngắt cho phụ đề.

## Về biên tập

**Mạch lạc tối đa.** Ưu tiên `overlay` lên một đoạn quay liên tục hơn `broll` hay cắt-rồi-ghép mỗi khi lời nói cần liền mạch. Câu hỏi đầu tiên với mọi ý cần nhấn: "đoạn này có PHẢI cắt cảnh không, hay chỉ cần một lớp chữ đè lên?"

**Ba loại nội dung nên chủ động đề xuất overlay** không chờ người dùng yêu cầu: tên chương trình/framework được xướng; các bước hoặc cấu phần; key message.

**Thời lượng overlay tính theo nội dung**: lớn hơn giữa thời lượng lời nói về chủ đề đó và thời gian đọc chữ, cộng đệm 1-2 giây. Không đặt số tròn.

**Hook trước intro** không chỉ cho clip ngắn; bài dài mà câu mở là câu chốt mạnh cũng nên tách hook làm segment đầu, intro là `insert` ngay sau.

**Kiểm cropFocus của khung dọc bằng khung hình đang có cử chỉ tay, không chỉ khung tay để yên.** Tiêu chí đúng không phải "mặt đã giữa khung" mà là "toàn thân/cử chỉ còn đủ trong khung" - một giá trị cropFocus có thể đúng về mặt giữa khung mà vẫn cắt mất tay/cùi chỏ nếu người nói đang khoát tay rộng.

**Pill ở `position:'bottom'` bị hiểu lầm là phụ đề** khi nhiều pill nối tiếp trên clip dài; ưu tiên `left`/`right` khi người nói ở giữa khung. Từ 3 mục trở lên, xuất thử một khung hình để xem người nói có bị đè trước khi chọn vị trí.

**Tối thiểu 5 giây cảnh quay chính giữa hai thẻ toàn màn hình**; dày hơn thì đổi sang overlay bán trong suốt.

**Kể cả khi người dùng không yêu cầu duyệt nháp, vẫn chủ động mời xem trước** ở clip có nhiều thay đổi khung hình, tránh dựng lại toàn bộ nhiều lần.

## Về đồ họa và CSS

**`maxWidth` dạng % không đáng tin trong khối chữ nằm trong flex-column căn giữa không có width cố định**; dùng px thật từ `useLayout().width`. Tiêu đề ngắn từng tự xuống dòng giữa từ dù còn rất nhiều chỗ trống.

**Sửa lỗi hiển thị CSS phải verify bằng khung hình thật**, không dừng ở "đã áp đúng thuộc tính lý thuyết sẽ sửa". Khi wrap không theo tính toán (giảm cỡ chữ rất nhỏ mà vẫn ngắt y hệt), vẽ border debug hoặc chuyển sang kiểm soát chủ động điểm ngắt (`title` dạng mảng dòng + `nowrap`).

**Cỡ chữ pill đã tăng hai lần sau góp ý "nhỏ quá" trên điện thoại**; xuất phát từ cỡ hiện tại (`unit*4.5` dọc, `unit*4.0` ngang) cho component mới, không nhỏ hơn.

**Mọi component mới phải commit file nguồn về máy ngay sau khi viết**; sandbox đám mây mất khi hết phiên, một component đã mất vì quên bước này.

**Overlay Benefits nhiều mục tích lũy dần thành một khối lớn - kiểm ở trạng thái tích lũy ĐẦY ĐỦ, không chỉ khung hình vừa hiện mục đầu.** Mục cũ không biến mất khi mục mới xuất hiện, chỉ thu nhỏ/mờ đi; với cảnh quay tĩnh một khuôn mặt cố định, khối pill tích lũy có thể che đúng vùng mặt dù từng mục riêng lẻ không che gì. Luôn chồng thử lên khung hình thật (không phải nền màu đặc) ở đúng thời điểm đã tích lũy đủ tất cả các mục trước khi coi là xong. Quy tắc ưu tiên cứng cho mọi overlay/pill đè lên video có người nói: (1) không che cả người lẫn mặt nếu tránh được; (2) buộc phải đánh đổi thì tuyệt đối không che mặt, có thể che một phần thân người. Khung dọc cần cả pill lẫn phụ đề cùng lúc: dùng prop `edgeInset` của `Benefits` để neo pill cách đáy khung một khoảng tùy chỉnh, tránh chồng lấn phụ đề burn-in ở sát đáy.

**Alpha của webm VP8: ffprobe báo `yuv420p` ngay cả khi file có alpha thật**; kiểm bằng `alpha_mode=1` trong tag hoặc ép `-c:v libvpx` khi decode để test. Bẫy này chỉ xảy ra khi TỰ TAY soạn lệnh ffmpeg để xem/test - pipeline overlay chính thức của `assemble.py` đã có sẵn flag đúng.

**Render alpha webm dài rất chậm**; chia thành nhiều overlay ngắn độc lập rồi truyền list vào `overlay` của một segment.

## Về nguồn mặc định và góp ý lặp lại

**Một câu góp ý sửa chữ xuất hiện lần thứ hai là tín hiệu phải sửa NGUỒN MẶC ĐỊNH** (brand.json, defaultProps, preset), không chỉ sửa file job của dự án đang làm. Một chức danh từng bị rút gọn sai qua ba dự án vì mỗi lần chỉ sửa tại chỗ. Trong xưởng này, chức danh nguyên văn và "từ ngữ phải viết đúng" nằm ở `phong-cach/PHONG-CACH.md`; mọi góp ý lặp lại ghi vào "Sổ tay góp ý" ở cuối file đó.

## Về màu

**Số liệu lệch kênh phụ thuộc bối cảnh, mắt quyết.** "Trội kênh G" trên năm clip hoá ra là cây cỏ trong khung. So chéo lệch màu giữa nguồn chỉ đáng xử lý khi các nguồn cắt qua lại cùng cảnh. Đa số clip đạt không chỉnh; HDR là trường hợp bắt buộc tonemap, kiểm từng file bằng `color_transfer`, không đoán theo thiết bị.

## Về hạ tầng

**`concat()` và `finalize()` không có resume như `build_parts()`**; bài dài (~10 phút) dễ vượt 180 giây lặp lại mà không tiến triển. Cách thoát: chia đôi danh sách part, xử lý từng nửa, ghép `-c copy`; hoặc khi `.tam/body.mp4` và `.tam/mix.wav` đã hợp lệ thì chạy thẳng hai lệnh ffmpeg còn lại của finalize thay vì gọi lại `run()`. Preset `ultrafast` chỉ là giải pháp tình thế: file nặng gấp 3.

**Burn phụ đề bằng `subtitles=...:force_style='Key1=Val1,Key2=Val2,...'` không đáng tin khi truyền nhiều key cùng dấu phẩy** - libass có thể chỉ áp key đầu tiên hoặc rơi về mặc định (Arial/16/MarginV=10) một cách im lặng, không báo lỗi. Đáng tin hơn: sinh file `.ass` riêng có khối `[Script Info]` khai đúng `PlayResX`/`PlayResY` bằng độ phân giải thật của video xuất, và khối `[V4+ Styles]` khai đủ font/cỡ chữ/màu/`MarginV`, rồi burn bằng `ass=file.ass` thay vì `subtitles=...:force_style=...`. Thiếu `PlayResX`/`PlayResY`, libass tự giả định một độ phân giải thấp rồi nhân tỷ lệ ngược lại - giá trị FontSize/MarginV không còn là pixel thật, gây mập mờ khi tinh chỉnh.

**Font tiếng Việt cho phụ đề burn-in phải cài trên đúng máy chạy ffmpeg** (`fc-match` kiểm); tải từ `raw.githubusercontent.com/google/fonts/main/ofl/bevietnampro/` vào `~/.fonts` rồi `fc-cache -f`.

**`-ss` đặt SAU `-i`** khi cần PTS khớp chính xác với subtitle/overlay filter lúc trích khung hình kiểm tra.

**Tránh `pkill -f <tên composition>`** trong sandbox: cụm từ có thể khớp luôn tiến trình node cha đang render hợp lệ.
