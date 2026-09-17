# Quy chuẩn biên tập bài giảng - tiêu chí quyết định giữ/bỏ/nhấn

Người dựng là ai không quan trọng bằng việc mọi dự án cùng tuân theo một gu: điềm tĩnh, sạch, tôn trọng người xem và tôn trọng nhịp giảng của người nói. Video giáo dục chuyển hóa không phải video giải trí - không chạy theo nhịp cắt dồn dập của mạng xã hội, nhưng cũng không nể nang giữ lại những đoạn loãng.

**Nguyên tắc bao trùm: mạch lạc tối đa, tránh ngắt ngắt dừng dừng.** Mỗi mối nối (concat) là một điểm rủi ro, kể cả khi rơi đúng khoảng lặng - vẫn có xác suất nghe khựng nhẹ vì hai bên mối nối là hai lần encode riêng biệt. Vì vậy số lượng mối nối càng ít càng tốt: khi phải giữ một đoạn nói liên tục nhưng muốn đổi hình (đè infographic, bảng tên, B-roll) thì dùng kỹ thuật `overlay` (xem mục "Infographic/overlay" dưới) để giữ NGUYÊN một lần encode liên tục, thay vì bổ đôi thành nhiều đoạn rồi ghép lại. Chỉ tạo mối nối mới khi thực sự cần BỎ nội dung ở giữa (không phải chỉ để đổi hình).

## Tiêu chí GIỮ

- Đoạn có một ý trọn vẹn: nêu vấn đề, giảng giải, ví dụ, chốt ý
- Câu chuyện, giai thoại, ví dụ đời thực - đây là phần đắt giá nhất của lối giảng này, thà dài một chút còn hơn cắt cụt
- Khoảnh khắc tự nhiên có chủ đích: câu hỏi tu từ, khoảng lặng mời người xem tự chiêm nghiệm (phân biệt với khoảng lặng do quên lời - nghe transcript và ngữ cảnh để nhận ra)
- Lời mời thực hành, hướng dẫn từng bước

## Tiêu chí BỎ

- Lần nói hỏng khi có lần nói lại tốt hơn (người tự quay thường nói lại 2-3 lần; chọn lần trôi chảy và có năng lượng tốt nhất, thường là lần cuối)
- Khoảng dừng dài giữa các nội dung (dấu hiệu: khoảng lặng >2s trong silences.json), tiếng ho, thử mic, chỉnh máy, nhìn tài liệu lâu
- Lặp ý không chủ đích, câu đệm kéo dài ("thì", "ừm", "như mình vừa nói đó" khi vừa nói thật)
- Nội dung lạc đề so với mục tiêu clip mà user đặt ra - kể cả khi hay, có thể đánh dấu "để dành làm clip ngắn" thay vì đưa vào bài chính

## Nhịp và điểm cắt

- Mỗi điểm cắt phải rơi vào khoảng lặng THẬT (assemble tự snap theo silences.json, nhưng khi chọn mốc trong phương án đã nên chọn gần ranh giới tự nhiên của ý)
- Sau cắt, câu mới nên bắt đầu bằng ý mới - tránh vào giữa chừng một lập luận
- **Vùng có tạp âm nền liên tục (không phải khoảng lặng thật) không phải chỗ để đặt mối nối, dù cố "nhắm" cho khéo**: hai file encode riêng ghép lại ở một vùng như vậy vẫn dễ nghe giật vì không khớp pha/biên độ. Nếu nội dung hai bên vùng đó vẫn cần giữ liền mạch, cách đúng là gộp lại thành MỘT đoạn quay xuyên suốt luôn cả vùng tạp âm (thường chỉ là hơi thở/tiếng nền rất nhỏ, để nguyên nghe tự nhiên hơn là cắt), rồi dùng `overlay` nếu vùng đó cần đồ họa gì đó đè lên.
- Khi transcript không có mốc theo từng từ và cần cắt ngay giữa một câu (ví dụ hook chỉ lấy nửa sau một câu dài): đừng chỉ ước tính theo tỷ lệ âm tiết - sai số có thể hơn 1 giây. Chạy `ffmpeg -af silencedetect=noise=-28dB:d=0.08 ...` (ngưỡng nhạy hơn mặc định) quanh điểm nghi ngờ để tìm khoảng ngừng hơi thật giữa hai từ, neo điểm cắt vào đó (trừ thêm margin ~0.12s như cơ chế snap). Nếu ngay cả ngưỡng nhạy này cũng không tách được (silencedetect/VAD báo liên tục một đoạn, thường gặp khi hai vế câu nối liền không có hơi thở thật - ví dụ một câu ghép có dấu phẩy trong văn viết nhưng người nói không ngừng hơi): trích đoạn audio ngắn 4-6 giây quanh điểm nghi ngờ (`ffmpeg -ss ... -t ... -c:a pcm_s16le -ar 16000 -ac 1`), đọc bằng `wave` + `numpy`, tính RMS từng khung 20ms để tìm khoảng TRŨNG NĂNG LƯỢNG nhỏ nhất (dù VAD không đủ nhạy để coi là khoảng lặng) - cắt vào GIỮA khoảng trũng đó thay vì mép ngoài, để có biên độ an toàn cả hai phía, tránh cắt hụt chữ cuối vế trước hoặc lẹm vào chữ đầu vế sau.
- Hai đoạn liền nhau cùng một góc máy: cắt thẳng [jump cut] là chấp nhận được với talking-head, nhưng nếu vị trí đầu/người lệch nhiều giữa hai đoạn thì che bằng một trong ba cách, theo thứ tự ưu tiên: đổi góc máy (nếu có góc khác cùng nội dung), overlay đồ họa đè lên (xem mục dưới), hoặc thẻ chuyển phần nếu trùng ranh giới phần
- fadeIn/fadeOut chỉ dùng ở biên bài hoặc trước/sau thẻ phần; giữa các câu nói KHÔNG fade

