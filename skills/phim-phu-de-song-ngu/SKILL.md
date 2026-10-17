---
name: "phim-phu-de-song-ngu"
description: "Dựng clip NGANG MỘT NGUỒN có PHỤ ĐỀ SONG NGỮ ghi cứng (Anh-Việt hoặc hai thứ tiếng bất kỳ) để chiếu cho khán giả hai thứ tiếng hay người ngồi xa nghe không rõ: lời chúc, thông điệp gửi từ xa, lời chia sẻ chiếu ở đám cưới, lễ kỷ niệm, hội trường. Gồm gỡ băng nguồn nói tiếng khác hoặc trộn hai tiếng, tuỳ chọn cắt gọn theo mạch cảm xúc (phương án trên giấy, người dùng duyệt), viết cue dịch theo mốc nguồn, burn hộp chữ lớn, nghiệm thu và giao. Kích hoạt khi người dùng nói 'phụ đề song ngữ', 'burn phụ đề Anh-Việt', 'khách ở xa không nghe rõ', 'clip lời chúc', 'cắt gọn mà vẫn giữ tình cảm', hoặc thả một clip nói tiếng Anh cần chiếu cho khách Việt. Không dùng cho clip dọc đăng mạng (phim-clip-ngan), bài giảng nhiều đoạn (phim-dung-bai), hay chỉ cần file SRT (phim-transcript)."
---

# Phụ đề song ngữ ghi cứng cho clip ngang một nguồn

Người xem ở hội trường không như người xem trên điện thoại: ngồi xa, tiếng loa dội, có người chưa nghe quen tiếng Anh, có người không nghe được tiếng Việt, và cả phòng cùng nhìn một màn hình. Vì vậy phụ đề phải ghi cứng vào hình, hai ngôn ngữ cùng lúc, chữ đủ to để đọc từ cuối phòng, và clip đủ ngắn để người không thân với người gửi vẫn ở lại đến câu chúc cuối. Mọi quyết định (cắt đâu, dịch sao, chữ to cỡ nào) bắt đầu từ câu hỏi: ở giây này người ngồi xa đọc được gì, cảm được gì.

Công cụ: `tools/phu-de-song-ngu.py` (`khoi-tao`, `dung`, `burn`, `khung`). Cue viết theo MỐC NGUỒN (giây trong file quay) trong `Du an/<x>/phu-de/cues.json`, nên cắt lại phim thì sinh lại phụ đề bằng một lệnh. Bài học và số đo: `docs/BAI-HOC.md` mục 29. Cắt dựng và cổng nghiệm thu dùng chung với `phim-dung-bai`; màu HDR theo `phim-mau-sac`.

## Bước 0 - hỏi một lượt

Đọc `skills/_chung/van-hanh.md` (nguyên lý trước khuôn mẫu). Hỏi người dùng bằng AskUserQuestion những gì chưa có (tối đa bốn câu, kèm mặc định):

1. **Dịp, người xem, cách chiếu**: đám cưới, kỷ niệm, họp mặt; khách nói thứ tiếng nào; chiếu một lần cho cả phòng hay phát lặp. Chỉ chiếu tại chỗ thì KHÔNG làm gói đăng tải; chưa rõ thì hỏi một câu.
2. **Cắt gọn hay giữ nguyên**: mặc định đề xuất bản ngắn (khoảng 4 phút cho lời chúc, người xem không thân với người gửi) và nói rõ bản nguyên vẹn dài bao nhiêu. Cắt gọn thì có thêm chốt duyệt trên giấy.
3. **Tên riêng và quan hệ**: chính tả có dấu của từng người trong clip, ai là ai (cô dâu, chú rể, người gửi, người nhận). QUAN HỆ CHƯA BIẾT THÌ KHÔNG SUY RA: dịch bằng cách nói trung tính (hai bạn, chúng mình) và nói với người dùng rằng đã giữ trung tính.
4. **Nhạc**: mặc định không nhạc, giữ âm thanh tự nhiên của người nói.

## Bước 1 - gỡ băng đúng ngôn ngữ

Nguồn nói tiếng Anh hay trộn hai tiếng thì `--lang auto` (Whisper tự nhận ngôn ngữ từng đoạn, ghi vào trường `lang`); để mặc định `vi` sẽ ra chữ vô nghĩa. Đường chuẩn là large-v3 trên Mac qua hàng đợi (xem `skills/phim-transcript/SKILL.md`):

```
python3 tools/hang-doi-go-bang.py them "../Du an/<x>/nguon/<file>" --out-dir "../Du an/<x>/transcript" --model large-v3 --lang auto
python3 tools/nghiem-thu.py transcript "../Du an/<x>"
```

