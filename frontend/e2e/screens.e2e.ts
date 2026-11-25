import { join } from 'node:path';
import type { Page, Request } from '@playwright/test';
import type { CategorySettings } from '../src/api';
import { expect, test, THEMES, type ApiRoutes } from './fixtures';
import { SCREENSHOT_DIR } from './global-setup';
import { CATEGORIES, GUILD, GUILD_DETAIL, INVITE_URL, MANY_CATEGORIES, ME, OTHER_GUILD } from './mocks';

const reply = (status: number, body: unknown) => () => ({ status, body });

const loggedIn: ApiRoutes = { 'GET /api/me': reply(200, ME) };
const loggedOut: ApiRoutes = { 'GET /api/me': reply(401, { error: 'Not logged in' }) };

test.describe('logged out', () => {
  test.use({ api: loggedOut });

  test('home', async ({ page, shoot }) => {
    await page.goto('/');
    await expect(page.getByRole('heading', { name: /Welcome to AutoChannel/ })).toBeVisible();
    await expect(page.getByRole('img', { name: 'AutoChannel settings' })).toBeVisible();
    await shoot('home');
  });

  test('instructions', async ({ page, shoot }) => {
    await page.goto('/instructions');
    await expect(page).toHaveTitle(/Instructions to use Auto-chan/);
    await expect(page.getByRole('main').getByRole('heading').first()).toBeVisible();
    await shoot('instructions');
  });

  test('dashboard logged out', async ({ page, shoot }) => {
    await page.goto('/dashboard');
    const login = page.getByRole('main').getByRole('link', { name: 'Login' });
    await expect(login).toBeVisible();
    await expect(login).toHaveAttribute('href', '/login');
    await shoot('dashboard-logged-out');
  });

  test('not found', async ({ page, shoot }) => {
    await page.goto('/no-such-page');
    await expect(page.getByRole('heading', { name: 'Not Found' })).toBeVisible();
    await shoot('not-found');
  });
});