## Khoảng cách tối thiểu giữa các thẻ/slide toàn màn hình

Khi bài (hoặc clip ngắn) có nhiều thẻ/slide toàn màn hình (insert cắt cảnh hẳn: thẻ mở InfoQuote, SectionTitle, hook card...) xuất hiện gần nhau, đừng để hai thẻ liền kề chỉ cách nhau 1-2 giây cảnh quay chính, và tuyệt đối không để hai thẻ dính liền nhau không chừa khung hình chính nào ở giữa - cả hai đều làm người xem mất phương hướng (vừa thấy mặt người nói đã bị cắt tiếp sang thẻ khác, không kịp định hình lại đang xem ai/ở đâu). **Quy tắc cứng: giữa hai thẻ toàn màn hình liên tiếp, phải giữ tối thiểu 5 giây cảnh quay chính (thấy được người nói) trước khi chuyển sang thẻ kế tiếp.** Mở rộng: "cảnh quay chính" ở đây bao gồm cả một lần LỘ MẶT NGẮN xen giữa hai B-roll - nếu khe hở lộ mặt người nói giữa hai B-roll dưới 5 giây (có khi chưa tới 1 giây), người xem chịu cùng một cú "lóe" giật mắt không kịp nhận ra ai; ưu tiên NỐI LIỀN B-roll (mở rộng phạm vi bao phủ của B-roll trước tới hết khe hở) thay vì giữ khe.

Nếu nội dung cần nhấn thêm một khái niệm ngay sau một thẻ vừa hiện mà chưa đủ 5 giây cách nhau, đừng cố nhồi thêm một thẻ toàn màn hình nữa - đổi khái niệm đó sang overlay bán trong suốt (`Caption`/`Benefits`, xem mục "Infographic/overlay" dưới), vì overlay không chiếm trọn khung hình nên không tính vào quy tắc 5 giây này và vẫn giữ được mạch nhìn thấy người nói liên tục.

## Cấu trúc bài giảng dài (>15 phút)

- Chia phần bằng SectionTitle mỗi 8-15 phút, tên phần lấy từ chính lời giảng
- Gắn chapter cho mọi phần để YouTube hiện mục lục
- Intro 5-7s, outro 6-8s; bài càng dài intro càng không được dài

## Hook trước Intro - không chỉ dành cho clip ngắn

Quy tắc "hook trước, intro sau" (đã áp dụng cho `phim-clip-ngan`) cũng áp dụng được cho bài giảng/clip giới thiệu dài dạng `phim-dung-bai` khi câu MỞ ĐẦU của tư liệu gốc tự nó đã là một câu chốt mạnh, đáng để người xem nghe/đọc TRƯỚC khi thấy thẻ tiêu đề (đã xác nhận qua một dự án thật, theo yêu cầu trực tiếp của user). Kỹ thuật: tách một đoạn Hook riêng (`in`/`out` snap đúng khoảng lặng thật quanh câu mở đầu) đặt làm segment ĐẦU TIÊN, chèn segment `type: "insert"` cho Intro NGAY SAU đó (không dùng field `intro` cấp cao nhất của timeline vì field đó luôn được build TRƯỚC mọi segment, kể cả Hook), rồi mới tới đoạn nội dung chính. Có thể lặp lại nguyên văn câu Hook bằng một overlay Benefits 1 mục (`wrap:true`) đè lên trong lúc người nói đang nói, giúp người xem tắt tiếng vẫn nắm được ý mở đầu. `fadeIn` nhẹ (~0.3s) ở đúng segment Hook là hợp lệ vì nó rơi vào "biên bài" (đầu tuyệt đối của clip) - xem quy tắc fadeIn/fadeOut ở mục "Nhịp và điểm cắt" phía trên.

