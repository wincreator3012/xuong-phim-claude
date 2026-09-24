# QUY TRÌNH KỸ THUẬT - nguồn sự thật về môi trường, dành cho Claude

Đọc file này ở đầu mỗi phiên làm việc trong xưởng, sau `CLAUDE.md`. Các skill trong `skills/` mô tả CÁCH LÀM từng loại việc; file này mô tả MÔI TRƯỜNG mà các skill trỏ về: cái gì nằm ở đâu, chạy ở đâu, giới hạn gì, quy ước chất lượng nào. Bài học rút ra từ các dự án thật (không gắn với môi trường) nằm ở `docs/BAI-HOC.md`.

## Bản đồ tài nguyên chuẩn (vận dụng thay vì làm lại từ đầu)

| Tài nguyên | Ở đâu | Dùng khi nào |
|---|---|---|
| Phong cách và bản sắc người dùng | `phong-cach/PHONG-CACH.md` (đọc trước mọi dự án), `brand/brand.json` (máy đọc), `brand/logo/`, mẫu trong `phong-cach/mau/` | mọi đồ họa, mọi lựa chọn nhạc, mọi chữ trên màn hình; chức danh và "từ ngữ phải viết đúng" là bất khả xâm phạm |
| Preset intro/outro (placeholder title/subtitle, thông điệp kết, liên hệ, QR; hàng 1-3 logo) | `do-hoa-chung/preset-intro-outro-<ngang\|doc>.json` + `GHI-CHU.md` | MỌI intro/outro: copy preset vào dự án, thay chữ, render bản riêng |
| 18 composition đồ họa (Intro, Outro, SectionTitle, InfoList, InfoQuote, InfoStat, InfoSteps, LowerThird, Benefits, mỗi cái ngang và dọc) | `studio/` (Remotion) | mọi đồ họa động; không có composition "Caption": câu caption nổi bật = Benefits một mục, `showIndex:false`, `wrap:true`; minh họa khái niệm/số liệu ưu tiên infographic hơn ảnh tải |
| Thư viện âm thanh | danh mục kiểm định `thu-vien/AM-THANH.md` + `am-thanh.json`; file thật và LUFS đo thật ở `nhac-nen/THU-VIEN.md` (sinh bởi `tools/nhap-am-thanh.py`) | mọi nhạc nền và hiệu ứng; không dùng nhạc ngoài danh mục trừ nhạc riêng người dùng ở `nhac-nen/rieng/` |
| Nguồn hình minh hoạ | `thu-vien/HINH-ANH.md` | skill phim-tu-lieu, tải theo từng dự án vào `du-an/<x>/tu-lieu/` + `TU-LIEU.md` |
| Bộ công cụ pipeline | `tools/`: `mediainfo.py`, `transcribe.py`, `assemble.py` (timeline → thành phẩm), `nghiem-thu.py`, `render-do-hoa.mjs`, `mau-sac.py`, `slide-nguon.py`, `slide-khop.py`, `bo-cuc-slide.py`, `multicam-khop.py`, `multicam-dan.py`; cài đặt `cai-dat.py`, `kiem-tra-xuong.py`, `tai-chat-lieu.py`, `nhap-am-thanh.py` | theo quy trình từng skill; docstring đầu mỗi file là tài liệu tham số |
| Thư viện Python và model | `tools/pylib/` (numpy, sherpa-onnx, pillow, python-pptx), `tools/models/` (silero VAD + whisper) | các tool tự thêm `pylib` vào `sys.path`; không cần PYTHONPATH |
| Hệ màu sắc | `tools/mau-sac.py kham\|soi` + đơn màu `du-an/<x>/mau-sac.json` mà `assemble.py` tự áp | skill phim-mau-sac; HDR (color_transfer smpte2084/arib-std-b67) bắt buộc tonemap; đa số kết luận đạt-không-chỉnh |
| Bài giảng có slide (5 bố cục) | `tools/slide-nguon.py`, `tools/slide-khop.py`, `do-hoa-chung/bo-cuc/` (sinh bởi `bo-cuc-slide.py`, màu theo brand.json), trường `layout`/`slide` trong timeline | skill phim-bai-giang-slide |
| Multicam (2-3 góc, podcast) | `tools/multicam-khop.py`, `tools/multicam-dan.py`, trường `audioSrc`/`audioIn` trong timeline | skill phim-multicam |
| Phim tài liệu phỏng vấn (nhiều nhân vật, dự án/sự kiện) | `skills/phim-tai-lieu-phong-van/` + mẫu 5 file hồ sơ trong `references/mau-ho-so.md`, mẫu thư mục `du-an/_mau/tai-lieu-phong-van/` | khi user mô tả sự kiện sắp quay (Pha 1) hoặc thả nhiều file phỏng vấn nhiều người (Pha 2); mục "Phim tài liệu phỏng vấn" |
| Cổng nghiệm thu tự động | `tools/nghiem-thu.py video\|transcript\|do-hoa`, `assemble.py --kiem-tra`, `render-do-hoa.mjs` tự đo | BẮT BUỘC trước khi báo "xong" |
| Dự án mẫu | `du-an/_mau/` (cấu trúc, timeline mẫu, job đồ họa mẫu) | tham khảo cấu trúc; dự án thật tạo cạnh nó |
| Nguồn skill | `skills/phim-*/SKILL.md` | đọc SKILL.md tương ứng khi việc khớp mô tả; sửa skill thì sửa ở đây |

