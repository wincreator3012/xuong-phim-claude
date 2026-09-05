// Hệ thống theme minimalist cho toàn bộ đồ họa.
// Hai tông: "light" (giấy & mực zen) và "dark" (trầm sang trọng).
// Giá trị mặc định ở đây; brand/brand.json (thư mục gốc) ghi đè qua input props.

export type ThemeName = 'light' | 'dark';

export type Palette = {
  bg: string; // nền
  ink: string; // chữ chính
  inkSoft: string; // chữ phụ
  accent: string; // màu nhấn
  line: string; // đường kẻ mảnh
};

export const PALETTES: Record<ThemeName, Palette> = {
  light: {
    bg: '#FAF7F1',
    ink: '#23282D',
    inkSoft: '#6E7278',
    accent: '#2F5D50',
    line: '#D8D2C6',
  },
  dark: {
    bg: '#15181C',
    ink: '#F2EEE5',
    inkSoft: '#9AA0A6',
    accent: '#C7A97B',
    line: '#3A3F45',
  },
};

// Một logo trong hàng logo: file nằm ở public/brand/
export type LogoSpec = {
  file: string;
  scale?: number; // hệ số phóng riêng khi logo quá cao/quá dẹt (mặc định 1)
};

export type Brand = {
  name: string;
  credentials?: string;
  tagline?: string;
  logoFile?: string | null; // (cũ, vẫn hỗ trợ) - ưu tiên dùng logos
  logos?: (string | LogoSpec)[]; // hàng 1-3 logo, chuẩn hóa theo chiều cao
  socialLine?: string;
  contactLines?: string[]; // mặc định cấp brand cho khối liên hệ ở outro
  palettes?: Partial<Record<ThemeName, Partial<Palette>>>;
};

// Giá trị dự phòng khi job không truyền brand - bản thật nằm ở brand/brand.json
// (tools/render-do-hoa.mjs nạp file đó và truyền vào props, nên bình thường
// không bao giờ thấy các chữ này trên video).
export const DEFAULT_BRAND: Brand = {
  name: 'Tên của bạn',
  credentials: '',
  tagline: 'Chức danh hoặc câu định vị',
  logoFile: null,
  logos: [],
  socialLine: '',
  contactLines: [],
};

export const normalizeLogos = (brand?: Brand | null): LogoSpec[] => {
  const raw = brand?.logos?.length
    ? brand.logos
    : brand?.logoFile
      ? [brand.logoFile]
      : [];
  return raw
    .slice(0, 3)
    .map((l) => (typeof l === 'string' ? {file: l} : l));
};

export const FONT_HEADING = 'Lora';
export const FONT_BODY = 'Be Vietnam Pro';

export const resolvePalette = (
  theme: ThemeName,
  brand?: Brand | null,
): Palette => {
  const base = PALETTES[theme] ?? PALETTES.light;
  const override = brand?.palettes?.[theme] ?? {};
  return {...base, ...override};
};

// Easing chậm rãi, "thở" - dùng chung cho mọi chuyển động
export const EASE_GENTLE: [number, number, number, number] = [0.22, 1, 0.36, 1];
