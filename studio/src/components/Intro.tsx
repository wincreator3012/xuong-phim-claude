import React from 'react';
import {AbsoluteFill} from 'remotion';
import {useLayout} from '../layout';
import {Brand, DEFAULT_BRAND, ThemeName, resolvePalette} from '../theme';
import {AccentLine, BrandBlock, Canvas, FadeUp, LogoRow} from '../common';

export type IntroProps = {
  title: string; // PLACEHOLDER: tên clip/bài giảng - NGẮN. Nếu cần xuống dòng, dùng
  // ký tự '\n' NGAY TẠI ranh giới an toàn (cuối cụm từ, không cắt giữa từ ghép
  // như "Hạnh Phúc") - render sẽ tôn trọng '\n' này (whiteSpace: pre-line),
  // KHÔNG để trình duyệt tự chọn điểm ngắt.
  subtitle?: string; // PLACEHOLDER: tên chuỗi chương trình (kicker phía trên)
  // Câu mô tả dài hơn, hiện NHỎ HƠN ngay dưới title (vd phụ đề sách) - câu
  // văn xuôi bình thường nên để tự xuống dòng theo bề rộng là ổn, khác với
  // "title" (tên riêng ngắn - KHÔNG được để trình duyệt tự ngắt dòng giữa
  // chừng một cụm từ, xem ghi chú "ngắt dòng trong đồ họa" trong bien-tap.md).
  description?: string;
  // Các dòng nhỏ phía dưới description (vd "Tác giả: …", "Đơn vị xuất bản
  // và phát hành: …") - mỗi phần tử một dòng riêng, không tự ngắt.
  creditLines?: string[];
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
  theme,
  brand,
  logoMono,
  showBrandName = false,
}) => {
  const palette = resolvePalette(theme, brand);
  const {pad, titleSize, subtitleSize, isVertical, unit, width} = useLayout();
  const mono = logoMono ?? theme === 'dark';

  return (
    <Canvas palette={palette} fadeIn={0} fadeOut={20}>
      <AbsoluteFill
        style={{
          padding: pad,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          textAlign: 'center',
          gap: titleSize * 0.55,
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
              // đây chính là lỗi khiến "Hạnh Phúc" bị tách "Hạnh" / "Phúc".
              maxWidth: width * (isVertical ? 0.92 : 0.78),
              margin: '0 auto',
              // Cho phép xuống dòng THỦ CÔNG có kiểm soát: truyền '\n' trong title
              // tại đúng ranh giới an toàn (cuối cụm từ) để tránh trình duyệt tự
              // ngắt dòng giữa một từ ghép/cụm từ liền nghĩa (vd "Hạnh Phúc").
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
