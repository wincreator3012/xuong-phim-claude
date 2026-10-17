# Kỹ thuật động cơ slideshow ảnh

Công cụ: `tools/slideshow-anh/` (`run.py` là bộ lệnh, `engine.py` là động cơ, `tools/slideshow-anh/fonts/` gồm Cormorant Garamond và Great Vibes theo giấy phép OFL, `tools/slideshow-anh/mau/` là mẫu hồ sơ). Phụ thuộc: Python 3, numpy, OpenCV (có `FaceDetectorYN`), Pillow, ffmpeg có libx264, model `tools/models/face_detection_yunet_2023mar.onnx` (OpenCV Zoo; thiếu thì `faces` báo rõ).

## Hồ sơ dự án

```
Du an/<dự án>/slideshow/spec.py          cốt truyện: SEQ, REMOVED, TARGET, build()
Du an/<dự án>/slideshow/slideshow.json   nguồn ảnh, bảng màu, focus_override, denoise, các thẻ chữ
Du an/<dự án>/.tam/                       nháp: faces.json, sheets, stills, review, chunks, qc (dọn khi duyệt)
```

`slideshow.json`:

| Khoá | Ý nghĩa |
|---|---|
| `nguon` | thư mục ảnh, tuyệt đối hoặc tương đối với thư mục dự án (`SLIDE_SRC` ghi đè) |
| `palette` | `ivory`, `ivory_hi`, `gold`, `ink`, `frame`, `warmwhite` (mã màu RGB dạng `#RRGGBB`) |
| `focus_override` | `"<số hoặc tên ảnh>": [tâm x, tâm y, nửa rộng, nửa cao]` theo tỉ lệ ảnh |
| `denoise` | danh sách ảnh cần khử nhiễu thay vì làm nét |
| `cards` | các thẻ chữ (mục 5 của `cot-truyen-va-chuyen-canh.md`) |

`spec.py` dùng `S(ids, hold, tr, ...)`, `BURST(i, hold, tr)`, `build_timeline(SEQ, TARGET)` của động cơ. `ids` là số thứ tự (trên bảng ảnh) hoặc tên tệp. Một cảnh có 1 ảnh (bìa hay khung tuỳ tỉ lệ; ép bằng `mode='cover'|'tile'`), 2-3 ảnh (khung đặt cạnh nhau, ảnh sau hiện trễ) hay 4 ảnh (lưới 2x2). Thông số `mood='mono'` cho nền tối, `kb=...` cho kiểu zoom, `tr` là chuyển cảnh vào cảnh này (`(tên, giây)` để ghi đè thời gian).

## Cách động cơ chạy

- Mỗi khung hình là một mảng numpy BGR 1920x1080, truyền thẳng vào ffmpeg qua ống (libx264, CRF 17, `stillimage`, keyint 60, bt709, `-an`). Không có tiến trình nền: chạy tuần tự trong một đoạn 300 khung.
- Ảnh được phóng lớn trước một lần bằng Lanczos kèm làm nét nhẹ (`prep`), rồi mỗi khung chỉ `warpAffine` (cubic) theo trạng thái zoom và tâm. Nhờ vậy khung nào cũng tương đương một lần lấy mẫu từ ảnh gốc, không lặp lại làm mờ.
- Thời gian là mô hình ô (`Timeline`): mỗi cảnh có giờ vào `a[i]`, cảnh được dựng từ `a[i] - T_vào/2` đến `a[i] + giữ + T_ra/2`; trong vùng chồng hai cảnh, hàm chuyển cảnh (`tr_*`) nhận hai khung và `p` từ 0 đến 1. Tiến độ zoom của cảnh tính trên cả khoảng nó hiện, nên không giật ở chỗ nối.
- Thẻ chữ được vẽ bằng Pillow thành mặt nạ một lần rồi trộn từng khung (mờ hiện hoặc quét từ trái qua), kèm hạt vàng trôi và đường kẻ.
- `render` mở các tiến trình con `run.py <dự án> chunk <k>`: mỗi tiến trình dựng lại `build()` (nhẹ) rồi chỉ dựng khung của đoạn mình. Tệp ghi `.part.mp4` rồi đổi tên, nên đoạn nào có tệp chính thức là xong.