## Hai nơi chạy lệnh

Xưởng được thiết kế cho Claude Cowork với thư mục xưởng kết nối từ máy người dùng. Tuỳ phiên, có một hoặc hai nơi chạy lệnh:

**Máy người dùng** (`device_bash`, máy ảo Linux của Cowork trên máy Mac/PC; trong phiên cục bộ thì chính là `Bash`): nơi có video nguồn, có ffmpeg (bản 4.4 trong máy ảo), python3, node. Mọi việc nặng chạm tới footage làm ở đây: mediainfo, transcript (dữ liệu không rời máy), khám màu, cắt ghép (`assemble.py`), nghiệm thu, burn phụ đề. Đường dẫn gốc xưởng trong `device_bash` là `$HOME/mnt/<tên thư mục đã kết nối>`; với các tool stage/commit/list_dir là đường dẫn thật trên máy (lấy từ `get_device_info.connectedFolders`). KHÔNG hardcode đường dẫn tuyệt đối vào file nào của xưởng.

Giới hạn máy ảo Cowork cần nhớ: mỗi lần gọi tối đa 180 giây; tiến trình nền không sống qua các lần gọi; `$HOME` mất khi hết phiên (nên thư viện Python nằm trong `tools/pylib`, model trong `tools/models`); `rm` bị cấm mặc định (dọn file bằng ghi rỗng `open(f,"w").close()` hoặc chuyển vào `_to_delete/`; cần xoá thật thì xin `device_request_delete_permission`); mạng theo allowlist của tổ chức (github, pypi, npm thường được; nhiều host khác bị chặn).

**Sandbox đám mây** (`Bash` trong phiên cloud): nơi render đồ họa Remotion, vì máy ảo cục bộ thường không tải được Chrome headless. Có node, ffmpeg 6.1, Chromium tại đường dẫn đã cấu hình trong `studio/remotion.config.ts`. Sandbox tạm thời: mỗi phiên dựng lại từ thư mục xưởng (mục "Khởi động phiên"). Không đưa footage người dùng lên đây trừ vài khung hình để xem.

Phiên chỉ có một nơi (Cowork cục bộ không có sandbox): mọi thứ chạy tại máy; render Remotion cần Chrome, nếu máy ảo không tải được thì hướng dẫn người dùng chạy một lệnh `npx remotion render` trong Terminal macOS (Remotion tự tải Chrome trên macOS), hoặc dùng đồ họa tĩnh tạm thời.

**Truyền file hai chiều**: `device_stage_files` máy → đám mây (≤400MB/file); `SendUserFile` + `device_commit_files` đám mây → máy (≤20MB/file, ≤100MB/lần; file lớn hơn `split -b 19m`, commit từng phần rồi `cat` nối lại trong `device_bash`). Lỗi "untrusted_device" khi stage: phiên đăng nhập app Claude trên máy đã cũ, nhờ người dùng đăng nhập lại, không retry.

## Khởi động phiên (checklist)

