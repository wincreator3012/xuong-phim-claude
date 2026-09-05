import {continueRender, delayRender, staticFile} from 'remotion';

// Nạp font từ public/fonts (đóng gói offline qua @fontsource, không cần mạng).
// Mỗi weight gồm 2 subset: latin + vietnamese, phân biệt bằng unicodeRange.

const RANGE_VIETNAMESE =
  'U+0102-0103, U+0110-0111, U+0128-0129, U+0168-0169, U+01A0-01A1, U+01AF-01B0, U+0300-0301, U+0303-0304, U+0308-0309, U+0323, U+0329, U+1EA0-1EF9, U+20AB';
const RANGE_LATIN =
  'U+0000-00FF, U+0131, U+0152-0153, U+02BB-02BC, U+02C6, U+02DA, U+02DC, U+0304, U+0308, U+0329, U+2000-206F, U+20AC, U+2122, U+2191, U+2193, U+2212, U+2215, U+FEFF, U+FFFD';

const loadOne = (
  family: string,
  file: string,
  weight: string,
  unicodeRange: string,
) => {
  if (typeof FontFace === 'undefined') {
    return;
  }
  const handle = delayRender(`font ${file}`);
  const face = new FontFace(
    family,
    `url(${staticFile(`fonts/${file}`)}) format('woff2')`,
    {weight, unicodeRange},
  );
  face
    .load()
    .then((loaded) => {
      (document.fonts as unknown as {add: (f: FontFace) => void}).add(loaded);
      continueRender(handle);
    })
    .catch((err) => {
      // Thiếu font không được phép chặn render
      // eslint-disable-next-line no-console
      console.warn('Không nạp được font', file, err);
      continueRender(handle);
    });
};

let loaded = false;

export const loadFonts = () => {
  if (loaded) {
    return;
  }
  loaded = true;
  const sets: Array<[string, string, string]> = [
    ['Lora', 'lora-latin-500-normal.woff2', '500'],
    ['Lora', 'lora-latin-600-normal.woff2', '600'],
    ['Be Vietnam Pro', 'be-vietnam-pro-latin-400-normal.woff2', '400'],
    ['Be Vietnam Pro', 'be-vietnam-pro-latin-500-normal.woff2', '500'],
    ['Be Vietnam Pro', 'be-vietnam-pro-latin-600-normal.woff2', '600'],
  ];
  for (const [family, file, weight] of sets) {
    loadOne(family, file, weight, RANGE_LATIN);
    loadOne(family, file.replace('-latin-', '-vietnamese-'), weight, RANGE_VIETNAMESE);
  }
};
