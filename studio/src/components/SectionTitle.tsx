import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {AccentLine, Canvas, FadeUp, LogoRow} from '../common';

export type SectionTitleProps = {
  kicker?: string; // ví dụ "Phần 2"
  title: string;
  theme: ThemeName;
  brand: Brand;
  showLogos?: boolean; // hiện hàng logo nhỏ ở đáy (mặc định false - dùng khi
  // slide chuyển cần nhắc nhà tài trợ/đối tác, vd phim tài liệu phỏng vấn)
  logoMono?: boolean; // ép logo đơn sắc; mặc định: theme tối = true
  durationInSeconds?: number;
};

export const sectionTitleDefaults: SectionTitleProps = {
  kicker: 'Phần 1',
  title: 'Tên phần',
  theme: 'light',
  brand: DEFAULT_BRAND,
  showLogos: false,
  durationInSeconds: 4,
};

export const SectionTitle: React.FC<SectionTitleProps> = ({
  kicker,
  title,
  theme,
  brand,
  showLogos = false,
  logoMono,
}) => {
  const palette = resolvePalette(theme, brand);
  const {pad, titleSize, smallSize, isVertical, width, unit} = useLayout();
  const mono = logoMono ?? theme === 'dark';
  return (
    <Canvas palette={palette} fadeIn={12} fadeOut={16}>
      <AbsoluteFill
        style={{
          padding: pad,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: titleSize * 0.45,
        }}
      >
        {kicker ? (
          <FadeUp from={8} duration={24}>
            <div
              style={{
                fontSize: smallSize,
                fontWeight: 500,
                color: palette.accent,
                letterSpacing: '0.26em',
                textTransform: 'uppercase',
              }}
            >
              {kicker}
            </div>
          </FadeUp>
        ) : null}
        <FadeUp from={16} duration={30}>
          <div
            style={{
              fontFamily: 'Lora',
              fontWeight: 600,
              fontSize: titleSize * 0.86,
              color: palette.ink,
              lineHeight: 1.25,
              maxWidth: width * (isVertical ? 0.92 : 0.76),
              margin: '0 auto',
              whiteSpace: 'pre-line',
            }}
          >
            {title}
          </div>
        </FadeUp>
        <FadeUp from={34} duration={22} distance={0}>
          <AccentLine palette={palette} from={0} width={70} />
        </FadeUp>
      </AbsoluteFill>
      {showLogos ? (
        <AbsoluteFill
          style={{
            justifyContent: 'flex-end',
            alignItems: 'center',
            paddingBottom: pad * 0.6,
          }}
        >
          <FadeUp from={30} duration={26} distance={12}>
            <LogoRow
              brand={brand}
              palette={palette}
              height={unit * (isVertical ? 4.5 : 5)}
              mono={mono}
            />
          </FadeUp>
        </AbsoluteFill>
      ) : null}
    </Canvas>
  );
};
