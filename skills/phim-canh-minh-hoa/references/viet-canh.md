# Viết, soi, chụp và ghép một cảnh minh hoạ

Tài liệu kỹ thuật của skill phim-canh-minh-hoa: hợp đồng runtime, khung một file cảnh, bộ class của kit, lệnh, bốn kiểu chèn kèm mẫu timeline. Nguyên lý thiết kế ở `skills/phim-canh-minh-hoa/references/nguyen-ly-canh.md`.

## 1. Hợp đồng runtime và luật tất định

Kit ở `do-hoa-chung/canh-kit/`: `canh.js` (runtime), `canh.css` (hệ thiết kế), `do-hoa-chung/canh-kit/fonts/` (Be Vietnam Pro, JetBrains Mono, Lora, bản quyền OFL, đủ dấu tiếng Việt), `do-hoa-chung/canh-kit/mau/` (cảnh mẫu), `do-hoa-chung/canh-kit/phong-thu/` (khuôn trang xem thử). Cảnh không nhúng kit bằng tay: đặt dấu `<!-- canh-kit -->` trong `<head>`, `tools/canh.mjs` thay dấu đó bằng font, CSS, JS nhúng sẵn khi đóng gói, xem, chụp.

```js
CANH.canh({
  thoiLuong: 14,                       // giây; bằng đúng ô của cảnh trong timeline
  khung: ['ngang', 'doc'],             // khung cảnh này có bố cục
  chuanBi(K) { ... },                  // chạy MỘT lần sau khi font sẵn sàng: dựng path, đo chữ, đặt viewBox theo K.khung
  ve(t, K) { ... }                     // đặt trạng thái MỌI phần tử tại thời điểm t; không được phụ thuộc lần gọi trước
});
```

Luật tất định (bắt buộc; `canh.mjs kiem` bắt vi phạm): trạng thái chỉ là hàm của t. Không `Date`, không `Math.random` (dùng `K.hat(n)` có hạt), không `setTimeout`/`setInterval`, không CSS `transition`, không video hay GIF tự chạy, không biến cộng dồn qua các lần gọi `ve`. CSS `@keyframes` được phép: runtime dừng mọi animation và tua `currentTime` theo t.

Trợ giúp trong `K` (cũng có ở `CANH.*`):

| Tên | Làm gì |
|---|---|
| `p(t, batDau, dai=0.8, e=E.em)` | tiến độ 0-1 đã easing của một chuyển động |
| `pVaoRa(t, bd, kt, vao, ra)` | hiện ở bd, lui ở kt |
| `hien(el, x, {y, x, s, blur})` | mờ sang rõ, trồi, phóng nhẹ; x = 1 thì trả phần tử về tĩnh (để tua thẳng và chạy tuần tự ra cùng điểm ảnh) |
| `ve(path, x)` | vẽ nét SVG theo tiến độ |
| `diem(path, x)` | toạ độ điểm trên nét tại tiến độ x (cho chấm đi theo đường) |
| `dem(tu, den, x, le)` | số đếm dồn định dạng Việt (1.240; 3,5) |
| `go(chu, x)` | gõ chữ, an toàn với dấu tổ hợp |
| `song(t, chuKy, bien, pha)` | dao động đều (chuyển động sống nhỏ của chủ thể) |
| `hat(n)` | số giả ngẫu nhiên có hạt, 0-1 |
| `E.em`, `E.vaora`, `E.deu`, `E.ra` | easing: chữ ký xưởng, đi từ A sang B, đều, rời đi |
| `K.W`, `K.H`, `K.khung`, `K.theme`, `K.alpha`, `K.CHUP` | kích thước, khung, họ màu, nền trong suốt, đang chụp hay đang xem |

## 2. Khung một file cảnh

