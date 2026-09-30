# Nguyên lý thiết kế cảnh minh hoạ

Tài liệu gốc về CÁCH NGHĨ một cảnh: vì sao cảnh phải lớn dần theo lời, ngữ pháp khung, mười một khuôn cảnh, bố cục theo khung, màu theo vai, chuyển động, chữ, danh sách cấm. Mọi giá trị ở đây là điểm xuất phát đã kiểm; cảnh nào cần khác vì người xem thì làm khác và nói rõ lý do ở chốt duyệt (`skills/_chung/van-hanh.md` mục "Nguyên lý trước khuôn mẫu").

## 1. Vì sao cảnh phải lớn dần theo lời

- **Lời và hình đi cùng nhau, từng nhịp.** Mayer (nguyên tắc liền kề thời gian, phân đoạn, báo hiệu): người học hiểu sâu hơn khi hình của một ý xuất hiện đúng lúc lời nói tới ý đó, nội dung được chia thành đoạn nhỏ theo nhịp người nói, và phần quan trọng được báo hiệu bằng màu, độ sáng, vị trí. Tổng hợp tổng quan các phân tích gộp về thiết kế đa phương tiện (Noetel và cộng sự, 2022) xếp báo hiệu, phân đoạn và liền kề thời gian vào nhóm có bằng chứng vững.
- **Hình động hơn hình tĩnh khi thứ cần hiểu là SỰ THAY ĐỔI.** Phân tích gộp của Berney và Bétrancourt (2016, Computers & Education) cho thấy hình động nhìn chung giúp học tốt hơn hình tĩnh (g = 0,23 trên 140 cặp so sánh), lợi thế lớn hơn khi hình động đi cùng lời nói (g = 0,34) và khi không kèm chữ viết dài (g = 0,88): đúng với B-roll trong bài giảng, và là lý do chữ trên cảnh chỉ là cụm nhấn; Ploetzner và cộng sự (2020) lưu ý hiệu quả đến từ chỗ nội dung có đặc điểm thay đổi cần học. Hệ quả cho xưởng: cảnh minh hoạ đáng làm khi ý có chuyển động tự thân (một quá trình, một vòng lặp, một ngưỡng bị vượt rồi trở về); ý tĩnh thì một dòng chữ nổi (Benefits) hay một YNiem là đủ.
- **Báo hiệu có hiệu quả thật** (Schneider, Beege, Nebel và Rey, 2018; Richter, Scheiter và Eitel, 2016): màu theo vai và điểm sáng ở chỗ đang nói là báo hiệu, không phải trang trí. Một cảnh chỉ nên có một điểm được báo hiệu tại mỗi thời điểm.
- **Lỗi kiểu slide.** Bộ skill "faceless explainer" của HyperFrames (HeyGen, mã nguồn mở Apache 2.0) gọi tên lỗi thường gặp nhất khi AI dựng video giải thích: dồn toàn bộ khung ra trong khoảng một phần tư đầu rồi đứng yên. Thuốc chữa là viết mỗi cảnh thành một chuỗi cảnh con có mốc theo lời, phần lớn các lần hiện nằm ở nửa sau cảnh, và giữ yên khi ý đã đủ.

## 2. Ngữ pháp khung

Rút từ phong cách explainer người dùng chọn (2026-10-01). Một khung đầy đủ có năm lớp, không phải khung nào cũng cần đủ:

1. **Nhãn nhỏ** [kicker] (`.kicker`): FULL-CAP ngắn nói vai của cảnh trong mạch bài: NGUYÊN LÝ, VẤN ĐỀ, BƯỚC 2 / 4, THỰC HÀNH NGAY, MẸO, SO SÁNH. Nhãn có cấu trúc thật (bước 2 trên 4 là thứ tự thật), không đánh số cho đẹp.
2. **Tiêu đề** (`.tieu-de`): hai dòng là đẹp nhất, một cụm (1-3 từ) tô màu theo vai (`<em class="vai-...">`). Sentence case.
3. **Phụ đề** (`.phu-de`): một câu nói cảnh này trả lời câu hỏi gì, màu chữ phụ.
4. **Vùng sơ đồ** (`.the`, SVG): nhân vật chính, chiếm 40-60% khung, lớn dần theo lời.
5. **Dòng đọng** (`.ket`, `.nguon`): con số hay câu đúc kết ở cuối cảnh, kèm nguồn, tác giả.

