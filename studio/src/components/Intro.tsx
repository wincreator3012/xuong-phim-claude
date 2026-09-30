import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {AccentLine, BrandBlock, Canvas, FadeUp, LogoRow, QrPlate} from '../common';

export type IntroProps = {
  title: string; // PLACEHOLDER: tên clip/bài giảng - NGẮN. Nếu cần xuống dòng, dùng
  // ký tự '\n' NGAY TẠI ranh giới an toàn (cuối cụm từ, không cắt giữa từ ghép
  // như "Chánh niệm") - render sẽ tôn trọng '\n' này (whiteSpace: pre-line),
  // KHÔNG để trình duyệt tự chọn điểm ngắt.
  subtitle?: string; // PLACEHOLDER: tên chuỗi chương trình (kicker phía trên)
  // Câu văn xuôi ngắn thì để tự xuống dòng theo bề rộng là ổn. NHƯNG khi
  // subtitle là một nhãn ngắn kiểu "Tên - Chức danh" (kicker viết hoa, có
  // letter-spacing) thì PHẢI tự chủ động chèn '\n' tại ranh giới an toàn
  // (vd sau tên, trước chức danh) - từ 2026-09-21 subtitle đã tôn trọng
  // '\n' (whiteSpace: pre-line) đúng như "title", để tránh trình duyệt tự
  // ngắt dòng làm rớt một từ đơn độc xuống dòng cuối (lỗi đã gặp: một tên
  // trường dài xuống dòng, chữ cuối còn lại một mình ở dòng dưới).
  description?: string;
  // Các dòng nhỏ phía dưới description (vd "Tác giả: …", "Đơn vị xuất bản
  // và phát hành: …") - mỗi phần tử một dòng riêng, không tự ngắt.
  creditLines?: string[];
  qrFile?: string | null; // file QR trong public/brand/ (đưa vào qua "assets" của job)
  qrCaption?: string; // chú thích dưới QR
  scheduleLabel?: string; // PLACEHOLDER: nhãn nhỏ phía trên lịch (vd "Lịch 5 chặng")
  scheduleLines?: string[]; // PLACEHOLDER: các mốc ngày, nối bằng dấu ·
  theme: ThemeName;
  brand: Brand; // brand.logos: hàng 1-3 logo hiển thị đáy màn hình
  logoMono?: boolean; // ép logo đơn sắc; mặc định: theme tối = true
  showBrandName?: boolean; // hiện thêm tên chữ (khi logo không chứa tên)
  durationInSeconds?: number;
};

export const introDefaults: IntroProps = {
  title: 'Tên bài giảng hoặc clip',
  subtitle: 'Tên chuỗi chương trình',
  theme: 'light',
  brand: DEFAULT_BRAND,
  durationInSeconds: 6,
};

