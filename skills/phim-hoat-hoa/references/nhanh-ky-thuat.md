# Hai nhánh kỹ thuật: Canvas HTML và Remotion (phim-hoat-hoa)

Đặc tả kỹ thuật của hai nhánh dựng. Nhánh A đi vào mục [1] của bộ lệnh; nhánh B theo quy ước studio của xưởng (phim-do-hoa) và pipeline nền của phim-infomotion.

## Phần 5. Hai nhánh kỹ thuật

### 5.1. Nhánh A: Canvas HTML tự chứa

Dùng khi: làm nhanh một phim độc lập, chia sẻ bộ lệnh cho người khác dán vào claude.ai, dạy trong khoá học, hoặc cần một file HTML xem trực tiếp.

Đặc tả cốt lõi (đưa nguyên vào mục [1] của bộ lệnh):

- Canvas 2D, khung logic 1280×720 vẽ ở hệ số S = 1,5 (1920×1080 thật); bản dọc 720×1280 logic.
- `render(t)` thuần; PRNG mulberry32 + hash số nguyên + value-noise 1D; cấm `Math.random()` trong vòng render.
- Boil nét tay: `BOIL = floor(t*6)`, biên độ nhỏ; đóng băng BOIL ở khoảnh khắc tĩnh và sau khi chữ ký viết xong.
- Timeline mảng cue `{scene, duration, k, tr, td, at}`; gọi `scene(lt/k, t)`; chuyển cảnh vẽ cảnh trước ở `(duration + lt)` rồi clip cảnh mới theo mặt nạ.
- Điều khiển: Space play/pause, thanh tua, `?t=`, nút bật/tắt nhạc (mặc định tắt), nút bật/tắt caption, nút Record (`captureStream(30)` + audio track → WebM).
- Hiệu năng: lớp nặng cache ra offscreen canvas theo N pha, dựng lười, prewarm khi rảnh; chất giấy dựng một lần bằng PRNG seed rồi phủ `multiply`.
- Bộ vẽ tối thiểu: `wobbleLine/wobbleShape` (resample polyline, dịch theo pháp tuyến bằng noise chậm + boil), `partial` (vẽ dần một đường), `catmull`, `cam(zoom, focus)`, `glow`, `breath(t, chu kỳ)` trả về pha thở 0-1 với pha thở ra dài hơn, `person` (hai trạng thái thân trở lên, trả về toạ độ bàn tay), mô-típ có tham số morph 0 → 1 qua các trạng thái.
- Xuất MP4: Playwright + Chromium headless (sandbox đám mây có sẵn tại `/opt/pw-browsers`, không chạy `playwright install`); chờ `document.fonts.load` và kiểm `fonts.check` với ký tự 'ạ'; mỗi khung `render(i/30)` và `toDataURL('image/jpeg', 0.93)` trong CÙNG một evaluate; âm thanh qua `window.renderSoundtrack()`; ffmpeg `-f mjpeg -framerate 30 -i frames.mjpeg -i soundtrack.wav -af "highpass=f=35,loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=<DUR-1>:d=1" -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart`, CRF 17 nếu không giới hạn dung lượng.
- Trong xưởng: file ở `Du an/<tên>/canvas/index.html`, MP4 xuất ra `Du an/<tên>/nguon/` để đi tiếp qua `assemble.py` nếu cần outro hoặc nhạc thư viện, rồi `nghiem-thu.py video`.
- **Khi có voice:** file giọng là ngoại lệ duy nhất của luật "không file âm thanh". Mốc nhịp từ transcript nhúng thành mảng `BEATS` `{id, start, end, loai, tu_khoa_at}` và bảng cue sinh từ đó (không cộng dồn danh nghĩa). Khi xem trực tiếp, đồng hồ của `render(t)` lấy từ `audio.currentTime` của phần tử `<audio>` chứa voice, thanh tua điều khiển cả hai. Khi xuất: `renderSoundtrack()` chỉ render nhạc + SFX; ffmpeg trộn với voice bằng `sidechaincompress` (voice làm tín hiệu điều khiển) rồi `loudnorm`. Clip dài hơn 3 phút: render khung theo chương, ghép bằng concat, tránh một evaluate khổng lồ.

