import React from 'react';
import {AbsoluteFill, Img, staticFile, useVideoConfig} from 'remotion';
import {Brand, DEFAULT_BRAND, FONT_BODY, Palette, ThemeName, resolvePalette} from '../theme';

// Ảnh bìa [thumbnail] tĩnh cho YouTube (ngang 16:9) và bìa Shorts/Reels (dọc 9:16).
// Nguyên lý (skill phim-dang-tai, references/nghien-cuu-thumbnail.md): một lời hứa rõ mà video giữ
// được; độ phức tạp vừa phải (một khuôn mặt thật hoặc hai, một cụm chữ, một nét nhấn); tương phản
// hình-nền cao để đọc được ở bề rộng ~170 px; cảm xúc nằm ở gương mặt thật, chữ thì điềm tĩnh;
// góc dưới bên phải để trống (YouTube đè nhãn thời lượng).
//
// Ảnh người lấy từ khung hình thật của clip (tools/chon-khung-thumbnail.py), không tách nền, không
// ghép cảnh: file đặt ở public/brand/ (khai báo trong "assets" của job). cx, cy, faceH chép từ khung.json.

export type ThumbPhoto = {
  file: string; // tên file trong public/brand/
  w: number; // kích thước ảnh gốc (px)
  h: number;
  cx: number; // tâm khuôn mặt, chuẩn hoá 0-1 theo ảnh
  cy: number;
  faceH: number; // chiều cao khuôn mặt / chiều cao ảnh
  faceScale?: number; // ghi đè cỡ mặt riêng ảnh này (tỉ lệ chiều cao mặt / chiều cao ô ảnh)
  focusX?: number; // vị trí mong muốn của tâm mặt trong ô ảnh (0-1), mặc định 0.5
  focusY?: number; // mặc định 0.42 (mắt nằm quanh đường một phần ba trên)
};

export type ThumbnailLayout = 'chia-doi' | 'toan-anh' | 'chu-chinh';

export type ThumbnailProps = {
  layout: ThumbnailLayout;
  headline: string; // 2-5 chữ; xuống dòng chủ động bằng "\n"
  accent?: string; // một cụm con của headline tô màu nhấn
  kicker?: string; // dòng nhỏ viết hoa phía trên (tên chuỗi); để trống nếu không cần
  photos?: ThumbPhoto[]; // 0-2 ảnh
  photoSide?: 'left' | 'right'; // phía đặt ảnh ở khung ngang (bỏ trống: tự chọn theo vị trí mặt)
  faceScale?: number; // cỡ mặt mặc định: chiều cao mặt / chiều cao ô ảnh
  headlineSize?: number; // px, ghi đè cỡ chữ tự tính
  logoFile?: string; // logo nhỏ trong public/brand/ (tuỳ chọn, dấu nhận diện chuỗi)
  theme: ThemeName;
  brand: Brand;
};

export const thumbnailDefaults: ThumbnailProps = {
  layout: 'chu-chinh',
  headline: 'Một ý\nđáng giữ lại',
  accent: 'đáng giữ lại',
  kicker: '',
  photos: [],
  theme: 'light',
  brand: DEFAULT_BRAND,
};

// Bề rộng một ký tự Be Vietnam Pro 700 tính theo em, lấy dư (chữ thường có dấu đo được 0.55-0.58) để dòng chủ động không bị ngắt thêm
const CHAR_EM = 0.6;
const LINE_H = 1.14;

const fitSize = (text: string, availW: number, availH: number, maxSize: number) => {
  const lines = text.split('\n');
  const longest = Math.max(...lines.map((l) => l.length), 1);
  let size = Math.min(maxSize, availW / (longest * CHAR_EM), availH / (lines.length * LINE_H));
  // dòng không xuống thủ công: ước lượng số dòng khi tự ngắt
  if (lines.length === 1 && longest * CHAR_EM * size > availW) {
    for (let s = size; s > 20; s -= 2) {
      const perLine = Math.floor(availW / (CHAR_EM * s));
      const n = Math.ceil(longest / Math.max(1, perLine));
      if (n * LINE_H * s <= availH) {
        size = s;
        break;
      }
    }
  }
  return Math.floor(size);
};

