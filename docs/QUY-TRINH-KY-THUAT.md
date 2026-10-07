# QUY TRÌNH KỸ THUẬT - dành cho Claude

File này giữ những gì đang đúng lúc này: môi trường (máy người dùng và sandbox), lệnh, bản đồ tài nguyên, quy ước chất lượng, cổng nghiệm thu và cách xử lý khi một khâu hỏng. Sửa thẳng vào đúng mục khi sự thật đổi; không nối thêm ghi chú có ngày ở cuối file.

Các file đi cùng nhau:

| File | Giữ gì | Khi nào đọc |
|---|---|---|
| `CLAUDE.md` | thứ tự đọc, bảng việc sang skill, quy tắc cứng | đầu mỗi phiên |
| `docs/QUY-TRINH-KY-THUAT.md` (file này) | môi trường, lệnh, quy ước hiện hành | đầu mỗi phiên, và khi cần lệnh |
| `docs/BAI-HOC.md` | bài học đã chưng cất theo chủ đề, mỗi bài một nguồn | trước khâu tương ứng (dựng, đồ họa, gỡ băng, phụ đề...) và khi gặp lỗi lạ |
| `phong-cach/PHONG-CACH.md` (điền lần đầu bằng skill phim-thiet-lap, mẫu màu ở `phong-cach/mau/`) | tên, chức danh, từ ngữ, tông hình, sổ tay góp ý | trước mọi việc có chữ trên hình |

Giá trị mặc định trong file này (cỡ, vị trí, mật độ, nhạc, nhịp) là điểm xuất phát, không phải khuôn: chỉ bất biến kỹ thuật (cổng nghiệm thu, hình = tiếng, chuẩn phát hành) là giữ tuyệt đối; lựa chọn sáng tạo theo trải nghiệm người xem của từng clip (`CLAUDE.md` mục "Tinh thần làm việc").

Bài học mới sau mỗi dự án ghi vào `docs/BAI-HOC.md` đúng chủ đề (một dòng bài học, một dòng nguồn). Chỉ khi bài học làm đổi môi trường, lệnh hoặc quy ước thì mới sửa file này.

## Phân công và các skill

Hệ thống dựng video cho người dùng: cắt ghép bài giảng, clip ngắn, podcast nhiều góc, phim tài liệu phỏng vấn, infomotion, hoạt hình; intro, outro và đồ họa minimalist bằng Remotion; nhạc nền; xuất 16:9 và 9:16. Nguyên tắc phân công: **video nặng xử lý trên máy của người dùng (`device_bash` + ffmpeg), đồ họa Remotion render trong sandbox đám mây** (đồ họa không chứa hình người), gỡ băng chạy trên máy (dữ liệu không rời máy).

Mười bốn skill trong `skills/` là quy trình chuẩn của từng loại việc: phim-thiet-lap (cài đặt và phong cách lần đầu), phim-dung-bai, phim-clip-ngan, phim-do-hoa, phim-canh-minh-hoa, phim-transcript, phim-tu-lieu, phim-bai-giang-slide, phim-multicam, phim-mau-sac, phim-tai-lieu-phong-van, phim-infomotion, phim-hoat-hoa, phim-dang-tai. Việc nào dùng skill nào: bảng trong `CLAUDE.md`. Phần dùng chung cho mọi skill nằm ở `skills/_chung/` (`van-hanh.md`: hai máy, truyền file, chức danh, khi hỏng, khép dự án; `timeline-va-dung.md`; `overlay-va-the.md`; `nghiem-thu-dung-y.md`; `bao-tri-skill.md`). Skill sửa ở `skills/`; tham chiếu tới references luôn ghi đủ đường dẫn `skills/<skill>/references/<file>.md`.

## Bản đồ tài nguyên chuẩn

Vận dụng những gì đã có thay vì làm lại.