1. Đọc `CLAUDE.md`, file này, `phong-cach/PHONG-CACH.md`, `brand/brand.json`
2. Kiểm cài đặt tại máy: `python3 tools/cai-dat.py --trang-thai` (chưa cài → skill phim-thiet-lap)
3. Nếu phiên có sandbox và sẽ render đồ họa: `mkdir -p ~/work && cd ~/work`, stage `studio/` (không kèm `node_modules`), `tools/render-do-hoa.mjs`, `brand/` (brand.json + logo); `cd ~/work/studio && npm install` (~40 giây, package-lock đã pin); `npx remotion compositions src/index.ts` phải ra 18 composition
4. Máy: `ls tools/models/` có `silero_vad.onnx` + `sherpa-onnx-whisper-turbo/` (hoặc small)

## Quy trình một dự án (chi tiết ở skill phim-dung-bai)

1. Nhận tư liệu ở `du-an/<x>/nguon/`; `python3 tools/mediainfo.py "du-an/<x>/nguon"`; khám màu `python3 tools/mau-sac.py kham "du-an/<x>"`
2. Transcript: `python3 tools/transcribe.py "<file>" --out-dir "du-an/<x>/transcript"` rồi `python3 tools/nghiem-thu.py transcript "du-an/<x>"`
3. Phương án cắt và overlay, trình người dùng duyệt MỘT lần (bảng mốc nguồn, nội dung, giữ/bỏ, lý do; bảng overlay theo lời nói)
4. Đồ họa: intro/outro từ preset, đồ họa khác theo `du-an/_mau/do-hoa/job-do-hoa.json`; `node tools/render-do-hoa.mjs <job> --studio <studio>`; commit về `du-an/<x>/do-hoa/<ngang|doc>/`
5. Timeline `du-an/<x>/timeline.json` theo schema trong docstring `tools/assemble.py`; `python3 tools/assemble.py --project "du-an/<x>" --kiem-tra`
6. Bản nháp: `python3 tools/assemble.py --project "du-an/<x>" --preview` → người dùng xem `xuat-nhap/<x>-<khung>-nhap.mp4`, lặp tới khi ưng
7. Bản chính: bỏ `--preview`; `python3 tools/nghiem-thu.py video "<file>" --khung <ngang|doc> --anh` ĐẠT; nhìn ảnh lưới `.luoi.jpg`; kiểm mối nối theo `.map.json`
8. Copy sang `du-an/<x>/xuat-hoan-chinh/`; báo tên file, thời lượng, dung lượng, dòng ghi công nhạc CC-BY nếu có, chapters nếu có, và "nghiệm thu máy: ĐẠT"

## Việc chạy dài hơn 180 giây

`assemble.py` tự resume: mỗi part encode xong có `.sig` (chữ ký gồm `TOOL_VERSION`, tham số, kích cỡ/mtime mọi file nguồn liên quan). Lệnh bị ngắt thì gọi lại y nguyên tới khi thấy "✓ Xong"; part lấy từ cache vẫn qua kiểm hình = tiếng. Không truyền `--out` (script tự đặt tên và tự ghi vào `xuat-nhap/`), trừ dự án con `clip-ngan/<slug>/` phải `--out <slug>-<khung>`.

`transcribe.py` với bài >90 phút: tách audio từng 30 phút (`ffmpeg -ss -t`), transcript từng phần, cộng offset. `render-do-hoa.mjs`: mỗi job chỉ 1-2 composition; webm alpha dài (>15 giây) render chậm, chia thành nhiều overlay ngắn độc lập rồi đưa vào `overlay` dạng list của một segment.

Việc khác cần chạy lâu: ghi vào script trong `du-an/<x>/.tam/run.sh`, chạy `timeout 170 bash ... >> run.log 2>&1; tail -5 run.log`, script tự bỏ qua bước đã xong.

## Hai thư mục xuất

`xuat-nhap/`: mọi thứ `assemble.py` ghi ra (bản nháp 480p và bản chính chưa qua hậu kỳ khác như burn phụ đề). `xuat-hoan-chinh/`: CHỈ file đã hoàn tất hậu kỳ và qua nghiệm thu; nơi duy nhất trỏ người dùng tới khi báo hoàn thành. Không cần hậu tố `-final`.

## Quy ước chất lượng

