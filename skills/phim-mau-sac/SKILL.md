---
name: phim-mau-sac
description: Đánh giá và căn chỉnh màu video tinh gọn cho clip talking head/podcast theo quy trình KHÁM - KÊ ĐƠN - SOI LẠI, chạy trong thư mục xưởng (tools/mau-sac.py + đơn màu mau-sac.json mà assemble.py tự áp). Kích hoạt khi user yêu cầu "khám màu", "đánh giá màu", "chỉnh màu", "căn màu", "color grade", "clip bị bạc màu", "màu da xấu", "hai góc máy lệch màu", "video nhìn nhạt", "footage HDR bị xám", hoặc bất kỳ than phiền nào về màu sắc/độ sáng/độ tương phản của video. Cũng kích hoạt TỰ ĐỘNG trong bước khảo sát tư liệu của skill phim-dung-bai (khám màu mọi nguồn trước khi dựng) và khi mediainfo/ffprobe cho thấy color_transfer là smpte2084 hay arib-std-b67 (HDR - bắt buộc xử lý). KHÔNG dùng cho chỉnh màu đồ họa Remotion (skill phim-do-hoa - đồ họa đã đúng màu thiết kế).
---

# Đánh giá và căn chỉnh màu: KHÁM - KÊ ĐƠN - SOI LẠI

Triết lý đã chốt với user: **đa số clip không cần chỉnh** - chỉ can thiệp khi có bệnh thật, chỉnh thì nhỏ và tự nhiên [correction], tuyệt đối không "look" nghệ thuật. User không canh màu - Claude đo, Claude nhìn, Claude kê đơn; user chỉ duyệt một tấm ảnh trước/sau trong 30 giây. Mọi lệnh chạy từ gốc xưởng qua device_bash.

## Bước 1 - KHÁM (mỗi dự án một lần, trước khi dựng)

```
python3 tools/mau-sac.py kham "du-an/<x>"
```

Script đo từng file nguồn (metadata màu, sáng p5/p50/p95, lệch kênh RGB, bão hòa, so chéo giữa các nguồn), xuất `mau-sac-kham.json` + 5 frame/file vào `.tam/mau/`. Sau đó BẮT BUỘC stage vài frame tiêu biểu lên và NHÌN BẰNG MẮT - số liệu chỉ là gợi ý, hai bẫy đã gặp thật:

- "Trội kênh G/lệch kênh" thường chỉ là cây cỏ, tường màu trong khung hình chứ không phải ám màu - cast thật phải THẤY trên da và vùng trắng/xám (áo, tường, giấy)
- "So chéo lệch nhau" giữa các file chỉ đáng xử lý khi chúng CẮT QUA LẠI trong cùng cảnh (đa góc máy); các clip khác bối cảnh khác buổi quay thì lệch là tự nhiên

Kết luận chắc chắn duy nhất từ số liệu: `color_transfer` = smpte2084 (PQ/Dolby Vision) hoặc arib-std-b67 (HLG) → footage HDR, BẮT BUỘC tonemap, không cần hỏi (iPhone/Osmo/Insta360 hay quay HDR mặc định - kiểm tra từng file, không đoán theo thiết bị).

## Bước 2 - KÊ ĐƠN (ba bậc, trần an toàn cứng)

**Bậc 0 - đạt**: không chỉnh. Đây là kết luận kỳ vọng cho số đông (nghiệm thu thật trên năm clip quay ngoài trời bằng nhiều thiết bị: 3/5 đạt nguyên bản).

**Bậc 1 - sửa bệnh kỹ thuật** (công thức chuẩn, điều chỉnh con số theo mắt):

- HDR → SDR (bắt buộc): `zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,format=yuv420p` (hable giữ chi tiết sáng tối, desat=0 giữ bão hòa; nếu ra hơi tối thử reinhard)
- Mặt chìm/hơi tối: `eq=brightness=0.02..0.05:gamma=1.03..1.10`
- Bạc/thiếu tương phản thật: `curves=master='0/0 0.12/0.09 0.5/0.5 0.88/0.91 1/1'` hoặc eq contrast 1.02-1.08
- Ám màu thật: `colortemperature=temperature=<K>` (ấm lên >6500, lạnh xuống <6500, dịch tối đa ±800K) hoặc colorbalance nhẹ
- Nhạt thật: eq saturation tối đa 1.15

TRẦN AN TOÀN (không vượt dù mắt muốn thêm): brightness ±0.05, gamma 0.90-1.10, contrast 0.95-1.08, saturation 0.90-1.15, nhiệt màu ±800K. Cần vượt trần = bệnh nặng từ khâu quay → báo user cân nhắc quay lại thay vì cứu bằng hậu kỳ.

**Bậc 2 - khớp góc máy** (chỉ khi các góc cắt qua lại cùng cảnh): chọn góc có da đẹp nhất làm CHUẨN (Claude tự chọn, user duyệt ở bước soi); khớp SÁNG trước (đưa p50 hai góc về gần nhau bằng brightness/gamma), khớp MÀU sau (so kênh RGB trên vùng da và vùng trung tính chung, sửa bằng colortemperature/colorbalance); hai clip cùng bối cảnh nên dùng CÙNG một đơn để khỏi lệch nhau.

## Bước 3 - SOI LẠI (cổng duyệt của user, bắt buộc trước khi áp)

```
python3 tools/mau-sac.py soi "du-an/<x>/nguon/<file>" --vf "<đơn>"
```

Ra 3 ảnh ghép trái gốc | phải sau đơn. Claude tự nhìn trước (đạt "sửa mà như không sửa" chưa - da tự nhiên, nền không cháy, không bị "màu instagram"), rồi stage 1 ảnh gửi user gật/lắc. User gật → ghi đơn vào `du-an/<x>/mau-sac.json`:

```json
{"<tên file nguồn>": {"vf": "<chuỗi filter>", "note": "<bệnh gì, vì sao đơn này>"}}
```

## Thực thi - không tốn gì thêm

assemble.py TỰ đọc mau-sac.json và chèn đơn vào trước chuỗi chuẩn hóa của mọi đoạn cắt từ file đó (cả B-roll theo file hình), ngay trong lượt encode duy nhất sẵn có - không thêm pass, cache part tự vô hiệu khi đơn đổi. Không cần làm gì thêm ngoài việc file mau-sac.json nằm đúng chỗ. Đơn theo TỪNG FILE này độc lập với "colorGrade" toàn cục trong timeline.json (hiếm dùng - chỉ khi user muốn đẩy nhẹ toàn bài).

## Phòng bệnh khi quay (nhắc user khi có dịp, đáng giá hơn mọi thuốc)

- Thiết bị nào tắt được HDR/Dolby Vision thì tắt khi quay để đăng mạng xã hội SDR
- Quay nhiều góc cùng cảnh: khóa cân trắng [white balance lock] cùng một giá trị trên các máy, đừng để auto
- Đứng quay ngược sáng giờ hoàng hôn thì bù sáng khuôn mặt +0.3..0.7EV từ lúc quay

## Ghi nhớ vận hành

- Khám màu chạy ở bước khảo sát tư liệu của skill phim-dung-bai, trước khi soạn phương án cắt; clip ngắn (skill phim-clip-ngan) thừa hưởng mau-sac.json sẵn có của dự án, không khám lại
- Duyệt màu của user thực hiện trên màn Mac (đã chốt); Claude nhìn frame staged là đủ tin cho bậc 1, bậc 2
- Frame khám nằm trong `.tam/mau/` - dọn theo .tam như thường lệ