## Xuống dòng trong thẻ tiêu đề toàn màn hình (Intro/SectionTitle)

**Không bao giờ để tiêu đề ngắn/tên riêng tự động xuống dòng giữa từ hoặc giữa cụm từ liền nghĩa** (ví dụ tuyệt đối tránh "Tâm lý học <xuống dòng> tích cực" - xuống dòng giữa "Hạnh" và "Phúc" cắt đôi một từ ghép, rất vô duyên và đã bị user góp ý trực tiếp). Nguyên tắc xử lý:
- Trường `title`/`headline` của `Intro`/`Outro` chỉ nên chứa cụm từ NGẮN, đủ an toàn để không tự wrap ở khung ngang chuẩn (khẩu quyết: xem trước độ dài so với khung, không đoán) - toàn bộ thông tin dài hơn (mô tả sách, tên tác giả, đơn vị phát hành...) phải tách sang các field RIÊNG, không nhồi vào `title`.
- `Intro` đã có thêm hai field tùy chọn để tách nội dung dài khỏi `title` (2026-08-31): `description` (một dòng mô tả phụ, cỡ chữ `subtitleSize*0.92`) và `creditLines` (mảng các dòng credit như "Tác giả:...", "Đơn vị xuất bản:...", cỡ chữ `subtitleSize*0.62`, mỗi dòng một `FadeUp` riêng) - dùng hai field này thay vì cố nhồi tất cả vào `title`/`subtitle`.
- Nếu BẮT BUỘC phải xuống dòng một cụm dài (trong `description`/`creditLines` hoặc caption khác), chỉ xuống dòng ở ranh giới cuối vế/cuối cụm từ có nghĩa (sau dấu phẩy, sau một cụm danh từ trọn vẹn, trước một liên từ) - không bao giờ xuống dòng giữa một từ ghép hay giữa tính từ và danh từ nó bổ nghĩa.
- **Lỗi gốc rễ đã xác nhận (đo bằng Playwright trên đúng cấu trúc CSS thật): `whiteSpace: 'pre-line'` + tự chèn `\n` ở ranh giới an toàn KHÔNG ĐỦ để tránh wrap sai** - vẫn xảy ra trường hợp cụm từ NGẮN (một từ ghép 9 ký tự) tự bị tách làm hai dòng dù còn dư rất nhiều khoảng trống. Nguyên nhân thật: `maxWidth` của `title` được đặt bằng **% CSS** (`'78%'`/`'92%'`), nhưng div chứa `title` nằm bên trong một `<FadeUp>` (chỉ có `opacity`/`transform`, KHÔNG có `width` cố định) lồng trong container `display:flex; flexDirection:'column'; alignItems:'center'` - với `alignItems` khác `'stretch'`, flex item con co theo nội dung (`shrink-to-fit`), khiến containing block của `title` có bề rộng KHÔNG XÁC ĐỊNH; browser resolve `%` trong tình huống này không đáng tin (đã tái hiện và đo trực tiếp bằng Playwright: cùng CSS nhưng đặt độc lập ngoài chuỗi flex/FadeUp thì đúng 2 dòng, lồng đúng cấu trúc thật thì tự nhảy thành 3 dòng). **Cách sửa đúng (đã áp dụng trong `Intro.tsx`)**: không dùng `%` cho `maxWidth` của các khối chữ nằm trong `FadeUp`/flex-column căn giữa - tính bằng **px thật** từ `useVideoConfig().width` (đã thêm `width`/`height` vào `useLayout()` ở `layout.ts` để dùng chung), ví dụ `maxWidth: width * (isVertical ? 0.92 : 0.78)`. Nếu phát hiện một khối chữ khác (`SectionTitle`, `InfoStat`, `InfoQuote`...) cũng dùng `maxWidth` dạng `%` bên trong cấu trúc `FadeUp`/flex-column tương tự và bị wrap sai, áp dụng đúng cách sửa này (px thật thay vì %) thay vì chỉ chỉnh nội dung chữ.

## Ba loại nội dung nên chủ động rà và đề xuất overlay (trước khi dựng, không chờ user yêu cầu)

