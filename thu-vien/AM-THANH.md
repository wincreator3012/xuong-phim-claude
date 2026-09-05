# Thư viện âm thanh: danh mục đã kiểm định bản quyền

Repo không chứa file nhạc (để nhẹ và để tôn trọng điều khoản phân phối lại). Thay vào đó, đây là danh mục 15 track nhạc nền và 10 hiệu ứng đã được kiểm từng trang nguồn, dùng được trên mọi nền tảng (YouTube, Facebook, Instagram, TikTok) cho mục đích thương mại và KHÔNG đăng ký Content ID (track có nhãn "Content ID Registered" trên Pixabay bị loại dù được phép dùng, vì sẽ gây khiếu nại tự động). Bản máy đọc: `am-thanh.json`. Sau khi tải về, danh mục thật của máy bạn (có LUFS đo thật) nằm ở `nhac-nen/THU-VIEN.md`.

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
| acoustic-cam-xuc_universfield_pixabay-232913 | Sentimental Acoustic Tune, Universfield | 1:39 | -15 / -7 | Pixabay |
| acoustic-guitar-diu_moonpub_pixabay-506572 | Gentle acoustic guitar melody, Moonpub | 1:18 | -16 / -8 | Pixabay |
| acoustic-stinger-30s_universfield_pixabay-239071 | Relaxing Acoustic Guitar 30s, Universfield | 0:30 | -14 / -6 | Pixabay |

### nang-luong-nhe: sáng và nhẹ, Reels/Shorts (mẫu hien-dai)

| File | Track gốc, tác giả | Dài | gainDb full / bookends | Giấy phép |
|---|---|---|---|---|
| soft-piano-nhe_andriih_pixabay-579821 | Soft - Soft Music, andriih | 2:09 | -9 / -1 | Pixabay |

Nhóm này còn mỏng. Khi tìm thêm, ưu tiên Pixabay (kiểm không có Content ID) rồi incompetech.com.

### rieng: nhạc của chính bạn

Thả vào `nhac-nen/rieng/`, chạy `nhap-am-thanh.py`. Claude ghi chú "nhạc riêng của người dùng" và không kiểm định thêm. Bạn chịu trách nhiệm về quyền sử dụng.

## Hiệu ứng âm thanh (tất cả Pixabay, không cần ghi công)

Dùng tiết chế: không phải chuyển cảnh nào cũng cần tiếng, chỉ dùng khi nhấn có chủ đích. Mức trộn: hiệu ứng thấp hơn đỉnh lời nói khoảng 20-26 dB.

| Nhóm | File | Dài | Dùng khi |
|---|---|---|---|
| chuyen-canh | whoosh-manh_universfield_pixabay-352756 | 1.6s | mặc định cho thẻ chuyển phần |
| chuyen-canh | whoosh-cham_universfield_pixabay-567191 | 3.1s | chuyển phần lớn |
| chuyen-canh | whoosh-nhanh_universfield_pixabay-352855 | 1.2s | nhịp cắt nhanh của Reels |
| chuong-thien | chuong-xoay-go_freesound_pixabay-33366 | 14.8s | mở đầu thực hành |
| chuong-thien | chuong-xoay-eb_freesound_pixabay-38746 | 12.6s | điểm nhấn chiêm nghiệm |
| chuong-thien | chuong-xoay-ngan-dai_freesound_pixabay-55786 | 1:26 | kết bài thiền, fade tuỳ ý |
| nhan-do-hoa | chime-mem-1 / chime-mem-2 (pixabay-146623 / 131438) | 1.4s | khi infographic hiện |
| nhan-do-hoa | pop-sach_dragon_pixabay-467466 | 1.6s | từng mục danh sách hiện |
| nhan-do-hoa | pop-nhe_humordome_pixabay-451232 | 5s | nhiều click nhẹ, cắt lấy đoạn cần |

Trang nguồn cụ thể của từng file nằm trong `am-thanh.json` (trường `trang`).

## Quy tắc bổ sung thư viện (cho Claude)

1. Nguồn ưu tiên: Pixabay (kiểm trang track không có nhãn "Content ID Registered" trước khi tải), rồi incompetech.com (CC-BY, thêm dòng ghi công)
2. Tải qua trình duyệt: bấm "Free download", chờ 6-8 giây sau mỗi cú bấm rồi mới điều hướng tiếp (điều hướng sớm sẽ huỷ lượt tải)
3. Đặt tên `<mô-tả>_<tác-giả>_<nguồn-id>.mp3`, để vào đúng nhóm, chạy `nhap-am-thanh.py`
4. Không nhận nhạc không rõ nguồn; nhạc người dùng tự có thì để `nhac-nen/rieng/`