| Tài nguyên | Ở đâu | Dùng khi nào |
|---|---|---|
| Preset intro, outro (title, subtitle, thông điệp kết, liên hệ, QR; hàng 1-3 logo) | `do-hoa-chung/preset-intro-outro-<ngang\|doc>.json`, `do-hoa-chung/GHI-CHU.md` | mọi intro, outro: copy preset, thay chữ, render bản riêng cho dự án |
| Bộ logo và thương hiệu | `brand/logo/`, `brand/brand.json` | `render-do-hoa.mjs` tự đồng bộ logo; đổi bộ logo bằng props `logos` theo dự án |
| Tên, chức danh, từ ngữ, tông hình | `phong-cach/PHONG-CACH.md` | mọi chữ trên hình; chức danh lấy nguyên văn ở đây hoặc bảng nhân vật của dự án |
| Thư viện nhạc và hiệu ứng đã kiểm định bản quyền (có LUFS, `gainDb` gợi ý từng track) | `nhac-nen/`, `hieu-ung/`, danh mục `thu-vien/AM-THANH.md`, kiểm kê `nhac-nen/THU-VIEN.md` (sinh bằng `tools/nhap-am-thanh.py`), nhạc riêng ở `nhac-nen/rieng/` | mọi nhạc nền và SFX; không dùng nhạc ngoài thư viện trừ nhạc riêng người dùng đưa |
| 24 composition: 22 đồ họa động (Intro, Outro, SectionTitle, InfoList, InfoQuote, InfoStat, InfoSteps, LowerThird, Benefits, YNiem, YCanh, mỗi loại hai khung ngang/dọc) và `Thumbnail` ảnh tĩnh ngang/dọc | `studio/` | mọi đồ họa động. KHÔNG có `Caption`: một dòng chữ nổi = Benefits một mục `showIndex:false`, `wrap:true`. Benefits có `position` top/bottom (mặc định)/left/right, `wrap`, `scale`, `edgeInset`; màu pill theo `palette.accent`. YNiem, YCanh nổi mặc định canh giữa (khi dựng hỏi người dùng có muốn đổi) |
| Từ điển ẩn dụ hình ảnh (chưa có sẵn: tạo ở dự án infomotion đầu tiên) | `do-hoa-chung/an-du-y-niem.json`; slug YNiem ở `studio/src/y-niem/index.ts` | infomotion, hoạt hình: tra trước khi sáng tạo, ghi mục mới ngay sau khi người dùng duyệt; slug YNiem và mục từ điển phải khớp hai chiều |
| Màu sắc | `tools/mau-sac.py` (`kham`, `soi`), đơn màu `du-an/<x>/mau-sac.json` được `assemble.py` tự áp | khám mọi nguồn ở bước khảo sát (skill phim-mau-sac); HDR bắt buộc tonemap; đa số kết luận đạt, không chỉnh |
| Bàn dựng và Dựng bằng lời (người dùng tự tinh chỉnh) | `Mo ban dung.command`, `tools/ban-dung.py`, `tools/ban-dung/`; mốc lời `tools/moc-tu.py`, điểm cắt `tools/ban_dung_loi.py` | chốt nháp và sau đó, skill phim-ban-dung; mục "Bàn dựng" bên dưới |
| Công cụ pipeline | `tools/`: `mediainfo.py`, `transcribe.py`, `hang-doi-go-bang.py`, `assemble.py`, `nghiem-thu.py`, `render-do-hoa.mjs`, `uoc-luong.py`, `nhan-doan.py`, `chuong-youtube.py`, `slide-nguon.py`, `slide-khop.py`, `bo-cuc-slide.py`, `multicam-khop.py`, `multicam-proxy.py`, `multicam-dan.py`, `kiem-tra-xuong.py`, `kiem-dong-bo.py`, `do-dong-bo.py`, `kiem-tai-lieu.py`, `chon-khung-thumbnail.py`, `dang-tai.py`, `canh.mjs`, `canh-ghep.py`, `moc-tu.py`, `ban_dung_loi.py`, `ban-dung.py` (trang ở `tools/ban-dung/`), `cai-dat.py`, `tai-chat-lieu.py`, `nhap-am-thanh.py`; model trong `tools/models/`, thư viện trong `tools/pylib/` | theo quy trình từng skill |
| Cổng nghiệm thu tự động | `tools/nghiem-thu.py`, `assemble.py --kiem-tra`, `render-do-hoa.mjs` tự đo | bắt buộc trước khi báo "xong" - mục "Phòng ngừa lớp lỗi ngầm" |
| Tư liệu minh họa theo dự án | `du-an/<x>/tu-lieu/`, `TU-LIEU.md` (skill phim-tu-lieu tạo); nguồn đã thẩm định ở `thu-vien/HINH-ANH.md` | đọc `TU-LIEU.md` khi soạn timeline; ảnh qua Ken Burns thành insert hoặc B-roll |
| Dự án mẫu và kiểm thử | `du-an/_mau/` (cấu trúc, job, timeline mẫu), `du-an/_kiem-tra-tu-dong/` (dựng thử sau khi sửa tool) | tham khảo cấu trúc; sau mỗi lần sửa tool chạy `python3 tools/kiem-tra-xuong.py` (dựng lại `_kiem-tra-tu-dong` qua cổng nghiệm thu), bắt buộc khi đổi `TOOL_VERSION` |
| Bài giảng có slide | `tools/slide-nguon.py`, `tools/slide-khop.py`, `do-hoa-chung/bo-cuc/`, trường `layout`/`slide` trong timeline | khi nguồn có slide - mục "Bài giảng có slide" |
| Multicam | `tools/multicam-khop.py`, `tools/multicam-proxy.py`, `tools/multicam-dan.py`, trường `audioSrc`/`audioIn` | khi nguồn có nhiều thư mục góc - mục "Multicam" |
| Phim tài liệu phỏng vấn | skill phim-tai-lieu-phong-van, mẫu hồ sơ `references/mau-ho-so.md`, mẫu `du-an/_mau/tai-lieu-phong-van/` | khi người dùng mô tả sự kiện sắp quay (Pha 1) hoặc thả nhiều file phỏng vấn (Pha 2) |
| Gói đăng tải (tiêu đề, mô tả YouTube, status Facebook, thumbnail) | skill phim-dang-tai, `tools/chon-khung-thumbnail.py` (dò mặt bằng `tools/models/face_detection_yunet_2023mar.onnx`), `tools/dang-tai.py` (`job`, `kiem`), composition `Thumbnail` | tự làm ngay khi một clip qua nghiệm thu; kết quả nằm trong thư mục clip ở `Thanh pham/` (`dang-tai/`) |
| Cảnh minh hoạ (sơ đồ động vẽ riêng từng ý, trang web thời gian ảo chụp ra video) | skill phim-canh-minh-hoa; bộ thiết kế `do-hoa-chung/canh-kit/` (runtime, hệ màu theo vai ba họ Đêm xanh, Than đồng, Giấy mực, font nhúng, cảnh mẫu, khuôn trang phòng thử); `tools/canh.mjs` (sandbox: kiem, người dùng, phong-thu, chup), `tools/canh-ghep.py` (máy: khung nền mờ, ghép người nói vào góc) | B-roll giải thích trong bài giảng (bốn kiểu chèn) và giọng hình sơ đồ của infomotion |
| Infomotion | skill phim-infomotion, `references/mau-kich-ban.md`, `references/hinh-tuong-hoa.md` | khi nguồn là file âm thanh không có hình |

## Môi trường

### Máy của người dùng: VM Cowork (`device_bash`)

- Có sẵn: node 22, npm, ffmpeg 4.4 (libx264, x265, giải mã vp8/vp9 alpha), python3.10, pip, git, curl, make, g++; apt-get dùng được với archive.ubuntu.com.
- Cấu hình VM mỗi máy một khác: kiểm `nproc`, `free -g` ở phiên đầu tiên. sherpa-onnx cài vào `tools/pylib` bằng `python3 tools/cai-dat.py` (skill phim-thiet-lap).
- `$HOME` của VM theo phiên, mất khi hết phiên: mọi thứ cần bền phải nằm trong thư mục mount `$HOME/mnt/<thư mục xưởng>/`.
- Tiến trình nền (`nohup ... &`) không sống qua các lượt gọi. Mỗi lượt tối đa 180 giây: việc dài chạy bằng script ghi log với `timeout 170`, gọi lặp để theo dõi (mục "Việc chạy dài hơn 180 giây").
- Xoá bị cấm mặc định: file cần bỏ chuyển vào `_to_delete/`; xin quyền xoá bằng `device_request_delete_permission` khi thật cần.
- Egress được phép (tuỳ cài đặt mạng của tổ chức; danh sách dưới là cấu hình đã gặp): registry.npmjs.org, pypi.org, files.pythonhosted.org, github.com (kể cả codeload, api, release assets, raw.githubusercontent.com, media.githubusercontent.com), archive.ubuntu.com. Bị chặn: huggingface.co, storage.googleapis.com, remotion.dev, jsdelivr và các CDN model khác. Vì không tải được Chrome headless nên KHÔNG render Remotion trong VM.
- RAM nhỏ nên Whisper large-v3 không chạy được trong VM (chết lặng); `transcribe.py --model auto` trong VM ra turbo.

### Mac thật (qua hàng đợi gỡ băng)

Việc duy nhất chạy trên Mac thật: gỡ băng large-v3. Claude xếp việc bằng `python3 tools/hang-doi-go-bang.py them "<file>" --out-dir "<thư mục>"`, người dùng bấm đúp `Go bang tren Mac.command` trong Finder (lần đầu trên mỗi máy tự dựng môi trường vài phút). Kiểm kết quả bằng `hang-doi-go-bang.py trang-thai` (phải thấy `xong` và `model=large-v3`), rồi `don`. `--model auto` chọn large-v3 khi đủ RAM (Linux: từ 7 GB còn trống; macOS: tổng RAM từ 12 GB), không thì turbo; dòng "model tự chọn: whisper-..." trong log ghi model đã dùng. Trên Mac mà trạng thái ghi turbo là bất thường: báo người dùng, không coi là large-v3. Chi tiết model: `tools/models/TAI-MODEL.md`.

### Sandbox đám mây (`Bash`, x86_64, 2 lõi, 8 GB RAM)

