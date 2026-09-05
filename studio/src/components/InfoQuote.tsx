import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {AccentLine, Canvas, FadeUp} from '../common';

export type InfoQuoteProps = {
  quote: string;
  author?: string;
  theme: ThemeName;
  brand: Brand;
  durationInSeconds?: number;
};

export const infoQuoteDefaults: InfoQuoteProps = {
  quote: 'Câu trích dẫn hoặc thông điệp cốt lõi của đoạn nói.',
  author: '',
  theme: 'light',
  brand: DEFAULT_BRAND,
  durationInSeconds: 7,
};

export const InfoQuote: React.FC<InfoQuoteProps> = ({quote, author, theme, brand}) => {
  const palette = resolvePalette(theme, brand);
  const {pad, titleSize, bodySize, isVertical} = useLayout();
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
          gap: bodySize * 1.2,
        }}
      >
        <FadeUp from={8} duration={22} distance={0}>
          <AccentLine palette={palette} from={0} width={60} />
        </FadeUp>
        <FadeUp from={18} duration={32}>
          <div
            style={{
              fontFamily: 'Lora',
              fontWeight: 500,
              fontSize: titleSize * 0.62,
              color: palette.ink,
              lineHeight: 1.45,
              maxWidth: isVertical ? '94%' : '72%',
              margin: '0 auto',
            }}
          >
            {'“'}
            {quote}
            {'”'}
          </div>
        </FadeUp>
        {author ? (
          <FadeUp from={44} duration={26}>
            <div
              style={{
                fontSize: bodySize * 0.8,
                fontWeight: 500,
                color: palette.inkSoft,
                letterSpacing: '0.1em',
              }}
            >
              {'- '}
              {author}
            </div>
          </FadeUp>
        ) : null}
      </AbsoluteFill>
    </Canvas>
  );
};
