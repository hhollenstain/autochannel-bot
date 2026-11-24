// Discord ids are snowflakes (> 2^53) so the API always sends them as strings.

export interface User {
  id: string;
  username: string;
  avatar: string;
}

export interface Guild {
  id: string;
  name: string;
  icon: string;
}

export interface CategorySettings {
  enabled: boolean;
  prefix: string;
  channel_size: number;
  empty_count: number;
  custom_enabled: boolean;
  custom_prefix: string;
}

export interface Category extends CategorySettings {
  id: string;
  name: string;
}

export interface Me {
  user: User;
  guilds: Guild[];
}

export interface GuildDetail {
  guild: Guild;
  categories: Category[];
}

export class ApiError extends Error {
  status: number;
  body: Record<string, unknown>;

  constructor(status: number, body: Record<string, unknown>) {
    super(typeof body.error === 'string' ? body.error : `Request failed (${status})`);
    this.status = status;
    this.body = body;
  }

  /** Per-field validation messages from a 400 response. */
  get fields(): Record<string, string> {
    return (this.body.fields as Record<string, string>) ?? {};
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`/api${path}`, {
    credentials: 'same-origin',
    ...init,
    headers: { Accept: 'application/json', ...init?.headers },
  });
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(res.status, body);
  return body as T;
}

export const api = {
  me: () => request<Me>('/me'),

  guild: (guildId: string) => request<GuildDetail>(`/guilds/${guildId}`),

  updateCategory: (guildId: string, categoryId: string, changes: Partial<CategorySettings>) =>
    request<{ category: CategorySettings & { id: string } }>(
      `/guilds/${guildId}/categories/${categoryId}`,
      {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(changes),
      },
    ),
};