Nhãn `lang` của đoạn rất ngắn không đáng tin (một tên riêng có dấu bị gắn `ar`): quyết định ngôn ngữ theo cả clip. Chữ Whisper tiếng Anh ra chữ thường, không dấu câu, tên riêng bị nghe thành từ gần âm: đây là bản thô, hiệu đính ở Bước 4. Nguồn HDR (iPhone hay quay HLG): khám màu và tonemap theo `phim-mau-sac`; nếu da hơi gắt thì thêm `eq=saturation=0.90:gamma=1.04` vào `mau-sac.json` và so với khung gốc bằng mắt.

## Bước 2 - phương án cắt trên giấy (chốt duyệt số 1, nếu cắt gọn)

Đọc transcript, rồi trình người dùng một bảng: mốc nguồn, nội dung, giữ hay bỏ, lý do, thời lượng còn lại. Nguyên lý cắt gọn lời chúc, lời chia sẻ cá nhân:

- Giữ nhịp cảm xúc của người gửi: lời mở gọi tên, ký ức chung, lời cảm ơn từng người, lời khuyên hay điều mong cuối cùng, câu chúc. Bỏ chỗ lặp, chỗ nói lạc, chuyện kể dài mà người ngoài không theo được, chỗ ngập ngừng.
- Giữ trọn các câu có sức nặng; cắt ngay trong câu chỉ khi điểm cắt rơi đúng chỗ ngừng thật (`snap` của `assemble.py` hút về khoảng lặng gần nhất). Hai người nói thay phiên thì giữ lượt của cả hai cho cân; gán người nói bằng cao độ giọng từng đoạn đối chiếu khung hình, không đoán theo nội dung.
- Nói rõ trong phương án điều gì mất đi và vì sao chịu mất. Số phút trên giấy do công cụ cộng, không cộng tay.

## Bước 3 - bản nháp 480p (chốt duyệt số 2)

`timeline.json` một track video, `aspect: "ngang"`, `snap: true`, fade vào ở đoạn đầu và fade ra ở đoạn cuối, không nhạc, không intro, không outro (clip chiếu tại sự kiện thường để người nói mở đầu ngay). Dựng như `phim-dung-bai`:

```
python3 tools/assemble.py --project "../Du an/<x>" --kiem-tra
python3 tools/assemble.py --project "../Du an/<x>" --preview --out "<tên>-ngang-nhap1"
```

Bản nháp đưa người dùng xem phải có phụ đề (Bước 4), vì phụ đề là thứ người dùng duyệt.

## Bước 4 - cue song ngữ

```
python3 tools/phu-de-song-ngu.py khoi-tao "../Du an/<x>" <tên>-ngang-nhap1    # nháp phu-de/cues.json: chữ gốc từ transcript, phần dịch để trống
```

Mở `cues.json` và hoàn thiện (khung ví dụ):

```
{"nguon": "nguon/<file>.mov",
 "kieu": {"font": "Lato", "co-chu": 64, "rong-dong": 42, "hop": true, "mau-2": "FFE9A8"},
 "the-ten": {"dong-1": "Tên người gửi", "dong-2": "Từ <nơi> · From <place>", "tu": 0.6, "den": 4.6},
 "cues": [{"s": 31.9, "e": 41.6,
           "c": [["English line one.", "Dòng tiếng Việt một."], ["English line two.", "Dòng tiếng Việt hai."]],
           "ghi-chu": "chỗ nghe không chắc, để chủ nhân nghe lại"}]}
```

- **Hiệu đính chữ gốc** theo tai và ngữ cảnh: dấu câu, viết hoa, tên riêng đúng chính tả. Cue lấy mốc nguồn theo câu Whisper, cắt gọn thì `s` và `e` bám sát đoạn giữ lại (công cụ chiếu cue sang thành phẩm bằng `map.json`, cue nằm ngoài phần giữ lại thì báo lỗi).
- **Dịch cho người đọc lướt trên màn hình lớn:** câu ngắn, bám nghĩa và giọng người nói (thân mật hay trang trọng), không thêm ý, không văn hoa. Đại từ chọn theo quan hệ ĐÃ BIẾT; chưa biết thì trung tính. Tên riêng giữ nguyên chính tả có dấu.
- **Một câu dài tách thành nhiều cặp** trong `c`: mỗi cue tối đa hai dòng mỗi ngôn ngữ ở 42 ký tự, công cụ chia thời gian theo tỉ lệ ký tự rồi hút về khoảng ngừng gần nhất. Cảnh báo đọc nhanh (hơn 21 ký tự mỗi giây) thì rút câu hoặc tách cue.
- **Chỗ nghe không chắc thì ghi `ghi-chu`**, không đoán thầm. Bản dịch theo ý đoán cũng ghi. Mốc các chỗ này nằm cuối `phu-de/<tên>.bao-cao.txt` để báo người dùng khi nộp bản nháp và khi giao.

