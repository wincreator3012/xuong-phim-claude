import React from 'react';
import {AbsoluteFill, Easing, interpolate, useCurrentFrame, useVideoConfig} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, EASE_GENTLE, ThemeName, resolvePalette} from '../theme';

export type BenefitItem = {
  label: string;
  // Giây - thời điểm mục này xuất hiện (khớp lúc lời thoại nhắc tới nó).
  // Bỏ trống thì các mục sẽ chia đều theo durationInSeconds.
  revealAt?: number;
};

export type BenefitsProps = {
  items: (string | BenefitItem)[];
  theme: ThemeName;
  brand: Brand;
  // 'top'/'bottom': hang ngang giua man hinh (mac dinh cu).
  // 'left'/'right': cot doc bam theo canh, dung khi nguoi noi ngoi giua
  // khung va con nhieu khoang trong hai ben - tranh de nhieu pill/hang doi
  // de len mat khi list co tu 3-4 muc tro len (xem bien-tap.md).
  position?: 'top' | 'bottom' | 'left' | 'right';
  durationInSeconds?: number;
  // false: an vong tron so thu tu - dung khi day la cac tu khoa doc lap,
  // khong phai mot chuoi buoc/tien trinh co thu tu. Mac dinh true (giu
  // hanh vi cu cho cac du an da dung truoc, vd Mo hinh 5A).
  showIndex?: boolean;
  // true: cho phep xuong dong, dung cho MOT cau dai (vd cau Hook lam caption)
  // thay vi tu khoa/cum tu ngan. Mac dinh false (nowrap, hanh vi cu).
  wrap?: boolean;
  // He so nhan them vao co chu/vong tron so/padding - dung khi mac dinh
  // van bi che la nho (xem docs/BAI-HOC.md).
  // Mac dinh 1 (khong doi so voi truoc).
  scale?: number;
};

export const benefitsDefaults: BenefitsProps = {
  items: [
    {label: 'Mục một', revealAt: 0.5},
    {label: 'Mục hai', revealAt: 2},
    {label: 'Mục ba', revealAt: 3.5},
  ],
  theme: 'light',
  brand: DEFAULT_BRAND,
  position: 'top',
  durationInSeconds: 6,
};

// Danh sách "pill" NỀN TRONG SUỐT, hiện dần từng mục đúng lúc được nhắc tới
// trong lời thoại (không phải slide tĩnh) - render alpha webm rồi phủ lên
// video thật, giữ nguyên hình người nói. Mục đã hiện thì lùi về dạng nhỏ,
// mờ hơn (như một chuỗi tiến trình đã đi qua); mục vừa hiện thì nổi bật.
export const Benefits: React.FC<BenefitsProps> = ({
  items,
  theme,
  brand,
  position = 'top',
  showIndex = true,
  wrap = false,
  scale = 1,
}) => {
  const palette = resolvePalette(theme, brand);
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  const {unit, isVertical, pad} = useLayout();
  const isSide = position === 'left' || position === 'right';

  const normalized = items.map((it, i) =>
    typeof it === 'string' ? {label: it, revealAt: undefined as number | undefined, i} : {...it, i},
  );
  const list = normalized.map((it) => {
    const frameAt =
      it.revealAt != null
        ? Math.round(it.revealAt * fps)
        : Math.round((durationInFrames / (normalized.length + 1)) * (it.i + 1));
    return {label: it.label, frame: frameAt};
  });

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent'}}>
      <div
        style={{
          position: 'absolute',
          left: isSide ? undefined : 0,
          right: isSide ? undefined : 0,
          top: position === 'top' ? pad * 0.75 : isSide ? 0 : undefined,
          bottom: position === 'bottom' ? pad * 0.75 : isSide ? 0 : undefined,
          ...(position === 'left' ? {left: pad * 0.7} : null),
          ...(position === 'right' ? {right: pad * 0.7} : null),
          display: 'flex',
          flexDirection: isSide ? 'column' : 'row',
          flexWrap: isSide ? 'nowrap' : 'wrap',
          alignItems: isSide ? (position === 'left' ? 'flex-start' : 'flex-end') : 'center',
          justifyContent: 'center',
          gap: unit * 1.6 * scale,
          padding: isSide ? undefined : `0 ${pad * 0.6}px`,
        }}
      >
        {list.map((it, i) => {
          if (frame < it.frame) return null;
          const localFrame = frame - it.frame;
          const inO = interpolate(localFrame, [0, 16], [0, 1], {
            easing: Easing.bezier(...EASE_GENTLE),
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const y = interpolate(localFrame, [0, 18], [12, 0], {
            easing: Easing.bezier(...EASE_GENTLE),
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const entrance = interpolate(localFrame, [0, 10, 20], [0.88, 1.05, 1], {
            extrapolateLeft: 'clamp',
            extrapolateRight: 'clamp',
          });
          const next = list[i + 1];
          const settle = next
            ? interpolate(frame, [next.frame, next.frame + 16], [1, 0.9], {
                extrapolateLeft: 'clamp',
                extrapolateRight: 'clamp',
              })
            : 1;
          // Muc cuoi cung khong co muc ke tiep: tu mo dan bien mat truoc khi
          // composition ket thuc, thay vi dung yen toi frame cuoi (dung cho
          // overlay tu khoa ngan doc lap, khong phai chuoi tien trinh dai).
          const endFade = next
            ? 1
            : interpolate(
                frame,
                [durationInFrames - 18, durationInFrames - 2],
                [1, 0],
                {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
              );
          const scale = Math.min(entrance, settle);
          const isActive = !next || frame < next.frame + 16;

          const bg = isActive
            ? theme === 'light'
              ? 'rgba(47,93,80,0.92)'
              : 'rgba(199,169,123,0.92)'
            : theme === 'light'
              ? 'rgba(250,247,241,0.85)'
              : 'rgba(21,24,28,0.78)';
          const fg = isActive ? (theme === 'light' ? '#FAF7F1' : '#15181C') : palette.ink;

          return (
            <div
              key={i}
              style={{
                opacity: inO * endFade,
                transform: `translateY(${y}px) scale(${scale})`,
                display: 'flex',
                alignItems: 'center',
                gap: unit * 1.25 * scale,
                backgroundColor: bg,
                borderRadius: wrap ? unit * 3 : 999,
                padding: wrap
                  ? `${unit * 2.2 * scale}px ${unit * 3.6 * scale}px`
                  : `${unit * 1.5 * scale}px ${unit * 3.3 * scale}px`,
                boxShadow: isActive ? '0 6px 22px rgba(0,0,0,0.18)' : 'none',
              }}
            >
              {showIndex ? (
                <div
                  style={{
                    width: unit * 3.1 * scale,
                    height: unit * 3.1 * scale,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontFamily: 'Be Vietnam Pro',
                    fontWeight: 700,
                    fontSize: unit * 2.9 * scale,
                    color: fg,
                    border: `1.5px solid ${fg}`,
                    flexShrink: 0,
                  }}
                >
                  {i + 1}
                </div>
              ) : null}
              <div
                style={{
                  fontFamily: 'Be Vietnam Pro',
                  fontWeight: isActive ? 600 : 500,
                  fontSize: (isVertical ? unit * 4.5 : unit * 4.0) * scale,
                  color: fg,
                  whiteSpace: wrap ? 'normal' : 'nowrap',
                  maxWidth: wrap ? unit * 70 : undefined,
                  textAlign: wrap ? 'center' : undefined,
                  lineHeight: wrap ? 1.35 : undefined,
                }}
              >
                {it.label}
              </div>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