Khi đọc transcript ở Bước 3, chủ động rà tìm và đề xuất overlay cho ba loại sau - trình bày thành bảng cùng lúc với phương án cắt, kèm mốc thời gian THEO LỜI NÓI (không phải số tùy chọn):

1. **Tên chương trình/chuyên đề/framework**: chỗ người nói xướng tên hoặc nhấn lại tên chương trình/framework - dùng `Caption` (thẻ chữ nổi bật, không che hết hình) đè lên đúng lúc nhắc tên; nếu trùng ranh giới phần lớn thì dùng `SectionTitle` full-screen thay vì Caption.
2. **Các bước của một quy trình, các cấu phần của một framework**: chỗ người nói liệt kê ("thứ nhất... thứ hai...", "bước một...", số đếm kèm danh từ). Dùng `InfoList` (câu dài) hoặc `InfoSteps` (nhãn ngắn, có thứ tự) - ưu tiên `overlay` đè lên hình đang nói (giữ tiếng liên tục) hơn là cắt cảnh sang đồ họa full-screen, trừ khi đó đúng là ranh giới chuyển phần.
3. **Các key message**: câu chốt, câu có sức nặng, đáng nhớ, đáng trích riêng (thường là câu tóm một ý lớn vừa giảng, hoặc câu hô ứng lại với tên bài/hook). Dùng `Caption` hoặc `InfoQuote` đè đúng lúc người nói câu đó.

Với mỗi đề xuất, ghi rõ: mốc bắt đầu-kết thúc theo LỜI NÓI về chủ đề đó trong transcript (không phải một số giây tùy ý), nội dung chữ dự kiến (trích/tóm từ transcript, không bịa), và loại overlay. Chờ user duyệt cùng lúc với phương án cắt (không cần thêm một vòng chờ riêng).

## Xác định thời lượng hiển thị overlay - theo NỘI DUNG, không theo số tròn

Thời lượng một overlay/infographic (kể cả bảng tên, Caption, Benefits, InfoList...) phải lấy GIÁ TRỊ LỚN HƠN giữa hai mốc sau, cộng thêm khoảng 1-2s đệm để không biến mất ngay khi người nói vừa chuyển ý:

- **Thời lượng người nói thực sự bàn về chủ đề đó** trong transcript (từ câu bắt đầu nhắc tới câu chuyển ý khác) - đây thường là mốc quyết định với nội dung được giảng kỹ, không phải lướt qua
- **Thời gian đọc chữ trên màn hình**: một dòng ngắn (tên chương trình, key message) cần tối thiểu 2.5-3s để mắt kịp nhận diện và đọc; danh sách nhiều dòng cần khoảng 1.3-1.6s mỗi dòng sau khi dòng đó đã hiện ra hết

Không đặt một con số "cho gọn" (ví dụ tròn 5s, 9s) rồi để mặc định - phải tính theo hai mốc trên rồi mới chốt số giây. Nếu overlay nằm trong một đoạn dùng kỹ thuật `overlay` (không cắt), nhiều overlay có thể chồng nối tiếp nhau trong CÙNG một đoạn quay liên tục (xem `overlay` dạng list trong tools/assemble.py) - mỗi overlay có mốc `at` riêng theo lời nói, miễn khoảng hiển thị của chúng không chồng lấn nhau.

**`Benefits` có cơ chế riêng, không tính thời lượng theo cách trên**: mỗi mục trong `items` nhận một prop `revealAt` (giây, tính từ mốc bắt đầu của chính overlay đó - khớp mốc `at`) để mục đó xuất hiện đúng lúc lời nói nhắc tới nó, thay vì cả danh sách hiện cùng lúc như slide tĩnh. Dùng cách này khi cần liệt kê một tiến trình/framework nhiều bước mà người nói giải thích trải dài qua nhiều chục giây (không hợp làm slide `InfoSteps` toàn màn hình một lần vì sẽ che mất hình quá lâu) - tra transcript lấy đúng câu/từ nhắc tới từng mục để tính `revealAt`, KHÔNG chia đều theo số mục.

## Xác định mốc `at` cho overlay theo đúng lời nói - kỹ thuật tra mốc và bẫy suy luận cộng dồn

