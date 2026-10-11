# Mẫu bảng cảnh, job đồ họa và timeline cho recap

## 1. Bảng cảnh `Du an/<x>/recap/canh.json`

Viết sau khi người dùng duyệt phương án. Mỗi dòng một cảnh theo thứ tự phim; dòng `the` là thẻ đồ họa chèn. `clip` là số thứ tự ba chữ số (sau `recap.py doi-ten`) hoặc tên tệp; `tu`, `den` là giây trong tệp nguồn.

```json
[
 {"id": "a1", "clip": "005", "tu": 8, "den": 12, "tieng": "tat", "chuong": "Welcome", "mo": 0.4, "ghi_chu": "khách vào phòng"},
 {"id": "a2", "clip": "001", "tu": 6, "den": 10, "tieng": "tat"},
 {"id": "k1", "clip": "010", "tu": 52, "den": 60, "tieng": "giu", "chuong": "Opening", "mo": 0.3, "ghi_chu": "lời chào của khách hàng"},
 {"the": "do-hoa/ngang/phan1.mp4"},
 {"id": "b1", "clip": "013", "tu": 155, "den": 161, "tieng": "tat", "chuong": "Part 1",
  "chu": "do-hoa/ngang/tm-y-chinh.webm", "chu_at": 0.8},
 {"id": "q1", "clip": "019", "tu": 274, "den": 299, "tieng": "giu", "chu": "do-hoa/ngang/tm-dut-ket.webm", "chu_at": 0.5},
 {"id": "p1", "clip": "038", "tu": 965, "den": 973, "tieng": "tat", "chuong": "Closing", "tat_dan": 0.5, "ghi_chu": "ảnh chung"}
]
```

Trường: `tieng` `giu` (tiếng gốc, `snap` bật, có tệp khoảng lặng) hay `tat` (`volumeDb -90`); `chuong` tên chương; `chu` webm chữ nổi, `chu_at` giây tính từ đầu cảnh, `chu_dai` giữ chữ dài hơn hay ngắn hơn tệp; `mo` / `tat_dan` mờ vào, mờ ra (giây); `volumeDb` chỉnh tiếng riêng đoạn giữ tiếng; `ghi_chu` để đối chiếu, không vào timeline.

## 2. Job đồ họa recap (đã render, kiểm khung)

```json
{
 "aspect": "ngang", "theme": "light", "brandFile": "@xuong/brand/brand.json", "outDir": "ngang",
 "jobs": [
  {"comp": "Intro", "out": "intro.mp4", "props": {"title": "<Tên buổi, dòng 1>\n<dòng 2>", "subtitle": "<CHUỖI CHƯƠNG TRÌNH>",
    "description": "<đơn vị> - <dịp>", "creditLines": ["<ngày>"], "durationInSeconds": 6, "brand": "<brand không logo, xem dưới>"}},
  {"comp": "SectionTitle", "out": "phan1.mp4", "props": {"kicker": "PART 1", "title": "<tên phần>", "durationInSeconds": 4}},
  {"comp": "Benefits", "out": "tm-y-chinh.webm", "alpha": true, "props": {"items": [{"label": "Everyone moves by their own rule"}],
    "position": "bottom", "showIndex": false, "wrap": true, "durationInSeconds": 5}},
  {"comp": "Outro", "out": "outro.mp4", "props": {"headline": "Thank you, <đơn vị>,\nfor spending this afternoon together",
    "ctaLines": [], "programName": "", "contactLines": [], "showTagline": false, "durationInSeconds": 7}}
 ]
}
```

- Không logo: mỗi job truyền `"brand"` là bản sao của `brand/brand.json` với `"logos": []`, `"logoFile": null`, `"name": ""`, `"tagline": ""`, `"socialLine": ""`, `"contactLines": []` (giữ `palettes`). Kiểm tên prop thật của SectionTitle, Intro trong `skills/phim-do-hoa/references/props-va-bay.md` trước khi render.
- Benefits một mục không cần `revealAt` (tự hiện sau 0,3 giây); nhiều mục thì đặt `revealAt` theo lời.
- Outro tôn trọng `\n` trong `headline`; trường nào không dùng phải ghi rỗng tường minh, nếu không chữ mẫu của component lộ ra.

## 3. Timeline sinh ra

`recap.py timeline` viết `timeline.json` (đã có thì ghi `timeline.recap.json`, `--ghi-de` để thay; có `_chinhTay` thì từ chối). Mỗi đoạn video giữ trường `_recap` là id cảnh để `khop-nhip` và `kiem` báo theo tên cảnh. Nhạc lấy từ `Du an/<x>/recap/nhip.json` (mode full, duck, gainDb gợi ý cho recap ít lời) nếu timeline cũ chưa có. Phim chữ tiếng Anh: `--chuong-dau Intro` ghi `"chapterIntro": "Intro"`.