- node 22, ffmpeg 6.1, Chromium có sẵn. Remotion dùng bản headless shell `/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell` (đã cấu hình trong `studio/remotion.config.ts`); bản `/opt/pw-browsers/chromium` là Chrome mới, không chạy old-headless với Remotion.
- Cảnh minh hoạ HTML (`tools/canh.mjs`) chạy bằng Playwright cài toàn cục trong sandbox (thiếu thì `npm i -g playwright@1.56.0`) với Chromium mặc định của Playwright trong `/opt/pw-browsers`; không cần `npm ci` studio. Đo thật: cảnh 15 giây 1080p nền đặc chụp khoảng 35 giây với 2 luồng.
- Tiến trình nền trong sandbox sống qua nhiều lượt gọi (`nohup ... & disown`, theo dõi bằng `tail` log).
- Sandbox là tạm: mỗi phiên dựng lại từ máy (mục "Khởi động phiên mới"). Máy là bản gốc; file nào sửa ở sandbox (nhất là `.tsx`) phải commit về máy ngay.
- Không có sandbox đám mây (Claude chạy thẳng trên máy của người dùng): render Remotion ngay trên máy, các bước khác giữ nguyên.

### Truyền file hai chiều

- Máy lên sandbox: `device_stage_files`, tối đa 400 MB mỗi file, chỉ file trong thư mục mount. Lỗi `untrusted_device`: phiên đăng nhập app Claude trên Mac đã cũ, nhờ người dùng đăng nhập lại, không thử lại trước đó.
- Sandbox về máy: chép file vào `/mnt/user-data/outputs/<thư mục>/` rồi `device_commit_files` với `stagedPath` và đường dẫn tuyệt đối trên máy. Tối đa 20 MB mỗi file, 100 MB mỗi lần: file lớn hơn thì `split -b 19m`, commit từng phần rồi `cat` nối trên máy.
- Mỗi lần commit bản sửa dùng một tên staged MỚI (commit lại cùng `stagedPath` từng ghi bản cũ). So md5 hai phía với file chữ và webm; mp4 và ảnh đi qua `outputs/` có thể được gắn thêm một hộp `uuid` (manifest nguồn gốc) nên md5 khác dù hình tiếng giữ nguyên: so bằng `ffprobe` (thời lượng, số khung).
- Đường dẫn quy đổi: `$HOME/mnt/<thư mục xưởng>/x` trong `device_bash` bằng `<đường dẫn gốc thư mục>/x` với stage, commit, list_dir. Không hardcode đường dẫn tuyệt đối: lấy từ `get_device_info.connectedFolders` ở đầu phiên.

### Nhiều máy dùng chung một thư mục xưởng (tuỳ chọn)

- Thư mục xưởng có thể đồng bộ iCloud hay Dropbox giữa nhiều máy Mac. Cùng kiến trúc chip thì `tools/pylib` và `tools/models` dùng chung; khác kiến trúc thì chạy lại `python3 tools/cai-dat.py` trên máy đó.
- File có thể đang chỉ nằm trên mây (`device_list_dir` đánh dấu `cloudOnly`): trước việc nặng, bảo đảm nguồn đã tải về máy đang ngồi.
- Quyền thư mục và quyền tải tự động của Chrome theo từng máy, không đồng bộ: lần đầu làm trên máy mới phải xin lại. `Go bang tren Mac.command` phải chạy lần đầu trên từng máy.
- Encode bài dài tạo file lớn sẽ bị đồng bộ lên mây: nhắc người dùng để ý dung lượng; file tạm `.tam/` đã được thu về 0 byte.

## Khởi động phiên mới

1. Đọc `CLAUDE.md`, file này, `phong-cach/PHONG-CACH.md`; xem `brand/brand.json`.
2. Sandbox: stage từ máy toàn bộ `studio/` (không có `node_modules`, thứ chỉ tồn tại ở sandbox), `tools/render-do-hoa.mjs`, `brand/brand.json` và logo cần dùng. Dự án có cảnh minh hoạ: stage thêm `tools/canh.mjs`, cả `do-hoa-chung/canh-kit/` và `du-an/<x>/canh/`, giữ nguyên cấu trúc thư mục tương đối (công cụ tìm kit theo đường dẫn so với chính nó).
3. `cd <studio> && npm ci` (khoảng 40 giây, `package-lock.json` đã ghim phiên bản). Chạy trong lúc máy làm bước 5 (mục "Hai làn song song").
4. Kiểm: `npx tsc --noEmit` sạch và `npx remotion compositions src/index.ts` liệt kê đúng 24 composition (22 đồ họa động, 2 Thumbnail tĩnh).
5. Máy: `python3 tools/cai-dat.py --trang-thai` (sherpa-onnx, model, ffmpeg); thiếu gì thì theo skill phim-thiet-lap.

## Quy trình một dự án

Khung chung; từng loại việc theo skill tương ứng.

1. **Nhận tư liệu**: người dùng thả file vào `du-an/<x>/nguon/`. `python3 tools/mediainfo.py "du-an/<x>/nguon"` để nắm thông số; khám màu nếu là cảnh quay.
2. **Gỡ băng**: large-v3 trên Mac qua hàng đợi là đường ưu tiên; turbo trong VM (`python3 tools/transcribe.py "<file>" --out-dir "du-an/<x>/transcript"`) là dự phòng, ghi rõ trong báo cáo. Ra bốn file `.transcript.json`, `.srt`, `.txt`, `.silences.json`. Luôn qua `nghiem-thu.py transcript`.
3. **Phân tích và duyệt giấy**: đọc transcript, chọn đoạn giữ hoặc bỏ, đề xuất overlay (tên chương trình, các bước, key message) cùng lúc. Gửi phương án cắt cho người dùng duyệt trước khi dựng. Infomotion và phim tài liệu có kịch bản trên giấy; con số trên giấy do `tools/uoc-luong.py` cộng, không cộng tay.
4. **Đồ họa** (sandbox): intro, outro từ preset; đồ họa khác soạn job theo mẫu `du-an/_mau/do-hoa/`. `node tools/render-do-hoa.mjs <job.json> --studio <studio>`: script tự đồng bộ logo, file riêng của dự án khai báo trong trường `"assets"`, bỏ qua job đã render đúng props (`--lam-lai` để render lại), `--gioi-han <giây>` để dừng gọn và chạy lặp. QR theo dự án: python `qrcode` ở sandbox. Commit về `du-an/<x>/do-hoa/<ngang|doc>/`, kiểm đủ file và `ffprobe` đúng thời lượng trước khi dựng.
5. **Timeline**: soạn `du-an/<x>/timeline.json` theo docstring đầu `tools/assemble.py` (mục "timeline.json: những điều phải nhớ" bên dưới). Chạy `assemble.py --kiem-tra` trước khi dựng.
6. **Bản nháp**: `python3 tools/assemble.py --project "du-an/<x>" --preview --out "<tên>-<khung>-nhapN"` rồi nghiệm thu và gửi người dùng duyệt.
7. **Bản chính**: bỏ `--preview`, `--out "<tên>-<khung>"`. Bài dài gọi lặp y nguyên lệnh (tự resume).
8. **Giao**: bản đạt nghiệm thu (và đã burn phụ đề nếu là clip dọc) đặt vào thư mục clip trong `Thanh pham/` (xem mục "Quy ước hai thư mục xuất và tên file"). Báo tên file, đúng thư mục clip trong `Thanh pham/`, thời lượng, dung lượng, kèm chapters nếu có.
9. **Đăng tải** (tự làm, không chờ nhắc): skill phim-dang-tai. Chọn khung mặt bằng `python3 tools/chon-khung-thumbnail.py --map <video>.map.json` (rồi `--quanh kNN`), soạn `dang-tai.json` và `thumbnail.json`, `python3 tools/dang-tai.py job` rồi render thumbnail ở sandbox bằng `render-do-hoa.mjs --lam-lai` (job `"still": true`), cuối cùng `python3 tools/dang-tai.py kiem` ĐẠT và nhìn `soi-thumbnail.jpg`. Báo cùng lượt với bước 8.