Mốc `at`/`revealAt` của một overlay đồng bộ lời nói (Caption, hoặc nhiều pill Benefits rời rạc đặt ở các đoạn khác nhau) PHẢI được tra trực tiếp trong transcript, KHÔNG được ước lượng bằng cách cộng dồn thời lượng danh nghĩa của các đoạn trước đó cộng thêm một hệ số hiệu chỉnh "đã hiệu chỉnh bằng mắt". Cách làm sai này (từng dùng thật ở một dự án, đặt sai 2 trong 7 pill cuối clip, lệch 85-93 giây) có thể cho ra một overlay HIỂN THỊ ĐÚNG NỘI DUNG (chữ đúng, đồ họa đúng, không lỗi render) nhưng XUẤT HIỆN SAI THỜI ĐIỂM so với lời đang nói - lỗi này KHÔNG bị bắt bởi cách nghiệm thu quen thuộc (trích một khung hình tại mốc tính toán rồi xem đồ họa có hiện đúng không), vì khung hình đó vẫn hiện đúng nội dung của chính overlay đó, chỉ là tại một thời điểm sai trong lời nói - phải xem kỹ mục nghiệm thu bên dưới.

**Kỹ thuật tra mốc đúng - neo theo tỷ lệ ký tự trong chunk Whisper**: với mỗi cụm từ/câu cần neo overlay vào, tìm chunk Whisper (trong `.transcript.json`) chứa cụm từ đó, xác định vị trí ký tự của cụm từ trong `chunk.text` (`pos_char`), tính `frac = pos_char / len(chunk.text)` (dùng vị trí NGAY SAU khi cụm từ đó vừa dứt nếu muốn neo lúc ý đã nói xong), rồi `mốc_tuyệt_đối = chunk.start + frac * (chunk.end - chunk.start)`. Cách này bám sát nội dung THỰC SỰ đang được nói tại từng chunk, đáng tin hơn nhiều so với cộng dồn thời lượng danh nghĩa các đoạn trước (sai số cộng dồn qua nhiều đoạn, đặc biệt các đoạn `snap:true` có thời lượng thực khác thời lượng danh nghĩa - xem log "đoạn N: ... [X → Y]" sau khi assemble chạy). Khi một overlay không có cụm từ neo thật (thuần biên tập, ví dụ một callout không được nói thành lời), đặt vào một khoảng lặng thật gần nhất trong `silences.json` thay vì đoán bừa một con số giây.

**Nghiệm thu PHẢI đối chiếu nội dung overlay với lời đang nói tại đúng khung hình đó, không chỉ xác nhận overlay hiện ra không lỗi**: trích khung hình tại mốc `at` (cộng thêm độ trễ hiện dần như đã ghi ở mục cao nguyên phía trên), rồi đọc lại đúng đoạn transcript `[chunk.start, chunk.end]` bao quanh khung hình đó, xác nhận nội dung overlay khớp với ý đang được nói lúc đó - không dừng lại ở việc "khung hình có hiện chữ, chữ đúng chính tả, không lỗi render" như trước đây. Frame-check chỉ xác nhận overlay RENDER đúng, không xác nhận overlay ĐỒNG BỘ đúng - hai việc khác nhau.

## Overlay không có câu nói literal (editorial, không tra được transcript) - cách đặt và minh bạch với user

Không phải mọi overlay đồng bộ lời nói đều có một câu nói LITERAL để neo vào - một số là điểm biên tập (editorial) do user tự liệt kê muốn nhấn mạnh (ví dụ một trong '6 quyền lợi' user tự đặt ra cho sách) mà chính user cũng không nói thành lời đúng ý đó trong lần quay. Gặp trường hợp này:

- **Tìm kiếm CẠN KIỆT trước khi kết luận không có anchor**: grep toàn bộ transcript (không chỉ đoạn lân cận dự kiến) theo các từ khoá liên quan tới ý đó (đồng nghĩa, từ gần nghĩa) - chỉ khi chắc chắn không có mới coi là "không có anchor".
- **KHÔNG đặt bừa vào khoảng lặng gần nhất nếu khoảng lặng đó rơi vào GIỮA một mạch nói đang bàn chủ đề khác hẳn** - dù là một khoảng dừng hơi thật (không phải mid-word), nội dung pill vẫn sẽ trông "lạc quẻ" nếu lời đang nói ở đó thuộc một chủ đề không liên quan (đã xảy ra thật: pill "không tóm tắt được bằng AI" từng đặt vào khoảng lặng duy nhất tìm được, nhưng khoảng lặng đó nằm giữa đoạn giới thiệu bài tự đánh giá - hoàn toàn không liên quan tới AI/tóm tắt).
- **Ưu tiên đặt cạnh (ngay trước/sau) một overlay KHÁC cùng nhóm chủ đề**, trong vùng transcript đang bàn đúng chủ đề lớn đó (dù không có câu chữ khớp 100%), hơn là đặt đúng một khoảng lặng kỹ thuật nhưng sai chủ đề - ví dụ pill "không tóm tắt được bằng AI" nên đứng liền kề pill "không cần đọc từ đầu đến cuối" (cùng nhóm ý "cách tiếp cận cuốn sách"), không đứng ở đoạn đang nói về bài tự đánh giá.
- **LUÔN báo minh bạch với user** overlay nào không có câu nói literal và lý do chọn vị trí đó (không tự tin lặng lẽ coi như đã sync đúng) - để user xác nhận cách đặt hợp lý hay cung cấp thêm ngữ cảnh/câu nói thật mà Claude bỏ sót.

