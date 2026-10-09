# Clip ngắn có minh hoạ: nguyên lý rút từ ba short đã dựng

Rút từ ba short đã dựng và được người dùng đánh giá cao: một clip 179 giây có tám cảnh minh hoạ, một clip 73 giây có hai cột so sánh, một clip 61 giây có một thẻ khung đi qua hộp AI. Khi cả loạt short cần đồng đều với mặt ở ô trên và cảnh ở ô dưới thì dùng khuôn `mat-tren` và bộ công cụ `short-*` ở `skills/phim-clip-ngan/references/short-mat-tren.md`. Đây là điều rút ra để hiểu, không phải khuôn để lặp: mỗi clip mới có lời, người nói và nhịp riêng, nên cách làm của nó có thể và nên khác. Bất biến kỹ thuật và giá trị vẫn giữ tuyệt đối (`skills/_chung/van-hanh.md` mục "Nguyên lý trước khuôn mẫu").

## 1. Chọn đoạn: một ý trọn, tự đứng được

- **Người lạ không có bối cảnh.** Đoạn đáng làm short là đoạn mà người chưa xem bài dài vẫn hiểu từ đầu đến cuối. Nghe thấy "hồi nãy khách mời có nói", "như phần trước", tên một người thứ ba chưa giới thiệu là tín hiệu cần xử lý: cắt vào sau câu đó nếu nhịp hơi cho phép, nếu không thì chọn điểm vào khác. Điều đã bỏ ghi vào mục "cần người dùng xem lại" để người dùng biết.
- **Lập luận có hình dạng thì short có sức.** Ba short đều có cùng hình dạng tự nhiên trong lời: luận đề rõ (một khung, một định nghĩa, một câu hỏi), rồi ví dụ cụ thể từ chính người nói, rồi khái quát hay mở rộng. Short Skill AI: "skill AI là khung chuyên môn mô tả rõ ràng" (luận đề) → skill làm slide của người dùng gồm màu, phông chữ, ít chữ, sơ đồ quen dùng (ví dụ) → "nhìn từ phía AI, khung chuyên môn là bộ skill đã đóng gói, dùng được rất nhiều lần" (khái quát). Hình minh hoạ đi theo đúng hình dạng này.
- **Hook là luận đề của chính người nói**, không nhất thiết là câu gây sốc. Câu nào cho người lạ biết "mình sắp hiểu điều gì" mà vẫn thật với lời gốc thì đủ. Hook có thể lấy từ ngay trước thân vài giây rồi thân vào lại ở nhịp thở kế tiếp, miễn không lặp lại câu đã nói. Có khi nên dừng hook giữa câu để tạo tò mò (7C), có khi hook đã là một câu trọn (Skill AI); chọn theo cảm giác người xem ở giây thứ ba.
- **Con số hay nhận định người nói ước lượng tại chỗ** ("có thể gọi là 90-100%"): giữ trong lời nếu đó là giọng của họ, nhưng không đưa lên chữ trên hình, thumbnail hay mô tả (chưa có nguồn, dễ bị đọc như khẳng định). Ghi vào mục cần người dùng xem lại và hỏi người dùng giữ hay cắt.
- **Gọi ứng viên bằng slug và tên nội dung**, không chỉ bằng số thứ tự: số trong kế hoạch và cách người dùng gọi có thể lệch nhau ("S5" của người dùng là short thứ tư của kế hoạch). Không chắc thì hỏi một câu bằng nội dung ("cái nói về skill AI hay cái về người làm bạn khó chịu?").

## 2. Điểm vào và điểm ra

- **Kết ở chữ cuối của ý đã trọn.** Sau đó outro lên ngay. Các cue và nhận dạng tự động thường kéo dài sang nửa câu kế tiếp; phần "câu thừa" ấy là chỗ người dùng nghe ra ngay còn máy không thấy. Đừng chốt điểm kết theo mốc cuối của cue hay của đoạn Whisper.
- **Tìm điểm cắt bằng đường bao năng lượng 10-20 ms của chính thành phẩm đã dựng**, không chỉ bằng ASR: ASR trên cửa sổ ngắn hay bịa chữ ở cuối ("Hãy subscribe cho kênh..."). Đếm âm tiết sau chữ cuối: khoảng trũng 0,05-0,15 giây ngay sau chữ cuối là chỗ cắt, `fadeOut` 0,05 giây để không có tiếng bụp. Kiểm lại bằng đường bao quanh mối cắt: năng lượng phải tụt gọn, không còn đuôi.
- **Người dùng yêu cầu rút đuôi sau khi đã dựng xong** (đã xảy ra ở cả 7C và Skill AI) là việc nhỏ nếu nhớ đúng thứ tự: đổi `out` của đoạn thân, bớt phần giữ cuối của cảnh minh hoạ bằng `overlay.duration` kèm `giu` (không cần render lại cảnh, xem `skills/phim-canh-minh-hoa/references/viet-canh.md` mục 5), sửa mốc kết cue cuối, dựng lại, burn lại, nghiệm thu lại, cập nhật độ dài trong ghi chú gói đăng tải. Để việc này dễ, làm cảnh minh hoạ có 1-2 giây giữ yên ở cuối.

## 3. Hình minh hoạ: một chủ thể biến hình theo lập luận

