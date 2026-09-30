# Chuyển cảnh, âm thanh, caption, mật độ, danh mục cấm (phim-hoat-hoa)

Nguyên liệu tham khảo khi viết bảng cảnh và dựng. Nhánh A (Canvas) và nhánh B (Remotion trong xưởng) khác nhau ở cách làm âm thanh: xem mục 4.2.

## Phần 4. Nguyên liệu tham khảo

### 4.1. Từ vựng chuyển cảnh (chọn 4-5 cho một phim)

| Kiểu | Nghĩa tự sự | Gợi ý kỹ thuật |
|---|---|---|
| Vòng tròn nở từ một điểm sáng | Đi vào nội tâm, vào hồi ức | clip theo đĩa tròn, viền nét mực 3 px run nhẹ, easing ease-out |
| Mô-típ dẫn cảnh | Liên tục của hành trình | vật mô-típ bay/lăn ngang, cảnh mới lộ ra sau nó |
| Cắt thẳng vào tĩnh lặng | Khoảnh khắc dừng lại | cắt cứng, tắt nhạc, đóng băng boil |
| Nét 3 px quét như mép giấy lật | Sang hồi mới | mặt nạ theo một đường thẳng di chuyển, có nét nhấn đi kèm |
| Giọt mực/nước loang | Nảy mầm | mặt nạ hình loang theo noise, nở chậm từ tâm |

Cấm: crossfade liên tục, zoom xoáy, glitch, lắc máy, spring nảy, lật 3D.

### 4.2. Âm thanh

- **Nhánh Canvas:** một hàm `buildAudio(ac, out, from, base)` lên lịch toàn bộ timeline, dùng chung cho phát trực tiếp (AudioContext, tua được) và render offline (OfflineAudioContext 48 kHz stereo → WAV).
- **Nhánh Remotion:** nhạc lấy từ thư viện trong `nhac-nen/`, SFX từ `hieu-ung/` theo `thu-vien/AM-THANH.md`; SFX tổng hợp chỉ khi thư viện không có (render Web Audio offline thành WAV rồi đưa vào `<Audio>`).
- **Hoà âm theo cung:** mắc kẹt (La thứ, drone 55 Hz, tích tắc dồn) → dừng lại (gần im lặng) → nhận biết (một chuông chánh niệm, ngân dài) → nới ra (pad trưởng mở Fmaj7 - Cadd9) → nảy mầm và tái hợp (thêm một giọng nhạc cụ ấm: đàn tranh, sáo trúc hoặc cello). Nhịp độ 60-72 BPM (gần nhịp tim nghỉ). Kết bằng hợp âm ngân 3-4 giây.
- **SFX chữ ký:** tiếng thở (noise lọc dải, bao theo chu kỳ thở), bút lướt giấy khi nét vẽ hiện, giấy xào xạc, gió nhẹ, nước. SFX theo từng nấc tự sự, đặt dưới nhạc (hệ số khoảng 0,55).
- **Tránh "ting ting":** không rải chuông, không hộp nhạc, không chùm lấp lánh; tối đa một nốt trầm mỗi ô nhịp.
- Master qua compressor; -14 LUFS, true peak -1,5 dB (cổng nghiệm thu của xưởng chấp nhận -14 ± 1 LUFS, true peak không quá -1 dB). Xuất nhạc và SFX thành hai stem.
- **Khi có voice (lối vào 1):** giọng người dùng là lớp trên cùng, không bao giờ bị nhạc hay SFX che. Hoà âm đi theo cung cảm xúc của chính bài nói (đọc ở Phần 3.1), không áp khuôn sáu nấc; bài giải thích cấu trúc thì chỉ cần một pad ấm ổn định đổi hợp âm theo chương. Nhạc dưới giọng 15-18 dB, có quãng giọng đứng một mình. Cách hạ nhạc tuỳ nhánh: nhánh A trộn bằng `sidechaincompress` trong ffmpeg (voice làm tín hiệu điều khiển); nhánh B dùng `music` của `assemble.py` với track và `gainDb` theo `thu-vien/AM-THANH.md`, `mode: "full"` + `duck: true`. Giọng tổng hợp chỉ dùng khi người dùng yêu cầu (ví dụ lời đọc bổ sung cho phim lối vào 2).

### 4.3. Caption

- Cú pháp `'thân chữ |cụm nhấn|'`. Thân: Lora italic 500 (khoảng 33 px ở khung logic 1280); cụm nhấn: Lora italic 600, màu nhấn, gạch chân 3 px vẽ dần.
- Hiện từng từ (mờ → rõ, trồi nhẹ), stagger = min(0,085; 0,33 × thời lượng / số từ); thoát bằng mờ dần, không bay vụt.
- Khai báo tương đối theo cảnh `{cue, a, end | until}`; đặt ở vùng trời trống, không che mặt hay bàn tay nhân vật (bàn tay mang cử chỉ soma).
- Hai kiểu: `giay` (chữ mực trên nền sáng) và `sang` (chữ kem có quầng tối nhẹ trên nền đêm).

### 4.4. Mật độ và nhịp

- 60-90 giây: 8-12 cảnh. Cảnh ngắn nhất 3 giây, trừ chuỗi mắc kẹt được phép 1,5-2,5 giây để tạo cảm giác dồn (chính sự tương phản nhanh-chậm mang nghĩa).
- Cảnh dừng lại và cảnh nới ra thuộc nhóm dài nhất phim.
- Clip có voice: thời lượng cảnh do lời quyết định; trần một ý hình mới mỗi 8-12 giây, sàn một biến đổi nhỏ mỗi 25 giây (Phần 3.3).
- Khung 9:16 là bố cục lại (chân trời, vùng caption, chủ thể), không cắt từ 16:9.

### 4.5. Danh mục cấm

Biểu đồ đi lên, sân khấu vỗ tay, cúp, bục vinh quang, so sánh hơn-kém; chữ trong hình (biển hiệu, màn hình); emoji; caption giảng giải kiểu bài học đạo đức; câu hỏi A/B; hình AI hoặc ảnh chụp; placeholder còn sót; em dash trong mọi chữ.
