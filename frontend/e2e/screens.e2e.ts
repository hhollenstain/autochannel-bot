import type { Request } from '@playwright/test';
import type { CategorySettings } from '../src/api';
import { expect, test, type ApiRoutes } from './fixtures';
import { CATEGORIES, GUILD, GUILD_DETAIL, INVITE_URL, ME, OTHER_GUILD } from './mocks';

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
    await expect(main.getByRole('heading', { name: 'hank: Guilds' })).toBeVisible();
    await expect(main.getByRole('link', { name: 'Planet Express' })).toHaveAttribute('href', `/dashboard/${GUILD.id}`);
    await expect(main.getByRole('link', { name: 'Mom Corp' })).toBeVisible();
    await shoot('dashboard-logged-in');
  });

  test('guild categories', async ({ page, shoot }) => {
    await page.goto(`/dashboard/${GUILD.id}`);
    await expect(page.getByRole('main').getByRole('heading', { name: 'Planet Express' })).toBeVisible();
    await expect(page.getByRole('tab', { name: 'AutoChannel' })).toHaveAttribute('aria-selected', 'true');
    await expect(page.getByRole('switch', { name: 'Raids enabled' })).toBeChecked();
    await expect(page.getByRole('textbox', { name: 'Deliveries prefix' })).toHaveValue('PE!');
    await expect(page.locator('.alert-danger')).toHaveCount(0);
    await shoot('guild-categories');
  });

  test('guild categories custom channels tab', async ({ page, shoot }) => {
    await page.goto(`/dashboard/${GUILD.id}`);
    await page.getByRole('tab', { name: 'Custom Channels' }).click();
    await expect(page.getByRole('textbox', { name: 'Deliveries custom prefix' })).toHaveValue('DL!');

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
});