## Bàn dựng: người dùng tự tinh chỉnh

Bàn dựng [timeline editor] để người dùng tự tay chỉnh nhỏ một clip đã có bản nháp, thay vì mô tả cho Claude. Đặc tả và nền nghiên cứu: tài liệu "ban-dung-dac-ta" trong Project.

- **Mở**: người dùng bấm đúp `Mo ban dung.command` ở gốc xưởng (Mac thật, không phải VM). `tools/ban-dung.py` chạy máy chủ 127.0.0.1:8765 bằng python3 có sẵn của macOS (chỉ thư viện chuẩn), tự mở Chrome. Trang là JS thuần trong `tools/ban-dung/` (không có bước build): sửa thẳng file trên máy rồi kiểm ở sandbox.
- **Làm gì được**: tỉa đầu, cuối đoạn (kéo mép, khung xem hiện đúng khung hình ở mép), tách, xoá, đổi thứ tự, nối lại hai đoạn liền nhau; dời đồ họa nổi (kể cả sang đoạn khác) và kéo mép để đổi thời lượng thẻ (ghi `overlay.duration`), dời và tỉa B-roll; tiếng riêng đoạn (`volumeDb`); nhạc nền (mức, kiểu, mờ, giảm khi có lời); mờ vào, mờ ra, chỉ mờ tiếng; chương; hoàn tác không giới hạn trong phiên. Kéo tỉa tay tự ghi cứng điểm hút khoảng lặng rồi đặt `snap: false`; tỉa đầu đoạn tự bù `overlay.at` (thẻ giữ đúng câu) và `audioIn` (multicam).
- **Dựng bằng lời** (thẻ "Lời" ở cột phải): văn bản nguyên văn của mọi đoạn theo thứ tự dòng thời gian, mượn cách viết hoa và dấu câu của large-v3 chỗ nào khớp (trường `h`, chỉ để đọc), từ đệm gạch chân chấm. Chữ mờ là chữ ngay trước/sau đoạn chưa đoạn nào dùng; chữ gạch là chữ đã bỏ giữa hai đoạn liền nhau cùng file. Bôi đen rồi Delete: bỏ ở đầu hay cuối đoạn thì tỉa, ở giữa thì tách đoạn; Enter: khôi phục (kéo dài đoạn, hoặc nối lại hai đoạn qua quãng đã bỏ). Điểm cắt luôn do `tools/ban_dung_loi.py` tính trên máy chủ (`/api/cat`), ranh giới dính liền thì trang hỏi người dùng bỏ thêm, giữ lại hay vẫn cắt. Sửa `ban_dung_loi.py` thì người dùng phải đóng và mở lại Bàn dựng (máy chủ giữ bản đã nạp).
- **Chuẩn bị** khi đưa một clip cho người dùng chỉnh: `python3 tools/moc-tu.py "du-an/<x>"` để có dạng sóng, chữ trong khối và khung Lời (bản 10 phút khoảng 2,5 phút; bài dài chạy lặp tới khi báo xong). Không cần proxy với nguồn H.264 hoặc HEVC mà Chrome giải mã được.
- **Khi người dùng báo đã chỉnh xong**: đọc dòng cuối `du-an/<x>/ke-hoach-dung/_ban-dung/nhat-ky.jsonl` (danh sách thay đổi, đường dẫn bản cũ), chạy `assemble.py --kiem-tra`, dựng nháp với `--out` tường minh rồi nghiệm thu như mọi lần. Bản cũ mỗi lần lưu nằm ở `du-an/<x>/ke-hoach-dung/_phien-ban/` (clip ngắn: tên có tiền tố `clip-ngan__<slug>__`).
- **Ghi có khoá**: file đã đổi từ lúc người dùng mở thì trang hỏi nạp bản mới hay ghi đè; không bao giờ ghi lặng lẽ đè lên sửa của Claude hay của máy kia.
- **Nhật ký là góp ý thật**: một kiểu chỉnh tay lặp lần thứ hai (quy tắc cứng 6 của CLAUDE.md) thì đề xuất sửa nguồn mặc định.
- **Xem trước gần đúng**: chưa có bố cục slide, đơn màu, chuẩn hoá -14 LUFS, nhạc giảm khi có lời, phụ đề burn. Bản nháp 480p vẫn là chốt duyệt.
- **Kiểm ở sandbox**: Chromium của Playwright không giải mã H.264/AAC; dựng một dự án thử bằng WebM (VP9, Opus) từ `du-an/_kiem-tra-tu-dong` rồi chạy kịch bản kéo, tách, lưu, xung đột.

## timeline.json: những điều phải nhớ

Schema đầy đủ trong docstring đầu `tools/assemble.py`. Những điểm hay nhầm:

- **Hai hệ mốc thời gian**: `in`, `out`, `broll[].at` là mốc TRONG FILE NGUỒN; `overlay[].at` là giây TƯƠNG ĐỐI từ đầu đoạn (sau snap). Overlay muốn hiện lúc lời nói ở mốc nguồn T: `at = T - in`. B-roll muốn vào sau đầu đoạn s giây: `at = in + s`. `--kiem-tra` bắt phần lớn lỗi này.
- `overlay` nhận một dict hoặc một list nhiều lớp (không chồng khoảng hiển thị); overlay chỉ phủ lên quãng đầu của đoạn cho tới B-roll đầu tiên. Thêm `"duration"` để thẻ hiện lâu hoặc ngắn hơn độ dài file (từ `assemble.py` r7): dài hơn thì giữ khung tại `"giu"` (mặc định giữa file, nơi thẻ đứng yên), ngắn hơn thì bỏ một quãng từ `"giu"`; hoạt cảnh vào và ra giữ nguyên. Khi cần thẻ dài hơn hẳn (gấp đôi trở lên) hoặc thẻ có chuyển động suốt, render lại thẻ với thời lượng mới vẫn đẹp hơn.
- **Hook trước intro**: intro là segment `insert` mang `"role": "intro"`; outro chèn giữa danh sách mang `"role": "outro"`. Nhạc `bookends` bám theo `intro`/`outro` cấp cao nhất hoặc các insert có role; timeline `bookends` không có intro, outro nào thì assemble báo lỗi.
- Đồ họa chèn (intro, outro, insert) có đuôi tiếng AAC thừa 0,02-0,06 giây: assemble tự cắt, in một dòng thông báo. Không strip `-an`, không ép `-t` bằng tay.
- `snap: true` hút điểm cắt về khoảng lặng gần nhất: đọc dòng log `đoạn N: ... [X → Y]` để biết mốc thật đã dùng.
- Trường tuỳ chọn: `chapter` (tạo chapters), `label` (nhãn đoạn ổn định A/B/T/M cho phim tài liệu, `tools/nhan-doan.py`), `fadeIn`, `fadeOut`, `fadeOutAudio`, `cropFocus` (khung dọc), `volumeDb` (tiếng riêng đoạn, dB; chỉ có tác dụng từ `assemble.py` r7, trước đó bị bỏ qua lặng lẽ), `layout`/`slide`/`slideZoom` (bài giảng có slide), `audioSrc`/`audioIn` (multicam, đặt `snap:false`), `colorGrade` cấp cao nhất.
- Dự án con clip ngắn: `--project` trỏ DỰ ÁN GỐC, `--timeline "clip-ngan/<slug>/timeline.json"`, `--out "<slug>-<khung>[-nhapN]"`; đồ họa riêng đặt trong `clip-ngan/<slug>/do-hoa/`, đường dẫn tương đối so với dự án gốc.
- Sau khi dựng, `<thành phẩm>.map.json` ghi mốc từng part: dùng nó để tính lại phụ đề, chapter, nhãn đoạn và mốc trích khung (cue có `in ≤ t < out` thì mốc mới `start + (t - in)`), không cộng trừ tay.

