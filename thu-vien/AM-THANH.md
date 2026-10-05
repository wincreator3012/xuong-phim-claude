# Thư viện âm thanh: danh mục theo mức tin cậy bản quyền

Repo không chứa file nhạc (để nhẹ và để tôn trọng điều khoản phân phối lại). Có hai đường: tự soạn nhạc riêng bằng `python3 tools/soan-nhac.py` (đảm bảo nhất, xem ngay dưới), hoặc tải từ danh mục các track dùng được thương mại trên mọi nền tảng.

## Mức tin cậy bản quyền: đọc trước khi chọn nhạc

Content ID dò dấu vân âm thanh, không đọc giấy phép, và một track miễn phí có thể được đăng ký sau khi bạn tải về. Nhãn "không đăng ký Content ID" trên trang nguồn chỉ đúng tại lúc nhìn: một track Pixabay không nhãn từng bị nhà phân phối thứ ba đăng ký, khiến một Short dùng nó làm nhạc nền chạy suốt bị YouTube chặn toàn cầu. Vì vậy:

1. **Nhạc riêng (đảm bảo nhất).** `python3 tools/soan-nhac.py --danh-sach` liệt kê bốn bản (guitar mộc, piano trầm, nền thiền, sáng nhẹ); `python3 tools/soan-nhac.py <tên> --ra nhac-nen/<nhóm>` tổng hợp ra file mp3 chuẩn -15 LUFS bằng code, không dùng mẫu thu hay nhạc của ai nên không ai đăng ký Content ID được. `--hieu-ung` soạn bộ whoosh, chuông, pop. Đặt tên thêm hậu tố `_xuong-rieng` rồi chạy `nhap-am-thanh.py`. Nghe thử một lượt trước khi dùng; đừng đưa các bản này lên dịch vụ phát hành nhạc hay Content ID.
2. **Kevin MacLeod (CC BY 4.0).** Rủi ro thấp đến vừa, có đường gỡ rõ: ghi công đúng, kháng nghị, biểu mẫu gỡ hàng loạt của tác giả.
3. **Pixabay.** Dùng sau khi đăng bản riêng tư lên YouTube và mục Bản quyền của YouTube Studio báo sạch.
4. **Track đã bị claim**: thêm tên file vào `nhac-nen/CAM-DUNG.json` (`{"cam": {"<tên file>": "lý do"}}`); `assemble.py` báo lỗi khi timeline dùng track đó.

Trước khi đăng một lô clip mới, đăng một bản riêng tư và đọc mục Bản quyền.

## Cách tải (Claude làm, bạn chỉ bấm khi được nhờ)

1. `python3 tools/tai-chat-lieu.py --mau <tên mẫu phong cách>` in ra danh sách track hợp mẫu đó và tự tải những track có link tải thẳng (Kevin MacLeod) nếu mạng cho phép
2. Track Pixabay phải tải qua trình duyệt (trang yêu cầu bấm nút "Free download"). Claude mở từng trang bằng trình duyệt (Claude in Chrome hoặc trình duyệt tích hợp), bấm tải, chờ 6-8 giây rồi mới sang trang kế; nếu không có trình duyệt, Claude gửi bạn danh sách link để bấm, file về thư mục Downloads
3. Claude chuyển file vào đúng nhóm `nhac-nen/<nhóm>/` hoặc `hieu-ung/<nhóm>/`, đặt tên theo mẫu `<mô-tả>_<tác-giả>_<nguồn-id>.mp3`, rồi chạy `python3 tools/nhap-am-thanh.py` để đo LUFS và ghi `nhac-nen/THU-VIEN.md`

Không cần đủ 15 track mới dùng được: hai track đúng mẫu phong cách (một cho intro/outro, một chạy nền) là đủ cho hầu hết clip.

## Hai loại giấy phép

**Pixabay Content License** (file có đuôi `_pixabay-<id>`): dùng thương mại mọi nền tảng, không cần ghi công, không được bán lại file nhạc như sản phẩm độc lập. Giữ nguyên id trong tên file để tra ngược. Nếu gặp khiếu nại hiếm gặp: tạo tài khoản Pixabay miễn phí, tải lại track một lần để lấy chứng chỉ giấy phép [license certificate], nộp kèm đơn phản đối.

**CC BY 4.0, Kevin MacLeod** (file có đuôi `_macleod_ccby`): dùng thương mại mọi nền tảng, bắt buộc ghi công. Claude tự thêm dòng sau vào mô tả video mỗi khi dùng:

    Music: "<Tên track gốc>" - Kevin MacLeod (incompetech.com)
    Licensed under Creative Commons: By Attribution 4.0 - https://creativecommons.org/licenses/by/4.0/

## Nhạc nền theo nhóm công dụng

`gainDb` là giá trị đặt trong `timeline.json`: `full` khi nhạc chạy suốt dưới lời nói, `bookends` khi chỉ ở intro/outro (để to hơn). Số này đã tính từ LUFS gốc để mọi track nghe đều nhau; `nhap-am-thanh.py` sẽ đo lại trên file thật của bạn.

### thien-ambient: nền thiền, thực hành, bài giảng chiêm nghiệm (mẫu tinh-lang, hoc-thuat)

