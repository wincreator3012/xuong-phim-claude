import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {Canvas, FadeUp, ease} from '../common';
import {useCurrentFrame} from 'remotion';

export type InfoStepsProps = {
  title?: string;
  steps: string[];
  theme: ThemeName;
  brand: Brand;
  durationInSeconds?: number;
};

export const infoStepsDefaults: InfoStepsProps = {
  title: 'Tiến trình',
  steps: ['Bước một', 'Bước hai', 'Bước ba'],
  theme: 'light',
  brand: DEFAULT_BRAND,
};

// Sơ đồ tiến trình tối giản: chấm số + nhãn, đường nối mảnh "vẽ" dần
export const InfoSteps: React.FC<InfoStepsProps> = ({title, steps, theme, brand}) => {
  const palette = resolvePalette(theme, brand);
  const frame = useCurrentFrame();
  const {pad, subtitleSize, bodySize, isVertical} = useLayout();
  const start = title ? 36 : 14;
  const stagger = 30;
  const dot = bodySize * 1.7;

  return (
    <Canvas palette={palette} fadeIn={12} fadeOut={18}>
      <AbsoluteFill
        style={{
          padding: pad,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {title ? (
          <FadeUp from={8} duration={26}>
            <div
              style={{
                fontFamily: 'Lora',
                fontWeight: 600,
                fontSize: subtitleSize * 1.35,
                color: palette.ink,
                marginBottom: bodySize * 2,
                textAlign: 'center',
                lineHeight: 1.25,
              }}
            >
              {title}
            </div>
          </FadeUp>
        ) : null}
        <div
          style={{
            display: 'flex',
            flexDirection: isVertical ? 'column' : 'row',
            alignItems: 'flex-start',
            justifyContent: 'center',
            gap: isVertical ? bodySize * 1.15 : bodySize * 0.9,
            width: isVertical ? '100%' : '86%',
            margin: '0 auto',
          }}
        >
          {steps.map((step, i) => {
            const from = start + i * stagger;
            const lineProgress =
              i < steps.length - 1 ? ease(frame, from + 14, from + stagger + 8) : 0;
            return (
              <React.Fragment key={i}>
                <FadeUp from={from} duration={24} distance={14}>
                  <div
                    style={{
                      display: 'flex',
                      flexDirection: isVertical ? 'row' : 'column',
                      alignItems: 'center',
                      gap: bodySize * 0.6,
                      flex: isVertical ? undefined : 1,
                      minWidth: 0,
                      textAlign: isVertical ? 'left' : 'center',
                    }}
                  >
                    <div
                      style={{
                        width: dot,
                        height: dot,
                        borderRadius: '50%',
                        border: `2.5px solid ${palette.accent}`,
                        color: palette.accent,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontFamily: 'Lora',
                        fontWeight: 600,
                        fontSize: bodySize * 0.85,
                        flexShrink: 0,
                      }}
                    >
                      {i + 1}
                    </div>
                    <div
                      style={{
                        fontSize: bodySize * 0.82,
                        fontWeight: 500,
                        color: palette.ink,
                        lineHeight: 1.35,
                      }}
                    >
                      {step}
                    </div>
                  </div>
                </FadeUp>
                {i < steps.length - 1 && !isVertical ? (
                  <div
                    style={{
                      width: bodySize * 2.2,
                      marginTop: dot / 2,
                      flexShrink: 0,
                    }}
                  >
                    <div
                      style={{
                        height: 2,
                        backgroundColor: palette.line,
                        borderRadius: 1,
                        transform: `scaleX(${lineProgress})`,
                        transformOrigin: 'left',
                      }}
                    />
                  </div>
                ) : null}
              </React.Fragment>
            );
          })}
        </div>
      </AbsoluteFill>
    </Canvas>
  );
};

export const infoStepsSuggestedSeconds = (steps: string[], hasTitle: boolean) => {
  const frames = (hasTitle ? 36 : 14) + steps.length * 30 + 24 + 60;
  return Math.max(5, Math.ceil(frames / 30));
};