- **Một chủ thể xuyên suốt, không phải chuỗi hình rời.** 7C là một sân bóng mini bảy chỗ đứng, từng cầu thủ sáng lên theo lời gọi tên. Người làm bạn khó chịu là hai cột so sánh rồi bảy vị trí Dream Team. Skill AI là một thẻ khung đi từ điền từng mục, qua hộp AI, ra slide, rồi đóng gói thành skill. Cái xuyên suốt cho người xem một thứ để theo dõi bằng mắt trong lúc tai nghe, nên họ ở lại.
- **Lấy ví dụ người nói nêu làm nội dung hình**, đúng từng mục họ nhắc, đúng thứ tự họ nhắc: hình không thêm ý, không đoán. Tên khái niệm, vai, mã màu hay phông chữ được gọi tên thì hiện ra đúng lúc được gọi tên.
- **Ba nhịp là điểm xuất phát:** hiện hay điền theo lời (chất liệu), vận hành (cái vừa dựng đi vào, biến đổi, đi ra), khái quát hay đóng gói (một câu đúc kết thành một hình: phương trình "khung chuyên môn = skill AI, nhìn từ phía AI", gói có băng "đã đóng gói", đội đủ bảy người). Khoảnh khắc đúc kết đặt đúng lúc lời nói tới ý chính. Lời ít bước hơn thì ít nhịp hơn.
- **Cảnh liền mạch qua các điểm cắt.** Khi thân được ghép từ nhiều đoạn, mỗi cảnh phát lại các sự kiện trước nó để thẻ không "quên" trạng thái sau mỗi mối nối (7C làm tám cảnh theo cách này). Thân là một đoạn liên tục thì một cảnh dài là đủ.
- **Bố cục trên khung dọc:** mặt người nói luôn thấy ở nửa trên; thẻ ở nửa dưới, đủ lớn để đọc khi lướt điện thoại (thẻ rộng khoảng 80% khung, chữ trong hình từ 30 px); phụ đề nằm dưới thẻ; cảnh bắt đầu sau khi LowerThird tắt để mặt và bảng tên được nhìn trọn. Cảnh thu nhỏ để nhường chỗ (thẻ khung thu về góc khi AI lên) vẫn phải đọc được ở cỡ đó. Dài hơn khoảng hai phút rưỡi thì cho mặt người nói một quãng thở lớn giữa chừng (7C làm ở Coach).
- **Họ màu và nhận diện đi theo chương trình** ; cả loạt một họ màu. Chữ trên hình là cụm nhấn trích từ lời, câu trích chưa rõ tác giả thì ghi "chưa rõ tác giả" thay vì gán.
- **Soi trước khi báo:** ảnh từng mốc cảnh con trên contact sheet, rồi khung ghép thật ở ba chỗ: hook, lúc LowerThird và phụ đề cùng hiện, và khung cuối của cảnh. Nền trong suốt (`data-alpha`) phải thử bằng khung ghép thật vì theme có thể đè nền đặc lên (đã gặp ở 7C).

## 4. Phụ đề và tiếng

- Phụ đề theo hơi nói, không theo số ký tự thuần: nhóm cân bằng giữa hai dòng, ưu tiên ngắt ở dấu câu, khoảng 28 ký tự mỗi dòng trên điện thoại, dài hơn thì hai dòng. Chi tiết và chuỗi burn cùng chuẩn hoá âm lượng: `references/phu-de-ass.md` mục 4.
- Cue đặt theo ranh giới cụm nghe được ở chính thành phẩm (ASR file đã dựng, mốc thành phẩm), chữ soát tay theo large-v3 và tai nghe. Chỗ nhận dạng chưa chắc ("Thực ra" hay "Thật ra", "xài") liệt kê cho người dùng nghe lại, không tự quyết im lặng.
- Chuẩn hoá âm lượng trong cùng lượt burn phụ đề (nén nhẹ, nâng, giới hạn đỉnh), rồi đo: đạt -14 ± 1 LUFS và true peak không quá -1 dB trước khi báo. Chỉnh 1-2 dB nếu lệch, đo lại.

## 5. Nhịp làm việc với người dùng

1. Đề xuất danh sách ứng viên kèm mốc, hook, ý chính, độ dài, khuôn hình đề xuất, các câu hỏi mở (một danh sách, người dùng chốt một lần).
2. Hỏi trước khi dựng đúng những điều đáng hỏi: họ màu, vẽ theo lời hay người dùng có sơ đồ gốc, độ dài khi vượt trần, có giữ câu nhạy cảm hay không. Sau khi người dùng chốt thì không hỏi lại.
3. Dựng từng clip đến hết: cắt, cảnh, ghép, phụ đề, nghiệm thu máy, nhìn khung thật, gói đăng tải, hồ sơ dự án. Báo ngắn: video ở đâu, gói đăng tải ở đâu, các điểm cần người dùng nghe lại.
4. Người dùng góp ý mốc cắt hay chữ thì sửa tại chỗ theo thứ tự ở mục 2, báo lại một hai câu.

## 6. Mẫu tham chiếu

| Short | Nguồn | Hình chủ thể | Điều đáng học |
|---|---|---|---|
| doi-bong-7c | người trình bày, 179 s | sân bóng mini, bảy vai | một sân xuyên suốt; cảnh phát lại sự kiện trước để liền qua mối nối; quãng thở cho mặt; QR ở outro |
| nguoi-lam-ban-kho-chiu | khách mời, 73 s | hai cột, rồi bảy vị trí Dream Team, kính lúp | cắt "Dạ" xen giữa ở mối nối; câu trích không rõ tác giả không gán tên; mô tả không khẳng định điều người nói không nói |
| skill-ai-khung-chuyen-mon | người trình bày, 61 s | thẻ khung đi qua hộp AI ra slide, đóng gói | hook là luận đề; ví dụ của chính người nói; số ước lượng giữ trong lời, không lên hình; kết đúng chữ cuối |

Nhật ký và số liệu kỹ thuật chi tiết của mỗi clip nên ghi lại trong `docs/BAI-HOC.md` hoặc ghi chú dự án của bạn.
