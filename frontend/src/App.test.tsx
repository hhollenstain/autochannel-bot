import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router';
import { describe, expect, it, vi } from 'vitest';
import App from './App';
import { SessionProvider } from './session';
import { ToastProvider } from './toasts';

const GUILD = { id: '321048288574963722', name: 'Planet Express', icon: '/i.png' };
const ME = { user: { id: '1', username: 'hank', avatar: '/a.png' }, guilds: [GUILD] };
const CATEGORY = {
  id: '400000000000000001',
  name: 'Raids',
  enabled: false,
  prefix: 'AC!',
  channel_size: 10,
  empty_count: 1,
  custom_enabled: false,
  custom_prefix: 'VC!',
};

type Handler = (init?: RequestInit) => [number, unknown];

function mockApi(routes: Record<string, Handler>) {
  return vi.spyOn(globalThis, 'fetch').mockImplementation(async (input, init) => {
    const key = `${init?.method ?? 'GET'} ${String(input)}`;
    const handler = routes[key];
    if (!handler) throw new Error(`unexpected request ${key}`);
    const [status, body] = handler(init);
    return new Response(JSON.stringify(body), { status });
  });
}

function renderAt(path: string) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <SessionProvider>
        <ToastProvider>
          <App />
        </ToastProvider>
      </SessionProvider>
    </MemoryRouter>,
  );
}

const guildUrl = `/api/guilds/${GUILD.id}`;
const categoryUrl = `${guildUrl}/categories/${CATEGORY.id}`;

describe('App', () => {
  it('asks logged out users to log in', async () => {
    mockApi({ 'GET /api/me': () => [401, { error: 'Not logged in' }] });
    renderAt('/dashboard');
    const main = within(screen.getByRole('main'));
    expect(await main.findByRole('link', { name: 'Login' })).toHaveAttribute('href', '/login');
  });

  it('lists managed servers', async () => {
    mockApi({ 'GET /api/me': () => [200, ME] });
    renderAt('/dashboard');
    const main = within(screen.getByRole('main'));
    expect(await main.findByRole('link', { name: 'Planet Express' })).toHaveAttribute(
      'href',
      `/dashboard/${GUILD.id}`,
    );
  });

  it('toggles a category and confirms with a toast', async () => {
    const fetch = mockApi({
      'GET /api/me': () => [200, ME],
      [`GET ${guildUrl}`]: () => [200, { guild: GUILD, categories: [CATEGORY] }],
      [`PATCH ${categoryUrl}`]: (init) => [
        200,
        { category: { ...CATEGORY, ...JSON.parse(String(init?.body)) } },
      ],
    });
    renderAt(`/dashboard/${GUILD.id}`);

    const toggle = await screen.findByRole('switch', { name: 'Raids enabled' });
    await userEvent.click(toggle);

    expect(await screen.findByRole('status')).toHaveTextContent('Raids: true');
    expect(toggle).toBeChecked();
    const patch = fetch.mock.calls.find(([, init]) => init?.method === 'PATCH');
    expect(JSON.parse(String(patch?.[1]?.body))).toEqual({ enabled: true });
  });

  it('shows the validation error and restores the saved value', async () => {
    mockApi({
      'GET /api/me': () => [200, ME],
      [`GET ${guildUrl}`]: () => [200, { guild: GUILD, categories: [CATEGORY] }],
      [`PATCH ${categoryUrl}`]: () => [
        400,
        { error: 'Invalid', fields: { empty_count: 'must be a whole number between 1 and 10' } },
      ],
    });
    renderAt(`/dashboard/${GUILD.id}`);

    const input = await screen.findByRole('spinbutton', { name: 'Raids empty count' });
    await userEvent.clear(input);
    await userEvent.type(input, '5{Enter}');

    expect(await screen.findByRole('status')).toHaveTextContent('between 1 and 10');
    await waitFor(() => expect(input).toHaveValue(1));
  });

  it('switches to the custom channel settings tab', async () => {
    mockApi({
      'GET /api/me': () => [200, ME],
      [`GET ${guildUrl}`]: () => [200, { guild: GUILD, categories: [CATEGORY] }],
    });
    renderAt(`/dashboard/${GUILD.id}`);

    await userEvent.click(await screen.findByRole('tab', { name: 'Custom Channels' }));
    expect(screen.getByRole('textbox', { name: 'Raids custom prefix' })).toHaveValue('VC!');
    expect(screen.queryByRole('textbox', { name: 'Raids prefix' })).not.toBeInTheDocument();
  });

  it('offers the bot invite when it is not in the server', async () => {
    mockApi({
      'GET /api/me': () => [200, ME],
      [`GET ${guildUrl}`]: () => [409, { error: 'not added', invite_url: 'https://discord.test/invite' }],
    });
    renderAt(`/dashboard/${GUILD.id}`);
    expect(await screen.findByRole('link', { name: /Add Auto-chan to Planet Express/ })).toHaveAttribute(
      'href',
      'https://discord.test/invite',
    );
  });

  it('redirects old /dashboard/:userId/:guildId links', async () => {
    mockApi({
      'GET /api/me': () => [200, ME],
      [`GET ${guildUrl}`]: () => [200, { guild: GUILD, categories: [CATEGORY] }],
    });
    renderAt(`/dashboard/1/${GUILD.id}`);
    expect(await screen.findByRole('switch', { name: 'Raids enabled' })).toBeInTheDocument();
  });
});
