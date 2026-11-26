import { rmSync } from 'node:fs';
import { join } from 'node:path';

export const SCREENSHOT_DIR = process.env.SCREENSHOT_DIR ?? join(import.meta.dirname, 'screenshots');

// Start every run with an empty screenshot folder so no stale files survive.
export default function globalSetup() {
  rmSync(SCREENSHOT_DIR, { recursive: true, force: true });
}