## Phòng ngừa lớp lỗi ngầm

Bối cảnh: một bất biến của hệ (hình = tiếng ở mọi file trung gian) từng bị vi phạm mà không chỗ nào kiểm, cộng với một nhánh tự sửa ngầm nuốt mất tín hiệu, làm thành phẩm lệch tiếng cộng dồn tới 4,5 giây. Chi tiết: `docs/BAI-HOC.md` chủ đề "Đồng bộ hình tiếng".

**Bốn nguyên tắc**

1. Bất biến phải được ĐO ở mọi bước: từng part sau encode, thân phim sau ghép, thành phẩm sau finalize đều qua `check_av()`: part và thân phim (tiếng PCM, đúng từng mẫu) hình = tiếng trong 4 ms và tổng đúng dự kiến trong 0,02 giây; thành phẩm (AAC, hạt 21 ms) trong 0,06 giây. Ngưỡng 0,06 giây chỉ hợp cho AAC: áp cho part từng bỏ lọt part lệch đúng một khung, cộng dồn qua 200 part thành lệch 0,1-0,2 giây. Đồ họa render xong tự đo. Transcript qua `nghiem-thu.py transcript`.
2. Không có nhánh sửa ngầm: sai là dừng với bảng chẩn đoán. Hạ ngưỡng, bắt ngoại lệ rồi bỏ qua, "gần đúng là được" đều bị cấm.
3. Cache phải biết code và dữ liệu đã đổi: chữ ký `.sig` gồm `TOOL_VERSION` và kích cỡ, mtime mọi file nguồn liên quan; part lấy từ cache vẫn qua `check_av()`. Muốn ép dựng lại một part: thu `part-*.mp4` và `.sig` của nó về 0 byte bằng `open(f, "w").close()` (đây là ghi, không cần quyền xoá). Sửa logic encode thì đổi `TOOL_VERSION` (hằng số đầu `tools/assemble.py`) rồi chạy `python3 tools/kiem-tra-xuong.py` (dựng lại `du-an/_kiem-tra-tu-dong` qua cổng nghiệm thu, và chạy `kiem-dong-bo.py`: bắt buộc ĐẠT trước khi dựng thật).
4. Đồng bộ phải được đo TUYỆT ĐỐI, không chỉ so thời lượng: `tools/kiem-dong-bo.py` dựng nguồn giả có chớp trắng và tiếng click đúng cùng một khung, cắt tại mốc lẻ, rồi đo "tiếng - hình" từng sự kiện trên thành phẩm (mỗi cặp trong ±40 ms, trôi dưới 15 ms mỗi phút). Nó là bài kiểm hồi quy [regression] của `assemble.py`: mọi lần sửa logic encode, ghép hay finalize phải chạy lại. `tools/do-dong-bo.py` làm cùng việc trên phim thật (so thành phẩm với nguồn tại 10-12 mốc); `nghiem-thu.py video` tự gọi nó khi có `map.json`.
5. Kiểm cấu hình trước khi tốn thời gian: `assemble.py --kiem-tra` bắt lỗi timeline (file thiếu, mốc vượt nguồn, nhầm hai hệ mốc, B-roll chồng nhau, insert đầu phim thiếu role) trong một giây.

**Bổ sung 2026-09-30 (`CONCAT_REV` c8)**: (a) `concat.txt` luôn ghi `duration` chính xác n/fps từng part; (b) map ghi dur frame-exact của insert và `write_time_map` dừng khi tổng dur map lệch tổng part quá 5 ms; (c) finalize đo loudness nghiêm ngặt, cache `.ln` chỉ nhận kết quả có `input_i`, không rơi về loudnorm một lượt. Sửa ghép hay finalize thì đổi `TOOL_VERSION` hoặc `CONCAT_REV`, chạy `kiem-tra-xuong.py`, rồi mới dựng thật.

**Công cụ**

| Việc | Lệnh (từ gốc "xuong-phim-claude") |
|---|---|
| Kiểm timeline trước khi dựng | `python3 tools/assemble.py --project "du-an/<x>" --kiem-tra` |
| Dựng (tự kiểm từng part, thân phim, thành phẩm; ghi `.map.json`, `.nghiem-thu.json`) | `python3 tools/assemble.py --project "du-an/<x>" [--preview] --out "<tên>"` |
| Kiểm đồng bộ hình-tiếng tuyệt đối của `assemble.py` (dựng thử chớp/click, hồi quy) | `python3 tools/kiem-dong-bo.py` (`--assemble <bản khác>` để thử một bản cũ) |
| Đo đồng bộ trên phim thật (thành phẩm so với nguồn, trôi theo thời gian) | `python3 tools/do-dong-bo.py "<file.mp4>" [--mau 12]` (nghiệm thu tự gọi) |
| Nghiệm thu thành phẩm (hình = tiếng, đồng bộ so với nguồn, LUFS, khung, im lặng, hình đứng, ảnh lưới) | `python3 tools/nghiem-thu.py video "<file.mp4>" --khung ngang\|doc [--nhap] --anh` |
| Nghiệm thu transcript (Whisper bỏ đoạn, mốc đảo) | `python3 tools/nghiem-thu.py transcript "du-an/<x>" [--nguon <tên file>]` |
| Nghiệm thu đồ họa đã render | `python3 tools/nghiem-thu.py do-hoa "du-an/<x>/do-hoa"` |
| Kiểm giấy kịch bản (thời lượng, độ phủ infomotion) | `python3 tools/uoc-luong.py "du-an/<x>/KICH-BAN-<...>.md" [--muc-tieu 5-6p] [--khoang-hinh 8]` |
| Dựng thử cả xưởng sau khi sửa tool (chạy cả cổng kiểm tài liệu) | `python3 tools/kiem-tra-xuong.py [--co-slide]` |
| Chỉ kiểm tài liệu và skill (YAML, đường dẫn, tên skill, kho ẩn dụ, dấu phiên bản) | `python3 tools/kiem-tai-lieu.py` |

