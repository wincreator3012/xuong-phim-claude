import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {Canvas, FadeUp} from '../common';

export type InfoListProps = {
  title?: string;
  items: string[];
  theme: ThemeName;
  brand: Brand;
  durationInSeconds?: number; // nếu bỏ trống: tự tính theo số mục
};

export const infoListDefaults: InfoListProps = {
  title: 'Ba điểm chính',
  items: ['Điểm thứ nhất', 'Điểm thứ hai', 'Điểm thứ ba'],
  theme: 'light',
  brand: DEFAULT_BRAND,
};

// Mỗi mục xuất hiện lần lượt, có khoảng thở để người xem kịp đọc
export const InfoList: React.FC<InfoListProps> = ({title, items, theme, brand}) => {
  const palette = resolvePalette(theme, brand);
  const {pad, subtitleSize, bodySize, isVertical} = useLayout();
  const startItems = title ? 34 : 12;
  const stagger = 34;

  return (
    <Canvas palette={palette} fadeIn={12} fadeOut={18}>
      <AbsoluteFill
        style={{
          padding: pad,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
        }}
      >
        <div style={{width: isVertical ? '100%' : '72%'}}>
          {title ? (
            <FadeUp from={8} duration={26}>
              <div
                style={{
                  fontFamily: 'Lora',
                  fontWeight: 600,
                  fontSize: subtitleSize * 1.35,
                  color: palette.ink,
                  marginBottom: bodySize * 1.4,
                  lineHeight: 1.25,
                }}
              >
                {title}
              </div>
            </FadeUp>
          ) : null}
          <div style={{display: 'flex', flexDirection: 'column', gap: bodySize * 0.95}}>
            {items.map((item, i) => (
              <FadeUp key={i} from={startItems + i * stagger} duration={26} distance={18}>
                <div style={{display: 'flex', alignItems: 'baseline', gap: bodySize * 0.7}}>
                  <div
                    style={{
                      width: bodySize * 0.5,
                      height: 3,
                      borderRadius: 2,
                      backgroundColor: palette.accent,
                      flexShrink: 0,
                      transform: 'translateY(-6px)',
                    }}
                  />
                  <div
                    style={{
                      fontSize: bodySize,
                      fontWeight: 400,
                      color: palette.ink,
                      lineHeight: 1.45,
                    }}
                  >
                    {item}
                  </div>
                </div>
              </FadeUp>
            ))}
          </div>
        </div>
      </AbsoluteFill>
    </Canvas>
  );
};

// Thời lượng gợi ý (giây) theo số mục - dùng ở Root khi tính metadata
export const infoListSuggestedSeconds = (items: string[], hasTitle: boolean) => {
  const frames = (hasTitle ? 34 : 12) + items.length * 34 + 26 + 60; // vào + giữ
  return Math.max(5, Math.ceil(frames / 30));
};