```html
<!doctype html>
<html lang="vi" data-theme="dem" data-khung="ngang">
<head>
<meta charset="utf-8">
<title>Tên cảnh ngắn</title>
<!-- canh-kit -->
<style>
  /* bố cục riêng từng khung: :root[data-khung='ngang'] ... / :root[data-khung='doc'] ... */
</style>
</head>
<body>
<div class="san">
  <!-- nội dung cảnh: .kicker, .tieu-de, .phu-de, .the + svg, .ket, .nguon, .o-pip ... -->
</div>
<script>
const M = {tieuDe: 0.5, soDo: 2.0, dinh: 7.1};   // mốc trong cảnh = mốc nguồn - mốc bắt đầu cảnh
CANH.canh({thoiLuong: 14, khung: ['ngang', 'doc'], chuanBi(K) {}, ve(t, K) {}});
</script>
</body>
</html>
```

Thuộc tính trên thẻ `html`: `data-theme` (`dem`, `than`, `giay`), `data-khung` (`ngang` 1920 x 1080, `doc` 1080 x 1920), `data-ben` (thẻ nổi: `phai`, `trai`), `data-pip` và `data-alpha` do công cụ đặt khi chụp. `.san` là khung video; đơn vị `--u` = 10,8 px ở cả hai khung.

Class của kit (định nghĩa trong `canh.css`): `.kicker`, `.tieu-de` (kèm `em` tô màu), `.phu-de`, `.ghi`, `.nguon`, `.so-lon`, `.ma` (mã có tô màu `.k .s .n .c`), `.the` (thẻ bo góc), `.o` (ô nhãn trong sơ đồ), `.chip`, `.nut-lon` (khối kết quả sáng), `.cau` (quả cầu phát sáng), `.phat-sang` (quầng cho nét SVG), `.dai-phim`, `.cua-so-web` (chỉ khi chủ đề nói về giao diện), `.vai-chinh .vai-ketqua .vai-tot .vai-xau .vai-khac` (gắn vai màu cho một khối), `.o-pip` (ô chừa chỗ người nói), `.an-khi-pip` (ẩn khi chụp kiểu thu vào góc). Màu luôn qua biến vai (`var(--c-tot)`...), không viết mã màu cứng trong cảnh.

## 3. Soi

Chạy trong sandbox, từ gốc xưởng đã stage (`tools/canh.mjs`, `do-hoa-chung/canh-kit/`, `du-an/<x>/canh/`). Cần Playwright (sandbox có sẵn bản cài toàn cục; thiếu thì `npm i -g playwright@1.56.0`, Chromium có sẵn ở `/opt/pw-browsers`).

```
node tools/canh.mjs kiem "du-an/<x>/canh/03-cua-so.html" [--khung doc] [--pip]
node tools/canh.mjs người dùng  "du-an/<x>/canh/03-cua-so.html" --t 1.5,4,7.2,11 --out-dir /tmp/soi-03 [--khung doc]
node tools/canh.mjs người dùng  "du-an/<x>/canh/04-tho-hop.html" --alpha --xem-tren /tmp/khung-0412.jpg --t 6
node tools/canh.mjs phong-thu "du-an/<x>/canh/03-cua-so.html" --out /tmp/phong-thu-03.html [--nen-anh <khung.jpg>]
```

- `kiem`: tua thẳng tới ba mốc phải ra cùng ảnh như chạy tuần tự tới đó; lệch dưới 40 dB là lỗi thật, lệch nhẹ hơn là khử răng cưa của chữ đang chuyển động (vẫn ĐẠT).
- `người dùng`: ảnh tĩnh từng mốc + `contact-sheet.jpg`; xem bằng Read. Mốc nên là đầu mỗi cảnh con và trạng thái cuối.
- `--xem-tren`: đặt một khung hình thật (rõ, không mờ) dưới thẻ nổi để soi có che mặt không. Chỉ dùng để soi, lệnh `chup` từ chối cờ này.
- `phong-thu`: trang tự chứa để đăng bằng Artifact; người dùng xem cảnh chạy thật, đổi họ màu, khung, cách chèn (nút nền mờ chỉ hiện khi có `--nen-anh`, nút chừa góc chỉ hiện khi cảnh có `.o-pip`).

