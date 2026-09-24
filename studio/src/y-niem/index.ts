// Kho ẩn dụ hình vẽ nét dần [YNiem] - mỗi slug là một bộ đường nét đơn giản
// (viewBox 0 0 100 100, nét 3px, không tô đặc) minh hoạ MỘT khái niệm trừu
// tượng bằng một hình ảnh sơ đồ [image schema] quen thuộc: đường đi, trên-dưới,
// chứa đựng, trung tâm-ngoại vi, tầng lớp, vòng lặp... Cách chọn ẩn dụ và bảy
// image schema thường dùng: xem mục "Tra từ điển, đề xuất ẩn dụ mới" trong
// `skills/phim-infomotion/SKILL.md`.
//
// Slug mới thêm vào đây PHẢI có một mục tương ứng trong
// `do-hoa-chung/an-du-y-niem.json` sau khi người dùng duyệt - không để slug
// "mồ côi" (có hình mà không có trong từ điển, hoặc ngược lại).
//
// File này là kho CHUNG cho mọi dự án nên chỉ giữ những ẩn dụ đủ tổng quát để
// dùng lại nhiều lần (một đường đi lên/xuống, một cấu trúc rễ sâu...). Ẩn dụ
// gắn riêng với nội dung của một dự án cụ thể thêm trực tiếp vào file này khi
// dự án đó duyệt xong, kèm chú thích ngắn về khái niệm nó minh hoạ.

export type YNiemShape = {
  // Mỗi phần tử là một nét vẽ riêng, vẽ NỐI TIẾP nhau theo thứ tự trong mảng
  // (không vẽ đồng thời) - đúng cảm giác "vẽ tay từng đường một". Mỗi path là
  // một chuỗi lệnh SVG dạng "M x,y C x1,y1 x2,y2 x3,y3 C ..." (một M rồi một
  // hay nhiều C nối tiếp) - YNiem.tsx phân tích được cú pháp này để tính toán
  // hiệu ứng chấm trôi/mũi tên bên dưới, path dạng L (đường thẳng) hay Q/A vẫn
  // vẽ được nhưng KHÔNG dùng được với travelDot/endArrow.
  paths: string[];
  // Tuỳ chọn: một chấm màu trôi dọc theo PATH CUỐI CÙNG trong mảng trong lúc
  // path đó đang vẽ, chớp tắt theo nhịp - gợi ý chuyển động đang diễn ra dọc
  // đường đi (ví dụ một đà giảm/tăng chưa dừng). Chỉ áp dụng cho path gồm toàn
  // đoạn cong bậc ba (C).
  travelDot?: boolean;
  // Tuỳ chọn: một mũi tên bật ra ở đúng điểm cuối của path cuối cùng, xoay
  // theo đúng tiếp tuyến tại đó, ngay khi path vẽ xong - gợi ý đường đi còn
  // tiếp diễn theo đúng hướng đang tới, không dừng lại ở điểm cuối.
  endArrow?: boolean;
};

const SHAPES: Record<string, YNiemShape> = {
  // Đường đi xuống [đường đi, trên-dưới] - một đà giảm không phải cú rơi đột
  // ngột mà là một độ dốc mòn dần theo thời gian: khởi đầu còn cao, chùng dần
  // về cuối. Có travelDot + endArrow để gợi ý đà giảm CHƯA DỪNG, còn tiếp diễn
  // qua khỏi khung hình.
  'duong-giam': {
    paths: ['M12,22 C34,18 48,32 58,40 C70,50 80,68 92,96'],
    travelDot: true,
    endArrow: true,
  },
  // Đường lên rồi bằng [đường đi, trên-dưới] - đã leo hết biên độ, giờ đi
  // ngang, chạm trần chứ không còn đà - dùng cho ý "đạt đỉnh rồi chững lại".
  'dinh-roi-bang': {
    paths: ['M13,83 C30,50 46,22 62,18 C71,16 80,16 88,16'],
  },
  // Đường đi lên đều [đường đi, trên-dưới] - còn dư địa, càng lúc càng dốc -
  // dùng cho ý "tăng trưởng liên tục, chưa tới hạn".
  'duong-tang': {
    paths: ['M13,85 C33,70 53,48 88,15'],
  },
  // Rễ sâu [trung tâm-ngoại vi, tầng lớp] - KHÔNG phải một đường quỹ đạo như
  // ba hình trên (cố ý khác schema): một thân neo xuống ba rễ toả - hình ảnh
  // về nền tảng không đo bằng đường đi lên/xuống mà bằng độ bám sâu, dùng cho
  // ý "bền vững, có gốc rễ" thay vì "đang chuyển động".
  'goc-re-sau': {
    paths: [
      'M50,18 L50,49',
      'M50,52 C41,61 35,73 29,89',
      'M50,52 C50,66 50,79 50,92',
      'M50,52 C59,61 65,73 71,89',
    ],
  },
};

export const yNiemSlugs = Object.keys(SHAPES);

export const getYNiem = (slug: string): YNiemShape => SHAPES[slug] ?? SHAPES['duong-tang'];
