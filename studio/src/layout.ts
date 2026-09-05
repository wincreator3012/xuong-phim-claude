import {useVideoConfig} from 'remotion';

// Kích thước chữ và khoảng đệm tự thích ứng theo khung ngang (16:9) hay dọc (9:16)
export const useLayout = () => {
  const {width, height} = useVideoConfig();
  const isVertical = height > width;
  const unit = Math.min(width, height) / 100; // 1 đơn vị ≈ 1% cạnh ngắn
  return {
    isVertical,
    unit,
    width, // px thật của khung hình - dùng để tính maxWidth theo px (KHÔNG dùng
    // % CSS cho các khối chữ nằm trong FadeUp/flex-column căn giữa: div bọc
    // ngoài không có width cố định nên % sẽ tự resolve theo kích thước co
    // theo nội dung [shrink-to-fit] của chính nó, không phải theo khung hình,
    // khiến chữ NGẮN bị ngắt dòng sai dù còn thừa rất nhiều chỗ trống)
    height,
    pad: isVertical ? unit * 10 : unit * 12,
    titleSize: isVertical ? unit * 7.4 : unit * 8.2,
    subtitleSize: isVertical ? unit * 3.9 : unit * 4.0,
    bodySize: isVertical ? unit * 4.2 : unit * 4.4,
    smallSize: isVertical ? unit * 3.0 : unit * 3.0,
  };
};