## 4. Chụp

```
node tools/canh.mjs chup "<cảnh>.html" --out "du-an/<x>/do-hoa/ngang/canh-03-cua-so.mp4"                      # toàn khung
node tools/canh.mjs chup "<cảnh>.html" --nen-anh "<khung.jpg>" --out ".../canh-03-cua-so-nen.mp4"                 # nền mờ
node tools/canh.mjs chup "<cảnh>.html" --alpha --out ".../canh-04-tho-hop.webm"                                   # thẻ nổi
node tools/canh.mjs chup "<cảnh>.html" --pip --out ".../canh-05-vong-lap-pip-nen.mp4"                             # chừa góc
   [--khung doc] [--theme than] [--fps 30] [--luong 2] [--tu <giây> --den <giây>] [--lam-lai]
```

- Công cụ chụp song song theo số luồng (mặc định 2 trong sandbox 2 lõi), nền đặc chụp JPEG chất lượng 95 rồi H.264 CRF 17; nền trong suốt chụp PNG rồi VP8 `yuva420p` (cùng cách `render-do-hoa.mjs` làm cho đồ họa alpha). Đo thật: cảnh 15 giây 1080p nền đặc chụp khoảng 35 giây; 1 giây alpha khoảng 5 giây.
- Ghi `do-hoa-manifest.json` cạnh file ra (thời lượng đo, fps, alpha, dấu vân tay nội dung; kiểu chừa góc thêm mục `pip` là toạ độ ô). Cảnh đã chụp đúng nội dung thì bỏ qua; `--lam-lai` để ép.
- `--tu`/`--den` chụp một đoạn để thử; bản dùng thật luôn chụp cả cảnh.

## 5. Bốn kiểu chèn và mẫu timeline

Nhắc lại hai hệ mốc (`skills/_chung/timeline-va-dung.md`): `broll.at` là mốc TRONG FILE NGUỒN; `overlay.at` tương đối từ `in` của đoạn. Overlay chỉ hiện ở quãng trước B-roll đầu tiên của đoạn.

**Toàn khung thay hình.** Cảnh mp4 vào `broll` của đoạn quay đang chứa lời giải thích; tiếng anh đi liền từ nguồn.

```json
{"type": "video", "src": "nguon/bai.mp4", "in": 812.4, "out": 905.0, "snap": true,
 "broll": [{"src": "do-hoa/ngang/canh-03-cua-so.mp4", "at": 840.2, "duration": 15.0, "from": 0}]}
```

**Nền là khung hình mờ.** Trên máy lấy khung ngay trước lúc cảnh bắt đầu, stage ảnh đó lên sandbox, chụp với `--nen-anh`, rồi ghép như toàn khung.

```
python3 tools/canh-ghep.py khung "du-an/<x>/nguon/bai.mp4" --at 840.0 --out "du-an/<x>/canh/nen/khung-0840.jpg"
```

Ảnh nền đi qua lớp mờ và phủ tối của kit (`.nen-anh`, `.nen-phu`), nên chỉ còn là màu và khối của căn phòng. Cảnh nền mờ thường bỏ tiêu đề lớn (người dùng đang nói), giữ sơ đồ và dòng đọng.

**Thẻ nổi cạnh người nói.** Chụp `--alpha`, ghép bằng `overlay` trên chính đoạn quay; chọn `data-ben` theo khung hình thật và soi `--xem-tren` trước.

```json
{"type": "video", "src": "nguon/bai.mp4", "in": 1203.0, "out": 1260.5, "snap": true,
 "overlay": [{"src": "do-hoa/ngang/canh-04-tho-hop.webm", "at": 14.6}]}
```

