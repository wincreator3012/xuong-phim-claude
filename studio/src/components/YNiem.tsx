import React, {useMemo} from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {Canvas, FadeUp} from '../common';
import {getYNiem} from '../y-niem';

export type YNiemProps = {
  // Tên hình trong kho src/y-niem/index.ts
  slug: string;
  label: string;
  sublabel?: string;
  theme: ThemeName;
  brand: Brand;
  // Giây để vẽ xong toàn bộ nét (chia đều cho số đường trong shape)
  drawSeconds?: number;
  // Giây nhãn chữ xuất hiện (mặc định: ngay sau khi vẽ xong)
  labelAt?: number;
  // true: nền trong suốt, hình nhỏ, dùng như overlay nổi
  floating?: boolean;
  // Vị trí khi floating=true - 'center' canh giữa cả hai trục, mặc định vì
  // dồn hết hình lên nửa trên khung để nửa dưới trống thường bị chê "không
  // cân bằng"
  position?: 'top' | 'bottom' | 'left' | 'right' | 'center';
  durationInSeconds?: number;
};

export const yNiemDefaults: YNiemProps = {
  slug: 'duong-tang',
  label: 'Tăng trưởng',
  sublabel: undefined,
  theme: 'light',
  brand: DEFAULT_BRAND,
  drawSeconds: 1.2,
  labelAt: 1.4,
  floating: false,
  position: 'bottom',
};

// Easing "vẽ tay" - chậm rãi, không nảy; easing "bật ra" - dùng cho mũi tên
// endArrow bung ra ở cuối đường.
const EASE_DRAW: [number, number, number, number] = [0.22, 1, 0.36, 1];
const EASE_POP: [number, number, number, number] = [0.34, 1.56, 0.64, 1];

type CubicSeg = {
  p0: [number, number];
  p1: [number, number];
  p2: [number, number];
  p3: [number, number];
};

// Phân tích một path "M x,y C x1,y1 x2,y2 x3,y3 C ..." (một M rồi một hay
// nhiều đoạn cong bậc ba nối tiếp) thành danh sách đoạn cong - TỔNG QUÁT cho
// mọi path viết đúng cú pháp này trong y-niem/index.ts, không hard-code toạ độ
// của một shape cụ thể. Path không đúng dạng (có L/Q/A xen giữa, ít hơn 8 số
// sau M) trả về mảng rỗng - travelDot/endArrow lặng lẽ không hiện, không lỗi.
const parseCubicPath = (d: string): CubicSeg[] => {
  const nums = (d.match(/-?\d*\.?\d+/g) ?? []).map(Number);
  if (nums.length < 8) return [];
  const segs: CubicSeg[] = [];
  let cur: [number, number] = [nums[0], nums[1]];
  for (let i = 2; i + 5 < nums.length; i += 6) {
    const p1: [number, number] = [nums[i], nums[i + 1]];
    const p2: [number, number] = [nums[i + 2], nums[i + 3]];
    const p3: [number, number] = [nums[i + 4], nums[i + 5]];
    segs.push({p0: cur, p1, p2, p3});
    cur = p3;
  }
  return segs;
};

// Điểm trên một đoạn cong bezier bậc 3 tại tham số t (0-1).
const cubicPoint = (s: CubicSeg, t: number): [number, number] => {
  const mt = 1 - t;
  const x = mt * mt * mt * s.p0[0] + 3 * mt * mt * t * s.p1[0] + 3 * mt * t * t * s.p2[0] + t * t * t * s.p3[0];
  const y = mt * mt * mt * s.p0[1] + 3 * mt * mt * t * s.p1[1] + 3 * mt * t * t * s.p2[1] + t * t * t * s.p3[1];
  return [x, y];
};

// Đạo hàm (hướng tiếp tuyến) tại t=1 của một đoạn cong - dùng để xoay mũi tên
// đúng theo chiều đường đang đi tới ở điểm cuối.
const cubicEndTangent = (s: CubicSeg): number => {
  const dx = 3 * (s.p3[0] - s.p2[0]);
  const dy = 3 * (s.p3[1] - s.p2[1]);
  return (Math.atan2(dy, dx) * 180) / Math.PI;
};

// Điểm trên TOÀN BỘ path (nhiều đoạn cong nối tiếp) tại tham số t (0-1) toàn
// cục - chia đều t cho số đoạn, dùng cho chấm trôi đi hết cả path multi-segment.
const pointOnPath = (segs: CubicSeg[], t: number): [number, number] => {
  if (segs.length === 0) return [0, 0];
  const scaled = Math.min(segs.length, Math.max(0, t * segs.length));
  const idx = Math.min(segs.length - 1, Math.floor(scaled));
  const localT = scaled - idx;
  return cubicPoint(segs[idx], localT);
};

