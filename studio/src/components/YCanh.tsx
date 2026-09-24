import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {Canvas, FadeUp} from '../common';

// Cảnh Câu chuyện [YCanh] - khác YNiem ở chỗ mỗi "variant" là MỘT cảnh vẽ tay
// riêng, không dùng chung một khuôn "vẽ nét rồi hiện nhãn". Dùng khi một đoạn
// kể chuyện (nhiều nhịp liên tiếp, thường trong một chương "Câu chuyện" hay
// "Hành trình" của video infomotion) cần mỗi nhịp có một kỹ thuật chuyển động
// RIÊNG (chấm bung theo cụm, đếm dồn, nét bút chạy, kim đồng hồ quét, lửa
// lớn dần...) để không đơn điệu, trong khi vẫn giữ chung nhịp thở [easing] và
// bảng màu của brand. Nếu chỉ cần MỘT hình vẽ nét dần cho một khái niệm đơn lẻ
// (không phải một chuỗi nhịp kể chuyện), dùng YNiem thay vì thêm variant mới ở
// đây - xem `skills/phim-infomotion/SKILL.md` mục chọn hình thức theo loại nội
// dung.
//
// Thêm variant mới: viết một sub-component theo đúng khuôn các variant dưới
// đây (nhận `frame` + các màu cần dùng từ `palette`, vẽ trong viewBox 0 0 100
// 100, nét 3px qua StrokePath hoặc drawProgress), đăng ký trong `YCanhVariant`,
// `VARIANT_LABEL_FRAME`, `VARIANT_LABEL_DURATION`, `yCanhSuggestedSeconds` và
// nhánh switch trong component chính - rồi làm theo 5 bước "Thêm component
// mới" của `skills/phim-do-hoa/SKILL.md` (tsc sạch, still tiếng Việt có dấu,
// commit về máy ngay).

// Ba tông phụ cho cụm chấm nhiều nhóm (variant hub-branches) - cùng họ với
// accent chính để không phá bảng màu, chỉ thêm sắc để phân biệt nhóm, không
// dùng màu rực.
const DOT_COLORS = ['#2F5D50', '#B0663F', '#B98A2E'];

const EASE_DRAW: [number, number, number, number] = [0.22, 1, 0.36, 1];
const EASE_POP: [number, number, number, number] = [0.34, 1.56, 0.64, 1];

