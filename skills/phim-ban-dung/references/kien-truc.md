# Bàn dựng: kiến trúc, dữ liệu, quy tắc điểm cắt

Tài liệu cho Claude khi cần sửa hay mở rộng Bàn dựng. Cách dùng hằng ngày ở mục "Bàn dựng" của `docs/QUY-TRINH-KY-THUAT.md`.

## Vì sao làm thế này

- Phần mềm có sẵn không hợp: Descript không hỗ trợ tiếng Việt; Premiere chưa có tiếng Việt; DaVinci Resolve 20 có dựng bằng lời tiếng Việt nhưng chỉ bản Studio, và chuyển qua lại bằng OpenTimelineIO chỉ giữ được mối cắt (mất mức nhạc, mờ, overlay, đồ họa). Xưởng đã có ba phần khó nhất của một phần mềm dựng (EDL `timeline.json`, bộ dựng chính xác từng mẫu tiếng, cổng kiểm), nên chỉ thiếu một "bàn tay".
- Nguyên tắc từ nghiên cứu: chỉ cắt trong khe giữa hai từ, hút về chỗ năng lượng thấp, giữ lề quanh lời, vi mờ chống tiếng bụp, chỗ không có khe sạch thì để người dùng quyết (Berthouzoz, Li và Agrawala, 2012; Rubin và cộng sự, 2013; Descript "avoid harsh cuts" và microfade).
- Lớp chữ để dựng phải là chữ nguyên văn: whisper chép theo ý định nói và bỏ phần lớn từ đệm (clip thử 10 phút: whisper 4 từ đệm, zipformer 39), đúng những chữ người dùng muốn cắt (Wagner, Thallinger và Zusag, 2024).

## Tệp

| Tệp | Việc |
|---|---|
| `Mo ban dung.command` | người dùng bấm đúp: tìm python3 có sẵn, chạy máy chủ, mở Chrome |
| `tools/ban-dung.py` | máy chủ thư viện chuẩn Python 3.8+: trang tĩnh, media có HTTP 206, danh sách timeline (cả `Du an/<x>/ke-hoach-dung/` và `Du an/<x>/clip-ngan/<slug>/`), đọc và ghi timeline có khoá lạc quan, cất bản cũ, nhật ký thay đổi, dữ liệu phụ (khoảng lặng, câu large-v3, âm tiết, năng lượng), làm đẹp chữ, `/api/cat` |
| `tools/ban-dung/index.html`, `ban-dung.css` | khung trang (tối, sentence case) |
| `tools/ban-dung/js/tien-ich.js` | tiện ích chung |
| `tools/ban-dung/js/mo-hinh.js` | mô hình: bố cục y hệt assemble, thao tác sửa, hoàn tác, kiểm |
| `tools/ban-dung/js/xem.js` | bộ xem: một thẻ video cho mỗi file nguồn, thẻ mang tiếng làm đồng hồ chủ |
| `tools/ban-dung/js/dong-thoi-gian.js` | dòng thời gian sáu kênh, kéo tỉa, kéo dời, đổi thứ tự, thu phóng, dạng sóng |
| `tools/ban-dung/js/thuoc-tinh.js` | bảng thuộc tính |
| `tools/ban-dung/js/loi.js` | thẻ Lời: văn bản, chọn chữ, bỏ, khôi phục, hỏi khi dính liền |
| `tools/ban-dung/js/app.js` | nối các phần, phím tắt, lưu, xung đột |
| `tools/moc-tu.py` | mốc âm tiết (VM): zipformer tiếng Việt chép chữ, omnilingual 300M CTC căn mốc, năng lượng 100 Hz |
| `tools/ban_dung_loi.py` | quy tắc điểm cắt, thuần Python |

## Dữ liệu

- `transcript/<nguồn>.tu.json`: `{"tu": [{"w", "s", "e", "c", "k"}], "khuc", "nangLuong": {"file", "hz", "san"}, "vanTay"}`. `k` là khúc nói do VAD cắt (giữa hai khúc luôn có khoảng lặng).
- `transcript/<nguồn>.nang-luong.bin`: mỗi byte là dB + 100, 100 byte mỗi giây.
- `timeline.json` thêm `_chinhTay` khi người dùng lưu từ Bàn dựng; `overlay[].duration` và `overlay[].giu` (assemble r7); `volumeDb` của đoạn (r7).
- Mọi lần lưu: bản cũ vào `Du an/<x>/ke-hoach-dung/_phien-ban/<đường dẫn timeline, / thành __>.<ngày-giờ>.json`, một dòng vào `Du an/<x>/ke-hoach-dung/_ban-dung/nhat-ky.jsonl`.