**Quy ước báo cáo**: chưa có dòng "nghiệm thu máy: ĐẠT" thì chưa được nói "xong". Ảnh lưới `<file>.luoi.jpg` là bước soi mắt, chạy SAU cổng máy, không thay cổng máy. Overlay đồng bộ lời nói cần thêm lớp thứ hai: trích khung tại mốc từng overlay (theo `map.json`) và đối chiếu với câu transcript đang nói ở đúng khung đó.

**Giới hạn của cổng máy**: `check_av()` so thời lượng (hình với tiếng của cùng một file), nên không thấy lệch căn chỉnh so với NGUỒN. Hai công cụ trên bù chỗ đó; sai số còn lại của một phim đạt là dưới một khung hình (nguồn 29.97 fps ra 30 fps), tiếng khớp tuyệt đối. Khi người xem báo lệch dù cổng đạt: chạy `do-dong-bo.py --mau 24` (mốc dày hơn) rồi rà khoảng cách gói bằng `ffprobe -select_streams a:0 -show_entries packet=pts_time -of csv=p=0` tại ranh giới đoạn đọc từ `map.json`. Công cụ đo tự viết phải thử trên nguồn biết trước đáp án (`docs/BAI-HOC.md` chủ đề "Đồng bộ hình tiếng").

## Việc chạy dài hơn 180 giây

- **`assemble.py` tự resume**: mỗi part encode xong lưu kèm `.sig`. Lượt gọi bị ngắt thì gọi lại Y NGUYÊN lệnh (cùng `--out`) nhiều lần tới khi thấy "✓ Xong"; part đã đúng tự bỏ qua.
- Bước ghép và finalize có cache từng chặng (thân phim theo `.sig`, mix nhạc, số đo loudness) nên phim dài cũng chạy được bằng cách gọi lại y nguyên lệnh nhiều lượt; nhưng chạy xong bản cuối thì `.tam/` bị thu về 0 byte, gọi lại sau đó là dựng lại từ đầu. Khi một chặng vẫn vượt 180 giây: stage các `part-*.mp4` đã encode và nhạc lên sandbox (tới 600 giây mỗi lệnh), chạy lại đúng hàm ghép (`_concat_exact`: hình copy và tiếng nối thẳng từng mẫu PCM) và finalize chép từ `assemble.py`, không tự gõ lại lệnh `concat` với `aresample` (cách cũ làm lệch hình-tiếng), rồi commit về `xuat-nhap/` (file lớn theo mục "Truyền file hai chiều"). `map.json` và chapters không phụ thuộc độ phân giải hay CRF nên dùng lại được số liệu của bản nháp preview cùng timeline. Không dùng preset `ultrafast` để thoát kẹt trừ khi người dùng chấp nhận file nặng hơn nhiều.
- **`render-do-hoa.mjs`**: đường alpha mặc định là PNG + ffmpeg libvpx (nhanh khoảng sáu lần encoder vp8 của Remotion); `--gioi-han <giây>` dừng gọn và thoát mã 2 để chạy lặp. Render tuần tự, không song song hai job trong sandbox 2 lõi.
- **Gỡ băng**: large-v3 trên Mac không bị giới hạn 180 giây. Turbo trong VM: script + `timeout 170` + log, gọi lặp đọc tiến độ; file dài hơn 90 phút tách audio thành khúc 30 phút, cộng offset khi ghép, kiểm mốc ở ranh giới khúc.
- Việc dài khác trên máy không có resume: ghi lệnh vào script trong dự án, chạy `timeout 170 bash du-an/<x>/.tam/run.sh >> du-an/<x>/.tam/run.log 2>&1; tail -5 du-an/<x>/.tam/run.log`, script tự bỏ qua bước đã xong.

## Quy ước hai thư mục xuất và tên file

- **`xuat-nhap/`**: mọi thứ `assemble.py` ghi ra (nháp 480p và bản chính chưa qua hậu kỳ nào khác). Vùng làm việc, không gửi người dùng như bản cuối; dọn được khi dự án xong.
- **`xuat-hoan-chinh/`** (trong dự án): CHỈ file đã hoàn tất hậu kỳ và qua nghiệm thu (clip dọc là bản đã burn phụ đề); bước đệm trước khi vào `Thanh pham/`.
- **`Thanh pham/`** (ngang hàng "xuong-phim-claude"): nơi duy nhất trỏ người dùng tới khi báo hoàn thành. MỖI DỰ ÁN MỘT THƯ MỤC MẸ `<tên dự án>/`, bên trong mỗi clip một thư mục tự đủ đánh số thứ tự: `Short NN <slug>/` cho short (NN hai chữ số), `00 Video day du/` cho clip dài; không tách thư mục ngang cấp ở `Thanh pham/`. Thư mục clip gồm video, `nghiem-thu.json`, `dang-tai/` (dang-tai.json, DANG-TAI.md, thumbnail-*.json, thumb-*.jpg, soi-thumbnail.jpg, khung/). Người dùng sao lưu bằng cách dời nguyên thư mục. Chép từ sandbox: chỉ khi render đã xong, đối chiếu md5; sau khi vào `Thanh pham/` chạy lại `dang-tai.py kiem`.
- **Nguồn dựng** (timeline, cues, phụ đề .ass, map.json, script, nguồn cảnh minh hoạ, gỡ băng) lưu ở `du-an/<dự án>/`, không nằm trong thư mục clip; nhờ đó dựng lại được khi cần.
- **Dọn nháp và rác chỉ sau khi người dùng nói "duyệt"** (xin quyền xoá rồi dọn cho trống ổ; xem CLAUDE.md quy tắc 12).
- Luôn truyền `--out` tường minh: nháp `<tên>-<khung>-nhapN` (tăng N mỗi vòng), bản chính `<tên>-<khung>`. Tên đã kết thúc bằng `-nhapN` thì script không nối thêm `-nhap`. Không cần hậu tố `-final` hay `-khong-phude`.

## Quy ước chất lượng