B-roll trong bài giảng thường chỉ cần 4 và 5 (người dùng đang nói tiêu đề bằng lời); cảnh mở một phần hay clip thuần minh hoạ dùng đủ năm lớp.

## 3. Chuỗi cảnh con

Mỗi cảnh viết thành các cửa sổ thời gian theo lời:

```
Cảnh con 1 (0,0-a s): chỉ phần lời đang nói ở t = 0 hiện ra, không phải cả khung
Cảnh con 2 (a-b s):   phần kế tiếp hiện khi lời nhắc tới nó (một nhãn, một lớp, một nút, một con số)
  ...                 số cảnh con = số điểm nhắc trong lời, không cố định
Cảnh con N (...-hết): ý đã đủ; giữ yên cho người xem đọc (chuyển động sống nhỏ ở chính chủ thể nếu có)
```

Chữ ký chuyển động của cảnh thường rơi vào cảnh con quan trọng nhất (lúc người dùng nói ý chính). Cảnh dài hơn 12 giây mà không có điểm nhắc mới thì tách thành hai cảnh, hoặc cho chủ thể một chuyển động sống thật (sóng chạy tiếp, chấm đi vòng tiếp), không lắc lư khung.

## 4. Mười một khuôn cảnh

Mỗi khuôn là một hình dạng đã có chữ ký chuyển động; chọn khuôn theo vai của ý, thay nội dung, giữ chữ ký. Không khuôn nào hợp thì tự dựng từ các chuyển động ở mục 6, vẫn theo chuỗi cảnh con.

| Khuôn | Hợp với ý | Chữ ký chuyển động | Ví dụ |
|---|---|---|---|
| Dòng chảy nguyên lý | A biến đổi thành B qua một cơ chế | vật đi qua từng trạm theo mũi tên có nhãn, trạm cuối bừng sáng | trang web → chụp từng khung → video |
| So sánh hai cách | cách cũ và cách mới, có và không có | hai làn chạy cùng một thước đo, một làn hỏng dần (đỏ), làn kia đều (xanh), số tổng kết hai bên | quay màn hình rớt khung, render từng khung đủ khung |
| Bước k trên N | một bước trong quy trình nhiều bước | nhãn BƯỚC k / N, sơ đồ con của riêng bước đó, thanh tiến trình nhỏ | bốn bước render |
| Vòng lặp | chu trình lặp lại | bốn nút quanh một tâm, điểm sáng đi vòng, số đếm ở tâm tăng | tua đồng hồ, chụp, lặp |
| Đường theo thời gian | trạng thái thay đổi qua thời gian, ngưỡng, vùng | đường vẽ dần, chạm ngưỡng thì vòng lan và đổi màu | cửa sổ dung nạp (mẫu có sẵn) |
| Nhịp thực hành | một bài tập có nhịp (thở, đếm, chú tâm) | chấm sáng đi quanh hình theo đúng nhịp thật, số đếm theo giây | thở hộp (mẫu có sẵn) |
| Song song | nhiều việc cùng chạy, chia phần | các làn màu khác nhau trượt vào cùng lúc, nối lại ở cuối | chia khung cho bốn luồng |
| Tầng lớp | cấu trúc nhiều tầng, bóc từng lớp | các tầng xếp dần từ đáy, tầng đang nói sáng lên, các tầng khác lùi | tầng nhu cầu, các lớp của một hệ |
| Trung tâm và mạng lưới | một lõi nối với nhiều thành phần | nút bung ra quanh tâm, đường nối vẽ dần, lõi sáng khi đủ | framework có một lõi và các nhánh |
| Con số có đối chiếu | một con số và ý nghĩa của nó | số đếm dồn, thanh so sánh mọc cùng lúc, mốc tham chiếu | 22 / 600 khung |
| Mô phỏng vật thể | cơ chế bên trong một vật, một cơ thể | vật vẽ giản lược bằng SVG, dòng chảy bên trong chuyển động, biểu đồ hiệu quả đi kèm | tản nhiệt buồng hơi trong điện thoại, hơi thở và cơ hoành |

