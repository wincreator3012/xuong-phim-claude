# Short dọc "mặt trên, cảnh dưới" (bố cục `mat-tren`)

Khuôn đã chạy trọn chín short từ một buổi giảng dài: nửa trên là mặt người nói, nửa dưới là một cảnh minh hoạ chuyển động vẽ theo lời trên nền giấy. Dùng khi nguồn là MỘT người nói (bản ghi Zoom `Speakers only`, một camera) và các đoạn đáng làm short là lập luận có ví dụ hay cơ chế mà hình vẽ giúp hiểu; cả loạt cần đồng đều từ khung hình, nhịp chữ đến nhạc. Đoạn nào cần thẻ nổi trên chính khung rộng thay vì ô riêng thì vẫn dùng `references/clip-co-minh-hoa.md`; hai cách khác nhau ở chỗ này: `mat-tren` chia khung cố định thành hai ô nên mặt không bao giờ bị che, còn cảnh có cả nửa khung để vẽ.

Bộ công cụ nằm ở `tools/` (tên bắt đầu bằng `short-`), mọi lệnh chạy từ gốc xưởng và trỏ hồ sơ dự án bằng `--du-an "../Du an/<x>"`:

| Việc | Công cụ |
|---|---|
| Chốt mép cắt theo âm tiết, sinh timeline, phụ đề gốc và dữ liệu cảnh của short | `tools/short-dung.py snap <slug>` |
| Soi âm tiết, năng lượng, quãng lặng, lời large-v3, độ khớp chữ | `tools/short-soi.py tu / nl / lang / lv3 / chu` |
| Sinh các trang cảnh HTML từ dữ liệu cảnh | `tools/short-canh.py <slug>` (khung: `do-hoa-chung/canh-kit/mau/canh-short.html`) |
| Chụp cảnh ra webm alpha trong sandbox đám mây | `tools/short-render-canh.sh` |
| Dựng, phụ đề, nén, âm lượng, nghiệm thu một short | `tools/short-xuat.sh "<dự án>" <slug> 2.4` |
| Soi khung thành phẩm hoặc cách cắt ô mặt | `tools/short-khung.sh "<dự án>" lat / crop ...` |
| Đặt short đạt vào thư mục thành phẩm | `tools/short-chot.sh` |

## 1. Bố cục và thông số

- `assemble.py` (r10 trở lên): `"layout": "mat-tren"` chỉ dùng với khung `doc` (1080x1920). Ô mặt cao `paneH` (mặc định 960 px, tỉ lệ 1,125), phần còn lại là `nen` (màu giấy) để overlay webm của cảnh vẽ lên. Các trường của segment: `cropFocus` (vị trí ngang của cửa sổ cắt, 0-1), `cropFocusY`, `cropZoom` (thu hẹp cửa sổ cắt).
- Bản ghi Zoom có tên người dự ở mép dưới khung: `cropZoom` 1,12 với `cropFocus` 0,45 và `cropFocusY` 0 đưa tên ra ngoài mép mà đầu vẫn còn khoảng thở. Mỗi nguồn khác nhau: soi bằng `tools/short-khung.sh "<dự án>" crop <focus> <zoom> <ba mốc trở lên>` trên nhiều tư thế (đang cử chỉ tay, ngả người) trước khi chốt, giá trị chốt ghi vào `spec.json` (`focus`, `zoom`) và dùng chung cả loạt.
- Cấu hình dự án (tuỳ chọn) ở `clip-ngan/short.json`: nguồn, nền, nhạc, đường dẫn intro, outro, bảng tên, font phụ đề; thiếu khoá nào dùng mặc định trong `tools/short-dung.py`.
- Gỡ băng làm một lần bằng `tools/moc-tu.py` (mốc âm tiết `<kd>.tu.json`, năng lượng `<kd>.nang-luong.bin`). Nếu `<kd>` là khúc cắt từ file dài, mốc lệch của khúc ghi ở `transcript/off.json` trong hồ sơ dự án. Không để file này trong thư mục tạm: dọn dự án sẽ mất nó, và dựng lại một short sau đó phải đo lại mốc lệch bằng cách đối chiếu đường năng lượng của khúc với âm thanh toàn buổi.

## 2. Quy trình từng short