test.describe('logged in', () => {
  test.use({
    api: {
      ...loggedIn,
      [`GET /api/guilds/${GUILD.id}`]: reply(200, GUILD_DETAIL),
      [`GET /api/guilds/${OTHER_GUILD.id}`]: reply(409, { error: 'Bot not in guild', invite_url: INVITE_URL }),
      ...Object.fromEntries(
        CATEGORIES.map((c) => [
          `PATCH /api/guilds/${GUILD.id}/categories/${c.id}`,
          (request: Request) => ({
            status: 200,
            body: { category: { ...c, ...(request.postDataJSON() as Partial<CategorySettings>) } },
          }),
        ]),
      ),
    },
  });

  test('dashboard logged in', async ({ page, shoot }) => {
    await page.goto('/dashboard');
    const main = page.getByRole('main');
    await expect(main.getByRole('heading', { name: 'Your servers' })).toBeVisible();
    await expect(main.getByText('Signed in as hank')).toBeVisible();
    await expect(main.getByRole('link', { name: 'Planet Express' })).toHaveAttribute('href', `/dashboard/${GUILD.id}`);
    await expect(main.getByRole('link', { name: 'Mom Corp' })).toHaveAttribute('href', `/dashboard/${OTHER_GUILD.id}`);
    // Each tile shows the server's name as visible text, not just an icon.
    await expect(main.getByText('Planet Express', { exact: true })).toBeVisible();
    await expect(main.getByText('Mom Corp', { exact: true })).toBeVisible();
    await shoot('dashboard-logged-in');
  });

  test('guild categories', async ({ page, shoot }) => {
    await page.goto(`/dashboard/${GUILD.id}`);
    await expect(page.getByRole('main').getByRole('heading', { name: 'Planet Express' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'AutoChannel' })).toHaveAttribute('aria-selected', 'true');
    await expect(page.getByRole('switch', { name: 'Raids enabled' })).toBeChecked();
    await expect(page.getByRole('textbox', { name: 'Deliveries prefix' })).toHaveValue('PE!');
    await expect(page.getByRole('spinbutton', { name: 'Raids channel size' })).toHaveValue('10');
    await expect(page.getByRole('spinbutton', { name: 'Raids empty count' })).toHaveValue('1');
    await expect(page.getByRole('button', { name: 'Save Raids prefix' })).toBeVisible();
    // Help text, defaults and ranges are on the page without hovering, shown once for all categories.
    const guide = page.locator('.settings-guide');
    await expect(guide.getByText('Must be unique for channels in this category')).toBeVisible();
    await expect(guide.getByText('Default: AC!')).toBeVisible();
    await expect(guide.getByText('Range: 0–99')).toBeVisible();
    await expect(guide.getByText('Range: 1–10')).toBeVisible();
    await expect(page.getByText('Range: 0–99')).toHaveCount(1);
    await expect(page.getByRole('region', { name: 'Raids' })).toBeVisible();
    // The filter only appears for long lists.
    await expect(page.getByRole('searchbox', { name: 'Filter categories' })).toHaveCount(0);
    await expect(page.locator('.alert-danger')).toHaveCount(0);
    await shoot('guild-categories');
  });

  test('guild categories custom channels tab', async ({ page, shoot }) => {
    await page.goto(`/dashboard/${GUILD.id}`);
    await page.getByRole('tab', { name: 'Custom Channels' }).click();
    await expect(page.getByRole('tab', { name: 'Custom Channels' })).toHaveAttribute('aria-selected', 'true');
    await expect(page.getByRole('textbox', { name: 'Deliveries custom prefix' })).toHaveValue('DL!');
    await expect(page.getByRole('switch', { name: 'Deliveries custom channels enabled' })).toBeChecked();
    await expect(page.getByText('Default: VC!')).toBeVisible();

    // Exercise the PATCH mock: the toggle saves and a toast confirms it.
    const toggle = page.getByRole('switch', { name: 'Raids custom channels enabled' });
    const patch = page.waitForRequest((r) => r.method() === 'PATCH');
    await toggle.click();
    expect((await patch).postDataJSON()).toEqual({ custom_enabled: true });
    await expect(page.getByRole('status').filter({ hasText: 'Raids: true' })).toBeVisible();
    await expect(toggle).toBeChecked();
    await shoot('guild-categories-custom');
  });

  test('guild categories when the bot is not in the server', async ({ page, shoot }) => {
    await page.goto(`/dashboard/${OTHER_GUILD.id}`);
    const invite = page.getByRole('link', { name: 'Add Auto-chan to Mom Corp' });
    await expect(invite).toBeVisible();
    await expect(invite).toHaveAttribute('href', INVITE_URL);
    await shoot('guild-not-added');
  });

  test('guild added', async ({ page, shoot }) => {
    await page.goto(`/guild-added/${GUILD.id}`);
    await expect(page.getByRole('main').getByRole('heading', { name: 'Planet Express' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Dashboard' })).toHaveAttribute('href', `/dashboard/${GUILD.id}`);
    await shoot('guild-added');
  });

  test('guild categories while saving', async ({ page, shoot }) => {
    // Hold the PATCH so the busy state stays on screen.
    let release!: () => void;
    const held = new Promise<void>((resolve) => (release = resolve));
    await page.route('**/api/guilds/*/categories/*', async (route) => {
      await held;
      await route.fallback();
    });
    await page.goto(`/dashboard/${GUILD.id}`);
    const input = page.getByRole('textbox', { name: 'Raids prefix' });
    await input.fill('RD!');
    const save = page.getByRole('button', { name: 'Save Raids prefix' });
    await save.click();
    await expect(save).toBeDisabled();
    await expect(save).toHaveAttribute('aria-busy', 'true');
    await expect(save.locator('.spinner-border')).toBeVisible();
    await shoot('guild-categories-saving');
    release();
    await expect(save).toBeEnabled();
    await expect(input).toHaveValue('RD!');
  });
});

test.describe('many categories', () => {
  test.use({
    api: {
      ...loggedIn,
      [`GET /api/guilds/${GUILD.id}`]: reply(200, { guild: GUILD, categories: MANY_CATEGORIES }),
    },
  });

  test('guild categories with a long list', async ({ page, shoot }) => {
    await page.goto(`/dashboard/${GUILD.id}`);
    const rows = page.locator('.category-row');
    await expect(rows).toHaveCount(MANY_CATEGORIES.length);
    // Help is shown once, not once per category.
    await expect(page.getByText('Must be unique for channels in this category')).toHaveCount(1);
    await expect(page.getByText('Range: 0–99')).toHaveCount(1);
    await shoot('guild-categories-many');

    const filter = page.getByRole('searchbox', { name: 'Filter categories' });
    await filter.fill('raid');
    await expect(rows).toHaveCount(2);
    await expect(page.getByRole('switch', { name: 'Raids enabled' })).toBeVisible();
    await expect(page.getByRole('switch', { name: 'Raid Planning enabled' })).toBeVisible();
    await expect(page.getByText(`Showing 2 of ${MANY_CATEGORIES.length} categories`)).toBeVisible();

    // The filter is kept when switching tabs.
    await page.getByRole('tab', { name: 'Custom Channels' }).click();
    await expect(page.getByRole('textbox', { name: 'Raids custom prefix' })).toBeVisible();
    await expect(rows).toHaveCount(2);

    await filter.fill('nothing like this');
    await expect(rows).toHaveCount(0);
    await expect(page.getByText('No categories match')).toBeVisible();
  });
});

test.describe('no managed servers', () => {
  test.use({ api: { 'GET /api/me': reply(200, { ...ME, guilds: [] }) } });

  test('dashboard empty state', async ({ page, shoot }) => {
    await page.goto('/dashboard');
    await expect(page.getByRole('main').getByRole('heading', { name: 'No servers to manage yet' })).toBeVisible();
    await expect(page.getByText('Manage Server')).toBeVisible();
    await shoot('dashboard-empty');
  });
});

test.describe('theme', () => {
  test.use({ api: loggedOut, colorScheme: 'dark' });

  test('follows the OS at first paint and remembers the toggle', async ({ page }) => {
    // Hold back the app bundle: index.html alone must already have set the theme.
    let release!: () => void;
    const held = new Promise<void>((resolve) => (release = resolve));
    let bundleRequested = false;
    await page.route('**/assets/*.js', async (route) => {
      bundleRequested = true;
      await held;
      await route.fallback();
    });

    await page.goto('/', { waitUntil: 'commit' });
    await expect.poll(() => bundleRequested).toBe(true);
    await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'dark');
    expect(await page.locator('#root').innerHTML(), 'the app should not have rendered yet').toBe('');

    release();
    const toggle = page.getByRole('banner').getByRole('button', { name: 'Dark theme' });
    await expect(toggle).toHaveAttribute('aria-pressed', 'true');
    await toggle.click();
    await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'light');
    await expect(toggle).toHaveAttribute('aria-pressed', 'false');

    await page.reload();
    await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'light');
    await expect(toggle).toHaveAttribute('aria-pressed', 'false');
  });

  test('uses the light theme when the OS prefers light', async ({ page }) => {
    await page.emulateMedia({ colorScheme: 'light' });
    await page.goto('/');
    await expect(page.locator('html')).toHaveAttribute('data-bs-theme', 'light');
  });
});