const Headline: React.FC<{
  text: string;
  accent?: string;
  palette: Palette;
  size: number;
  align: 'left' | 'center';
  maxWidth: number;
}> = ({text, accent, palette, size, align, maxWidth}) => {
  const render = (line: string, key: number) => {
    if (accent && line.includes(accent)) {
      const [a, ...rest] = line.split(accent);
      return (
        <div key={key}>
          {a}
          <span style={{color: palette.accent}}>{accent}</span>
          {rest.join(accent)}
        </div>
      );
    }
    // cụm nhấn trải qua nhiều dòng: tô cả dòng nằm trong cụm
    if (accent && accent.includes(line.trim()) && line.trim().length > 1) {
      return (
        <div key={key} style={{color: palette.accent}}>
          {line}
        </div>
      );
    }
    return <div key={key}>{line}</div>;
  };
  return (
    <div
      style={{
        fontFamily: FONT_BODY,
        fontWeight: 700,
        fontSize: size,
        lineHeight: LINE_H,
        letterSpacing: '-0.01em',
        color: palette.ink,
        textAlign: align,
        maxWidth,
        // chừa chỗ cho dấu tiếng Việt chồng tầng (ể, ặ, ỗ) không bị cắt
        paddingTop: size * 0.06,
      }}
    >
      {text.split('\n').map(render)}
    </div>
  );
};

const Kicker: React.FC<{text?: string; palette: Palette; size: number}> = ({
  text,
  palette,
  size,
}) =>
  text ? (
    <div
      style={{
        fontFamily: FONT_BODY,
        fontWeight: 600,
        fontSize: size,
        letterSpacing: '0.2em',
        textTransform: 'uppercase',
        color: palette.accent,
      }}
    >
      {text}
    </div>
  ) : null;

const Line: React.FC<{palette: Palette; width: number}> = ({palette, width}) => (
  <div style={{height: 3, width, backgroundColor: palette.accent, borderRadius: 2}} />
);

// Một ô ảnh: phóng ảnh sao cho mặt đạt cỡ mong muốn, đặt tâm mặt vào điểm hội tụ, luôn phủ kín ô
const PhotoCell: React.FC<{
  photo: ThumbPhoto;
  x: number;
  y: number;
  w: number;
  h: number;
  faceScale: number;
  radius?: string;
}> = ({photo, x, y, w, h, faceScale, radius}) => {
  const target = (photo.faceScale ?? faceScale) * h;
  const fx = (photo.focusX ?? 0.5) * w;
  const fy = (photo.focusY ?? 0.42) * h;
  let s = target / Math.max(1, photo.faceH * photo.h);
  s = Math.max(s, w / photo.w, h / photo.h);
  // Mặt nằm sát mép ảnh thì phải phóng thêm mới đưa được tâm mặt tới điểm hội tụ mà ảnh vẫn phủ kín ô;
  // giới hạn 1.6 lần để không cắt quá chặt (thà lệch điểm hội tụ một chút)
  const need = Math.max(
    fx / Math.max(0.01, photo.cx * photo.w),
    (w - fx) / Math.max(0.01, (1 - photo.cx) * photo.w),
    fy / Math.max(0.01, photo.cy * photo.h),
    (h - fy) / Math.max(0.01, (1 - photo.cy) * photo.h),
  );
  s = Math.max(s, Math.min(need, s * 1.6));
  const iw = photo.w * s;
  const ih = photo.h * s;
  const left = Math.min(0, Math.max(w - iw, fx - photo.cx * iw));
  const top = Math.min(0, Math.max(h - ih, fy - photo.cy * ih));
  return (
    <div
      style={{
        position: 'absolute',
        left: x,
        top: y,
        width: w,
        height: h,
        overflow: 'hidden',
        borderRadius: radius,
      }}
    >
      <Img
        src={staticFile(`brand/${photo.file}`)}
        style={{position: 'absolute', left, top, width: iw, height: ih, maxWidth: 'none'}}
      />
    </div>
  );
};

const PhotoRow: React.FC<{
  photos: ThumbPhoto[];
  x: number;
  y: number;
  w: number;
  h: number;
  faceScale: number;
  gap: number;
  vertical?: boolean;
}> = ({photos, x, y, w, h, faceScale, gap, vertical}) => {
  const n = Math.max(1, photos.length);
  return (
    <>
      {photos.map((p, i) =>
        vertical ? (
          <PhotoCell
            key={i}
            photo={p}
            x={x}
            y={y + i * ((h - gap * (n - 1)) / n + gap)}
            w={w}
            h={(h - gap * (n - 1)) / n}
            faceScale={faceScale}
          />
        ) : (
          <PhotoCell
            key={i}
            photo={p}
            x={x + i * ((w - gap * (n - 1)) / n + gap)}
            y={y}
            w={(w - gap * (n - 1)) / n}
            h={h}
            faceScale={faceScale}
          />
        ),
      )}
    </>
  );
};