Khuôn mới thành công qua dự án thật thì thêm một hàng vào bảng này và lưu cảnh làm mẫu vào `do-hoa-chung/canh-kit/mau/`.

## 5. Bố cục theo khung

- **Ngang 16:9**: hai bố cục chính. Cột chữ trái khoảng một phần ba, sơ đồ phải hai phần ba (mẫu cửa sổ dung nạp); hoặc chữ trên, sơ đồ trải ngang bên dưới (so sánh, song song, dải thời gian). Hai cảnh liền nhau không dùng cùng một bố cục.
- **Dọc 9:16**: xếp chồng từ trên xuống (nhãn, tiêu đề, phụ đề, sơ đồ, dòng đọng); tâm thị giác khoảng 0,42 chiều cao; chữ to hơn (tiêu đề khoảng `--u * 10.5-11`, phụ đề `--u * 3.7`); trục toạ độ sơ đồ hẹp hơn (mẫu: 700 x 900 thay cho 1000 x 620) để chữ trong sơ đồ không bé. Không đặt nội dung quan trọng ở 15% đáy khi clip dọc có phụ đề burn-in.
- **Mật độ**: nhân vật chính chiếm 40-60% khung; ít nhất ba lớp chiều sâu (nền có vệt sáng rất nhẹ, thẻ, sơ đồ và nhãn); không để một cụm nhỏ lọt thỏm giữa khoảng trống (bài học 2026-09-22 của infomotion áp nguyên ở đây).
- **Thẻ nổi cạnh người nói**: thẻ chiếm một bên (khoảng 35% bề ngang ở khung ngang), nửa kia để trống hoàn toàn cho người nói; chọn bên theo khung hình thật (`data-ben="phai|trai"`). Khung dọc: thẻ nằm nửa dưới, mặt ở nửa trên.
- **Ô người nói** (`.o-pip`): tỉ lệ 16:9 ở khung ngang, đặt ở góc hay cột chữ; cảnh nhường đúng chỗ đó (class `an-khi-pip` cho phần bị thay).

## 6. Màu theo vai và ba họ màu

Cảnh gọi màu theo VAI, không theo tên màu: `--c-chinh` (khái niệm đang nói), `--c-ketqua` (đầu ra, điểm nhấn kết), `--c-tot` (trạng thái tốt, trong tầm), `--c-xau` (lỗi, vượt ngưỡng), `--c-khac` (phương án thứ hai, vùng đối lập); chữ `--chu`, `--chu-phu`, `--chu-mo`; nền `--nen`, `--nen-2` (thẻ), `--nen-3` (ô nhỏ). Đổi họ màu là đổi cả bộ mà nghĩa vẫn giữ.

| Họ màu | Khi nào |
|---|---|
| Đêm xanh (mặc định, chốt 2026-10-01) | giải thích cơ chế, số liệu, quy trình; hợp nhất với B-roll trong bài giảng vì tách hẳn khỏi màu phòng quay |
| Than đồng | dự án đã chọn theme tối của brand; nội dung trầm, chiêm nghiệm |
| Giấy mực | dự án theme sáng; clip thiền, thực hành nhẹ; tiêu đề chuyển sang Lora |

Cả dự án một họ màu. Màu vai là màu ngữ nghĩa: một cảnh dùng tối đa ba vai cùng lúc; đỏ chỉ cho điều thật sự là lỗi hay ngưỡng bị vượt.

## 7. Chuyển động