- Chuẩn phát hành: 1080p, H.264 high, CRF 18 veryfast, AAC 192k 48kHz stereo, -14 LUFS (loudnorm hai lượt), +faststart, 30fps (nguồn 25fps đồng nhất thì đặt `"fps": 25`)
- Điểm cắt luôn hút về khoảng lặng (`snap: true`, dùng silences.json); không cắt giữa từ
- Đồ họa encode đồng nhất qua assemble để concat -c copy an toàn; concat không tự encode lại (sai là dừng)
- Phong cách đồ họa: minimalist, khoảng trắng rộng, chuyển động chậm (bezier 0.22,1,0.36,1), Lora + Be Vietnam Pro, hai theme từ brand.json; không hiệu ứng lòe loẹt, không emoji trong đồ họa
- Chữ trên màn hình theo mục 4 của PHONG-CACH.md; mặc định thuần Việt, sentence case, gạch ngang thường
- Nhạc: bài giảng mặc định `bookends`; clip quảng bá ngắn `full` + `duck: true`; gainDb tra `nhac-nen/THU-VIEN.md`; track CC-BY kèm dòng ghi công trong mô tả video
- Clip ngắn: hook TRƯỚC, intro SAU (intro 2.5-4 giây hoặc bỏ); kỹ thuật: không dùng trường `intro` của timeline, đưa file intro vào `segments` sau segment hook. Bài dài mà câu mở là câu chốt mạnh cũng áp dụng được
- Tối thiểu 5 giây cảnh quay chính giữa hai thẻ toàn màn hình liên tiếp; dày hơn thì đổi sang overlay bán trong suốt

## Phòng ngừa lớp lỗi ngầm (bắt buộc)

Một bất biến của hệ (hình = tiếng ở mọi file trung gian) từng bị vi phạm ở mọi đoạn có overlay mà không chỗ nào đo, cộng với một nhánh "tự encode lại" nuốt mất tín hiệu; thành phẩm lệch tiếng cộng dồn nhiều giây mà "xem vài frame" không phát hiện. Từ đó bốn nguyên tắc:

1. Bất biến phải được ĐO ở mọi bước, không suy ra từ bước trước: từng part sau encode, body sau concat, thành phẩm sau finalize đều qua `check_av()` (hình = tiếng ≤ 0.06 s, = dự kiến ≤ 0.15 s); đồ họa render xong qua `render-do-hoa.mjs` tự đo; transcript qua `nghiem-thu.py transcript`
2. Không có nhánh "sửa ngầm": sai là dừng với bảng chẩn đoán. Hạ ngưỡng, bắt ngoại lệ rồi bỏ qua, bật `--ep-encode-lai` cho qua đều bị cấm
3. Cache phải biết code và dữ liệu đã đổi: sửa logic encode trong `assemble.py` thì đổi `TOOL_VERSION`
4. Kiểm cấu hình trước khi tốn thời gian: `assemble.py --kiem-tra`

| Việc | Lệnh (từ gốc xưởng) |
|---|---|
| Kiểm timeline | `python3 tools/assemble.py --project "du-an/<x>" --kiem-tra` |
| Dựng (tự kiểm từng part, body, thành phẩm; ghi `.map.json`, `.nghiem-thu.json`) | `python3 tools/assemble.py --project "du-an/<x>" [--preview]` |
| Nghiệm thu thành phẩm | `python3 tools/nghiem-thu.py video "<file.mp4>" --khung ngang\|doc [--nhap] --anh` |
| Nghiệm thu transcript | `python3 tools/nghiem-thu.py transcript "du-an/<x>"` |
| Nghiệm thu đồ họa | `python3 tools/nghiem-thu.py do-hoa "du-an/<x>/do-hoa"` |
| Tính lại phụ đề/chapter theo thành phẩm | đọc `<thành phẩm>.map.json`: cue có `in ≤ t < out` → mốc mới `start + (t - in)` |
| Kiểm xưởng sau khi sửa tool | `python3 tools/kiem-tra-xuong.py --co-slide` |

Quy ước báo cáo: chưa có dòng "nghiệm thu máy: ĐẠT" thì chưa được nói "xong". Ảnh lưới là bước soi mắt, chạy SAU cổng máy, không thay cho cổng máy.

