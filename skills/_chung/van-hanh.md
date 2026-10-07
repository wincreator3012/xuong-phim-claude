# Vận hành chung cho mọi skill phim

## Nguyên lý trước khuôn mẫu

Xưởng làm việc bằng nguyên lý, không bằng khuôn. Mọi quyết định sáng tạo (cắt ở đâu, hình gì, đặt đâu, to cỡ nào, nhịp nào, nhạc nào, mở và kết ra sao) bắt đầu từ trải nghiệm của người xem: ở giây này họ đang thấy, nghe, cảm gì; họ cần gì để hiểu, để thở, để ở lại; chỗ nào họ sẽ mỏi, lạc hay trượt đi.

- **Mặc định là điểm xuất phát đã kiểm chứng, không phải đáp án.** Các con số, vị trí, cỡ, mật độ trong skill, PHONG-CACH và BAI-HOC ghi lại điều từng đúng với những clip cụ thể. Clip mới có nội dung, khung hình, nhịp khác thì ứng biến, và nói rõ lý do trong phương án trình người dùng.
- **Hai lớp khác nhau.** Bất biến kỹ thuật và giá trị giữ tuyệt đối: cổng nghiệm thu, hình = tiếng, chức danh và từ ngữ nguyên văn, không che mặt, chất liệu thật và giọng thật, không hình do AI tạo thay hình thật, không xoá file khi chưa được phép. Lựa chọn sáng tạo thì linh hoạt theo từng clip, dựa trên nguyên lý và trải nghiệm người xem.
- **Một khuôn lặp lại ở mọi clip là dấu hiệu cần nghĩ lại**, không phải dấu hiệu nhất quán. Nhất quán nằm ở tinh thần (tĩnh tại, thở, chân thật, mỗi khung một ý), không nằm ở việc mọi clip giống nhau.
- **Hỏi người dùng ở các chốt duyệt** khi một lựa chọn đáng để người dùng quyết (vị trí và cỡ đồ họa, nhịp, cách mở, cách kết, nhạc), kèm đề xuất của Claude và lý do; không hỏi những điều đã chốt hoặc thuần kỹ thuật.

## Đọc gì trước

1. `CLAUDE.md` ở gốc "xuong-phim-claude": thứ tự đọc, quy tắc cứng. Xưởng chưa thiết lập (chưa có `tools/.cai-dat.json`, hoặc PHONG-CACH còn dấu `[...]`): chạy skill phim-thiet-lap trước mọi việc.
2. `docs/QUY-TRINH-KY-THUAT.md`: môi trường, lệnh, cổng nghiệm thu, quy ước chất lượng. Phiên chưa dựng sandbox thì làm mục "Khởi động phiên mới".
3. `phong-cach/PHONG-CACH.md`: tên, chức danh, từ ngữ phải viết đúng, tông hình, sổ tay góp ý.
4. `docs/BAI-HOC.md`: đọc chủ đề của khâu sắp làm (dựng, overlay, gỡ băng, phụ đề, đồ họa, infomotion, phỏng vấn, multicam, truyền file).

## Hai nơi chạy lệnh

- **Máy của người dùng (`device_bash`)**: mọi xử lý video nặng, footage không rời máy. Mỗi lượt tối đa 180 giây, không giữ tiến trình nền qua các lượt: lệnh dài chạy đồng bộ trong một lượt, hoặc bằng script + `timeout 170` + log rồi gọi lặp; `assemble.py` tự resume khi gọi lại y nguyên. Gỡ băng large-v3 chạy trên Mac thật qua hàng đợi (`tools/hang-doi-go-bang.py`) khi máy là Mac thật và đã tải model này (`tools/models/TAI-MODEL.md`); không thì turbo trong VM.
- **Sandbox đám mây (`Bash`, 2 lõi)**: render Remotion. Tiến trình nền sống qua nhiều lượt (`nohup ... & disown`, theo dõi bằng `tail`). Render TUẦN TỰ: nhiều đồ họa gộp chung một job JSON cho `render-do-hoa.mjs` tự chạy lần lượt, không chạy hai lệnh render song song. Luôn truyền `--studio <đường dẫn tuyệt đối>` (thư mục làm việc của shell có thể bị đặt lại giữa các lượt; thiếu cờ này lệnh hỏng với lỗi khó đoán kiểu "could not determine executable to run").
- Hai máy làm song song được: khởi động việc dài ở sandbox trước, làm việc của máy trong lúc chờ (mục "Hai làn song song" của QUY-TRINH).
- Không có sandbox đám mây (Claude chạy thẳng trên máy): mọi bước, kể cả render Remotion, chạy trên máy; bỏ qua phần truyền file bên dưới.

## Truyền file