export const Intro: React.FC<IntroProps> = ({
  title,
  subtitle,
  description,
  creditLines,
  qrFile,
  qrCaption,
  scheduleLabel,
  scheduleLines,
  theme,
  brand,
  logoMono,
  showBrandName = false,
}) => {
  const palette = resolvePalette(theme, brand);
  const {pad, titleSize, subtitleSize, isVertical, unit, width} = useLayout();
  const mono = logoMono ?? theme === 'dark';
  const hasQr = Boolean(qrFile);
  const qrSize = isVertical ? unit * 22 : unit * 19;

  return (
    <Canvas palette={palette} fadeIn={0} fadeOut={20}>
      <AbsoluteFill
        style={{
          padding: pad,
          display: 'flex',
          flexDirection: isVertical ? 'column' : 'row',
          alignItems: 'center',
          justifyContent: 'center',
          gap: hasQr ? (isVertical ? unit * 5 : unit * 9) : 0,
        }}
      >
      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: titleSize * 0.55,
          maxWidth: hasQr && !isVertical ? '68%' : '100%',
        }}
      >
        {subtitle ? (
          <FadeUp from={14} duration={30}>
            <div
              style={{
                fontSize: subtitleSize * 0.78,
                fontWeight: 500,
                color: palette.accent,
                letterSpacing: '0.22em',
                textTransform: 'uppercase',
                whiteSpace: 'pre-line',
                maxWidth: width * (isVertical ? 0.95 : 0.78),
                textAlign: 'center',
              }}
            >
              {subtitle}
            </div>
          </FadeUp>
        ) : null}
        <FadeUp from={26} duration={34}>
          <div
            style={{
              fontFamily: 'Lora',
              fontWeight: 600,
              fontSize: titleSize,
              color: palette.ink,
              lineHeight: 1.22,
              // px THẬT (không dùng % CSS): div bọc ngoài (FadeUp) không có
              // width cố định nên % sẽ resolve sai (theo shrink-to-fit của
              // chính nó), khiến chữ NGẮN vẫn bị ngắt dòng dù còn dư chỗ -
              // đây chính là lỗi khiến "Chánh niệm" bị tách "Chánh" / "niệm".
              maxWidth: width * (isVertical ? 0.92 : 0.78),
              margin: '0 auto',
              // Cho phép xuống dòng THỦ CÔNG có kiểm soát: truyền '\n' trong title
              // tại đúng ranh giới an toàn (cuối cụm từ) để tránh trình duyệt tự
              // ngắt dòng giữa một từ ghép/cụm từ liền nghĩa (vd "Chánh niệm").
              // pre-line vẫn cho phép wrap tự nhiên NẾU một dòng tự đặt vẫn quá dài.
              whiteSpace: 'pre-line',
            }}
          >
            {title}
          </div>
        </FadeUp>
        {description ? (
          <FadeUp from={40} duration={28}>
            <div
              style={{
                fontFamily: 'Be Vietnam Pro',
                fontWeight: 400,
                fontSize: subtitleSize * 0.92,
                color: palette.inkSoft,
                lineHeight: 1.5,
                maxWidth: width * (isVertical ? 0.9 : 0.62),
                margin: '0 auto',
              }}
            >
              {description}
            </div>
          </FadeUp>
        ) : null}
        <FadeUp from={48} duration={26} distance={0}>
          <AccentLine palette={palette} from={0} />
        </FadeUp>
        {scheduleLines?.length ? (
          <FadeUp from={52} duration={26}>
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: unit * 0.5,
              }}
            >
              {scheduleLabel ? (
                <div
                  style={{
                    fontSize: subtitleSize * 0.55,
                    fontWeight: 600,
                    color: palette.accent,
                    letterSpacing: '0.12em',
                    textTransform: 'uppercase',
                  }}
                >
                  {scheduleLabel}
                </div>
              ) : null}
              <div
                style={{
                  fontFamily: 'Be Vietnam Pro',
                  fontWeight: 400,
                  fontSize: subtitleSize * 0.68,
                  color: palette.inkSoft,
                  letterSpacing: '0.02em',
                  maxWidth: width * (isVertical ? 0.9 : 0.62),
                  textAlign: 'center',
                  lineHeight: 1.5,
                }}
              >
                {scheduleLines.join(' · ')}
              </div>
            </div>
          </FadeUp>
        ) : null}
        {creditLines?.length ? (
          <FadeUp from={56} duration={26}>
            <div
              style={{
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                gap: unit * 0.9,
              }}
            >
              {creditLines.map((line, i) => (
                <div
                  key={i}
                  style={{
                    fontFamily: 'Be Vietnam Pro',
                    fontWeight: 400,
                    fontSize: subtitleSize * 0.62,
                    color: palette.inkSoft,
                    letterSpacing: '0.02em',
                  }}
                >
                  {line}
                </div>
              ))}
            </div>
          </FadeUp>
        ) : null}
      </div>
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
          paddingBottom: pad * 0.75,
        }}
      >
        <FadeUp from={72} duration={30} distance={16}>
          <div
            style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: unit * 2.2,
            }}
          >
            <LogoRow
              brand={brand}
              palette={palette}
              height={unit * (isVertical ? 6.5 : 7.5)}
              mono={mono}
            />
            {showBrandName ? (
              <BrandBlock brand={{...brand, logoFile: null, logos: []}} palette={palette} size={subtitleSize * 0.6} />
            ) : null}
          </div>
        </FadeUp>
      </AbsoluteFill>
    </Canvas>
  );
};
