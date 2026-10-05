# Mẫu bộ lệnh làm phim hoạt hoạ tự sự (phim-hoat-hoa, chế độ SOẠN LỆNH)

Nội dung để chép ra rồi điền biến số. Phần hằng số giữ nguyên; tự soát bằng `skills/phim-hoat-hoa/references/checklist.md` mục "Bộ lệnh" trước khi giao.

## Phần 7. Mẫu bộ lệnh (nhánh A, điền biến số trong ngoặc nhọn)

```
Bạn là đạo diễn kiêm lập trình viên hình hoạ sáng tạo [creative coding]. Hãy làm một phim hoạt hoạ tự sự dài khoảng {DUR} giây
trong MỘT file index.html tự chứa, và xuất thêm bản MP4 1080p có âm thanh.

[1] RÀNG BUỘC KỸ THUẬT
- Chỉ Canvas 2D. Không thư viện, không ảnh, không base64, không file âm thanh. Mọi pixel và âm thanh do code tạo.
- Ngoại lệ duy nhất: font Lora (400, 500, 600, italic) và Be Vietnam Pro (400, 500) từ Google Fonts, fallback serif/sans-serif.
- Khung logic {1280×720 | 720×1280}, vẽ ở hệ số S=1.5.
- render(t) thuần theo thời gian. PRNG seed (mulberry32 + hash + value-noise 1D). CẤM Math.random() trong vòng render.
  Kiểm chứng: render(t) hai lần phải ra ảnh giống hệt.
- Boil nét tay: BOIL = floor(t*6), biên độ nhỏ. Đóng băng BOIL ở các cảnh đánh dấu "tĩnh" và sau khi chữ ký viết xong.
- Timeline là mảng cue {scene, duration, k, tr, td, at}, start tự cộng dồn, gọi scene(lt/k, t).
- Chuyển cảnh: vẽ cảnh trước ở (duration + lt), clip cảnh mới theo mặt nạ.
- Điều khiển: Space, thanh tua, ?t=, nút nhạc (mặc định tắt), nút caption, nút Record (captureStream(30) + audio → WebM).
- Hiệu năng: lớp nặng cache offscreen theo N pha, dựng lười, prewarm; chất giấy dựng một lần rồi phủ 'multiply'.
- Hàm breath(t, chu kỳ): pha thở 0-1, pha thở ra dài hơn hít vào khoảng 1.5 lần.

[2] CÂU CHUYỆN
Thông điệp lõi: {một câu}
Cung chuyển hoá: mắc kẹt → dừng lại → nhận biết → nới ra → nảy mầm → tái hợp.
Mô-típ xuyên suốt: {MÔ-TÍP} qua các trạng thái {trạng thái 1 → 2 → 3 → 4}. Trạng thái cuối giữ dấu vết trạng thái đầu.
Cảnh gương: cảnh {a} và cảnh {b} cùng bố cục, đổi ánh sáng và cách hiện diện của nhân vật.
Không công thức thành công bề ngoài, không so sánh, không giảng đạo. Cảm xúc tĩnh, ấm, thật.

 # | scene | dur | k | chuyển cảnh | nội dung hình | thân | nhịp thở
{bảng cảnh 8-12 dòng}

[2B] BIẾN THỂ CÓ GIỌNG NÓI (thay [2] khi làm từ file voice; đính kèm voice.wav + transcript có mốc thời gian)
- Giọng là trục thời gian duy nhất. File voice là ngoại lệ của luật "không file âm thanh".
- Đọc trọn transcript hai lượt trước khi vẽ: lượt nghĩa (thông điệp lõi, bản đồ lập luận, khái niệm cố định, câu chuyện),
  lượt cảm (cung cảm xúc, câu đắt nhất, chỗ dừng lâu). Hình không được nói điều người nói không nói.
- Ẩn dụ gốc của bài làm mô-típ: {MÔ-TÍP} qua các trạng thái {…}. Chỉ dùng cung chuyển hoá nếu bài có cấu trúc đó;
  không thì bám cấu trúc của bài: {các bước / các lớp / các câu hỏi}.
- Thế giới: bối cảnh {2-4 bối cảnh có tham số}, nhân vật {1-3, các trạng thái thân}, không nhép miệng, lời là giọng kể ngoài hình.
- Mảng BEATS {id, start, end, loai, tu_khoa_at} từ transcript; cue sinh từ BEATS, không cộng dồn danh nghĩa.
  Cách xử lý theo loại: câu chuyện → cảnh diễn; khái niệm → cảnh ẩn dụ; framework → vật thể vẽ tay hiện đúng lúc gọi tên;
  số liệu → hình đếm vẽ tay; nhân quả → cảnh chuyển trạng thái; câu nhấn/câu hỏi → khoảng thở; chuyển ý → chuyển cảnh.
- Hình hiện trước từ khoá 0.2-0.5s. Chuyển cảnh chỉ đặt vào khoảng lặng giữa hai ý. Tối đa một ý hình mới mỗi 8-12s;
  giữa các ý, cảnh vẫn sống bằng chuyển động nhỏ; quá 25s chưa đổi thì đổi góc máy hoặc ánh sáng.
- Xem trực tiếp: đồng hồ render(t) = audio.currentTime của <audio> chứa voice. Xuất: nhạc + SFX render riêng,
  ffmpeg trộn với voice bằng sidechaincompress, nhạc dưới giọng 15-18dB. Caption chỉ hiện cụm nhấn, không chép lời.
{bảng BEATS: mốc | lời (rút gọn) | loại | cách xử lý | hình | thân | mô-típ | caption}

Credit (căn giữa dưới chữ ký, có nét 3px ngắn phía trên):
  dòng 1: "Thiết kế và tạo bởi {TÊN}"   (Lora italic 19px, mực, alpha 0.85)
  dòng 2: "{CHỨC DANH nguyên văn}"        (Lora italic 15px, alpha 0.62)
  dòng 3: "Cùng trí tuệ nhân tạo Claude của Anthropic" (Be Vietnam Pro 12px, alpha 0.5, tuỳ chọn)

[3] PHONG CÁCH HÌNH
- Tối giản, tĩnh tại, "thở". Giấy ngà sạch, hạt mịn, vignette rất nhẹ. Không photoreal.
- Bảng màu (chỉ các màu này và pha trộn): {danh sách hex}.
- Đường nét 3px là chữ ký thị giác. Silhouette đọc được trong 0.3 giây. Mỗi cảnh một chủ thể. Chân trời thấp.
- Chuyển động: easing cubic-bezier(0.22, 1, 0.36, 1), không nảy, không spring.
- Không chữ trong hình trừ caption, chữ ký và nhãn ngắn viết tay cho thành phần framework (khi có voice). Không emoji.
- Chuyển cảnh chỉ dùng: {chọn 4-5 từ bảng 4.1}. KHÔNG crossfade liên tục, không zoom xoáy, không glitch.
- Điểm neo thị giác cố định: {vật, toạ độ}.
- Nhịp thở nền ở cảnh tĩnh: dao động 1-1.5% theo breath(t, 10). Cảnh mắc kẹt: breath(t, 2.5).
- Khoảng lặng: cảnh {x} tắt nhạc, đóng băng boil, {2-3} giây.

[4] BỘ VẼ
wobbleLine/wobbleShape, partial, catmull, cam(zoom, focus), glow, breath,
person (ít nhất hai trạng thái thân: {co/mở...}, trả về toạ độ bàn tay), {mô-típ} với morph 0→1 qua các trạng thái,
{vật thể riêng của phim}.

[5] ÂM THANH: một hàm buildAudio(ac, out, from, base)
- Lên lịch toàn bộ timeline, dùng chung cho phát trực tiếp và OfflineAudioContext 48kHz → WAV.
- SFX neo theo cảnh: S(tên cảnh, u) = cue.start + u*k.
- Nhạc {60-72} BPM: mắc kẹt La thứ + drone 55Hz thưa; dừng lại gần im lặng; nhận biết MỘT chuông chánh niệm ngân ≥6s;
  nới ra pad trưởng Fmaj7-Cadd9; nảy mầm thêm {sáo trúc | đàn tranh | cello} tổng hợp; kết hợp âm ngân 3-4s.
- SFX: tiếng thở theo breath(), bút lướt giấy khi nét hiện, giấy xào xạc, {SFX riêng theo cảnh}.
- TRÁNH "ting ting": không rải chuông, không hộp nhạc, không chùm lấp lánh. SFX dưới nhạc (hệ số ~0.55). Xuất 2 stem.
- Master qua DynamicsCompressor, MP4 chuẩn hoá -14 LUFS, TP -1.5 dB.

[6] CAPTION
- Cú pháp 'text |cụm nhấn|'. Thân Lora italic 500 33px; cụm nhấn Lora italic 600 màu {nhấn} + gạch chân 3px vẽ dần.
- Hiện từng từ (mờ → rõ, trồi nhẹ), stagger = min(0.085, 0.33*thời lượng/số từ). Thoát bằng mờ dần.
- Khai báo tương đối theo cảnh {cue, a, end|until}. Đặt ở vùng trời trống, không che mặt và bàn tay.
- Ít nhất 30% thời lượng không caption.
- Nội dung:
  {scene}  "{caption}"
  ...
  {scene cuối} "{câu hỏi mở thực sự}"

[7] XUẤT MP4
Playwright + Chromium headless: chờ document.fonts.load cả hai font, kiểm fonts.check(...'ạ'); mỗi khung render(i/30)
và toDataURL('image/jpeg',0.93) trong CÙNG một evaluate, ghi nối vào frames.mjpeg; âm thanh qua window.renderSoundtrack().
ffmpeg: -f mjpeg -framerate 30 -i frames.mjpeg -i soundtrack.wav
-af "highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st={DUR-1}:d=1"
-c:v libx264 -crf 17 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart

[8] QUY TRÌNH: KHÔNG làm một phát cả phim
1) Engine + giấy + still cảnh mở → DỪNG, mô tả still, sửa chỗ khó đọc.
2) Nhân vật + mô-típ + chuỗi mắc kẹt.
3) Dừng lại + nhận biết + nới ra.
4) Nảy mầm + tái hợp + cảnh gương + chữ ký + credit.
5) Âm thanh + caption → render MP4.
Sau mỗi bước: contact sheet 2 khung/cảnh, tự soát rồi sửa. Checklist:
{dán checklist Phần 8 mục "Phim"}
```