## Nghiệm thu chuỗi overlay dài: dùng CONTACT SHEET dày đặc, không chỉ vài điểm rời rạc

Khi một đoạn dài (60-200s) có NHIỀU overlay liên tiếp cần nghiệm thu thứ tự + đồng bộ, đừng chỉ trích vài khung hình rời rạc tại các mốc tính toán (dễ bỏ sót lỗi ở NHỮNG CHỖ không kiểm) - trích một khung hình mỗi 2 giây xuyên suốt cả đoạn bằng một lệnh ffmpeg duy nhất (), rồi ghép tất cả vào MỘT ảnh lưới (contact sheet, dùng PIL) có nhãn thời gian trên từng ô, đọc một lần bằng Read. Cách này cho thấy TOÀN BỘ trình tự lên/xuống của từng pill trong một lần nhìn - phát hiện chồng lấn, thiếu, sai thứ tự dễ hơn nhiều so với chắp nối các điểm-kiểm rời rạc, và rẻ hơn nhiều so với đọc từng khung hình riêng lẻ.

## Khi đã sửa nhiều vòng vẫn bị chê "lộn xộn, không khớp" - để user tự cho mốc từ bản render

Nếu đã qua 2-3 vòng suy luận từ transcript/silence mà user vẫn thấy pill sai vị trí, đừng suy luận thêm vòng nữa - hỏi user xem trực tiếp bản render và tự ghi lại mốc phút'giây (ví dụ "7p14s - 7p17s") cho từng pill. Mốc này đo trên chính output cuối cùng nên chính xác hơn mọi suy luận ngược từ transcript nguồn. Cách quy đổi: vì các segment liền mạch (không cắt bỏ khung nào giữa các đoạn liên tiếp trong cùng dải), thời điểm tuyệt đối trên bản render trùng gần như 1:1 với tọa độ nguồn (in/out) của timeline - chỉ lệch khoảng 1-3 giây do chính hiệu ứng fade-in của pill (mắt người đọc "thấy chữ" khi pill đã hiện gần đầy, không phải ngay từ khung hình đầu tiên của fade). Không cần cố khớp lệch 1-3 giây này bằng cách chỉnh thêm - đó là biên độ tự nhiên của hiệu ứng, không phải lỗi.

Khi thời gian mới của một pill khiến nó tràn qua ranh giới segment kế tiếp (vì overlay không thể render xuyên ranh giới cắt), đừng ép webm hay bỏ phần cuối - dời NGAY ranh giới segment (đổi `out`/`in` liền kề) sang mốc đủ trễ để chứa trọn cả overlay, rồi tính lại `at` của các overlay còn lại trong segment bị đổi mốc theo điểm bắt đầu MỚI. Việc này an toàn khi hai segment vốn liền mạch cùng một cảnh quay (in của đoạn sau = out của đoạn trước) vì không có cắt cảnh thật ở ranh giới đó.

## Infographic/overlay - khi nào đáng chèn và chèn bằng kỹ thuật nào

Chèn khi lời giảng LIỆT KÊ hoặc ĐÚC KẾT: "ba điểm", "bốn bước", một định nghĩa then chốt, một con số nghiên cứu (xem thêm mục "Ba loại nội dung nên chủ động rà" ở trên). Không chèn khi đang kể chuyện hoặc giảng cảm xúc - đồ họa lúc đó phá mạch. Mật độ tối đa khoảng một infographic mỗi 4-6 phút bài dài. Chữ trong infographic phải trích/tóm từ lời giảng, giữ đúng thuật ngữ user dùng (xem mục 4 "Chữ trên màn hình" trong phong-cach/PHONG-CACH.md, ví dụ các cặp từ đúng/sai người dùng đã nêu, không "dẫn dắt", ngoặc vuông cho thuật ngữ tiếng Anh).

Chọn loại: InfoList cho liệt kê; InfoSteps cho tiến trình có thứ tự (chỉ hợp nhãn NGẮN 2-4 từ, câu dài dùng InfoList); InfoQuote cho câu đúc kết đáng nhớ; InfoStat cho con số; Caption cho chữ nổi bật đè lên hình mà VẪN giữ hình người nói (không che hết); Benefits cho danh sách quyền lợi/hạng mục ngắn dạng pill đè lên hình.