1. **Chốt danh sách** (chốt duyệt số 1, theo `SKILL.md` Bước 1): slug, mốc nguồn, hook, ý chính. Chờ người dùng chọn.
2. **Viết `clip-ngan/<slug>/spec.json`** (thường sinh bằng một script `mk-spec.py` nhỏ cạnh nó): `kd`, `tieu_de`, `focus`, `zoom`, `paneH`, `hook` (một đoạn `[A,B]` hoặc nhiều), `parts` (các đoạn thân, A là đầu âm tiết đầu, B là cuối âm tiết cuối, giây nguồn), `cues` (phụ đề `[a,b,"chữ"]` theo giây nguồn), `scene` và `hook_scene` (các phần tử cảnh, mục 4). Dùng `tools/short-soi.py tu` để lấy mốc âm tiết, `lv3` để đọc lời, `chu` để chọn chữ khi hai cách nghe khác nhau.
3. **Chốt mép cắt** (mục 3), rồi `python3 tools/short-dung.py snap <slug> --du-an "<dự án>"`: in từng đoạn kèm cờ "NĂNG LƯỢNG CAO ở mép cắt" nếu còn cắt giữa tiếng.
4. **Sinh và chụp cảnh**: `python3 tools/short-canh.py <slug> --du-an "<dự án>"`, stage thư mục cảnh của short lên sandbox, `bash tools/short-render-canh.sh <canh> <ra> 2`, nhìn contact sheet (`canh.mjs người dùng`) rồi commit từng webm về `clip-ngan/<slug>/do-hoa/doc/` trên máy.
5. **Dựng và xuất**: `EP=1 bash tools/short-xuat.sh "<dự án>" <slug> 2.4` (EP=1 sau khi webm mới về; lần đầu hết 170 giây thì chạy lại đúng lệnh). Lệnh tự chạy phụ đề (`short-dung.py ass`), đốt phụ đề, nén, chỉnh âm lượng và nghiệm thu. Phải ĐẠT.
6. **Soi khung** bằng `tools/short-khung.sh "<dự án>" lat <slug> <t1> <t2> <t3> ...` ở: khung đầu (hook), lúc bảng tên và cảnh cùng có mặt, khung cuối cảnh, mối nối hook và intro, cue dài nhất, chữ cuối. Nhìn ảnh, không chỉ đọc số.
7. **Gói đăng tải** theo `skills/phim-dang-tai/SKILL.md` (mục 5 dưới đây), rồi `bash tools/short-chot.sh` đưa vào `Thanh pham/<dự án>/Short NN <slug>/`.
8. **Sau khi người dùng nói "duyệt"**: giao trọn gói, dọn, cập nhật hồ sơ theo `CLAUDE.md` quy tắc 11, 12.

## 3. Điểm cắt: chỉ cắt ở quãng lặng thật

- `short-dung.py snap` đặt mép vào gần âm tiết rồi dời về chỗ lõm năng lượng gần nhất (không quá 0,6 giây và không vượt sang âm tiết bên cạnh) nếu mép rơi giữa tiếng (cao hơn sàn ồn 14 dB). Việc này đúng cho đa số mép; mép nào vẫn báo năng lượng cao thì chọn tay.
- Chọn tay bằng `short-soi.py lang <kd> A B`: đầu đoạn đặt ở mẫu lặng CUỐI CÙNG trước từ đầu, cuối đoạn đặt ở mẫu lặng ĐẦU TIÊN sau từ cuối cộng 0,02 giây. Không cắt giữa quãng nói liên tục (không có mẫu lặng): bỏ cả đoạn ngắn đó hoặc mở rộng tới câu có chỗ nghỉ. Mốc tuyệt đối đã chọn truyền cho `one(..., exact=True)` trong `short-dung.py` (tham số thứ năm của một phần tử `parts` là cờ này khi viết `[A,B,lead,tail,true]`).
- Phần thân đầu tiên phải dài tối thiểu khoảng 4,7 giây mới có đủ nhịp: bảng tên hiện ở 0,3 giây, cảnh vào ở 4,7 giây; ngắn hơn thì cảnh của phần đó không có (`short-canh.py` bỏ mọi cảnh còn dưới 0,5 giây), và nếu cần đẩy cảnh sớm hơn thì đặt `part0_at` trong `spec.json`.
- Hook ngắn 3-10 giây, intro khoảng 3 giây, rồi thân; outro khoảng 6,5 giây. Chi tiết nhịp và LowerThird: `SKILL.md` Bước 2.

## 4. Viết cảnh (dữ liệu, không viết HTML)

Mỗi cảnh là danh sách phần tử trong `spec.json` (`scene.items`), mốc `at`, `out` viết theo giây NGUỒN; `short-canh.py` đổi sang đồng hồ cảnh theo các đoạn đã chốt. Khung vẽ là 985x520 đơn vị, thẻ chiếm phần dưới trên nền giấy.