## Giới hạn máy và thời gian đo thật

- Máy ảo của người dùng: 3-4 GB RAM, mỗi lượt gọi 180 giây (đặt `timeout` của công cụ 120000 ms và dùng `timeout 112` quanh lệnh với ngân sách 95 giây cho an toàn), không giữ tiến trình nền. Bốn tiến trình song song là mức hợp; mỗi đoạn 10 giây mất khoảng 25 đến 40 giây (cảnh nặng như chuyển `focus` và `heart` thì lâu hơn). Phim 10 phút 60 đoạn xong trong khoảng 8 lượt, tệp khoảng 700 MB.
- Máy ảo không cho xoá tệp khi chưa xin quyền: `render` vì vậy không dọn `.part.mp4` cũ mà ghi đè lên. Muốn dọn thì xin quyền xoá (xem `duyet.py`).
- Cắt ngang một lượt `render` (hết giờ) là bình thường: gọi lại y nguyên.

## Kiểm bằng mắt, theo thứ tự

1. `plan`: tổng thời lượng đúng mục tiêu, không THIẾU hay TRÙNG, giữ hình rõ ngắn nhất từ 2,5 giây.
2. `review`: nhìn từng bảng (mặt có nguyên không, ảnh nào bị zoom lệch, chữ có chạm viền không).
3. `strip` cho những chuyển cảnh lạ (`doors`, `heart`, `sweep`): tìm vệt đen, vạch lạ, khung trắng loé.
4. `still` ở các mốc chữ của thẻ.
5. Sau khi ghép: `qc` rồi mở `.tam/qc/qc.jpg`.

## Lỗi và cách sửa đã gặp

- **Ảnh dọc vào bìa làm cắt mặt:** đừng ép `mode='cover'` cho ảnh dọc; để mặc định (khung có viền).
- **Zoom lệch khỏi người vì không nhận ra mặt** (ảnh ngược sáng, ảnh chụp lưng, đen trắng nhiều hạt): `focus_override`.
- **Vạch tối ở đầu chuyển `doors`:** đã sửa bằng cách làm bóng khe hiện dần (`min(1, off/40)`); nếu viết chuyển cảnh mới có khe hay mép, làm hiện dần như vậy.
- **`smooth()` nhận mảng:** hàm nội suy trong động cơ nhận số, không nhận mảng; chuyển cảnh theo từng điểm ảnh phải viết lại bằng numpy (xem `tr_sweep`).
- **Stage ảnh thử báo không có tệp:** tên ảnh thử có dạng `t0002.50.jpg` (`t%07.2f`: số giây rộng bảy ký tự kể cả dấu chấm), liệt kê thư mục `.tam/stills/` trước khi stage thay vì đoán tên.
- **Bỏ hoặc thêm ảnh sau khi đã render:** mọi đoạn hết giá trị (hệ số thời gian đổi). `mv .tam/chunks .tam/old/` rồi render lại.

## Thêm hiệu ứng chuyển cảnh mới

Viết `tr_<tên>(A, B, p, c)` trong `engine.py` (A là khung cảnh cũ, B là khung cảnh mới, `p` từ 0 đến 1, `c` có `dir` luân phiên và `focus` là toạ độ mặt chủ thể của cảnh mới), thêm vào `TRANS` kèm thời gian mặc định, chạy `strip` để nhìn sáu khung. Giữ nguyên nguyên tắc: đầu `p=0` phải giống hệt A và cuối `p=1` giống hệt B (kiểm bằng `still` ở hai mốc), và không để một khung nào trắng hoặc đen hoàn toàn trừ khi chủ đích. Chuyển cảnh viết xong phải thêm vào bảng mục 4 của `cot-truyen-va-chuyen-canh.md`.