## Hai hệ mốc thời gian trong timeline.json (nguồn nhầm lẫn kinh điển)

`in`, `out`, `broll[].at` là mốc TRONG FILE NGUỒN. `overlay[].at` là mốc TƯƠNG ĐỐI từ đầu đoạn (sau snap). Overlay muốn hiện lúc lời nói ở mốc nguồn T: `at = T - in`. Overlay chỉ phủ lên quãng đầu của đoạn cho tới B-roll đầu tiên. `revealAt` bên trong props của Benefits cũng tính theo cùng mốc 0 này.

## Bài giảng có slide (skill phim-bai-giang-slide)

| Việc | Lệnh |
|---|---|
| Nhập slide (PPTX cần soffice, PDF cần poppler - thường chạy ở sandbox; ảnh/quay màn hình chạy ở đâu cũng được) | `python3 tools/slide-nguon.py "<nguồn>" --project "du-an/<x>"` → `slide/slide-NN.png` + `slide/slide.json` |
| Khớp slide với lời giảng, đề xuất dàn hình | `python3 tools/slide-khop.py "du-an/<x>" --clip "<tên file nguồn>" [--lech s] [--bo-qua 1,2]` → `slide/DAN-HINH.md`, `slide/timeline-slide-nhap.json` |
| Sinh lại khung/mask (sau khi đổi màu brand hoặc toạ độ) | `python3 tools/bo-cuc-slide.py` |
| Dựng | timeline có `"theme"`, mỗi segment `"layout": mat\|slide\|ca-hai\|chia-doi\|mat-chinh`, `"slide": "slide/slide-03.png"`, tuỳ chọn `"slideZoom": [x,y,w,h]` |

## Multicam (skill phim-multicam)

Nguồn theo `nguon/<góc>/<file>`: thư mục chứa `toan` là góc toàn, bắt đầu bằng `tieng` là file tiếng riêng, còn lại là góc cận mang tên người.

| Việc | Lệnh |
|---|---|
| Đồng bộ các góc bằng âm thanh | `python3 tools/multicam-khop.py "du-an/<x>" [--chu toan] [--tron-tieng]` → `multicam.json`, `nguon/tieng-chu.wav` |
| Transcript tiếng chủ | `transcribe.py` trên `nguon/tieng-chu.wav` rồi `nghiem-thu.py transcript` |
| Người nói, session, dàn góc | `python3 tools/multicam-dan.py "du-an/<x>" --transcript "<tên>" [--che-do podcast\|bai-giang] [--phut 8]` → `multicam/DAN-GOC.md`, `timeline-multicam-nhap.json`, `job-session.json` |

Bài giảng một người nhiều góc phải truyền `--che-do bai-giang`. File có `tin_cay` < 1.1 hay `khop_r` < 0.2 phải soi khung hình hai góc tại cùng mốc trục.

## Phim tài liệu phỏng vấn (skill phim-tai-lieu-phong-van)

Khác bài giảng một người: lời đến từ nhiều file quay riêng, ý nghĩa nằm ở cách dệt các giọng theo chủ đề. Hai pha, hai cổng duyệt trên giấy trước khi dựng.

| Pha | Việc | File trong `du-an/<x>/` |
|---|---|---|
| 1 - Trước quay | mô tả/kịch bản dự kiến → `HO-SO-PHIM.md` → định hướng ba hồi (vấn đề - can thiệp - chuyển hoá), câu hỏi neo, cách kết → nhân vật + 5-8 câu hỏi mỗi người → danh mục cảnh trám (mã, chủ thể, cỡ, chuyển động, tối thiểu 10s, công dụng thiết lập/minh hoạ/che cắt/thở, phục vụ câu nào) → checklist ngày quay | `KE-HOACH-GHI-HINH.md` = Cổng duyệt 1 |
| 2 - Sau quay | `mediainfo.py`; transcript + `nghiem-thu.py transcript`; `ffprobe` thời lượng thật từng cảnh trám + lưới khung hình; khám màu → `KIEM-KE-NGUON.md` (đối chiếu kế hoạch ↔ thực tế) → chọn soundbite → `KICH-BAN-THUC-TE.md` (từng dòng dựng có mốc, tổng ước tính, hai phương án nếu vượt 30%, quyết định cần user) = Cổng duyệt 2 → timeline theo phim-dung-bai → nháp `--out "<x>-<khung>-nhapN"` → `SO-GOP-Y.md` → bản chính | `KIEM-KE-NGUON.md`, `KICH-BAN-THUC-TE.md`, `SO-GOP-Y.md`, `do-hoa/job/` |