```
python3 tools/phu-de-song-ngu.py dung "../Du an/<x>" <tên>-ngang-nhap1
python3 tools/phu-de-song-ngu.py burn "../Du an/<x>" <tên>-ngang-nhap1
python3 tools/phu-de-song-ngu.py khung "../Du an/<x>" <tên>-ngang-nhap1 2.5 60 120 --vao <tên>-ngang-nhap1-pd
```

Stage các khung rồi nhìn: bảng tên không che mặt, hộp chữ không chạm mép, dấu tiếng Việt đủ, không chữ nào bị cắt. Gửi người dùng bản nháp có phụ đề kèm danh sách chỗ cần nghe lại.

## Bước 5 - bản chính 1080p

Người dùng duyệt nháp thì bỏ `--preview` và dựng `--out "<tên>-ngang"`; sinh lại phụ đề bằng `map.json` của bản chính (`dung <tên>-ngang`), burn, nghiệm thu:

```
python3 tools/assemble.py --project "../Du an/<x>" --out "<tên>-ngang"
python3 tools/phu-de-song-ngu.py dung "../Du an/<x>" <tên>-ngang
timeout 170 python3 tools/phu-de-song-ngu.py burn "../Du an/<x>" <tên>-ngang      # ra xuat-nhap/<tên>-ngang-pd.mp4
python3 tools/nghiem-thu.py video "../Du an/<x>/xuat-nhap/<tên>-ngang-pd.mp4"
```

`burn` dùng `-preset veryfast -crf 17 -c:a copy` (clip 4 phút mất 60 đến 100 giây); clip dài hơn khoảng 6,5 phút thì chạy trên Mac. Bản burn là một lượt encode mới và là bản hoàn chỉnh cuối cùng: nghiệm thu phải chạy trên chính file này, rồi trích khung (`khung`) ở đầu, giữa và cuối clip để nhìn.

## Bước 6 - giao

Đặt `<tên>-ngang-pd.mp4` kèm ba tệp SRT (`.srt` song ngữ, `.en.srt`, `.vi.srt`) vào `xuat-hoan-chinh/` và thư mục clip trong `Thanh pham/<YYYY-MM tên dự án>/00 Video day du/` cùng `nghiem-thu.json` và `transcript/` (quy tắc 11 của `CLAUDE.md`). Báo người dùng: tên file và nơi để, thời lượng, dung lượng, "nghiệm thu máy: ĐẠT", các chỗ cần nghe lại cùng mốc, và các điều đã giữ trung tính. Không làm gói đăng tải khi clip chỉ chiếu tại chỗ. Không dọn nháp trước khi người dùng nói "duyệt" (quy tắc 12, 18).

## Quy tắc cứng

1. Chưa qua `tools/nghiem-thu.py video` ĐẠT trên chính bản đã burn thì chưa nói "xong"; không hạ ngưỡng.
2. Hai chốt duyệt với người dùng: phương án cắt (nếu cắt gọn), rồi bản nháp 480p CÓ phụ đề, trước bản chính.
3. Không suy diễn quan hệ giữa những người trong clip và không đoán chính tả tên riêng: hỏi, hoặc dịch trung tính và báo.
4. Chữ nghe không chắc phải nằm trong `ghi-chu` và báo cáo giao; không bao giờ để một chỗ đoán trông như chắc chắn.
5. Cue theo mốc nguồn, chiếu bằng `map.json`; không cộng trừ mốc bằng tay.
6. Không che mặt ai: bảng tên ở góc trên trái, hộp chữ ở đáy; kiểm trên khung thật ở đầu clip (bảng tên cộng cue đầu), giữa và cuối.
7. Chữ trên hình đúng hai ngôn ngữ của khán giả, tên riêng đúng dấu; không emoji; tiếng Việt thuần Việt, không chen tiếng Anh tuỳ tiện.
8. Bản burn kiểm thời lượng bằng bản gốc (công cụ tự làm); file cụt không bao giờ được dùng.
9. Clip chỉ chiếu tại sự kiện: không gói đăng tải, không đăng mạng, trừ khi người dùng yêu cầu.
10. Không xoá nháp, nguồn quay hay `cues.json` khi chưa được phép; `cues.json` là nguồn phụ đề của dự án, giữ lại.

Sửa skill này theo `skills/_chung/bao-tri-skill.md`; bài học mới vào `docs/BAI-HOC.md` mục 29 (hoặc mục 8 nếu là phụ đề nói chung).

<!-- ban-nguon: phim-phu-de-song-ngu 2026-10-17 a4183284 -->