- Chuẩn phát hành: 1080p, H.264 high, CRF 18 veryfast, AAC 192k 48 kHz stereo, -14 LUFS (loudnorm hai lượt, linear), true peak dưới -1 dB, +faststart, 30 fps (nguồn 25 fps đồng nhất thì đặt fps 25 để tránh giật).
- Ghép part: luôn giải mã rồi mã hoá lại (không `concat -c copy`); cờ `--ep-encode-lai` chỉ còn để lệnh cũ không vỡ.
- Điểm cắt: luôn hút về khoảng lặng thật; không cắt giữa từ; vùng có tạp âm nền không phải chỗ đặt mối nối.
- Giữ mạch: ưu tiên `overlay` (một lần encode liên tục) hơn `broll` hay `insert` khi lời nói cần liền; trước khi chọn insert, hỏi "đoạn này có phải cắt cảnh không, hay chỉ cần một lớp chữ đè lên". Giữa hai thẻ toàn màn hình liên tiếp có ít nhất 5 giây cảnh quay chính (không áp cho overlay bán trong suốt, không áp cho infomotion vì không có người trong khung).
- Overlay, pill, chữ đè lên hình người nói: (1) không che cả người lẫn mặt nếu tránh được; (2) buộc đánh đổi thì tuyệt đối không che mặt, chấp nhận che một phần thân. "Mặt" là mặt bất kỳ ai trong khung, kể cả người ngồi hoặc đứng phía sau người nói (khán phòng, sân khấu); khung có người ở nền thì không dùng `mat-chinh`. Kiểm ở trạng thái tích luỹ đầy đủ trên khung hình thật, tại MỌI mốc có lớp phủ. Khung dọc có cả pill lẫn phụ đề: phụ đề sát đáy, pill `position:'bottom'` + `edgeInset: 0.3`.
- Phong cách đồ họa, chữ trên hình, từ ngữ, chức danh: theo `phong-cach/PHONG-CACH.md` (minimalist, chuyển động chậm bezier 0.22, 1, 0.36, 1; Lora cho tiêu đề, Be Vietnam Pro cho nội dung; thuần Việt có ngoặc vuông [English]; sentence case; gạch ngang thường).
- Nhạc nền: `bookends` cho bài giảng, `full` + duck cho clip quảng bá; track và `gainDb` (khác nhau giữa full và bookends) theo từng track trong `thu-vien/AM-THANH.md`; track Kevin MacLeod kèm dòng ghi công CC-BY trong mô tả video. Bổ sung nhạc mới theo "Quy tắc bổ sung thư viện" trong file đó; không dùng track có nhãn Content ID.
- Hook trước, intro sau: clip ngắn không bao giờ mở bằng intro (intro 2,5-4 giây hoặc bỏ hẳn); bài dài có câu mở mạnh cũng đặt hook trước intro.
- Kết bằng thẻ tĩnh (outro): mờ dần cả hình lẫn tiếng khoảng 1,5 giây.

## Khi một khâu hỏng

Mỗi khâu có sẵn cách xử lý khi hỏng, để Claude không phải nghĩ lại mỗi lần và người dùng luôn biết chuyện gì đang xảy ra. Ba nguyên tắc:

1. Tìm nguyên nhân, sửa, rồi thử lại tối đa một lần. Lần thứ hai vẫn hỏng thì dừng khâu đó.
2. Không có cách bù ngầm. Kéo dài bằng khung đứng, mượn cảnh kề, thay hình khác nội dung, hạ ngưỡng nghiệm thu: mọi cách bù đều phải hiện ra thành một lựa chọn kèm lý do để người dùng chọn.
3. Hỏng một phần không kéo cả dự án dừng theo: phần độc lập vẫn làm tiếp, phần đã xong vẫn giữ (cache part, file trung gian, job JSON).

| Khâu | Hỏng thường gặp | Tự làm | Dừng và báo khi |
|---|---|---|---|
| Đưa file từ máy lên sandbox | lỗi `untrusted_device`, quá thời gian | file lớn: trích phần cần trên máy trước, stage riêng file lớn nhất | `untrusted_device`: không thử lại, nhờ người dùng đăng nhập lại app Claude |
| Gỡ băng | model chết lặng vì hết bộ nhớ; rớt cụm ở ranh giới lô 28 giây; hallucination khi có tạp âm | large-v3 qua hàng đợi Mac hoặc turbo trong VM, chia mảnh; gỡ lại cửa sổ rộng quanh chỗ hỏng | hai lần gỡ cùng đoạn cho kết quả khác hẳn nhau: nhờ người dùng nghe tại mốc cụ thể |
| Render đồ họa (sandbox) | treo không có log, `tsc` lỗi, file ngắn hơn dự kiến | kiểm khoá Chrome mồ côi, gộp job chạy tuần tự, render lại đúng thời lượng | sau một lần sửa vẫn lỗi: báo đồ họa nào, đề xuất hình thay để người dùng chọn |
| Dựng (`assemble.py`) | lượt gọi quá 180 giây; `check_av()` không đạt | gọi lại y nguyên (resume); ghép hoặc finalize kẹt thì chạy hai bước đó ở sandbox | `check_av()` không đạt: dừng, đọc bảng chẩn đoán, không encode lại cho qua |
| Nghiệm thu (`nghiem-thu.py`) | LUFS, true peak, khung, hình đứng | true peak vượt khi LUFS đã đúng: thêm `alimiter` ở bước cuối; lỗi khác: sửa ở gốc rồi dựng lại | chưa ĐẠT thì không giao, không nói "xong" |
| Đưa file về máy | ghi nhầm bản cũ; file lớn hơn 20 MB | mỗi lần sửa dùng tên staged mới, so md5 (mp4 so `ffprobe`); file lớn `split -b 19m` rồi nối lại trên máy | vẫn lệch: báo, không chạy tiếp trên file lệch |
| Kết nối với máy | máy ngủ, mất kết nối | làm tiếp phần làm được trong sandbox | cần file trên máy: nói rõ lúc này không với tới máy và cần gì |

Mẫu câu báo, bằng lời thường, không thuật ngữ kỹ thuật: "Đang dừng ở khâu <gỡ băng / làm đồ họa / dựng nháp / kiểm bản xuất> vì <chuyện gì, một câu>. Phần đã xong vẫn giữ nguyên. <Việc cần người dùng làm, cụ thể> hoặc <cách đang thử, khoảng bao lâu>."

## Thời gian đo thật

Bảng này để Claude báo tiến độ bằng số đo thật ("còn khoảng X phút, đang chờ máy chứ không chờ người dùng") thay vì đoán. Đo bằng `date +%s` trước và sau lệnh, hoặc thời gian ghi trong log; không ghi số ước lượng vào bảng. Sau mỗi dự án thêm hoặc sửa một dòng. Việc chưa có số đo thì báo với người dùng là ước lượng.

| Việc | Quy mô | Nơi chạy | Đo được | Nguồn |
|---|---|---|---|---|
| Khởi động studio (`npm ci`) | mỗi phiên một lần | sandbox | khoảng 40 giây | mục "Khởi động phiên mới" |
| Proxy 4K sang 1080p | mỗi góc máy | máy (VM 4 lõi) | khoảng 0,4 lần thời gian thực | skill phim-multicam |
| Nhận diện người nói bằng hình trên proxy | buổi 20 phút | máy | khoảng một phút | dự án thật, 2026-09-29 |
| Dựng part (`assemble.py`) | bài khoảng 10 phút | máy | xong trong hai lượt gọi (mỗi lượt tối đa 180 giây) | đo thật |
| Gỡ băng turbo | 6,6 giây tiếng mẫu | máy | khoảng 2,8 giây | đo thật, 2026-09-21 |
| Gỡ băng large-v3 trên Mac | mỗi 10 phút tiếng | Mac thật | chưa đo | |
| Render đồ họa đục (mp4) | một đồ họa 10-15 giây | sandbox | chưa đo | |
| Render đồ họa nổi (webm alpha) | một đồ họa 13 giây | sandbox | dưới 2 phút khi CRF 30 (encoder vp8 cũ: hơn 12 phút chưa xong) | dự án thật, 2026-09-22 |
| Xuất bản chính 1080p và nghiệm thu | mỗi 10 phút phim | máy | chưa đo | |