## Quy tắc điểm cắt (`tools/ban_dung_loi.py`)

- `khe(i)` là ranh giới giữa âm tiết i và i+1. Vùng tìm: từ max(đầu chữ trái + 0,08 s, cuối CTC chữ trái - 0,06 s), làm tròn lên khung, tới đầu chữ phải + 0,06 s. Lấy khung năng lượng thấp nhất:
  - dưới sàn ồn + 10 dB: dải lặng (`lang`), cắt vào với lề 0,12 s trước tiếng, cắt ra với lề 0,20 s sau tiếng, luôn cách chữ bị bỏ 0,03 s;
  - không lặng nhưng thung sâu từ 10 dB: `hep`, cắt đúng đáy thung;
  - còn lại: `gat`, không tự cắt.
- Âm tiết dính: chữ không có thân tiếng riêng (dưới 0,06 s) giữa khe trái và khe phải thì khe đó coi là `gat`.
- Vì sao như vậy: đỉnh CTC của nguyên âm kéo dài nằm bất kỳ đâu trong nguyên âm; chữ nhiều âm có khe lặng bên trong; sát đầu chữ là chỗ tiếng vừa nhú, năng lượng thấp dễ nhận nhầm là khe (chi tiết ở chủ đề 17 của `docs/BAI-HOC.md`).
- Đã nghe thử 16 điểm cắt thật: 16/16 sạch sau hai lượt sửa.

## Thẻ Lời

- Mỗi mục dòng thời gian một khối. Chữ `giu` (đang dùng), chữ `ngoai-truoc`/`ngoai-sau` (ngay trước/sau đoạn, chưa đoạn nào dùng, tối đa 8 chữ), chữ `bo` (quãng đã bỏ giữa hai đoạn kề nhau cùng file, tối đa 20 s). Chữ đã có ở đoạn khác không hiện mờ hay gạch, để khôi phục không thành lặp lời.
- Bỏ: đầu đoạn thì `tiaVao`, cuối thì `tiaRa`, giữa thì `tach` rồi `tiaVao` nửa sau, cả đoạn thì xoá. Khôi phục: chữ mờ trước/sau thì kéo dài đoạn; chữ gạch thì `noiQuaKhoang` khi chọn cả quãng, không thì kéo dài một bên.
- Multicam: mốc lời theo file tiếng chủ; đổi sang mốc hình bằng độ lệch `audioIn - in`; `tiaVao` tự dời `audioIn`.

## Kiểm

- `tools/kiem-tra-xuong.py --co-slide`: thêm ba phần cho Bàn dựng (điểm cắt trên lời tổng hợp; trường r7 đo trên thành phẩm; vi mờ ở mọi mép mối nối).
- Trang: Playwright ở sandbox với dự án WebM dựng từ `Du an/_tam/_kiem-tra-tu-dong` (VP9, Opus) và mốc lời tổng hợp; kịch bản kéo tỉa, tách, hoàn tác, dời và kéo dài thẻ, đổi thứ tự, lưu, xung đột, bỏ và khôi phục bằng lời.
- Dữ liệu thật: dùng chữ và năng lượng của một dự án thật, thay hình bằng video giả cùng thời lượng (footage không rời máy).

## Nguồn

- Berthouzoz, F., Li, W., & Agrawala, M. (2012). Tools for placing cuts and transitions in interview video. *ACM Transactions on Graphics, 31*(4).
- Rubin, S., Berthouzoz, F., Mysore, G. J., Li, W., & Agrawala, M. (2013). Content-based tools for editing audio stories. *UIST 2013*.
- Wagner, L., Thallinger, B., & Zusag, M. (2024). CrisperWhisper: Accurate timestamps on verbatim speech transcriptions. *Interspeech 2024*.
- Bain, M., Huh, J., Han, T., & Zisserman, A. (2023). WhisperX: Time-accurate speech transcription of long-form audio. *Interspeech 2023*.
- Descript Help Center: "Deleting vs. ignoring script text", "Filler words", "Automatic microfades".
- Meta Omnilingual ASR (Apache 2.0); VietASR zipformer tiếng Việt (Apache 2.0), qua bản phát hành của k2-fsa/sherpa-onnx.
