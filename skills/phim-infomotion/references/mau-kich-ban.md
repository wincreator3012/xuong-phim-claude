# Mẫu cho skill phim-infomotion

Bốn thứ: (1) lệnh tạo nền, (2) mẫu `KICH-BAN-INFOMOTION.md`, (3) mẫu job JSON và `timeline.json`, (4) schema `do-hoa-chung/an-du-y-niem.json`.

## 1. Tạo nền từ voice (chạy trong device_bash, từ gốc "xuong-phim-claude")

```
P="du-an/<tên>"
# chuẩn hoá tiếng (giữ file gốc), mono 48 kHz
ffmpeg -y -i "$P/nguon/<file gốc>" -ac 1 -ar 48000 -c:a pcm_s16le "$P/nguon/voice.wav"
# nền ngang: màu bg của theme (light #FAF7F1, dark #15181C), 30 fps, tiếng = voice
ffmpeg -y -f lavfi -i "color=c=0xFAF7F1:s=1920x1080:r=30" -i "$P/nguon/voice.wav" \
  -c:v libx264 -preset veryfast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest \
  "$P/nguon/nen-ngang.mp4"
# khung dọc: s=1080x1920 → nen-doc.mp4
ffprobe -v error -show_entries stream=codec_type,duration -of compact "$P/nguon/nen-ngang.mp4"
```

Kiểm: hình và tiếng cùng thời lượng (lệch ≤ 0,06 s). Nền là "clip nguồn" của dự án: transcript, silences, `in/out`, `broll.at` đều tính trên nó. Muốn nền có chuyển động rất chậm (thở) thì làm một composition nền riêng ở dự án sau, không phải ở dự án đầu.

## 2. Mẫu `KICH-BAN-INFOMOTION.md`

```
# Kịch bản hình tượng hoá - <tên video>

Thông điệp lõi: <một câu người xem mang theo>
Khung: ngang | Theme: light | Tổng: 7 phút 42 giây (voice) | Số nhịp: 31 | Số hình: 29 | Nhịp `Hình: KHÔNG`: 2
Nguồn: nguon/nen-ngang.mp4 (transcript/nen-ngang.json)
Chương: 1 Mở (0:00-1:10) · 2 Ba trụ cột (1:10-4:30) · 3 Thực hành (4:30-7:00) · 4 Kết (7:00-7:42)
Khung hình chung: theme light · màu nhấn accent của brand · họ hình chủ đạo: vẽ nét YNiem, YCanh cho đoạn kể chuyện · nhịp chuyển động chậm theo brand · đồ họa nổi mặc định canh giữa · độ phủ: phủ kín (không quá 1 giây nền trơn ngoài nhịp `Hình: KHÔNG - <lý do>`)
Kiểm giấy: python3 tools/uoc-luong.py "du-an/<tên>/KICH-BAN-INFOMOTION.md" → KIỂM GIẤY: ĐẠT

## Chương 1 - Mở

### Nhịp 1 · 0:00,2-0:09,8 (9,6 s) · Câu nhấn
Lời: "Điều khó nhất khi học một kỹ năng mới không nằm ở chính kỹ năng đó."
Hình: KHÔNG - nền trơn, để câu móc đứng một mình. Sau nhịp này chèn Intro (insert, 6 s).

### Nhịp 2 · 0:09,8-0:24,1 (14,3 s) · Thuật ngữ cố định - "Ba trụ cột của việc học"
Lời: "...có ba trụ cột: chú ý, lặp lại và nghỉ ngơi..."
Ẩn dụ: [ĐÃ CÓ] ba-tru-cot → ba đường dọc nâng một đường ngang
Thấy gì: ba nhãn chữ hiện lần lượt ở bên phải, đúng lúc người dùng gọi tên từng trụ cột, rồi ở lại cùng nhau.
Hình: Benefits nổi, position right, showIndex true, 3 mục revealAt 0 / 4,2 / 8,9 (đúng lúc nói từng tên)
Kiểm chứng: tên ba trụ cột đối chiếu hệ thuật ngữ đã chốt của người dùng (thuật ngữ người dùng đã chốt, không cần nguồn ngoài)
Ghi chú: pill tổng kết đủ ba tên xuất hiện lại ở nhịp 29 khi người dùng tự tổng kết.

### Nhịp 7 · 1:31,0-1:44,6 (13,6 s) · Khái niệm trừu tượng - "mắc kẹt"
Lời: "...bị mắc kẹt bởi những niềm tin cũ mà mình không nhìn thấy..."
Ẩn dụ: ẨN DỤ MỚI - cần duyệt. Đề xuất: một vòng tròn bị bốn đoạn dây siết dần vào (schema: chứa đựng/siết).
   Phương án khác: khung vuông thu nhỏ quanh một điểm. Người dùng chọn một, hoặc mô tả hình khác.
Thấy gì: một vòng tròn vẽ nét dần, bốn đoạn dây siết từ từ vào, chữ "mắc kẹt" hiện bên dưới.
Hình: YNiem toàn khung (vẽ nét dần 1,2 s, nhãn "mắc kẹt" xuất hiện ở giây 2), 13 s
Still mẫu: do-hoa/still/nhip-07.png (đính kèm)

### Nhịp 8 · 1:44,6-1:52,0 (7,4 s) · Câu nhấn
Lời: "...và đó là điều mình cần nhìn lại."
Hình: giữ hình nhịp 7 lắng lại - kéo dài ô YNiem nhịp 7 tới 1:52,0 (không thêm hình mới, không để nền trơn).

### Nhịp 12 · 2:40,0-2:52,5 (12,5 s) · Số liệu/so sánh
Lời: "...nghiên cứu theo dõi hơn tám mươi năm ở Harvard cho thấy..."
Thấy gì: con số lớn hiện giữa khung, dòng chữ nhỏ bên dưới ghi nghiên cứu và năm.
Hình: InfoStat toàn khung, value "<số>", caption "<tên nghiên cứu, năm>", 12 s
Kiểm chứng: <tác giả, năm, tên công trình, đường dẫn hoặc DOI>; lời khớp nguồn (nếu lệch: đưa ba cách vào câu hỏi cuối file)
...

## Cuối kịch bản

Ẩn dụ MỚI chờ duyệt: mắc kẹt (nhịp 7), bắt đầu lại (nhịp 18).
Nhịp `Hình: KHÔNG`: 1 (câu móc đứng một mình), 31 (câu hỏi kết để ngỏ). Các nhịp chuyển ý/cảm xúc khác giữ hình nhịp trước lắng lại hoặc có hình riêng.
Kiểm độ phủ: khoảng hở lớn nhất giữa hai nhịp 0,4 s; 2 nhịp không hình có ý đồ (tổng 14,2 s); hai nhịp liền nhau không lặp cùng khuôn chuyển động; 29 hình / 7,7 phút = 3,8 hình/phút (chỉ để tham khảo, không phải trần).
Dữ kiện lệch nguồn: <nhịp, lời nói, nguồn nói gì> - chọn (1) ghi âm lại câu đó / (2) giữ lời, hình không lặp dữ kiện / (3) cắt câu.
Cần người dùng quyết: (1) tên video trên Intro; (2) câu kết dùng InfoQuote hay để trống; (3) outro có QR đăng ký không.
```