## Hai làn song song: máy và sandbox

Máy và sandbox là hai nơi chạy độc lập nên làm cùng lúc được. Tiến trình nền trong `Bash` của sandbox sống qua nhiều lượt gọi, còn `device_bash` trên máy chạy đồng bộ từng lượt. Vì vậy: khởi động việc dài ở sandbox trước, rồi làm việc của máy trong lúc chờ.

- Khởi động phiên: sandbox `npm ci` trong lúc máy chạy `cai-dat.py --trang-thai` và chạy `mediainfo.py`.
- Sau cổng duyệt kịch bản: sandbox render đồ họa theo job đã duyệt, trong lúc máy khám màu, làm proxy, soạn `timeline.json`.
- Vòng góp ý: sandbox render lại riêng các đồ họa bị góp ý, trong lúc máy sửa `timeline.json` cho các điểm góp ý không dính đồ họa.

Không chạy song song: hai job render trong cùng sandbox (2 lõi, kẹt nhau); hai việc mà việc sau cần kết quả việc trước (kịch bản cần transcript đạt, dựng cần đồ họa đã về máy). Trước khi dựng, luôn kiểm đồ họa đã commit về máy đủ file và `ffprobe` đúng thời lượng.

## Bài giảng có slide

Skill phim-bai-giang-slide. Ba trạng thái hình theo NỘI DUNG lời nói: **mặt** (dẫn nhập, kể chuyện, chuyển ý, kết), **cả hai** (`ca-hai`: slide chính + mặt nhỏ; MẶC ĐỊNH cho mọi slide còn đọc được ở 73% khung), **slide toàn khung** (chỉ khi kiểm đọc thật ở 73% thất bại, hoặc slide có animation, quay màn hình). `ca-hai` là bố cục chủ đạo nên kiểm cropFocus rải đều nhiều mốc trong từng đoạn.

| Việc | Lệnh |
|---|---|
| Nhập slide (PPTX cần soffice, chạy ở sandbox; PDF cần poppler) | `python3 tools/slide-nguon.py "<nguồn>" --project "du-an/<x>"` ra `slide/slide-NN.png`, `slide/slide.json` |
| Khớp slide với lời giảng, đề xuất dàn hình | `python3 tools/slide-khop.py "du-an/<x>" --clip "<tên file nguồn>" [--lech s] [--bo-qua 1,2]` ra `slide/DAN-HINH.md`, `slide/timeline-slide-nhap.json` |
| Sinh lại khung, mask bố cục | `python3 tools/bo-cuc-slide.py` ra `do-hoa-chung/bo-cuc/` |
| Dựng | timeline có `"theme"`, mỗi segment `"layout": mat\|slide\|ca-hai\|chia-doi\|mat-chinh`, `"slide"`, tuỳ chọn `"slideZoom"`; rồi `--kiem-tra` và dựng như thường |

Bố cục ghép ở 1920x1080 rồi thu về preview; overlay và fade dùng được trên mọi bố cục; B-roll bỏ qua layout. `nghiem-thu.py video` không cảnh báo hình đứng trong quãng layout `slide`.

## Multicam

Skill phim-multicam. Nguồn để theo `nguon/<góc>/<file>`: thư mục chứa `toan` là góc toàn, bắt đầu bằng `tieng` là file tiếng riêng, còn lại là góc cận mang tên người. Tiếng luôn là MỘT track chủ liên tục (`audioSrc`/`audioIn`), hình đổi trên nền tiếng đó.

| Việc | Lệnh |
|---|---|
| Đồng bộ các góc bằng âm thanh | `python3 tools/multicam-khop.py "du-an/<x>" [--chu toan] [--tron-tieng]` ra `multicam.json`, `nguon/tieng-chu.wav` |
| Proxy 1080p đã căn sẵn (nguồn 4K nặng) | `python3 tools/multicam-proxy.py "du-an/<x>" [--gioi-han <giây>]` (chạy theo mảnh, gọi lặp tới khi xong; tự ghi multicam.json của proxy) |
| Gỡ băng tiếng chủ | trên `nguon/tieng-chu.wav` rồi `nghiem-thu.py transcript` |
| Người nói, session, dàn góc | `python3 tools/multicam-dan.py "du-an/<x>" --transcript "<tên>" [--che-do podcast\|bai-giang] [--nguoi-noi auto\|hinh\|file] [--khoa khoa-overlay.json] [--cua-so A-B --hau-to clipN]` ra `multicam/DAN-GOC.md`, `timeline-multicam-nhap.json`, `job-session.json` |
| Dựng | render SectionTitle từ `job-session.json`; timeline giữ `audioSrc`/`audioIn`, `snap: false` |

Kiểm riêng: file có `tin_cay` dưới 1,1 hay `khop_r` dưới 0,2 phải soi khung hai góc tại cùng mốc; sau dựng trích khung tại ba cú cắt xa nhau và nghe 2 giây quanh đó. Bài giảng một người nhiều góc phải truyền `--che-do bai-giang`.

## Phim tài liệu phỏng vấn và infomotion

Hai dòng này có cổng duyệt trên giấy trước khi dựng hoặc render; quy trình đầy đủ trong skill phim-tai-lieu-phong-van và phim-infomotion.

- Phim tài liệu: Pha 1 `HO-SO-PHIM.md` và `KE-HOACH-GHI-HINH.md` (cổng duyệt 1); Pha 2 `KIEM-KE-NGUON.md`, `KICH-BAN-THUC-TE.md` có cột "Kiểm chứng" (cổng duyệt 2), `SO-GOP-Y.md` từng vòng, `NHAN-DOAN.md` sinh bằng `tools/nhan-doan.py <timeline.json> <thành phẩm>.map.json --out NHAN-DOAN.md` sau mỗi lần render. Thư mục nguồn chuẩn: `nguon/phong-van/`, `nguon/canh-tram/`, `nguon/su-kien/`, `nguon/anh/`.
- Infomotion: nền `nguon/nen-<khung>.mp4` tạo bằng `ffmpeg -f lavfi color=<bg của theme>` ghép với giọng (`-shortest`) làm clip nguồn duy nhất; đồ họa toàn khung vào `broll` (mốc nguồn), đồ họa nổi vào `overlay` (mốc tương đối). Mặc định phủ kín: không quá 1 giây nền trơn trừ nhịp `Hình: KHÔNG - <lý do>`; `uoc-luong.py` kiểm độ phủ trên giấy. `nghiem-thu.py video` báo "hình đứng" ở quãng nền trơn: chỉ hợp lệ khi trùng nhịp không hình có lý do và không dài quá 20 giây. Overlay chỉ hiện trước B-roll đầu tiên của segment: chương có đồ họa nổi xen sau đồ họa toàn khung thì tách thành nhiều sub-segment liền mạch.

