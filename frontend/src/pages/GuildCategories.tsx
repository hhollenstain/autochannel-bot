import { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import { api, ApiError, type CategorySettings, type GuildDetail } from '../api';
import CategoryTable from '../components/CategoryTable';
import GuildHeader from '../components/GuildHeader';
import { useTitle } from '../hooks';
import { useSession } from '../session';
import NotFound from './NotFound';
import { Loading, RequireLogin } from './RequireLogin';

type State =
  | { status: 'loading' }
  | { status: 'ready'; detail: GuildDetail }
  | { status: 'invite'; inviteUrl: string }
  | { status: 'not-found' }
  | { status: 'error'; message: string };

export default function GuildCategories() {
  return (
    <RequireLogin>
      <GuildCategoriesInner />
    </RequireLogin>
  );
}

function GuildCategoriesInner() {
  const { guildId = '' } = useParams();
  const { me } = useSession();
  const [state, setState] = useState<State>({ status: 'loading' });
  const [tab, setTab] = useState<'auto' | 'custom'>('auto');
  const guild = me?.guilds.find((g) => g.id === guildId);

  useTitle(guild && me ? `Categories for ${guild.name}: ${me.user.username}` : 'Guild Categories');

  useEffect(() => {
    let cancelled = false;
    setState({ status: 'loading' });
    api
      .guild(guildId)
      .then((detail) => !cancelled && setState({ status: 'ready', detail }))
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 409) {
          setState({ status: 'invite', inviteUrl: String(e.body.invite_url) });
        } else if (e instanceof ApiError && e.status === 404) {
          setState({ status: 'not-found' });
        } else {
          setState({ status: 'error', message: e instanceof Error ? e.message : String(e) });
        }
      });
    return () => {
      cancelled = true;
    };
  }, [guildId]);

  function onUpdated(id: string, settings: Partial<CategorySettings>) {
    setState((s) =>
      s.status !== 'ready'
        ? s
        : {
            ...s,
            detail: {
              ...s.detail,
              categories: s.detail.categories.map((c) => (c.id === id ? { ...c, ...settings } : c)),
            },
          },
    );
  }

  switch (state.status) {
    case 'loading':
      return <Loading />;
    case 'not-found':
      return <NotFound />;
    case 'error':
      return <div className="alert alert-danger mt-3">Could not load this server: {state.message}</div>;
    case 'invite':
      return (
        <>
          <GuildHeader icon={guild?.icon}>{guild?.name}</GuildHeader>
          <div className="text-center mt-4">
            <h4>Auto-chan isn't in this server yet.</h4>
            <a className="btn btn-primary mt-3" href={state.inviteUrl}>
              Add Auto-chan to {guild?.name ?? 'this server'}
            </a>
          </div>
        </>
      );
    case 'ready': {
      const { guild: g, categories } = state.detail;
      return (
        <>
          <GuildHeader icon={g.icon}>{g.name}</GuildHeader>
          <ul className="nav nav-tabs justify-content-center mb-2" role="tablist">
            <TabButton active={tab === 'auto'} onClick={() => setTab('auto')}>
              AutoChannel
            </TabButton>
            <TabButton active={tab === 'custom'} onClick={() => setTab('custom')}>
              Custom Channels
            </TabButton>
          </ul>
          <CategoryTable guildId={guildId} categories={categories} mode={tab} onUpdated={onUpdated} />
        </>
      );
    }
  }
}

function TabButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: string;
}) {
  return (
    <li className={`nav-tab-header ${active ? 'active' : ''}`} role="presentation">
      <button type="button" role="tab" aria-selected={active} className="hvrcenter tab-button" onClick={onClick}>
        {children}
      </button>
    </li>
  );
}