## 3. Mẫu job JSON và timeline.json

`du-an/<tên>/do-hoa/job/job-nhip.json` (theo `du-an/_mau/do-hoa/job-do-hoa.json`, `brandFile` tương đối so với file job):

```json
{
  "aspect": "ngang", "theme": "light", "brandFile": "../../../../brand/brand.json", "outDir": "../ngang",
  "jobs": [
    {"comp": "Intro", "out": "intro.mp4", "props": {"title": "Tên video", "subtitle": "Tên chuỗi", "durationInSeconds": 6}},
    {"comp": "Benefits", "out": "nhip-02.webm", "alpha": true,
     "props": {"items": [{"label": "Chú ý", "revealAt": 0}, {"label": "Lặp lại", "revealAt": 4.2}, {"label": "Nghỉ ngơi", "revealAt": 8.9}],
               "position": "right", "showIndex": true, "durationInSeconds": 14.3}},
    {"comp": "InfoSteps", "out": "nhip-11.mp4", "props": {"title": "Năm bước của khung", "steps": ["Dừng", "Nhận biết", "Gọi tên", "Chấp nhận", "Trở về"], "durationInSeconds": 18}},
    {"comp": "InfoQuote", "out": "nhip-30.mp4", "props": {"quote": "Câu đắt nhất của bài.", "author": "", "durationInSeconds": 8}},
    {"comp": "Outro", "out": "outro.mp4", "props": {"headline": "Thông điệp kết", "durationInSeconds": 7}}
  ]
}
```

`timeline.json` - mỗi chương một segment cắt từ nền; đồ họa toàn khung là `broll` (at theo trục nguồn), đồ họa nổi là `overlay` (at tương đối so với `in`):

