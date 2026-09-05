import React from 'react';
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig, Easing} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, EASE_GENTLE, ThemeName, resolvePalette} from '../theme';

export type LowerThirdProps = {
  name: string;
  role?: string;
  theme: ThemeName;
  brand: Brand;
  durationInSeconds?: number;
};

export const lowerThirdDefaults: LowerThirdProps = {
  name: 'Tên người nói',
  role: 'Chức danh - đơn vị',
  theme: 'light',
  brand: DEFAULT_BRAND,
  durationInSeconds: 5,
};

// Bảng tên góc trái dưới, NỀN TRONG SUỐT - render ra webm alpha rồi phủ lên video
export const LowerThird: React.FC<LowerThirdProps> = ({name, role, theme, brand}) => {
  const palette = resolvePalette(theme, brand);
  const frame = useCurrentFrame();
  const {durationInFrames} = useVideoConfig();
  const {unit} = useLayout();

  const inO = interpolate(frame, [0, 18], [0, 1], {
    easing: Easing.bezier(...EASE_GENTLE),
    extrapolateRight: 'clamp',
  });
  const outO = interpolate(frame, [durationInFrames - 16, durationInFrames - 1], [1, 0], {
    extrapolateLeft: 'clamp',
  });
  const x = interpolate(frame, [0, 22], [-24, 0], {
    easing: Easing.bezier(...EASE_GENTLE),
    extrapolateRight: 'clamp',
  });
  const barH = interpolate(frame, [0, 20], [0, 1], {
    easing: Easing.bezier(...EASE_GENTLE),
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{backgroundColor: 'transparent'}}>
      <div
        style={{
          position: 'absolute',
          left: unit * 7,
          bottom: unit * 9,
          display: 'flex',
          alignItems: 'stretch',
          gap: unit * 1.6,
          opacity: Math.min(inO, outO),
          transform: `translateX(${x}px)`,
        }}
      >
        <div
          style={{
            width: unit * 0.55,
            borderRadius: 3,
            backgroundColor: palette.accent,
            transform: `scaleY(${barH})`,
            transformOrigin: 'bottom',
          }}
        />
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            gap: unit * 0.5,
            backgroundColor:
              theme === 'light' ? 'rgba(250,247,241,0.88)' : 'rgba(21,24,28,0.82)',
            padding: `${unit * 1.3}px ${unit * 2.2}px`,
            borderRadius: 6,
          }}
        >
          <div
            style={{
              fontFamily: 'Lora',
              fontWeight: 600,
              fontSize: unit * 3.4,
              color: palette.ink,
              letterSpacing: '0.03em',
            }}
          >
            {name}
          </div>
          {role ? (
            <div
              style={{
                fontFamily: 'Be Vietnam Pro',
                fontWeight: 400,
                fontSize: unit * 2.1,
                color: palette.inkSoft,
                letterSpacing: '0.05em',
              }}
            >
              {role}
            </div>
          ) : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};