### 5.2. Nhánh B: Remotion trong xưởng

Dùng khi: phim thuộc một dự án của xưởng, cần cả bản ngang lẫn dọc, cần tái dùng brand, từ điển ẩn dụ, thư viện âm thanh, intro/outro và cổng nghiệm thu sẵn có.

Ánh xạ nguyên lý sang Remotion:

| Nguyên lý | Cách làm trong Remotion |
|---|---|
| `render(t)` thuần | `useCurrentFrame()` / fps; không state, không `Math.random()` |
| PRNG seed | `random(seed)` của `remotion`; noise từ `@remotion/noise` nếu studio đã cài |
| Bảng cue + hệ số k | mảng cue trong `BANG-CANH.json` → `<Series>` / `<Sequence>`; thời gian nội bộ `lt = (frame - start) / k` |
| Vẽ nét dần | SVG với `@remotion/paths` (`evolvePath`) hoặc `strokeDashoffset`; ưu tiên SVG cho nét 3 px |
| Lớp nặng | `<canvas>` vẽ theo frame, cache pha như nhánh A |
| Chuyển cảnh | `@remotion/transitions` nếu đã cài (presentation tự viết cho vòng tròn nở, loang); chưa có thì hai `<Sequence>` chồng + clipPath |
| Âm thanh | `<Audio>` từ thư viện xưởng, `startFrom` và volume theo cue |

Quy ước xưởng:

- Mỗi phim một thư mục component `studio/src/hoat-hoa/<slug>/`, đăng ký composition `HoatHoa-<slug>-ngang` và `-doc` theo mục "Thêm component mới" của phim-do-hoa (tsc sạch, still tiếng Việt có dấu cả hai khung, commit nguồn về máy ngay).
- Bảng cảnh ở `Du an/<tên>/BANG-CANH.json`, là nguồn chân lý duy nhất cho thời lượng; component đọc từ đó qua props.
- Render qua `node tools/render-do-hoa.mjs <job.json> --studio <đường dẫn tuyệt đối>`; sandbox 2 CPU nên gộp nhiều job vào một job JSON, không chạy song song; kiểm `ffprobe` hình = tiếng.
- Quy tắc clip ngắn của xưởng vẫn áp dụng: không mở bằng intro; phim hoạt hoạ tự sự lấy cảnh chữ ký làm outro, preset outro chỉ gắn thêm khi cần thông tin đăng ký hoặc QR.
- **Khi có voice:** làm như phim-infomotion ở phần nguồn: chuẩn hoá tiếng, tạo `nguon/nen-<khung>.mp4` (nền màu giấy + tiếng voice), chạy phim-transcript trên nền, nghiệm thu transcript; từ đó nền là trục thời gian duy nhất. Phim hoạt hình render **câm, toàn khung, theo chương** (mỗi chương một job, cùng một job JSON để chạy tuần tự trên 2 CPU), `durationInSeconds` đúng bằng độ dài chương đo trên nền; `BANG-CANH.json` ghi mốc tuyệt đối trên trục nền. Ghép bằng `assemble.py`: mỗi chương là `broll` toàn khung đặt đúng `at` trên segment cắt từ `nen-<khung>.mp4`, tiếng voice đi liền theo nền; nhạc qua `bookends` hoặc `full` với gainDb theo `thu-vien/AM-THANH.md`. Như vậy hình và tiếng không thể trôi nhau.
- Clip 10 phút ở 30 fps là 18.000 khung: ưu tiên SVG nhẹ, cache lớp nặng, render nháp ở 720p để duyệt nhịp trước khi render 1080p.