export const YNiem: React.FC<YNiemProps> = ({
  slug,
  label,
  sublabel,
  theme,
  brand,
  drawSeconds = 1.2,
  labelAt,
  floating = false,
  position = 'bottom',
}) => {
  const palette = resolvePalette(theme, brand);
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const {unit, pad, height, width} = useLayout();
  const shape = getYNiem(slug);

  const drawFrames = Math.max(1, Math.round(drawSeconds * fps));
  const labelFrame = Math.round((labelAt ?? drawSeconds + 0.2) * fps);
  const segFrames = drawFrames / shape.paths.length;

  // Nổi gần bằng toàn khung khi dùng làm overlay - kích thước đã kiểm chứng
  // qua dự án thật, không nhỏ hơn.
  const iconSize = floating ? unit * 58 : unit * 44;
  const strokeW = 3;

  // Chấm trôi + mũi tên cuối đường: áp dụng cho PATH CUỐI CÙNG trong mảng
  // (path được vẽ sau cùng), tính tổng quát bằng parseCubicPath thay vì toạ độ
  // hard-code của một slug cụ thể - bật/tắt qua cờ shape.travelDot/endArrow.
  const lastPathIndex = shape.paths.length - 1;
  const lastPathSegs = useMemo(
    () => parseCubicPath(shape.paths[lastPathIndex] ?? ''),
    [shape.paths, lastPathIndex],
  );
  const lastDrawStart = lastPathIndex * segFrames;
  const lastDrawEnd = lastDrawStart + segFrames;

  const travelActive = Boolean(shape.travelDot) && lastPathSegs.length > 0;
  const travelT = travelActive
    ? interpolate(frame, [lastDrawStart, lastDrawEnd], [0, 1], {
        easing: Easing.linear,
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 0;
  const travelPoint = travelActive ? pointOnPath(lastPathSegs, travelT) : [0, 0];
  const travelBlink = 0.55 + 0.45 * Math.sin(frame / 3.2);
  const travelOpacity = travelActive
    ? interpolate(frame, [lastDrawStart, lastDrawStart + 4, lastDrawEnd - 4, lastDrawEnd], [0, 1, 1, 0], {
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      }) * travelBlink
    : 0;

  const arrowActive = Boolean(shape.endArrow) && lastPathSegs.length > 0;
  const arrowSeg = lastPathSegs[lastPathSegs.length - 1];
  const arrowT = arrowActive
    ? interpolate(frame, [lastDrawEnd - 2, lastDrawEnd + 8], [0, 1], {
        easing: Easing.bezier(...EASE_POP),
        extrapolateLeft: 'clamp',
        extrapolateRight: 'clamp',
      })
    : 0;
  const arrowAngle = arrowActive && arrowSeg ? cubicEndTangent(arrowSeg) : 0;
  const arrowPoint = arrowSeg ? arrowSeg.p3 : [0, 0];

  const icon = (
    <svg width={iconSize} height={iconSize} viewBox="0 0 100 100" style={{overflow: 'visible'}}>
      {shape.paths.map((d, i) => {
        const segStart = i * segFrames;
        const progress = interpolate(frame, [segStart, segStart + segFrames], [0, 1], {
          easing: Easing.bezier(...EASE_DRAW),
          extrapolateLeft: 'clamp',
          extrapolateRight: 'clamp',
        });
        return (
          <path
            key={i}
            d={d}
            fill="none"
            stroke={palette.accent}
            strokeWidth={strokeW}
            strokeLinecap="round"
            strokeLinejoin="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - progress}
          />
        );
      })}
      {travelActive ? (
        <circle cx={travelPoint[0]} cy={travelPoint[1]} r={3.2} fill={palette.accent} opacity={travelOpacity} />
      ) : null}
      {arrowActive ? (
        <g transform={`translate(${arrowPoint[0]},${arrowPoint[1]}) rotate(${arrowAngle}) scale(${arrowT})`}>
          <path
            d="M-9,-6 L2,0 L-9,6"
            fill="none"
            stroke={palette.accent}
            strokeWidth={strokeW}
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </g>
      ) : null}
    </svg>
  );

  const textBlock = (
    <FadeUp from={labelFrame} duration={22} style={{maxWidth: width * 0.86, padding: `0 ${pad * 0.1}px`}}>
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
        gap: unit * (floating ? 1.6 : 3.2),
      }}
    >
      {icon}
      {textBlock}
    </div>
  );

  if (floating) {
    const isSide = position === 'left' || position === 'right';
    const isCenter = position === 'center';
    const vInset = pad * 0.75;
    const hInset = pad * 0.7;
    return (
      <AbsoluteFill style={{backgroundColor: 'transparent'}}>
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

export const yNiemSuggestedSeconds = (drawSeconds = 1.2, labelAt?: number) =>
  Math.max(3, Math.ceil((labelAt ?? drawSeconds + 0.2) + 1.4));