test.describe('mobile 375px', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  async function expectFits(page: Page) {
    const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
    expect(scrollWidth, 'the page should not scroll sideways').toBeLessThanOrEqual(375);
  }

  async function expectNavReachable(page: Page) {
    const banner = page.getByRole('banner');
    await expect(banner.getByRole('link', { name: 'Servers' })).toBeInViewport();
    await expect(banner.getByRole('link', { name: 'How-To' })).toBeInViewport();
    await expect(banner.getByRole('button', { name: 'Dark theme' })).toBeInViewport();
  }

  test.describe('logged out', () => {
    test.use({ api: loggedOut });

    test('home', async ({ page, shoot }) => {
      await page.goto('/');
      await expect(page.getByRole('heading', { name: /Welcome to AutoChannel/ })).toBeVisible();
      await expectNavReachable(page);
      await expect(page.getByRole('banner').getByRole('link', { name: 'Login' })).toBeInViewport();
      await expectFits(page);
      await shoot('mobile-home-logged-out');
    });
  });

  test.describe('logged in', () => {
    test.use({ api: { ...loggedIn, [`GET /api/guilds/${GUILD.id}`]: reply(200, GUILD_DETAIL) } });

    async function expectLogoutReachable(page: Page) {
      await page.getByRole('banner').getByRole('button', { name: 'hank' }).click();
      const logout = page.getByRole('banner').getByRole('link', { name: 'Logout' });
      await expect(logout).toBeInViewport();
      await expect(logout).toHaveAttribute('href', '/logout');
      await expectFits(page);
      await page.keyboard.press('Escape');
      await expect(logout).toBeHidden();
    }

    const screens = [
      ['home', '/'],
      ['dashboard', '/dashboard'],
      ['guild-categories', `/dashboard/${GUILD.id}`],
    ] as const;

    for (const [name, path] of screens) {
      test(name, async ({ page, shoot }) => {
        await page.goto(path);
        await expect(page.getByRole('main').getByRole('heading').first()).toBeVisible();
        if (name === 'guild-categories') {
          await expect(page.getByRole('switch', { name: 'Raids enabled' })).toBeVisible();
          await expect(page.getByRole('button', { name: 'Save Deliveries empty count' })).toBeVisible();
          await page.getByRole('tab', { name: 'Custom Channels' }).click();
          await expect(page.getByRole('textbox', { name: 'Raids custom prefix' })).toBeVisible();
          await expectFits(page);
          await page.getByRole('tab', { name: 'AutoChannel' }).click();
        }
        await expectNavReachable(page);
        await expectLogoutReachable(page);
        await expectFits(page);
        await shoot(`mobile-${name}`);
      });
    }
  });
});