- Vào: mờ sang rõ, trồi 14-30 px, 0,6-0,9 giây, easing `CANH.E.em` (bezier 0.22, 1, 0.36, 1, chữ ký của xưởng). Đi từ A sang B có chủ đích (vẽ đường, di chuyển): `E.vaora`. Thời gian trôi đều (sóng, chấm đi quanh hình): tuyến tính.
- Không spring nảy, không "thở" lười (phóng to thu nhỏ cả thẻ theo vòng lặp), không lia hay đẩy máy chậm ở nửa sau cảnh (làm mỏi mắt), không nhiều thứ trôi độc lập như màn hình chờ.
- Chuyển động sống chỉ ở chính chủ thể đang làm việc của nó: đầu sóng hơi phập phồng, vòng lan ở điểm vượt ngưỡng, số đếm theo nhịp.
- Chữ chỉ hiện SAU khi phần hình nó gọi tên đã vẽ xong; hai chi tiết cùng vùng không gian thì tách cả vùng lẫn thời điểm.
- Ra: cảnh B-roll không cần tự mờ ra (lắp ghép cắt về cảnh quay); cảnh cuối chương hay cuối clip thuần minh hoạ mờ ra khoảng 0,5 giây.

## 8. Chữ

- Theo `phong-cach/PHONG-CACH.md` mục 4: thuần Việt, thuật ngữ gốc trong ngoặc vuông [English] cỡ nhỏ hơn màu chữ phụ, sentence case, gạch ngang thường, không Title Case, không emoji.
- Font: Be Vietnam Pro 800 cho tiêu đề (Lora 600 ở họ Giấy mực), 400-600 cho chữ; JetBrains Mono cho mã, số kỹ thuật. Tất cả nhúng sẵn trong kit, đủ dấu tiếng Việt.
- Cỡ tối thiểu sau khi quy đổi ra điểm ảnh của khung: chữ nội dung 22 px ở khung ngang, 30 px ở khung dọc; nhãn trong sơ đồ không nhỏ hơn 20 px.
- Chữ trên hình là cụm nhấn trích từ lời; con số và tên nghiên cứu phải có dòng "Kiểm chứng:" trong kịch bản cảnh.

## 9. Danh sách cấm

- Gradient tím sang xanh rực kiểu "AI", bokeh trôi, hạt sáng bay vô nghĩa, hình trang trí đứng thay cho một ẩn dụ được thiết kế.
- Giao diện giả (trình duyệt, điện thoại, cửa sổ ứng dụng) khi chủ đề không nói về giao diện đó.
- Hiện cả khung trong một phần tư đầu rồi đứng; nhiều thứ trôi độc lập; lắc lư cho có.
- Chép nguyên câu người dùng đang nói lên hình; bịa thêm ý, con số, trích dẫn.
- Ảnh, clip do AI tạo thay cho hình thật về người, nơi chốn, sự kiện.

## 10. Nguồn

- Mayer, R. E. (2021). *Multimedia learning* (ấn bản 3). Cambridge University Press.
- Berney, S., & Bétrancourt, M. (2016). Does animation enhance learning? A meta-analysis. *Computers & Education, 101*, 150-167. https://doi.org/10.1016/j.compedu.2016.06.005
- Ploetzner, R., Berney, S., & Bétrancourt, M. (2020). A review of learning demands in instructional animations. *Journal of Computer Assisted Learning, 36*(6), 838-860. https://doi.org/10.1111/jcal.12476
- Schneider, S., Beege, M., Nebel, S., & Rey, G. D. (2018). A meta-analysis of how signaling affects learning with media. *Educational Research Review, 23*, 1-24.
- Richter, J., Scheiter, K., & Eitel, A. (2016). Signaling text-picture relations in multimedia learning: A comprehensive meta-analysis. *Educational Research Review, 17*, 19-36.
- Noetel, M., và cộng sự (2022). Multimedia design for learning: An overview of reviews with meta-meta-analysis. *Review of Educational Research, 92*(3), 413-454. https://doi.org/10.3102/00346543211052329
- HeyGen (2026). HyperFrames, skill `faceless-explainer` (visual-design, motion-language). Mã nguồn mở Apache 2.0, https://github.com/heygen-com/hyperframes. Xưởng mượn nguyên lý (chuỗi cảnh con theo lời, khuôn cảnh có chữ ký, danh sách cấm), không dùng mã.
- Hình mẫu người dùng gửi ngày 2026-10-01 (clip "Render animation từ web ra video" của một người làm video giải thích trên Claude): nguồn của ngữ pháp khung ở mục 2 và họ màu Đêm xanh.
