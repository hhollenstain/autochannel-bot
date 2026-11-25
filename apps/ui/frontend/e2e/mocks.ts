import type { Category, Guild, GuildDetail, Me } from '../src/api';

// Icons point at files in public/img so no Discord CDN request is made.
export const GUILD: Guild = {
  id: '321048288574963722',
  name: 'Planet Express',
  icon: '/img/auto-chan-white.png',
};

export const OTHER_GUILD: Guild = {
  id: '321048288574963723',
  name: 'Mom Corp',
  icon: '/img/auto-chan-name.png',
};

export const ME: Me = {
  user: { id: '1', username: 'hank', avatar: '/img/auto-chan-white.png' },
  guilds: [GUILD, OTHER_GUILD],
};

export const CATEGORIES: Category[] = [
  {
    id: '400000000000000001',
    name: 'Raids',
    enabled: true,
    prefix: 'AC!',
    channel_size: 10,
    empty_count: 1,
    custom_enabled: false,
    custom_prefix: 'VC!',
  },
  {
    id: '400000000000000002',
    name: 'Deliveries',
    enabled: false,
    prefix: 'PE!',
    channel_size: 4,
    empty_count: 2,
    custom_enabled: true,
    custom_prefix: 'DL!',
  },
];

export const GUILD_DETAIL: GuildDetail = { guild: GUILD, categories: CATEGORIES };

/** A server with 20 categories, to check the page stays manageable with a long list. */
export const MANY_CATEGORIES: Category[] = [
  ...CATEGORIES,
  ...[
    'Raid Planning',
    'General',
    'Gaming',
    'Music',
    'Study Hall',
    'Movie Night',
    'Book Club',
    'Art',
    'Dev Talk',
    'Support',
    'Events',
    'Tournaments',
    'Off Topic',
    'Streaming',
    'Trading',
    'Voice Lounge',
    'Late Night',
    'AFK',
  ].map((name, i) => ({
    id: `4000000000000001${String(i).padStart(2, '0')}`,
    name,
    enabled: i % 3 !== 0,
    prefix: `${name.slice(0, 2).toUpperCase()}!`,
    channel_size: (i % 5) * 2,
    empty_count: (i % 3) + 1,
    custom_enabled: i % 4 === 0,
    custom_prefix: 'VC!',
  })),
];

export const INVITE_URL = 'https://discord.com/oauth2/authorize?client_id=0&scope=bot&guild_id=' + OTHER_GUILD.id;
