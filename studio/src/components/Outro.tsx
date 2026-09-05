import React from 'react';
import {AbsoluteFill, Img, staticFile} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, Palette, ThemeName, resolvePalette} from '../theme';
import {AccentLine, Canvas, FadeUp, LogoRow} from '../common';

export type OutroProps = {
  headline?: string; // PLACEHOLDER: thông điệp kết
  ctaLines?: string[]; // PLACEHOLDER: lời mời hành động (1-2 dòng)
  programName?: string; // PLACEHOLDER: tên chương trình đang mở đăng ký
  contactLines?: string[]; // PLACEHOLDER: web, email, điện thoại (fallback: brand.contactLines)
  qrFile?: string | null; // file QR trong public/brand/ (đưa vào qua "assets" của job)
  qrCaption?: string; // chú thích dưới QR
  theme: ThemeName;
  brand: Brand;
  logoMono?: boolean;
  showTagline?: boolean;
  durationInSeconds?: number; // có QR nên để ≥9s cho người xem kịp quét
};

export const outroDefaults: OutroProps = {
  headline: 'Thông điệp kết của clip',
  ctaLines: ['Lời mời hành động dành cho người xem'],
  programName: '',
  contactLines: [],
  qrFile: null,
  qrCaption: 'Quét để đăng ký',
  theme: 'light',
  brand: DEFAULT_BRAND,
  showTagline: true,
  durationInSeconds: 8,
};

const QrPlate: React.FC<{
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

export const Outro: React.FC<OutroProps> = ({
  headline,
  ctaLines,
  programName,
  contactLines,
  qrFile,
  qrCaption,
  theme,
  brand,
  logoMono,
  showTagline = true,
}) => {
  const palette = resolvePalette(theme, brand);
  const {pad, titleSize, bodySize, subtitleSize, isVertical, unit} = useLayout();
  const mono = logoMono ?? theme === 'dark';
  const contacts = contactLines?.length ? contactLines : brand.contactLines ?? [];
  const hasQr = Boolean(qrFile);
  const qrSize = isVertical ? unit * 24 : unit * 22;

  const MainColumn = (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
        gap: bodySize * 0.95,
        maxWidth: '100%',
      }}
    >
      {headline ? (
        <FadeUp from={10} duration={30}>
          <div
            style={{
              fontFamily: 'Lora',
              fontWeight: 600,
              fontSize: titleSize * (isVertical ? 0.72 : 0.76),
              color: palette.ink,
              lineHeight: 1.28,
            }}
          >
            {headline}
          </div>
        </FadeUp>
      ) : null}
      <FadeUp from={28} duration={24} distance={0}>
        <AccentLine palette={palette} from={0} width={70} />
      </FadeUp>
      {(ctaLines ?? []).map((line, i) => (
        <FadeUp key={i} from={40 + i * 12} duration={26}>
          <div
            style={{
              fontSize: bodySize * 0.9,
              fontWeight: 400,
              color: palette.inkSoft,
              lineHeight: 1.5,
            }}
          >
            {line}
          </div>
        </FadeUp>
      ))}
      {programName || contacts.length ? (
        <FadeUp from={58} duration={28}>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: bodySize * 0.42,
              marginTop: bodySize * 0.5,
            }}
          >
            {programName ? (
              <div
                style={{
                  fontSize: bodySize * 0.82,
                  fontWeight: 600,
                  color: palette.accent,
                  letterSpacing: '0.1em',
                  textTransform: 'uppercase',
                }}
              >
                {programName}
              </div>
            ) : null}
            {contacts.map((c, i) => (
              <div
                key={i}
                style={{
                  fontSize: bodySize * 0.72,
                  fontWeight: 400,
                  color: palette.inkSoft,
                  letterSpacing: '0.06em',
                }}
              >
                {c}
              </div>
            ))}
          </div>
        </FadeUp>
      ) : null}
    </div>
  );

  return (
    <Canvas palette={palette} fadeIn={14} fadeOut={22}>
      <AbsoluteFill
        style={{
          padding: pad,
          paddingBottom: pad * 1.55,
          display: 'flex',
          flexDirection: isVertical ? 'column' : 'row',
          alignItems: 'center',
          justifyContent: 'center',
          gap: isVertical ? unit * 5 : unit * 9,
        }}
      >
        <div style={{maxWidth: hasQr && !isVertical ? '58%' : '82%'}}>{MainColumn}</div>
        {hasQr ? (
          <FadeUp from={64} duration={30} distance={18}>
            <QrPlate
              qrFile={qrFile as string}
              qrCaption={qrCaption}
              palette={palette}
              size={qrSize}
            />
          </FadeUp>
        ) : null}
      </AbsoluteFill>
      <AbsoluteFill
        style={{
          justifyContent: 'flex-end',
          alignItems: 'center',
          paddingBottom: pad * 0.55,
        }}
      >
        <FadeUp from={86} duration={30} distance={14}>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: unit * 1.8,
            }}
          >
            <LogoRow
              brand={brand}
              palette={palette}
              height={unit * (isVertical ? 5.5 : 6)}
              mono={mono}
            />
            {showTagline && brand.tagline ? (
              <div
                style={{
                  fontFamily: 'Be Vietnam Pro',
                  fontSize: unit * 2.1,
                  fontWeight: 400,
                  color: palette.inkSoft,
                  letterSpacing: '0.16em',
                  textTransform: 'uppercase',
                }}
              >
                {brand.tagline}
              </div>
            ) : null}
          </div>
        </FadeUp>
      </AbsoluteFill>
    </Canvas>
  );
};