**Thân bị rút ngắn sau khi đã chụp cảnh (cảnh dài hơn ô còn lại).** Thêm `duration` (độ dài mong muốn, giây) và `giu` (mốc trong file overlay để giữ khung rồi bớt, nên chọn lúc cảnh đã lắng cuối) vào overlay; công cụ bớt ở quanh `giu` mà không chạm hoạt cảnh kết (tối đa tới `n - giu - 0,2` giây). Ví dụ cảnh 37,5 giây vào ô 36,46 giây: `{"src": "...canh-01.webm", "at": 4.7, "duration": 36.46, "giu": 36.2}`. Soi khung cuối sau khi dựng lại để chắc cảnh còn ở trạng thái đầy đủ.

**Người nói thu vào góc.** Chụp `--pip` (cảnh hiện ô `.o-pip`, manifest ghi toạ độ ô), commit về máy, rồi trên máy đặt đoạn quay thật vào ô; clip ra (không tiếng) vào `broll` với cùng `at`.

```
python3 tools/canh-ghep.py pip "du-an/<x>/do-hoa/ngang/canh-05-vong-lap-pip-nen.mp4" "du-an/<x>/nguon/bai.mp4" \
  --at 1502.0 --out "du-an/<x>/do-hoa/ngang/canh-05-vong-lap-pip.mp4" [--tieu-diem 0.45] [--tieu-diem-y 0.4]
```

```json
"broll": [{"src": "do-hoa/ngang/canh-05-vong-lap-pip.mp4", "at": 1502.0, "duration": 18.0, "from": 0}]
```

`--at` của `canh-ghep.py pip` phải bằng `broll.at`, nếu không hình trong ô lệch tiếng. `--tieu-diem` là tâm cắt theo chiều ngang của nguồn (0-1), đặt vào giữa mặt người dùng; kiểm bằng một khung trích từ clip ra. Nguồn nhiều góc máy: dùng đúng góc đang lên hình ở mốc đó. Ô hiện dần 0,35 giây ở đầu cảnh (`--vao`).

## 6. Hỏng thường gặp

| Dấu hiệu | Nguyên nhân | Sửa |
|---|---|---|
| `kiem` báo lệch dưới 40 dB | trạng thái cộng dồn, ngẫu nhiên, transition | viết lại thành hàm của t |
| Chữ nhảy khác nhau giữa ảnh soi và video | chữ ở trạng thái lắng vẫn giữ transform | dùng `hien` (tự trả phần tử về tĩnh khi x = 1) |
| Cảnh treo "không báo sẵn sàng" | lỗi JavaScript, thiếu `CANH.canh(...)` | `dong-goi` ra file, mở xem lỗi trong log của lệnh |
| Chữ Việt hiện font dự phòng | font chưa nạp hoặc tên họ font sai | chỉ dùng họ có trong `do-hoa-chung/canh-kit/fonts/fonts.css`; runtime chờ `document.fonts.ready` |
| Clip thu vào góc lệch ô hay méo | chụp thiếu `--pip`, hoặc nguồn khác tỉ lệ | chụp lại với `--pip`, hoặc truyền `--o x,y,w,h,r` |
| Scale hoặc toạ độ ra NaN ở vài mốc | hàm dựng khối trả về đối tượng thiếu trường (ví dụ mất `tick`, `tLab` của một dòng) rồi `ve()` đọc trường đó | trả đủ mọi trường mà `ve()` dùng; kiểm bằng `canh.mjs người dùng` ở mốc có mục đó |
| Hai dấu kiểm hay nhãn đè nhau | đặt theo toạ độ ước lượng, không đo | đo bề rộng chữ trong `chuanBi` rồi xếp theo số đo; dàn hàng với khoảng cách cố định |
| Webm alpha ra nền đặc che mặt | theme đặt `--nen` đè lên chế độ trong suốt | thêm `:root[data-theme='...'][data-alpha='1'] { --nen: transparent }`; luôn kiểm bằng khung ghép thật |
| Thẻ nổi che mặt ở trạng thái đầy đủ | chọn bên theo khung đầu đoạn | soi `--xem-tren` ở khung có người nói lệch nhất trong đoạn, đổi `data-ben` |