- Máy lên sandbox: `device_stage_files`, chỉ file cần cho bước đó; không stage chỉ để đọc hay sửa chữ.
- Sandbox về máy: chép vào `/mnt/user-data/outputs/<thư mục>/`, rồi `device_commit_files` với `stagedPath` và đường dẫn tuyệt đối trên máy. Mỗi lần commit bản sửa dùng tên staged MỚI; so md5 hai phía (mp4 và ảnh so bằng `ffprobe` vì có thể bị gắn thêm hộp manifest). File hơn 20 MB: `split -b 19m`, commit từng phần, `cat` trên máy, kiểm checksum.
- File `.tsx` sửa ở sandbox commit về `studio/src/...` trên máy NGAY sau khi sửa.
- Sửa file có dấu tiếng Việt trên máy bằng `python3 <<'PYEOF'` đọc sửa ghi, rồi đọc lại đoạn vừa ghi để chắc dấu còn nguyên.
- Không xoá file trong thư mục của người dùng khi chưa được phép; file cần bỏ chuyển vào `_to_delete/`. Ảnh kiểm tra tạm để trong thư mục nhà của VM, không để trong thư mục dự án.

## Chữ và chức danh

- Mọi chữ trên hình theo `phong-cach/PHONG-CACH.md` mục 4 (thuần Việt có ngoặc vuông [English], sentence case, gạch ngang thường, từ ngữ phải viết đúng).
- Chức danh của người dùng: theo từng dự án, do người dùng nói; không nói thì dùng mặc định trong PHONG-CACH mục 1, không hỏi lại. Chức danh đã dùng cho một chương trình ghi ở PHONG-CACH mục 1.
- Chức danh người khác: nguyên văn từ bảng nhân vật của dự án; chưa có thì hỏi người dùng trước khi render. Không suy ra từ `Intro.props.subtitle` hay tên chương trình.
- Dữ kiện lên hình (con số, năm, trích dẫn, tên tác giả của mô hình) phải có nguồn đối chiếu; không kiểm được thì không lên hình, đưa thành lựa chọn cho người dùng.

## Hai chốt duyệt và báo "xong"

- Phương án cắt và overlay duyệt trước khi dựng; nháp 480p duyệt trước bản chính. Infomotion và phim tài liệu có thêm cổng duyệt trên giấy. Ở chốt nháp, người dùng có thể tự chỉnh nhỏ trên Bàn dựng (skill phim-ban-dung); timeline có `_chinhTay` là nguồn sự thật, không sinh lại.
- Chưa có "nghiệm thu máy: ĐẠT" thì chưa nói "xong" (chi tiết: `skills/_chung/nghiem-thu-dung-y.md`).
- Báo giao: tên file, đúng thư mục clip trong `Thanh pham/`, thời lượng, dung lượng, chapters nếu có, dòng ghi công nhạc nếu dùng track CC-BY.
- Clip vừa qua nghiệm thu thì làm luôn gói đăng tải theo skill phim-dang-tai (ba tiêu đề và mô tả YouTube, status Facebook, ba thumbnail từ khung hình thật, qua `tools/dang-tai.py kiem`), không chờ người dùng nhắc; báo cùng lượt với báo giao. Video và gói đăng tải của mỗi clip nằm chung một thư mục tự đủ `Short NN <slug>/` (NN hai chữ số theo thứ tự dựng), và mọi clip cùng dự án nằm dưới MỘT thư mục mẹ `Thanh pham/<tên dự án>/` (clip dài ở `00 Video day du/`), không tách ngang cấp.

## Khi một khâu hỏng

Bảng từng khâu và mẫu câu báo ở mục "Khi một khâu hỏng" của `docs/QUY-TRINH-KY-THUAT.md`. Ba nguyên tắc: tìm nguyên nhân, sửa, thử lại tối đa một lần; không có cách bù ngầm (khung đứng, mượn cảnh kề, thay hình khác nội dung, hạ ngưỡng đều phải thành lựa chọn của người dùng); hỏng một phần thì phần độc lập vẫn làm tiếp, phần đã xong vẫn giữ. Mỗi skill chỉ ghi thêm điểm riêng của thể loại.

## Khép dự án hoặc khép phiên

- Bản đạt nghiệm thu đặt vào thư mục clip trong `Thanh pham/` (cùng gói đăng tải, md5 khớp); nguồn dựng lưu ở `du-an/<dự án>/`; nháp và rác chỉ dọn sau khi người dùng nói "duyệt"; job JSON đồ họa giữ trong `do-hoa/job/` tới khi giao xong.
- Bài học kỹ thuật mới: một dòng vào đúng chủ đề của `docs/BAI-HOC.md` (kèm dự án, ngày). Bài học làm đổi môi trường, lệnh hay quy ước thì sửa luôn đúng mục của `docs/QUY-TRINH-KY-THUAT.md`; không nối ghi chú có ngày vào cuối file đó.
- Góp ý phong cách của người dùng: một dòng vào sổ tay góp ý của `phong-cach/PHONG-CACH.md`; góp ý lặp lần hai thì sửa nguồn mặc định (brand.json, preset, defaultProps).
- Ẩn dụ hình mới được duyệt: ghi ngay vào `do-hoa-chung/an-du-y-niem.json` (chưa có file thì tạo theo schema ở `skills/phim-infomotion/references/mau-kich-ban.md` mục 4).
- Quy trình của skill cần đổi: theo `skills/_chung/bao-tri-skill.md`.
- Dự án kéo qua nhiều phiên: file hồ sơ của dự án (ví dụ `HO-SO-PHIM.md`, `SO-GOP-Y.md`) phải nói được đang ở bước nào, chờ ai, đã chốt gì, nháp mới nhất tên gì.