| File | Track gốc, tác giả | Dài | gainDb full / bookends | Giấy phép |
|---|---|---|---|---|
| thien-bed-dai_verclub_pixabay-550885 | Meditation Music, Verclub_Music | 8:43 | -14 / -6 | Pixabay |
| thien-bed-rat-dai_natureseye_pixabay-7618 | Autumn Sky Meditation, NaturesEye | 16:15 | -14 / -6 | Pixabay |
| thien-sao-truc_miromax_pixabay-455457 | Meditation Flute, MiroMaxMusic | 4:32 | -20 / -12 | Pixabay |
| thien-zen-moment_macleod_ccby | That Zen Moment, Kevin MacLeod | 10:02 | -11 / -3 | CC-BY |
| thien-impromptu-01/02/03_macleod_ccby | Meditation Impromptu 01-03, Kevin MacLeod | 3:33-4:15 | -7 / +1 | CC-BY |
| thien-ngan_prettyjohn_pixabay-495676 | Meditation, prettyjohn1 | 0:39 | -20 / -12 | Pixabay |

### piano-tinh-lang: piano trầm lắng, mở và kết bài giảng (mọi mẫu)

| File | Track gốc, tác giả | Dài | gainDb full / bookends | Giấy phép |
|---|---|---|---|---|
| piano-hy-vong_macleod_ccby | Dreams Become Real, Kevin MacLeod | 6:50 | -6 / +2 | CC-BY |
| piano-suy-tuong_macleod_ccby | Deliberate Thought, Kevin MacLeod | 2:58 | -12 / -4 | CC-BY |

### acoustic-am: guitar mộc ấm áp, clip quảng bá và kể chuyện (mẫu am-ap, hien-dai)

| File | Track gốc, tác giả | Dài | gainDb full / bookends | Giấy phép |
|---|---|---|---|---|
| acoustic-am-ap_macleod_ccby | Wholesome, Kevin MacLeod | 6:04 | -13 / -5 | CC-BY |
| acoustic-guitar-diu_moonpub_pixabay-506572 | Gentle acoustic guitar melody, Moonpub | 1:18 | -16 / -8 | Pixabay |

### nang-luong-nhe: sáng và nhẹ, Reels/Shorts (mẫu hien-dai)

| File | Track gốc, tác giả | Dài | gainDb full / bookends | Giấy phép |
|---|---|---|---|---|
| soft-piano-nhe_andriih_pixabay-579821 | Soft - Soft Music, andriih | 2:09 | -9 / -1 | Pixabay |

Nhóm này còn mỏng. Dùng `soan-nhac.py xuong-nhe-sang` cho nhịp nhanh; khi tìm thêm, ưu tiên nhạc riêng, rồi incompetech.com, rồi Pixabay (sau khi thử riêng tư).

### rieng: nhạc của chính bạn

Thả vào `nhac-nen/rieng/`, chạy `nhap-am-thanh.py`. Claude ghi chú "nhạc riêng của người dùng" và không kiểm định thêm. Bạn chịu trách nhiệm về quyền sử dụng.

## Hiệu ứng âm thanh

Whoosh chuyển cảnh và chuông mềm: soạn bằng `python3 tools/soan-nhac.py --hieu-ung --ra hieu-ung/<nhóm>` (không cần tải). Chuông xoay và pop dưới đây từ Pixabay (Content License, không cần ghi công).

Dùng tiết chế: không phải chuyển cảnh nào cũng cần tiếng, chỉ dùng khi nhấn có chủ đích. Mức trộn: hiệu ứng thấp hơn đỉnh lời nói khoảng 20-26 dB.

| Nhóm | File | Dài | Dùng khi |
|---|---|---|---|
| chuong-thien | chuong-xoay-go_freesound_pixabay-33366 | 14.8s | mở đầu thực hành |
| chuong-thien | chuong-xoay-eb_freesound_pixabay-38746 | 12.6s | điểm nhấn chiêm nghiệm |
| chuong-thien | chuong-xoay-ngan-dai_freesound_pixabay-55786 | 1:26 | kết bài thiền, fade tuỳ ý |
| nhan-do-hoa | pop-sach_dragon_pixabay-467466 | 1.6s | từng mục danh sách hiện |
| nhan-do-hoa | pop-nhe_humordome_pixabay-451232 | 5s | nhiều click nhẹ, cắt lấy đoạn cần |

Trang nguồn cụ thể của từng file nằm trong `am-thanh.json` (trường `trang`).

## Quy tắc bổ sung thư viện (cho Claude)

1. Nguồn ưu tiên: nhạc riêng (`soan-nhac.py`), rồi incompetech.com (CC-BY, thêm dòng ghi công), rồi Pixabay (nhãn trên trang không bảo đảm gì, thử riêng tư trước)
2. Tải qua trình duyệt: bấm "Free download", chờ 6-8 giây sau mỗi cú bấm rồi mới điều hướng tiếp (điều hướng sớm sẽ huỷ lượt tải)
3. Đặt tên `<mô-tả>_<tác-giả>_<nguồn-id>.mp3`, để vào đúng nhóm, chạy `nhap-am-thanh.py`
4. Không nhận nhạc không rõ nguồn; nhạc người dùng tự có thì để `nhac-nen/rieng/`
