import {Config} from '@remotion/cli/config';
import fs from 'fs';

// Trong sandbox đám mây, Chromium đã cài sẵn tại đường dẫn này.
// Trên máy khác (macOS…), Remotion tự tìm trình duyệt của hệ thống.
const CLOUD_CHROMIUM =
  '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
if (fs.existsSync(CLOUD_CHROMIUM)) {
  Config.setBrowserExecutable(CLOUD_CHROMIUM);
}

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setConcurrency(2);
Config.setOverwriteOutput(true);
Config.setChromiumOpenGlRenderer('swangle');