```json
{
  "aspect": "ngang", "fps": 30, "theme": "light",
  "outro": "do-hoa/ngang/outro.mp4",
  "segments": [
    {"type": "video", "src": "nguon/nen-ngang.mp4", "in": 0.2, "out": 9.8, "snap": true, "chapter": "Mở"},
    {"type": "insert", "src": "do-hoa/ngang/intro.mp4"},
    {"type": "video", "src": "nguon/nen-ngang.mp4", "in": 9.8, "out": 270.0, "snap": true, "chapter": "Ba trụ cột",
     "overlay": [
       {"src": "do-hoa/ngang/nhip-02.webm", "at": 0.0},
       {"src": "do-hoa/ngang/nhip-05.webm", "at": 61.4}
     ],
     "broll": [
       {"src": "do-hoa/ngang/nhip-07.mp4", "at": 91.0, "duration": 13.0, "from": 0},
       {"src": "do-hoa/ngang/nhip-11.mp4", "at": 150.5, "duration": 18.0, "from": 0}
     ]},
    {"type": "video", "src": "nguon/nen-ngang.mp4", "in": 270.0, "out": 462.0, "snap": true, "chapter": "Kết",
     "broll": [{"src": "do-hoa/ngang/nhip-30.mp4", "at": 440.0, "duration": 8.0, "from": 0}]}
  ],
  "music": {"src": "nhac-nen/<track>.mp3", "mode": "full", "gainDb": -26, "duck": true, "fadeIn": 2, "fadeOut": 4}
}
```

Lưu ý: `overlay.at` tính từ `in` của segment; `broll.at` tính theo thời gian trong file nguồn (nền). Overlay chỉ hiện ở quãng TRƯỚC B-roll đầu tiên của segment (trong mẫu trên, hai overlay ở 0,0 và 61,4 đều trước B-roll ở mốc nguồn 91,0): chương có đồ họa nổi xen sau đồ họa toàn khung thì tách thành nhiều sub-segment liền mạch (`out` đoạn trước = `in` đoạn sau) tại điểm kết thúc mỗi đồ họa toàn khung. `gainDb` trong mẫu chỉ là chỗ điền: lấy theo track trong `thu-vien/AM-THANH.md`. Chèn `insert` làm dịch mốc tuyệt đối của mọi thứ sau nó: phụ đề/chapter tính từ `map.json`, không cộng tay. Gọi `assemble.py --kiem-tra` trước, rồi `--preview --out "<tên>-ngang-nhap1"`.

## 4. Schema `do-hoa-chung/an-du-y-niem.json`

```json
{
  "_huong-dan": "Từ điển ẩn dụ hình ảnh cá nhân của người dùng. Khoá = slug không dấu của khái niệm. Chỉ ghi mục ĐÃ ĐƯỢC NGƯỜI DÙNG DUYỆT (có ngày và dự án). Skill phim-infomotion tra ở Bước 4, ghi thêm ở Bước 5 ngay sau duyệt. Không sửa mục đã duyệt trong lúc làm dự án khác mà không hỏi lại.",
  "schema": ["chua-dung", "duong-di", "can-bang", "tren-duoi", "day-keo", "sang-toi", "trung-tam-ngoai-vi", "vong-lap", "tang-lop"],
  "muc": {
    "mac-ket": {
      "khai-niem": "mắc kẹt",
      "tieng-anh": "being stuck",
      "schema": "chua-dung",
      "an-du": "một vòng tròn bị bốn đoạn dây siết dần vào",
      "hinh-thuc": "YNiem",
      "slug-hinh": "vong-day-siet",
      "props": {"drawSeconds": 1.2, "labelAt": 2.0},
      "phien-ban-khac": [],
      "duyet": "2026-09-xx",
      "du-an": "<tên dự án đầu tiên>",
      "ghi-chu": "MỤC VÍ DỤ - xoá khi có mục thật đầu tiên"
    }
  }
}
```

`slug-hinh` là slug YNiem (trong `studio/src/y-niem/index.ts`) hoặc tên variant YCanh (`hub-branches`, `filling-grid`...), trùng với giá trị trong `props`; mục đã đổi tên hình giữ tên cũ ở `variant-cu` và hình lúc duyệt ở `an-du-luc-duyet`.

Quy tắc: một khái niệm một khoá; khái niệm đồng nghĩa trong hệ thuật ngữ của người dùng (ví dụ "bắt đầu lại" và "starting over") trỏ về cùng một mục qua `phien-ban-khac`; đổi ẩn dụ đã duyệt là một quyết định có ghi ngày, không lặng lẽ ghi đè.
