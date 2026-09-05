import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {AccentLine, Canvas, FadeUp} from '../common';

export type SectionTitleProps = {
  kicker?: string; // ví dụ "Phần 2"
  title: string;
  theme: ThemeName;
  brand: Brand;
  durationInSeconds?: number;
};

export const sectionTitleDefaults: SectionTitleProps = {
  kicker: 'Phần 1',
  title: 'Tên phần',
  theme: 'light',
  brand: DEFAULT_BRAND,
  durationInSeconds: 4,
};

export const SectionTitle: React.FC<SectionTitleProps> = ({
  kicker,
  title,
  theme,
  brand,
}) => {
  const palette = resolvePalette(theme, brand);
  const {pad, titleSize, smallSize, isVertical} = useLayout();
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
              maxWidth: isVertical ? '92%' : '76%',
              margin: '0 auto',
            }}
          >
            {title}
          </div>
        </FadeUp>
        <FadeUp from={34} duration={22} distance={0}>
          <AccentLine palette={palette} from={0} width={70} />
        </FadeUp>
      </AbsoluteFill>
    </Canvas>
  );
};