test.describe('keyboard focus', () => {
  test.use({ api: { ...loggedIn, [`GET /api/guilds/${GUILD.id}`]: reply(200, GUILD_DETAIL) } });

  for (const theme of THEMES) {
    test(`guild categories shows a focus ring on every control (${theme})`, async ({ page }) => {
      await page.emulateMedia({ colorScheme: theme });
      await page.goto(`/dashboard/${GUILD.id}`);
      await expect(page.locator('html')).toHaveAttribute('data-bs-theme', theme);
      await expect(page.getByRole('switch', { name: 'Raids enabled' })).toBeVisible();

      // Tab from the top of the page until focus reaches the last save button.
      const seen: { name: string; ring: boolean }[] = [];
      const last = page.getByRole('button', { name: 'Save Deliveries empty count' });
      for (let i = 0; i < 40; i++) {
        await page.keyboard.press('Tab');
        const info = await page.evaluate(() => {
          const el = document.activeElement as HTMLElement;
          const style = getComputedStyle(el);
          return {
            name: `${el.getAttribute('role') ?? el.tagName.toLowerCase()} ${el.getAttribute('aria-label') ?? el.textContent?.trim()}`,
            inSettings: !!el.closest('[role=tabpanel], [role=tablist]'),
            ring: style.outlineStyle !== 'none' && parseFloat(style.outlineWidth) >= 2,
          };
        });
        if (info.inSettings) seen.push(info);
        if (await last.evaluate((el) => el === document.activeElement)) break;
      }

      // 2 tabs, then per category: a switch and three inputs with their save buttons.
      expect(seen.map((s) => s.name)).toHaveLength(2 + CATEGORIES.length * 7);
      expect(seen.filter((s) => !s.ring).map((s) => s.name), 'controls without a focus ring').toEqual([]);

      for (const [shot, target] of [
        ['tab', page.getByRole('tab', { name: 'AutoChannel' })],
        ['switch', page.getByRole('switch', { name: 'Raids enabled' })],
        ['input', page.getByRole('textbox', { name: 'Raids prefix' })],
        ['save', page.getByRole('button', { name: 'Save Raids prefix' })],
      ] as const) {
        await target.focus();
        await page.screenshot({ path: join(SCREENSHOT_DIR, `focus-${shot}-${theme}.png`), animations: 'disabled' });
      }
    });
  }
});
