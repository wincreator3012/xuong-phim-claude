import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, Easing} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, EASE_GENTLE, ThemeName, resolvePalette} from '../theme';
import {AccentLine, Canvas, FadeUp} from '../common';

export type InfoStatProps = {
  value: number; // con số đích
  prefix?: string;
  suffix?: string; // ví dụ "%", "+", " năm"
  label: string;
  decimals?: number;
  theme: ThemeName;
  brand: Brand;
  durationInSeconds?: number;
};

export const infoStatDefaults: InfoStatProps = {
  value: 85,
  suffix: '%',
  label: 'Mô tả ý nghĩa của con số',
  decimals: 0,
  theme: 'light',
  brand: DEFAULT_BRAND,
  durationInSeconds: 6,
};

export const InfoStat: React.FC<InfoStatProps> = ({
  value,
  prefix,
  suffix,
  label,
  decimals = 0,
  theme,
  brand,
}) => {
  const palette = resolvePalette(theme, brand);
  const frame = useCurrentFrame();
  const {pad, titleSize, bodySize, isVertical} = useLayout();
  const n = interpolate(frame, [12, 60], [0, value], {
    easing: Easing.bezier(...EASE_GENTLE),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  const shown = n.toLocaleString('vi-VN', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return (
    <Canvas palette={palette} fadeIn={12} fadeOut={18}>
      <AbsoluteFill
        style={{
          padding: pad,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: bodySize,
        }}
      >
        <FadeUp from={6} duration={24}>
          <div
            style={{
              fontFamily: 'Lora',
              fontWeight: 600,
              fontSize: titleSize * 1.6,
              color: palette.accent,
              lineHeight: 1.1,
              fontVariantNumeric: 'tabular-nums',
            }}
          >
            {prefix ?? ''}
            {shown}
            {suffix ?? ''}
          </div>
        </FadeUp>
        <FadeUp from={30} duration={24} distance={0}>
          <AccentLine palette={palette} from={0} width={60} />
        </FadeUp>
        <FadeUp from={40} duration={28}>
          <div
            style={{
              fontSize: bodySize,
              fontWeight: 400,
              color: palette.ink,
              lineHeight: 1.45,
              maxWidth: isVertical ? '92%' : '60%',
              margin: '0 auto',
            }}
          >
            {label}
          </div>
        </FadeUp>
      </AbsoluteFill>
    </Canvas>
  );
};
