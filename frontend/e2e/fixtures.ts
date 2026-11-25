import { mkdirSync } from 'node:fs';
import { join } from 'node:path';
import AxeBuilder from '@axe-core/playwright';
import { test as base, expect, type Page, type Request, type Route } from '@playwright/test';
import { SCREENSHOT_DIR } from './global-setup';

type Reply = { status: number; body: unknown };
type Handler = (request: Request) => Reply;

/** Mocked `/api` routes keyed by `METHOD /api/path`. */
export type ApiRoutes = Record<string, Handler>;

// Outside origins the page is allowed to ask for; each one is answered locally.
const EXTERNAL_STUBS: Record<string, { contentType: string; body: string }> = {
  // index.html loads the Poppins stylesheet; an empty sheet falls back to the system font.
  'fonts.googleapis.com': { contentType: 'text/css', body: '' },
  'fonts.gstatic.com': { contentType: 'font/woff2', body: '' },
};

function isLocal(url: URL) {
  return url.hostname === 'localhost' || url.hostname === '127.0.0.1';
}

export const test = base.extend<{
  api: ApiRoutes;
  unexpected: string[];
  /** Screenshots the page as `<name>-light.png` and `<name>-dark.png`, checking contrast in each. */
  shoot: (name: string) => Promise<void>;
}>({
  // Tests set their routes with `test.use({ api: {...} })`.
  api: [{}, { option: true }],

  unexpected: async ({}, use) => {
    const unexpected: string[] = [];
    await use(unexpected);
    // Guard: any request the mocks didn't expect fails the test.
    expect(unexpected, 'requests not handled by the mocks').toEqual([]);
  },

  page: async ({ page, api, unexpected }, use) => {
    await page.route('**/*', (route: Route) => {
      const request = route.request();
      const url = new URL(request.url());

      if (!isLocal(url)) {
        const stub = EXTERNAL_STUBS[url.hostname];
        if (stub) return route.fulfill({ status: 200, ...stub });
        unexpected.push(`${request.method()} ${request.url()}`);
        return route.abort('blockedbyclient');
      }

      if (url.pathname.startsWith('/api/')) {
        const handler = api[`${request.method()} ${url.pathname}`];
        if (!handler) {
          unexpected.push(`${request.method()} ${url.pathname}`);
          return route.fulfill({ status: 500, json: { error: 'unmocked API route' } });
        }
        const { status, body } = handler(request);
        return route.fulfill({ status, json: body });
      }

      return route.continue();
    });
    await use(page);
  },

  shoot: async ({ page }, use) => {
    mkdirSync(SCREENSHOT_DIR, { recursive: true });
    await use(async (name) => {
      const original = await page.evaluate(() => document.documentElement.getAttribute('data-bs-theme'));
      for (const theme of THEMES) {
        await setTheme(page, theme);
        await waitForImages(page);
        await page.screenshot({
          path: join(SCREENSHOT_DIR, `${name}-${theme}.png`),
          fullPage: true,
          animations: 'disabled',
        });
        await expectNoContrastViolations(page, `${name} (${theme})`);
      }
      if (original) await setTheme(page, original as Theme);
    });
  },
});

export const THEMES = ['light', 'dark'] as const;
export type Theme = (typeof THEMES)[number];

/** Switch the theme the same way the toggle does, without saving the choice. */
export async function setTheme(page: Page, theme: Theme) {
  await page.evaluate(async (t) => {
    document.documentElement.setAttribute('data-bs-theme', t);
    // Let color transitions (e.g. Bootstrap buttons) settle before measuring contrast.
    const transitions = document.getAnimations().filter((a) => a instanceof CSSTransition);
    await Promise.all(transitions.map((a) => a.finished.catch(() => {})));
  }, theme);
}

export async function expectNoContrastViolations(page: Page, label: string) {
  const { violations } = await new AxeBuilder({ page }).withRules(['color-contrast']).analyze();
  const nodes = violations.flatMap((v) => v.nodes.map((n) => `${n.target.join(' ')}: ${n.failureSummary}`));
  expect(nodes, `color-contrast violations on ${label}`).toEqual([]);
}

async function waitForImages(page: Page) {
  await page.waitForLoadState('load');
  await page.waitForFunction(() => Array.from(document.images).every((img) => img.complete));
}

export { expect };