**Ưu tiên kỹ thuật `overlay` hơn `broll` và hơn cắt cảnh full-screen, mỗi khi lời nói cần giữ liên tục qua đoạn đó**: `overlay` encode một lần liên tục, chỉ chồng lớp hình đồ họa lên trên (audio luôn từ nguồn, không bao giờ tách), nên không có mối nối nào cả trong lúc đồ họa hiện. `broll` (đổi hẳn hình, giữ tiếng) VẪN chia thành nhiều phần rồi concat - dù tiếng nói được giữ liên tục về NỘI DUNG, mỗi mối nối concat vẫn có rủi ro giật nhẹ về kỹ thuật. Chỉ dùng `broll` khi bắt buộc phải đổi cả một đoạn dài hình ảnh sang một nguồn hoàn toàn khác không thể overlay chồng lên được. Full-screen (insert cắt cảnh hẳn) chỉ dùng khi đó đúng là ranh giới chuyển phần, không phải để tránh làm overlay.

**Nguyên tắc này áp dụng cho MỌI độ dài clip, không chỉ clip ngắn Reels/Shorts**: với một clip kể chuyện dài hơn (ví dụ case study ~3-4 phút), nếu một đoạn nội dung cần một danh sách bước/số liệu đi kèm mà lời kể vẫn đang tiếp diễn liên tục, ưu tiên tách thành NHIỀU overlay Benefits độc lập (mỗi mục một file webm alpha ngắn ~4-5s, chỉ hiện đúng 1 mục, các mục trước đặt `label:""`/`revealAt:9999` để ẩn) đặt tại các mốc `overlay.at` khác nhau trong CÙNG một đoạn quay liên tục, thay vì cắt sang một slide toàn màn hình (`insert`) - kể cả khi lý do ban đầu muốn cắt là để "che" một đoạn tưởng có vấn đề (xem thêm lưu ý trong `phim-transcript/SKILL.md` về việc đừng vội kết luận một đoạn nghe lạ là hallucination chỉ vì transcript riêng một cửa sổ ngắn).

## B-roll (khi bắt buộc phải đổi hẳn nguồn hình)

- Chỉ dùng footage thật của user (cảnh lớp, hoạt động) - không bao giờ gợi ý stock footage
- Mỗi lần đè theo đúng thời lượng người nói đang nhắc tới điều B-roll chiếu (xem mục "Xác định thời lượng" ở trên), không chốt cứng 4-8s nếu nội dung nói dài hơn
- Tiếng của B-roll luôn bị thay bằng tiếng giảng (assemble làm sẵn) - chọn đoạn B-roll không có chữ/khẩu hình gây xao nhãng
- Cân nhắc trước: nếu B-roll chỉ để chèn đồ họa/infographic (không phải đổi sang cảnh quay khác hẳn), dùng `overlay` thay vì `broll` (xem mục trên) để tránh mối nối không cần thiết
- **`broll.at` là mốc thời gian TUYỆT ĐỐI trong file nguồn, KHÁC với `overlay.at` (tương đối so với đầu đoạn, xem mục "Overlay bán trong suốt" bên dưới)** - nhầm hai ngữ nghĩa này với nhau (đặt `broll.at` như thể tính từ đầu đoạn) khiến B-roll bật sai chỗ, thường là ngay từ đầu đoạn thay vì đúng lúc mong muốn (vì `max(in, at)` với `at` nhỏ hơn `in` sẽ luôn trả về `in`). Công thức đúng: `broll.at = in của đoạn + số giây muốn lùi vào trong đoạn`.

## Nhạc nền

- Chọn track và gainDb từ `nhac-nen/THU-VIEN.md` ở gốc thư mục (thư viện đã kiểm định bản quyền, có gainDb gợi ý theo từng track cho cả hai mode); track Kevin MacLeod phải kèm dòng ghi công trong mô tả video
- Bài giảng: mặc định `bookends` (chỉ intro/outro) - lời giảng cần không gian yên
- Clip quảng bá, highlight: `full` + duck; nếu user muốn nhạc "êm, không dập dồn" ngay cả ở mode full thì tắt duck (`"duck": false`) - nhạc vẫn fade đều, chỉ là không tự động lún xuống theo tiếng nói
- Không bao giờ để nhạc chèn lên lời ở mức nghe rõ giai điệu hơn lời
- Hiệu ứng âm thanh từ `hieu-ung/` dùng tiết chế: chuông xoay cho mở/kết thực hành, whoosh chỉ khi chuyển phần có chủ đích, chime khi infographic hiện

