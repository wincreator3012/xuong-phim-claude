import React from 'react';
import {
  AbsoluteFill,
  Img,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from 'remotion';
import {Brand, EASE_GENTLE, FONT_BODY, Palette, normalizeLogos} from './theme';

export const ease = (
  frame: number,
  from: number,
  to: number,
  outFrom = 0,
  outTo = 1,
) =>
  interpolate(frame, [from, to], [outFrom, outTo], {
    easing: Easing.bezier(...EASE_GENTLE),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

// Hiện dần + trồi nhẹ lên: chuyển động đặc trưng của toàn bộ hệ đồ họa
export const FadeUp: React.FC<{
  from: number;
  duration?: number;
  distance?: number;
  children: React.ReactNode;
  style?: React.CSSProperties;
}> = ({from, duration = 28, distance = 26, children, style}) => {
  const frame = useCurrentFrame();
  const o = ease(frame, from, from + duration);
  const y = ease(frame, from, from + duration, distance, 0);
  return (
    <div style={{opacity: o, transform: `translateY(${y}px)`, ...style}}>
      {children}
    </div>
  );
};

// Nền + mờ dần vào/ra ở hai biên để ghép cảnh êm (cắt thẳng vẫn mượt)
export const Canvas: React.FC<{
  palette: Palette;
  fadeIn?: number;
  fadeOut?: number;
  children: React.ReactNode;
}> = ({palette, fadeIn = 12, fadeOut = 18, children}) => {
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const opacity =
    Math.min(
      fadeIn > 0 ? interpolate(frame, [0, fadeIn], [0, 1], {extrapolateRight: 'clamp'}) : 1,
      fadeOut > 0
        ? interpolate(
            frame,
            [durationInFrames - fadeOut, durationInFrames - 1],
            [1, 0],
            {extrapolateLeft: 'clamp'},
          )
        : 1,
    );
  return (
    <AbsoluteFill style={{backgroundColor: palette.bg}}>
      <AbsoluteFill style={{opacity, fontFamily: FONT_BODY}}>{children}</AbsoluteFill>
    </AbsoluteFill>
  );
};

// Đường kẻ nhấn mảnh, "vẽ" ra từ giữa
export const AccentLine: React.FC<{
  palette: Palette;
  from: number;
  width?: number;
}> = ({palette, from, width = 84}) => {
  const frame = useCurrentFrame();
  const w = ease(frame, from, from + 30, 0, width);
  return (
    <div
      style={{
        height: 3,
        width: w,
        backgroundColor: palette.accent,
        borderRadius: 2,
      }}
    />
  );
};

// Hàng 1-3 logo, chuẩn hóa theo chiều cao, ngăn cách bằng vạch mảnh.
// mono=true: chuyển logo về đơn sắc màu mực (dùng cho theme tối - logo màu
// gốc thường chìm trên nền than; đơn sắc kem giữ được sự thanh lịch).
export const LogoRow: React.FC<{
  brand: Brand;
  palette: Palette;
  height: number;
  mono?: boolean;
  style?: React.CSSProperties;
}> = ({brand, palette, height, mono = false, style}) => {
  const logos = normalizeLogos(brand);
  if (logos.length === 0) {
    return null;
  }
  const inkIsLight = parseInt(palette.ink.slice(1, 3), 16) > 0x88;
  const monoFilter = inkIsLight
    ? // mực sáng (theme tối): logo trắng kem
      'brightness(0) saturate(100%) invert(93%) sepia(7%) saturate(300%) hue-rotate(10deg)'
    : // mực tối (theme sáng): logo than chì
      'brightness(0) saturate(100%) invert(13%)';
  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: height * 0.66,
        ...style,
      }}
    >
      {logos.map((l, i) => (
        <React.Fragment key={l.file}>
          {i > 0 ? (
            <div
              style={{
                width: 1.5,
                height: height * 0.72,
                backgroundColor: palette.line,
                flexShrink: 0,
              }}
            />
          ) : null}
          <Img
            src={staticFile(`brand/${l.file}`)}
            style={{
              height: height * (l.scale ?? 1),
              maxWidth: height * 4.2,
              objectFit: 'contain',
              filter: mono ? monoFilter : undefined,
              opacity: mono ? 0.92 : 1,
            }}
          />
        </React.Fragment>
      ))}
    </div>
  );
};

// Khối mã QR: nền trắng bo góc + chú thích dưới - dùng chung cho Intro/Outro
export const QrPlate: React.FC<{
  qrFile: string;
  qrCaption?: string;
  palette: Palette;
  size: number;
}> = ({qrFile, qrCaption, palette, size}) => (
  <div
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      gap: size * 0.09,
    }}
  >
    <div
      style={{
        backgroundColor: '#FFFFFF',
        padding: size * 0.09,
        borderRadius: size * 0.06,
        border: `1.5px solid ${palette.line}`,
        display: 'flex',
      }}
    >
      <Img
        src={staticFile(`brand/${qrFile}`)}
        style={{width: size, height: size, objectFit: 'contain'}}
      />
    </div>
    {qrCaption ? (
      <div
        style={{
          fontSize: size * 0.115,
          fontWeight: 500,
          color: palette.inkSoft,
          letterSpacing: '0.08em',
        }}
      >
        {qrCaption}
      </div>
    ) : null}
  </div>
);

// Khối thương hiệu: logo (nếu có) + tên + chức danh
export const BrandBlock: React.FC<{
  brand: Brand;
  palette: Palette;
  size?: number;
  showTagline?: boolean;
}> = ({brand, palette, size = 30, showTagline = false}) => {
  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: size * 0.45,
      }}
    >
      {brand.logoFile ? (
        <Img
          src={staticFile(`brand/${brand.logoFile}`)}
          style={{height: size * 2.4, objectFit: 'contain'}}
        />
      ) : null}
      <div
        style={{
          fontFamily: 'Lora',
          fontWeight: 600,
          fontSize: size,
          color: palette.ink,
          letterSpacing: '0.06em',
        }}
      >
        {brand.name}
        {brand.credentials ? (
          <span
            style={{
              fontFamily: 'Be Vietnam Pro',
              fontWeight: 400,
              fontSize: size * 0.62,
              color: palette.inkSoft,
              marginLeft: size * 0.5,
              letterSpacing: '0.04em',
            }}
          >
            {brand.credentials}
          </span>
        ) : null}
      </div>
      {showTagline && brand.tagline ? (
        <div
          style={{
            fontFamily: 'Be Vietnam Pro',
            fontWeight: 400,
            fontSize: size * 0.6,
            color: palette.inkSoft,
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
          }}
        >
          {brand.tagline}
        </div>
      ) : null}
    </div>
  );
};