const drawProgress = (frame: number, from: number, len: number) =>
  interpolate(frame, [from, from + len], [0, 1], {
    easing: Easing.bezier(...EASE_DRAW),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

const StrokePath: React.FC<{d: string; progress: number; color: string; width?: number}> = ({
  d,
  progress,
  color,
  width = 3,
}) => (
  <path
    d={d}
    fill="none"
    stroke={color}
    strokeWidth={width}
    strokeLinecap="round"
    strokeLinejoin="round"
    pathLength={1}
    strokeDasharray={1}
    strokeDashoffset={1 - progress}
  />
);

export type YCanhVariant =
  | 'hub-branches'
  | 'filling-grid'
  | 'radiant-sun'
  | 'rising-moon'
  | 'growing-bars'
  | 'tick-cluster'
  | 'clock-sweep'
  | 'growing-flame';

export type YCanhProps = {
  variant: YCanhVariant;
  label: string;
  sublabel?: string;
  theme: ThemeName;
  brand: Brand;
  floating?: boolean;
  // 'center' canh giữa cả hai trục - mặc định vì dồn hết hình lên nửa trên
  // khung để nửa dưới trống thường bị chê "không cân bằng".
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  durationInSeconds?: number;
};

export const yCanhDefaults: YCanhProps = {
  variant: 'hub-branches',
  label: 'Một người, nhiều việc cùng lúc',
  sublabel: undefined,
  theme: 'light',
  brand: DEFAULT_BRAND,
  floating: false,
  position: 'bottom',
};

// --- 1. hub-branches ---------------------------------------------------------
// Thân chữ Y vẽ nét dần, rồi ở BA đầu nhánh bung ra một cụm chấm tròn màu
// riêng - một trung tâm gánh nhiều việc/vai trò cùng lúc, mỗi cụm là một việc,
// người/vật ở giữa ôm cả ba. Dùng cho ý niệm "đa nhiệm", "một mình xoay nhiều
// đầu việc", "một vai trò trung tâm nuôi nhiều nhánh".
const HubBranches: React.FC<{frame: number; ink: string}> = ({frame, ink}) => {
  const hub = [
    'M50,50 C40,38 30,28 22,18',
    'M50,50 C60,38 70,28 78,18',
    'M50,50 C50,62 50,74 50,86',
  ];
  const drawFrames = 34;
  const dotStart = 40;
  const clusters = [
    {cx: 16, cy: 10, color: DOT_COLORS[0]},
    {cx: 84, cy: 10, color: DOT_COLORS[1]},
    {cx: 50, cy: 94, color: DOT_COLORS[2]},
  ];
  const dotOffsets = [
    [-8, -4], [0, -9], [8, -4], [-6, 4], [6, 4], [0, 1], [-4, -1], [4, -1], [0, 7],
  ];

  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{overflow: 'visible'}}>
      {hub.map((d, i) => (
        <StrokePath key={d} d={d} color={ink} progress={drawProgress(frame, i * (drawFrames / 3), drawFrames / 3)} />
      ))}
      {clusters.map((c, ci) =>
        dotOffsets.map(([dx, dy], di) => {
          const pop = dotStart + ci * 5 + di * 3;
          const s = interpolate(frame, [pop, pop + 12], [0, 1], {
            easing: Easing.bezier(...EASE_POP),
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          return (
            <circle key={`${ci}-${di}`} cx={c.cx + dx} cy={c.cy + dy} r={3.6 * s} fill={c.color} opacity={0.85} />
          );
        }),
      )}
    </svg>
  );
};

// --- 2. filling-grid -----------------------------------------------------
// Lưới chấm lấp dần theo hàng như một khán phòng đông lên, kèm số đếm dồn tới
// một mốc lớn đúng lúc chấm cuối cùng bung ra. Dùng cho ý niệm "quy mô lớn
// dần", "số lượng tích luỹ", "đông người/nhiều đơn vị theo thời gian".
const GRID_COLS = 9;
const GRID_ROWS = 5;

const FillingGrid: React.FC<{frame: number; accent: string; unit: number}> = ({frame, accent, unit}) => {
  const totalDots = GRID_COLS * GRID_ROWS;
  const fillFrames = 90;
  const count = Math.round(
    interpolate(frame, [0, fillFrames], [0, 108], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }),
  );
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6%', width: '100%', height: '100%', justifyContent: 'center'}}>
      <svg width="94%" height="auto" viewBox="0 0 100 56" style={{overflow: 'visible'}}>
        {Array.from({length: totalDots}).map((_, idx) => {
          const row = Math.floor(idx / GRID_COLS);
          const col = idx % GRID_COLS;
          const centerDist = Math.abs(col - (GRID_COLS - 1) / 2);
          const order = row * GRID_COLS + centerDist * 1.2;
          const pop = (order / (totalDots * 1.1)) * fillFrames;
          const s = interpolate(frame, [pop, pop + 8], [0, 1], {
            easing: Easing.bezier(...EASE_POP),
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const x = 6 + col * (88 / (GRID_COLS - 1));
          const y = 8 + (GRID_ROWS - 1 - row) * (40 / (GRID_ROWS - 1));
          return <circle key={idx} cx={x} cy={y} r={3.4 * s} fill={accent} opacity={0.82} />;
        })}
      </svg>
      <div style={{fontFamily: 'Lora', fontWeight: 700, fontSize: unit * 4.4, color: accent, fontVariantNumeric: 'tabular-nums'}}>
        {count}+
      </div>
    </div>
  );
};

// --- 3. radiant-sun -----------------------------------------------------------
// Mặt trời vẽ nét dần rồi toả 10 tia sáng bung ra vòng quanh, kèm vầng sáng
// đập nhịp liên tục. Dùng cho ý niệm "năng lượng, sung sức", "toả sáng, rực
// rỡ", "còn nhiều đà, còn trẻ khoẻ" - tránh dùng cho ý niệm cần cảm giác trầm,
// tĩnh (không hợp bảng màu/nhịp thở của những ý đó).
const RadiantSun: React.FC<{frame: number; accent: string}> = ({frame, accent}) => {
  const cx = 50;
  const cy = 50;
  const rDisk = 22;
  const rInner = rDisk + 6;
  const rOuter = rDisk + 17;
  const numRays = 10;
  const diskDrawFrames = 48;
  const diskProgress = drawProgress(frame, 0, diskDrawFrames);
  const rayStagger = 6;
  const rayDrawDur = 16;
  const glowOpacity = interpolate(frame, [diskDrawFrames, diskDrawFrames + 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const pulse = 0.5 + 0.5 * Math.sin(Math.max(0, frame - diskDrawFrames) / 7);
  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{overflow: 'visible'}}>
      {frame >= diskDrawFrames ? (
        <circle cx={cx} cy={cy} r={rDisk + 10 + pulse * 8} fill={accent} opacity={glowOpacity * (0.18 + pulse * 0.1)} />
      ) : null}
      <circle cx={cx} cy={cy} r={rDisk - 6} fill={accent} opacity={0.16 * diskProgress} />
      <circle
        cx={cx}
        cy={cy}
        r={rDisk}
        fill="none"
        stroke={accent}
        strokeWidth={3.2}
        pathLength={1}
        strokeDasharray={1}
        strokeDashoffset={1 - diskProgress}
      />
      {Array.from({length: numRays}).map((_, i) => {
        const angle = (i / numRays) * 2 * Math.PI - Math.PI / 2;
        const from = diskDrawFrames + i * rayStagger;
        const t = interpolate(frame, [from, from + rayDrawDur], [0, 1], {
          easing: Easing.bezier(...EASE_POP),
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        const x1 = cx + rInner * Math.cos(angle);
        const y1 = cy + rInner * Math.sin(angle);
        const x2 = cx + (rInner + (rOuter - rInner) * t) * Math.cos(angle);
        const y2 = cy + (rInner + (rOuter - rInner) * t) * Math.sin(angle);
        return (
          <line
            key={i}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke={accent}
            strokeWidth={2.6}
            strokeLinecap="round"
            opacity={interpolate(t, [0, 0.3, 1], [0, 1, 1])}
          />
        );
      })}
    </svg>
  );
};

// --- 4. rising-moon --------------------------------------------------------
// Trăng khuyết từ từ NHÔ LÊN CAO (dịch chuyển translateY trong lúc vẽ nét,
// dừng hẳn khi vẽ xong) rồi mới tới lượt TRANG GIẤY hiện dần từng dòng bên
// dưới, cách biệt hẳn với vùng trăng. Dùng cho ý niệm "làm việc/học tập ban
// đêm", "một khoảng lặng riêng tư trước khi tạo ra điều gì đó". Hai lớp
// chuyển động (trăng rồi mới tới chữ) PHẢI tách biệt cả về không gian (trăng
// chỉ chiếm y~10-40, chữ chỉ bắt đầu từ y=50) lẫn thời gian (chữ chỉ bắt đầu
// sau khi trăng đã yên vị) - gộp chung dễ chồng lấn nếu không cẩn thận.
const WRITE_LINES = [62, 74, 45, 68, 38, 71, 55, 26, 64, 33];

const RisingMoon: React.FC<{frame: number; ink: string; inkSoft: string}> = ({frame, ink, inkSoft}) => {
  const moonSettleFrame = 34;
  const moonA = drawProgress(frame, 0, 30);
  const moonB = drawProgress(frame, 6, 28);
  const riseOffset = interpolate(frame, [0, moonSettleFrame], [20, 0], {
    easing: Easing.bezier(...EASE_DRAW),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const base = 40;
  const lineGap = 5.5;
  const lineDraw = 11;
  const startY = 50;
  const stepY = 5.2;
  const lastStart = base + (WRITE_LINES.length - 1) * lineGap;
  const lastEnd = lastStart + lineDraw;
  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{overflow: 'visible'}}>
      <g transform={`translate(0,${riseOffset})`}>
        <StrokePath d="M40,10 C25,11.8 18,20.4 22,28.3 C26,36.2 40,39.9 52,37.4" color={ink} progress={moonA} width={2.4} />
        <StrokePath d="M40,10 C34,14.3 32,22.8 38,30.1" color={ink} progress={moonB} width={2.4} />
      </g>
      {WRITE_LINES.map((w, i) => {
        const from = base + i * lineGap;
        const p = drawProgress(frame, from, lineDraw);
        const y = startY + i * stepY;
        return <StrokePath key={i} d={`M12,${y} L${12 + w},${y}`} color={i === 0 ? ink : inkSoft} progress={p} width={2.2} />;
      })}
      {/* đầu bút - một chấm nhỏ chạy trên đúng dòng đang viết, tắt khi cả trang đã xong */}
      {frame < lastEnd ? (
        (() => {
          const activeIdx = Math.min(WRITE_LINES.length - 1, Math.max(0, Math.floor((frame - base) / lineGap)));
          const from = base + activeIdx * lineGap;
          const p = drawProgress(frame, from, lineDraw);
          const y = startY + activeIdx * stepY;
          return <circle cx={12 + WRITE_LINES[activeIdx] * p} cy={y} r={p > 0.02 && p < 0.98 ? 2.2 : 0} fill={ink} />;
        })()
      ) : null}
    </svg>
  );
};

// --- 5. growing-bars --------------------------------------------------------
// Bảy vạch ngang (dài ngắn xen kẽ, hai tông đậm/nhạt xen kẽ như văn bản thật)
// mọc dần từng cái một như một trang đang đầy lên, một con số chạy song song.
// Dùng cho ý niệm "sản lượng/khối lượng tích luỹ đều đặn theo thời gian" (số
// từ viết mỗi ngày, số trang, số đơn vị công việc).
const GrowingBars: React.FC<{frame: number; accent: string; ink: string; unit: number}> = ({frame, accent, ink, unit}) => {
  const bars = [
    {y: 8, w: 34},
    {y: 22, w: 58},
    {y: 36, w: 74},
    {y: 50, w: 44},
    {y: 64, w: 82},
    {y: 78, w: 36},
    {y: 92, w: 64},
  ];
  const count = Math.round(
    interpolate(frame, [10, 96], [0, 1240], {
      easing: Easing.out(Easing.cubic),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }),
  );
  return (
    <div style={{display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '6%', width: '100%', height: '100%', justifyContent: 'center'}}>
      <svg width="88%" height="auto" viewBox="0 0 100 108" style={{overflow: 'visible'}}>
        {bars.map((b, i) => {
          const p = drawProgress(frame, i * 12, 24);
          return (
            <line
              key={i}
              x1={10}
              y1={b.y}
              x2={10 + b.w * p}
              y2={b.y}
              stroke={i % 2 === 0 ? accent : ink}
              strokeWidth={4.4}
              strokeLinecap="round"
              opacity={i % 2 === 0 ? 0.95 : 0.5}
            />
          );
        })}
      </svg>
      <div style={{fontFamily: 'Lora', fontWeight: 700, fontSize: unit * 4.6, color: accent, fontVariantNumeric: 'tabular-nums'}}>
        {count.toLocaleString('vi-VN')}+
      </div>
    </div>
  );
};

// --- 6. tick-cluster -------------------------------------------------------------
// KHÔNG PHẢI một dấu tick mà một CHÙM tick - một tick lớn ở giữa (kèm vòng
// sáng loé) và năm tick nhỏ quanh nó, bật lần lượt rất nhanh, dứt khoát. Dùng
// cho ý niệm "nhiều việc cùng khép lại", "hoàn tất một loạt đầu việc" - tránh
// dùng cho "một việc đơn lẻ hoàn thành" (khi đó một tick đơn giản hợp hơn).
const TICK_D = 'M-15,2 L-3,15 L18,-13'; // path gốc, tâm ở (0,0), scale/dịch qua transform
const TickCluster: React.FC<{frame: number; ink: string; accent: string}> = ({frame, ink, accent}) => {
  const hero = interpolate(frame, [0, 16], [0, 1], {
    easing: Easing.bezier(0.3, 1.4, 0.5, 1),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const ringT = interpolate(frame, [14, 38], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const smalls = [
    {cx: 22, cy: 24, scale: 1.5, rot: -12, from: 20},
    {cx: 80, cy: 20, scale: 1.35, rot: 10, from: 30},
    {cx: 12, cy: 62, scale: 1.5, rot: -6, from: 40},
    {cx: 88, cy: 66, scale: 1.35, rot: 6, from: 50},
    {cx: 52, cy: 90, scale: 1.5, rot: 2, from: 60},
  ];
  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{overflow: 'visible'}}>
      <circle cx={50} cy={52} r={14 + ringT * 20} fill="none" stroke={accent} strokeWidth={2} opacity={(1 - ringT) * 0.5} />
      <g transform="translate(50,52) scale(2.0)">
        <StrokePath d={TICK_D} color={ink} progress={hero} width={2.6} />
      </g>
      {smalls.map((s, i) => {
        const p = interpolate(frame, [s.from, s.from + 12], [0, 1], {
          easing: Easing.bezier(0.3, 1.4, 0.5, 1),
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return (
          <g key={i} transform={`translate(${s.cx},${s.cy}) rotate(${s.rot}) scale(${s.scale * 0.42})`}>
            <StrokePath d={TICK_D} color={ink} progress={p} width={4.4} />
          </g>
        );
      })}
    </svg>
  );
};

// --- 7. clock-sweep -----------------------------------------------------------
// Mặt đồng hồ hở một khoảng, quanh mặt có 12 vạch chỉ giờ bật dần lên, một kim
// quét nhanh qua cả mặt rồi dừng đúng khoảng hở, tia sáng bừng lên ở đó. Dùng
// cho ý niệm "một chu kỳ có khuyết" (ngủ ít rồi dậy sớm, một quãng nghỉ ngắn
// giữa một nhịp làm việc dài) - vòng lặp có một điểm gãy, không phải vòng lặp
// đều.
const ClockSweep: React.FC<{frame: number; ink: string; accent: string}> = ({frame, ink, accent}) => {
  const faceProgress = drawProgress(frame, 0, 48);
  const sweepAngle = interpolate(frame, [20, 92], [20, 345], {
    easing: Easing.bezier(...EASE_DRAW),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const rad = (sweepAngle * Math.PI) / 180;
  const cx = 51.5;
  const cy = 51.5;
  const r = 36;
  const hx = cx + r * Math.sin(rad);
  const hy = cy - r * Math.cos(rad);
  const rayOpacity = interpolate(frame, [88, 112], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ticks = Array.from({length: 12}).map((_, i) => i);
  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{overflow: 'visible'}}>
      <StrokePath
        d="M55,15 C75,18 88,35 87,55 C86,75 70,88 50,88 C30,88 15,73 15,53 C15,36 25,22 40,17"
        color={ink}
        progress={faceProgress}
        width={2.6}
      />
      {ticks.map((i) => {
        const a = (i / 12) * 2 * Math.PI;
        const inner = r - 5;
        const outer = r + 1;
        const x1 = cx + inner * Math.sin(a);
        const y1 = cy - inner * Math.cos(a);
        const x2 = cx + outer * Math.sin(a);
        const y2 = cy - outer * Math.cos(a);
        const op = interpolate(frame, [40 + i * 2.8, 52 + i * 2.8], [0, 1], {
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return <line key={i} x1={x1} y1={y1} x2={x2} y2={y2} stroke={ink} strokeWidth={1.6} strokeLinecap="round" opacity={op * 0.55} />;
      })}
      <line x1={cx} y1={cy} x2={hx} y2={hy} stroke={accent} strokeWidth={2.4} strokeLinecap="round" opacity={interpolate(frame, [20, 32], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      <path d="M18,15 L28,24" fill="none" stroke={accent} strokeWidth={3} strokeLinecap="round" opacity={rayOpacity} />
      <path d="M10,26 L20,31" fill="none" stroke={accent} strokeWidth={2.4} strokeLinecap="round" opacity={rayOpacity} />
    </svg>
  );
};

// --- 8. growing-flame -----------------------------------------------------------
// Ngọn lửa vẽ nét dần rồi LỚN DẦN LÊN từ một đốm nhỏ ở đáy, phóng to quanh
// đúng điểm gốc [scale quanh điểm neo] chứ không phải từ tâm khung, rồi lung
// linh liên tục [ambient flicker] để không "đứng hình" nếu ô timeline còn dài.
// Dùng cho ý niệm "ý chí/quyết tâm hình thành dần", "một ngọn lửa nội tâm lớn
// lên theo thời gian" - khác `radiant-sun` ở chỗ đây là một quá trình LỚN DẦN
// từ nhỏ, không phải một trạng thái đã trọn vẹn ngay từ đầu.
const FLAME_OUTER =
  'M50,90 C36,78 30,60 36,44 C39,36 45,30 47,20 C46,30 52,34 52,42 C58,34 62,26 58,16 C68,26 72,38 70,48 C74,62 64,78 50,90 Z';
const FLAME_INNER = 'M50,82 C42,74 39,62 43,52 C45,47 49,43 50,36 C51,43 55,47 56,53 C58,60 56,70 50,82 Z';

const GrowingFlame: React.FC<{frame: number; ink: string; accent: string}> = ({frame, ink, accent}) => {
  const growFrames = 70;
  const growT = interpolate(frame, [0, growFrames], [0.22, 1], {
    easing: Easing.bezier(...EASE_DRAW),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const outerDraw = drawProgress(frame, 0, growFrames * 0.8);
  const innerDraw = drawProgress(frame, growFrames * 0.25, growFrames * 0.75);
  // Lung linh liên tục sau khi lớn đủ, để cảnh không đứng yên suốt ô dài.
  const flicker = frame > growFrames ? 1 + Math.sin((frame - growFrames) / 5) * 0.035 : 1;
  const innerFlicker = frame > growFrames ? 0.75 + Math.sin((frame - growFrames) / 4 + 1) * 0.2 : 0.75 * innerDraw;
  const glowPulse = 0.4 + 0.25 * Math.sin(frame / 9);
  const scale = growT * flicker;
  return (
    <svg width="100%" height="100%" viewBox="0 0 100 100" style={{overflow: 'visible'}}>
      <circle cx={50} cy={55} r={30 * scale} fill={accent} opacity={frame > 6 ? glowPulse * 0.18 : 0} />
      <g transform={`translate(50,92) scale(${scale}) translate(-50,-92)`}>
        <StrokePath d={FLAME_OUTER} color={ink} progress={outerDraw} width={3} />
        <path d={FLAME_INNER} fill={accent} opacity={innerFlicker} />
      </g>
    </svg>
  );
};

// Mốc hiện nhãn chữ cho từng variant. Mỗi ô timeline có NGÂN SÁCH KHUNG do
// `durationInSeconds` quyết định (thường LOCKED để giữ một lịch overlay không
// hở khung đã kiểm chứng trên timeline thật) nên khi cần "chậm nhịp vẽ lại"
// PHẢI tính ngân sách RIÊNG cho từng variant theo đúng durationInFrames của nó
// - không áp một hệ số chậm đồng nhất cho mọi cảnh (xem
// `skills/phim-infomotion/SKILL.md` mục "ngân sách khung"). Mốc luôn đặt SAU
// KHI phần hình vẽ chính đã xong, và labelFrame + label-duration vẫn phải
// xong trước lúc khung bắt đầu mờ dần ở cuối ô (durationInFrames - 14).
const VARIANT_LABEL_FRAME: Record<YCanhVariant, number> = {
  'hub-branches': 90,
  'filling-grid': 100,
  'radiant-sun': 122,
  'rising-moon': 104,
  'growing-bars': 100,
  'tick-cluster': 74,
  'clock-sweep': 118,
  'growing-flame': 80,
};

// Thời lượng hiện chữ [FadeUp duration] - mặc định 22 khung; rút ngắn ở các ô
// eo hẹp để chữ hiện xong gọn trong ngân sách còn lại sau khi đã dồn phần lớn
// khung cho hình vẽ.
const VARIANT_LABEL_DURATION: Record<YCanhVariant, number> = {
  'hub-branches': 16,
  'filling-grid': 22,
  'radiant-sun': 22,
  'rising-moon': 16,
  'growing-bars': 20,
  'tick-cluster': 14,
  'clock-sweep': 22,
  'growing-flame': 22,
};

export const yCanhSuggestedSeconds = (variant: YCanhVariant): number =>
  ({
    'hub-branches': 4.0,
    'filling-grid': 5.3,
    'radiant-sun': 5.4,
    'rising-moon': 4.5,
    'growing-bars': 4.6,
    'tick-cluster': 3.4,
    'clock-sweep': 6.6,
    'growing-flame': 11.8,
  })[variant];

export const YCanh: React.FC<YCanhProps> = ({
  variant,
  label,
  sublabel,
  theme,
  brand,
  floating = false,
  position = 'bottom',
}) => {
  const palette = resolvePalette(theme, brand);
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const {unit, pad, height, width} = useLayout();

  const labelFrame = VARIANT_LABEL_FRAME[variant];

  const scene = (() => {
    switch (variant) {
      case 'hub-branches':
        return <HubBranches frame={frame} ink={palette.ink} />;
      case 'filling-grid':
        return <FillingGrid frame={frame} accent={palette.accent} unit={unit} />;
      case 'radiant-sun':
        return <RadiantSun frame={frame} accent={palette.accent} />;
      case 'rising-moon':
        return <RisingMoon frame={frame} ink={palette.ink} inkSoft={palette.inkSoft} />;
      case 'growing-bars':
        return <GrowingBars frame={frame} accent={palette.accent} ink={palette.ink} unit={unit} />;
      case 'tick-cluster':
        return <TickCluster frame={frame} ink={palette.ink} accent={palette.accent} />;
      case 'clock-sweep':
        return <ClockSweep frame={frame} ink={palette.ink} accent={palette.accent} />;
      case 'growing-flame':
        return <GrowingFlame frame={frame} ink={palette.ink} accent={palette.accent} />;
      default:
        return null;
    }
  })();

  // Nổi gần bằng toàn khung khi dùng làm overlay - kích thước đã kiểm chứng
  // qua dự án thật, không nhỏ hơn.
  const iconBox = (
    <div
      style={{
        width: floating ? unit * 58 : unit * 40,
        height: floating ? unit * 58 : unit * 30,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}
    >
      {scene}
    </div>
  );

  const textBlock = (
    <FadeUp
      from={labelFrame}
      duration={VARIANT_LABEL_DURATION[variant]}
      style={{maxWidth: width * 0.86, padding: `0 ${pad * 0.1}px`}}
    >
      <div
        style={{
          fontFamily: 'Lora',
          fontWeight: 600,
          fontSize: floating ? unit * 6.0 : unit * 5.0,
          color: palette.ink,
          textAlign: 'center',
          lineHeight: 1.2,
        }}
      >
        {label}
      </div>
      {sublabel ? (
        <div
          style={{
            fontFamily: 'Be Vietnam Pro',
            fontWeight: 400,
            fontSize: floating ? unit * 3.9 : unit * 3.2,
            color: palette.inkSoft,
            textAlign: 'center',
            marginTop: unit * (floating ? 0.8 : 1.4),
          }}
        >
          {sublabel}
        </div>
      ) : null}
    </FadeUp>
  );

  const body = (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: unit * (floating ? 1.8 : 2.8),
      }}
    >
      {iconBox}
      {textBlock}
    </div>
  );

  if (floating) {
    const isSide = position === 'left' || position === 'right';
    const isCenter = position === 'center';
    const vInset = pad * 0.75;
    const hInset = pad * 0.7;
    // Mờ dần ở hai biên như Canvas làm cho bản toàn khung - để các cảnh nối
    // tiếp nhau êm, không cắt cứng.
    const fadeIn = 10;
    const fadeOut = 14;
    const opacity = Math.min(
      interpolate(frame, [0, fadeIn], [0, 1], {extrapolateRight: 'clamp'}),
      interpolate(frame, [durationInFrames - fadeOut, durationInFrames - 1], [1, 0], {extrapolateLeft: 'clamp'}),
    );
    return (
      <AbsoluteFill style={{backgroundColor: 'transparent', opacity}}>
        <div
          style={{
            position: 'absolute',
            left: isSide ? undefined : 0,
            right: isSide ? undefined : 0,
            top: position === 'top' ? vInset : isSide || isCenter ? 0 : undefined,
            bottom: position === 'bottom' ? vInset : isSide || isCenter ? 0 : undefined,
            ...(position === 'left' ? {left: hInset} : null),
            ...(position === 'right' ? {right: hInset} : null),
            display: 'flex',
            justifyContent: 'center',
            alignItems: isSide ? (position === 'left' ? 'flex-start' : 'flex-end') : isCenter ? 'center' : undefined,
            width: isSide ? undefined : width,
            height: isSide || isCenter ? height : undefined,
          }}
        >
          {body}
        </div>
      </AbsoluteFill>
    );
  }

  return (
    <Canvas palette={palette} fadeIn={12} fadeOut={18}>
      <AbsoluteFill style={{display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
        {body}
      </AbsoluteFill>
    </Canvas>
  );
};