## Khung dọc

- cropFocus theo vị trí người nói: xuất 1 frame thử bằng ffmpeg với crop dự kiến, xem trước khi dựng cả bài
- Nếu người nói di chuyển nhiều trong khung, chia segment và đổi cropFocus theo đoạn

## Overlay bán trong suốt (Benefits) - vị trí và đối tượng cần gắn

- **Đối chiếu khung hình thật trước khi chọn `top`/`bottom` cho list từ 3 mục trở lên**: nếu người nói ngồi/đứng giữa khung, list nhiều mục dễ tự xuống 2 hàng và hàng dưới đè lên mặt (đã xảy ra thật, phải sửa lại sau khi user xem bản nháp). Nếu khung hình còn nhiều khoảng trống hai bên (người nói không chiếm hết bề ngang), ưu tiên bố cục CỘT DỌC bám cạnh trái/phải (`position:'left'`/`'right'` - component đã hỗ trợ từ 2026-08-30) thay vì hàng ngang giữa khung. Cách kiểm nhanh: xuất một khung hình ở đúng đoạn sẽ overlay, xem người nói nằm đâu trong khung, rồi mới quyết định vị trí lúc soạn job đồ họa - đừng đợi user phát hiện ở bản nháp.
- **Câu Hook có thể lặp lại bằng chữ trên màn hình** (không chỉ nghe): khi câu Hook mở đầu là một câu chốt mạnh, cân nhắc chủ động đề xuất thêm một overlay caption (Benefits 1 mục, chế độ `wrap`) hiện nguyên văn câu đó ngay trong lúc người nói đang nói - tăng khả năng ghi nhớ và giữ chân người xem tắt tiếng lướt qua. Đặt ở `position:'bottom'` nếu người nói ở giữa/trên khung.
- **LowerThird không chỉ dành cho khách mời**: clip giới thiệu/quảng bá có người dẫn chính (host) xuất hiện xuyên suốt CŨNG nên có LowerThird cho chính người đó (tên + chức danh lấy từ `brand.json`), đặt ngay đầu đoạn sau slide tiêu đề/intro - không chỉ gắn cho chuyên gia khách mời xuất hiện cùng. Dễ bỏ sót vì mặc định nghĩ LowerThird là để giới thiệu người MỚI xuất hiện, nhưng với clip quảng bá thì khán giả xem trên mạng xã hội chưa chắc đã biết cả người dẫn chính.
- **`position:'bottom'` cho pill Benefits dễ bị hiểu lầm là phụ đề, nhất là khi có nhiều pill nối tiếp nhau xuyên suốt clip dài**: đã bị user góp ý trực tiếp ("hiện ở dưới nó giống phụ đề") ở một clip giới thiệu sách. Với clip có NHIỀU pill từ khoá xuất hiện dồn dập (ví dụ liệt kê tên các vùng/bước trong một framework), ưu tiên `position:'right'` hoặc `'left'` (cột dọc bám cạnh) thay vì `'bottom'`, và cân nhắc chủ động đề xuất trước thay vì đợi user phát hiện ở bản nháp.
- **Prop `scale` mới (2026-08-31)** cho phép phóng to đều toàn bộ pill Benefits (khoảng cách, padding, vòng tròn số thứ tự, cỡ chữ) mà không cần đổi riêng từng giá trị - dùng khi user muốn pill "to hơn, nổi bật hơn" mà bố cục hiện tại vẫn đúng, đặc biệt hợp cho các nhãn quan trọng cần nhấn mạnh (tên miền/zone của một framework). Giá trị đã dùng thực tế: `1.15` cho pill từ khoá đơn, `1.1` cho pill tổng kết nhiều mục (cần chừa chỗ hơn vì liệt kê dài).
- **Overlay tổng kết (recap) cuối cùng cho một framework nhiều bước**: khi clip liệt kê tuần tự từng thành phần của một mô hình/framework qua nhiều đoạn (mỗi đoạn một pill riêng), nên chủ động đề xuất thêm MỘT overlay Benefits tổng kết cuối cùng (liệt kê lại đầy đủ tên các thành phần + tên mô hình) đặt đúng vào đoạn mà người nói tự nhiên tổng kết lại ("6 cái vùng này...", "tóm lại..."), đối chiếu transcript để tìm đúng câu tổng kết đó thay vì đặt cứng theo số giây - xem đây là danh sách các mục `items` với `revealAt` cách nhau ~0.8s để hiện cascading.