- Loại phần tử: `dot` (nút tròn; `person: true` vẽ hình người; `below` là nhãn dưới nút, nằm khoảng bán kính cộng 34 đơn vị dưới tâm), `link` (nối hai nút theo `id`, `dash`, `pulse`), `chip` (viên chữ, `solid` là nền đặc), `text` (chữ lớn, `ink`, `wt`), `path` (nét vẽ dần, `head` có mũi tên), `ring` (vòng xung quanh một nút theo các mốc `t`), `rect` (khung nhóm). Vai màu: `chinh`, `ketqua`, `tot`, `xau`, `khac`, `mo`, `chu`, `trang`. `caps` là chú thích dưới đáy thẻ, `side` là chữ phụ bên phải hàng tiêu đề, `card` là mốc thẻ hiện (phần thân đầu mới đặt).
- Cỡ chữ: chip 28-36, chữ lớn của hook 44; dưới 28 không đọc được khi lướt điện thoại. Chip dài đặt giữa (x khoảng 490), chip ngắn dồn sang hai bên.
- **Chip va nhãn nút:** nhãn `below` của nút chiếm dải dưới nút, và một nút đã đổi chỗ (`mv`) mang nhãn theo; chip đặt gần đó thì dời chỗ (đổi y hay lệch x) trước khi chụp. Soi bằng contact sheet ở ba mốc: lúc phần tử vừa vào, lúc đầy nhất, lúc sắp ra.
- Một chủ thể xuyên suốt biến hình theo lời, ví dụ lấy đúng của người nói; nguyên lý ở `references/clip-co-minh-hoa.md` mục 3.
- Cảnh phát lại sự kiện trước nó khi thân ghép từ nhiều đoạn, nên mỗi đoạn có file cảnh riêng nhưng liền mạch (`short-canh.py` lo việc này khi bạn viết mốc theo giây nguồn).

## 5. Phụ đề, âm thanh, đăng tải

- Phụ đề `.ass` 1080x1920, font DejaVu Sans 54 đậm, cách đáy 110 px; trong cửa sổ bảng tên (0,3 đến 4,6 giây của phần thân đầu) dùng kiểu `Raised` cách đáy 230 px để không đè bảng tên; cue vắt qua mép cửa sổ này được tách thành hai dòng thoại (phần sau hạ về kiểu thường để khỏi đè chữ của cảnh). Mỗi dòng không quá 31 ký tự, tối đa hai dòng; `short-dung.py ass` báo `DÒNG DÀI` và cue ngoài mọi đoạn.
- Nhạc `xuong-guitar-am` chế độ `full`, duck, `gainDb` -23; chuỗi nén và `volume` trong `short-xuat.sh` với VOL 2.4 cho khoảng -13,5 đến -14 LUFS, true peak dưới -1 dB.
- Gói đăng tải mỗi short: ba tiêu đề, mô tả YouTube kết bằng một câu hỏi mở, status Facebook, thumbnail ngang (`chia-doi`) và thumbnail dọc. Chữ thumbnail ngang phải qua cổng 110 px (dọc 95 px): dòng dài nhất khoảng 8-10 ký tự, chia ba dòng ("3 phút / mỗi ngày / cho mình"); `tools/chon-khung-thumbnail.py` chọn khung, `tools/dang-tai.py job` ghi job, `render-do-hoa.mjs` chụp ở sandbox, `dang-tai.py kiem` kiểm. Chữ công khai (tiêu đề, mô tả, thumbnail) tránh ngày tháng, giá tiền, tên thương hiệu và mốc thời gian tương đối ("hôm qua", "tuần trước") vì sẽ cũ hoặc gán sai; những chi tiết đó có trong lời thì giữ trong lời và ghi vào `ghi_chu_kiem` cho người dùng. Chức danh người nói theo `phong-cach/PHONG-CACH.md`; các short đăng sau phim dài của cùng buổi.

## 6. Máy, sandbox và những bẫy đã gặp

- Sandbox có 2 CPU: chụp cảnh hai tiến trình một lúc là nhanh nhất; chụp hai short song song chỉ làm cả hai chậm.
- Sau mỗi lượt chụp, commit webm về máy rồi kiểm md5 hai đầu; lượt commit ĐẦU TIÊN ngay sau khi chụp từng ghi file cũ, commit lại (force) và so lại. Thumbnail `.jpg` sau commit có md5 khác nhưng điểm ảnh y hệt: so bằng điểm ảnh.
- Tiến trình nền trên máy chết khi lệnh trả về, mọi lệnh đều chạy ở tiền cảnh và dưới 180 giây: `short-xuat.sh` có timeout 170 giây, chạy lại tới khi xong.
- `fr.sh` kiểu xstack lỗi khi chỉ có một hai mốc: `short-khung.sh lat` đòi ít nhất ba mốc.
- Dựng lại một short sau khi dọn dự án: nguồn quay đã chuyển sang ổ lưu trữ (`CLAUDE.md` quy tắc 12), nên tạo liên kết `nguon/mat.mp4` trỏ tới file Zoom gốc (`ln -s`; dùng được ngay với `assemble.py`, không cần chép), dựng, rồi chuyển liên kết vào `Du an/_tam/_to_delete/`.
- Chạy lại `snap` trên short cũ chỉ để kiểm công cụ thì lưu bản sao các file snap, timeline, cues, spec-gen và phụ đề `.ass` của short trước rồi trả lại: bản đã duyệt có thể đã chỉnh tay hơn kết quả máy.