const Logo: React.FC<{file?: string; size: number; style: React.CSSProperties}> = ({
  file,
  size,
  style,
}) =>
  file ? (
    <Img
      src={staticFile(`brand/${file}`)}
      style={{position: 'absolute', height: size, objectFit: 'contain', ...style}}
    />
  ) : null;

export const Thumbnail: React.FC<ThumbnailProps> = (props) => {
  const {layout, headline, accent, kicker, logoFile, theme, brand} = props;
  const photos = (props.photos ?? []).slice(0, 2);
  // Không chỉ định phía ảnh: toàn ảnh một người thì theo vị trí mặt trong khung gốc (mặt lệch trái thì
  // chữ sang phải), tránh phải phóng quá tay; các bố cục khác mặc định ảnh bên phải
  const photoSide =
    props.photoSide ??
    (layout === 'toan-anh' && photos.length === 1 && photos[0].cx < 0.5 ? 'left' : 'right');
  const palette = resolvePalette(theme, brand);
  const {width: W, height: H} = useVideoConfig();
  const vertical = H > W;
  const u = Math.min(W, H) / 100;
  const pad = u * 7;
  const kickerSize = u * 3.3;
  const photoLeft = photoSide === 'left';

  // ---------- khung dọc 9:16 (bìa Shorts/Reels): chữ nằm trong vùng an toàn giữa khung ----------
  if (vertical) {
    const textTop = H * 0.6;
    const textH = H * 0.24;
    const availW = W - pad * 2;
    const size =
      props.headlineSize ?? fitSize(headline, availW, textH - kickerSize * 2.4, u * 14);
    const photoH = layout === 'toan-anh' ? H : H * 0.58;
    return (
      <AbsoluteFill style={{backgroundColor: palette.bg}}>
        {photos.length ? (
          <PhotoRow
            photos={
              photos.length > 1 && layout !== 'toan-anh'
                ? photos.map((p) => ({...p, focusY: p.focusY ?? 0.5})) // ô ngang thấp: mặt vào giữa
                : photos
            }
            x={0}
            y={0}
            w={W}
            h={photoH}
            faceScale={
              props.faceScale ?? (layout === 'toan-anh' ? 0.2 : photos.length > 1 ? 0.42 : 0.3)
            }
            gap={u * 0.8}
            vertical={photos.length > 1 && layout !== 'toan-anh'}
          />
        ) : null}
        {layout === 'toan-anh' ? (
          <AbsoluteFill
            style={{
              background: `linear-gradient(to bottom, ${palette.bg}00 0%, ${palette.bg}00 44%, ${palette.bg}F2 60%, ${palette.bg}F7 100%)`,
            }}
          />
        ) : null}
        <div
          style={{
            position: 'absolute',
            left: pad,
            right: pad,
            top: textTop,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: u * 2.6,
          }}
        >
          <Line palette={palette} width={u * 12} />
          <Kicker text={kicker} palette={palette} size={kickerSize} />
          <Headline
            text={headline}
            accent={accent}
            palette={palette}
            size={size}
            align="center"
            maxWidth={availW}
          />
        </div>
        <Logo file={logoFile} size={u * 7} style={{left: W / 2 - u * 3.5, bottom: H * 0.1}} />
      </AbsoluteFill>
    );
  }

  // ---------- khung ngang 16:9 ----------
  if (layout === 'toan-anh') {
    const textW = W * 0.46;
    const availW = textW - pad * 1.4;
    const size = props.headlineSize ?? fitSize(headline, availW, H * 0.56, u * 17);
    const dir = photoLeft ? 'to left' : 'to right';
    return (
      <AbsoluteFill style={{backgroundColor: palette.bg}}>
        {photos.length ? (
          <PhotoRow
            photos={photos.map((p) => ({
              ...p,
              focusX: p.focusX ?? (photos.length > 1 ? 0.5 : photoLeft ? 0.3 : 0.7),
            }))}
            x={photos.length > 1 ? (photoLeft ? 0 : W * 0.36) : 0}
            y={0}
            w={photos.length > 1 ? W * 0.64 : W}
            h={H}
            faceScale={props.faceScale ?? 0.3}
            gap={u * 0.8}
          />
        ) : null}
        <AbsoluteFill
          style={{
            background: `linear-gradient(${dir}, ${palette.bg}FA 0%, ${palette.bg}F0 34%, ${palette.bg}00 58%)`,
          }}
        />
        <div
          style={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            [photoLeft ? 'right' : 'left']: pad,
            width: availW,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            gap: u * 2.4,
          }}
        >
          <Kicker text={kicker} palette={palette} size={kickerSize} />
          <Line palette={palette} width={u * 11} />
          <Headline
            text={headline}
            accent={accent}
            palette={palette}
            size={size}
            align="left"
            maxWidth={availW}
          />
        </div>
        <Logo
          file={logoFile}
          size={u * 7}
          style={{bottom: pad * 0.6, [photoLeft ? 'right' : 'left']: pad}}
        />
      </AbsoluteFill>
    );
  }

  if (layout === 'chia-doi') {
    // hai ảnh: mỗi ô vẫn đủ rộng cho một khuôn mặt, nhường thêm chỗ cho chữ to
    const textW = W * (photos.length > 1 ? 0.5 : 0.44);
    const photoW = W - textW;
    const availW = textW - pad * 1.5;
    const size = props.headlineSize ?? fitSize(headline, availW, H * 0.6, u * 17);
    return (
      <AbsoluteFill style={{backgroundColor: palette.bg}}>
        {photos.length ? (
          <PhotoRow
            photos={photos}
            x={photoLeft ? 0 : textW}
            y={0}
            w={photoW}
            h={H}
            faceScale={props.faceScale ?? (photos.length > 1 ? 0.3 : 0.34)}
            gap={u * 0.8}
          />
        ) : null}
        <div
          style={{
            position: 'absolute',
            top: 0,
            bottom: 0,
            left: photoLeft ? photoW + pad * 0.9 : pad,
            width: availW,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            gap: u * 2.4,
          }}
        >
          <Kicker text={kicker} palette={palette} size={kickerSize} />
          <Line palette={palette} width={u * 11} />
          <Headline
            text={headline}
            accent={accent}
            palette={palette}
            size={size}
            align="left"
            maxWidth={availW}
          />
        </div>
        <Logo
          file={logoFile}
          size={u * 7}
          style={{bottom: pad * 0.6, left: photoLeft ? photoW + pad * 0.9 : pad}}
        />
      </AbsoluteFill>
    );
  }

  // chu-chinh: chữ làm chủ, ảnh người trong ô vòm nhỏ (tĩnh tại, như khung cửa)
  const archW = photos.length > 1 ? W * 0.36 : W * 0.27;
  const archH = H * 0.8;
  const archX = photoLeft ? pad : W - pad - archW;
  const textX = photoLeft ? archX + archW + pad : pad;
  const availW = W - archW - pad * 3.2;
  const size = props.headlineSize ?? fitSize(headline, availW, H * 0.62, u * 18);
  return (
    <AbsoluteFill style={{backgroundColor: palette.bg}}>
      {photos.map((p, i) => {
        const n = photos.length;
        const gap = u * 1.2;
        const cw = (archW - gap * (n - 1)) / n;
        return (
          <PhotoCell
            key={i}
            photo={p}
            x={archX + i * (cw + gap)}
            y={(H - archH) / 2}
            w={cw}
            h={archH}
            faceScale={props.faceScale ?? 0.26}
            radius={`${cw / 2}px ${cw / 2}px ${u * 1.2}px ${u * 1.2}px`}
          />
        );
      })}
      <div
        style={{
          position: 'absolute',
          top: 0,
          bottom: 0,
          left: textX,
          width: availW,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          gap: u * 2.6,
        }}
      >
        <Kicker text={kicker} palette={palette} size={kickerSize} />
        <Line palette={palette} width={u * 11} />
        <Headline
          text={headline}
          accent={accent}
          palette={palette}
          size={size}
          align="left"
          maxWidth={availW}
        />
      </div>
      <Logo file={logoFile} size={u * 7} style={{bottom: pad * 0.6, left: textX}} />
    </AbsoluteFill>
  );
};