Nguồn chia theo loại: `nguon/phong-van/`, `nguon/canh-tram/`, `nguon/su-kien/`, `nguon/anh/`. Mọi nháp đặt tên tường minh có số ngay từ nháp đầu (tên mặc định của `assemble.py` sẽ ghi đè lẫn nhau giữa các vòng). Quy tắc thể loại và định lượng cảnh trám (một cảnh dùng được cho mỗi 20-30 giây phim, quay gấp 2-3 danh mục, giữ máy tối thiểu 10 giây, ba cỡ mỗi chủ thể) trong `skills/phim-tai-lieu-phong-van/references/ke-chuyen-phong-van.md`.

## Infomotion - video dựng hoàn toàn từ đồ hoạ (skill phim-infomotion)

Khác mọi skill khác: không có cảnh quay để cắt, nguồn chỉ là một file ghi âm. Hai component riêng cho việc này, không dùng ở skill khác:

| Việc | Ghi chú |
|---|---|
| `YNiem` (`studio/src/components/YNiem.tsx`) | Một hình vẽ nét dần cho MỘT khái niệm đơn lẻ, hình lấy theo `slug` từ kho `studio/src/y-niem/index.ts`. Cờ tuỳ chọn `travelDot`/`endArrow` trên một shape gợi ý chuyển động chưa dừng dọc theo path cuối cùng - tính tổng quát từ cấu trúc path (`M x,y C ... C ...`), không hard-code toạ độ. |
| `YCanh` (`studio/src/components/YCanh.tsx`) | Một chuỗi cảnh vẽ tay, mỗi `variant` một kỹ thuật chuyển động riêng (8 variant sẵn có: `hub-branches`, `filling-grid`, `radiant-sun`, `rising-moon`, `growing-bars`, `tick-cluster`, `clock-sweep`, `growing-flame`) - dùng khi một đoạn kể chuyện có nhiều nhịp liên tiếp cần cảm giác riêng từng nhịp. |
| `do-hoa-chung/an-du-y-niem.json` | Từ điển ẩn dụ dùng chung mọi dự án infomotion của một người dùng. CHƯA TỒN TẠI cho tới dự án đầu tiên có ẩn dụ được duyệt - tạo mới dạng `{}` khi đó, không tạo trước. |

Cả hai component nhận `floating`/`position` như các đồ hoạ nổi khác trong xưởng; `position: 'center'` là mặc định khi `floating` (canh giữa cả hai trục thay vì dồn lên một cạnh). Kích thước `floating` đã kiểm chứng qua dự án thật: icon `unit*58`, nhãn `unit*6.0`/`unit*3.9` - ngưỡng dưới, không nhỏ hơn khi không có lý do cụ thể.

Quy trình đầy đủ (tám bước, ba nguyên tắc xuyên suốt, cách chọn ẩn dụ, ngân sách khung khi ô timeline LOCKED): `skills/phim-infomotion/SKILL.md`.


Cập nhật 2026-09-20 (từ một vòng tinh chỉnh không chờ góp ý bằng số của dự án tham chiếu): cắt câu là việc làm nhiều vòng, rút `in`/`out` sát dần qua các nháp bằng cách neo `silencedetect` vào khoảng lặng gần cụm cần bỏ; mở đầu nên là chuỗi 3-4 cảnh động ngắn nối tiếp, không phải một cảnh động đơn kéo dài; đồ họa nhận diện `LowerThird` (thông tin về NGƯỜI) và pill `Benefits` (thông tin về Ý) là hai lớp bắt buộc tách biệt, không thay thế nhau; thẻ chuyển `SectionTitle` dùng `kicker` (tên dự án, lặp lại xuyên suốt) + `title` (tên hồi) làm quy ước chuẩn. Chi tiết và lý do trong `skills/phim-tai-lieu-phong-van/references/ke-chuyen-phong-van.md` mục 1, 4, 6, 7.
