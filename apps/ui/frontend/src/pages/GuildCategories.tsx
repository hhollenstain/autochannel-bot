import { useEffect, useId, useState, type ReactNode } from 'react';
import { useParams } from 'react-router';
import { api, ApiError, type CategorySettings, type GuildDetail } from '../api';
import CategoryTable from '../components/CategoryTable';
import PageHeader from '../components/PageHeader';
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

type Tab = 'auto' | 'custom';

const BACK = { to: '/dashboard', label: 'All servers' };

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
  const [tab, setTab] = useState<Tab>('auto');
  const tabsId = useId();
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
      return (
        <>
          <PageHeader icon={guild?.icon} title={guild?.name ?? 'Server'} back={BACK} />
          <div className="alert alert-danger" role="alert">
            Could not load this server: {state.message}
          </div>
        </>
      );
    case 'invite':
      return (
        <>
          <PageHeader icon={guild?.icon} title={guild?.name ?? 'Server'} back={BACK} />
          <div className="state-panel surface">
            <h2>Auto-chan isn't in this server yet.</h2>
            <p>Add the bot through Discord, then come back here to choose its settings.</p>
            <a className="btn btn-primary btn-lg" href={state.inviteUrl}>
              Add Auto-chan to {guild?.name ?? 'this server'}
            </a>
          </div>
        </>
      );
    case 'ready': {
      const { guild: g, categories } = state.detail;
      const tabId = (t: Tab) => `${tabsId}-${t}`;
      return (
        <>
          <PageHeader
            icon={g.icon}
            title={g.name}
            description="Choose how Auto-chan manages voice channels in each category."
            back={BACK}
          />
          <div className="settings-toolbar">
            <div className="segmented" role="tablist" aria-label="Channel settings">
              <TabButton id={tabId('auto')} panel={`${tabsId}-panel`} active={tab === 'auto'} onClick={() => setTab('auto')}>
                AutoChannel
              </TabButton>
              <TabButton
                id={tabId('custom')}
                panel={`${tabsId}-panel`}
                active={tab === 'custom'}
                onClick={() => setTab('custom')}
              >
                Custom Channels
              </TabButton>
            </div>
            <p>
              After saving, run <code>!acupdate</code> in your server to sync the bot.
            </p>
          </div>
          <div role="tabpanel" id={`${tabsId}-panel`} aria-labelledby={tabId(tab)}>
            <CategoryTable guildId={guildId} categories={categories} mode={tab} onUpdated={onUpdated} />
          </div>
        </>
      );
    }
  }
}

function TabButton({
  id,
  panel,
  active,
  onClick,
  children,
}: {
  id: string;
  panel: string;
  active: boolean;
  onClick: () => void;
  children: ReactNode;
}) {
  return (
    <button
      type="button"
      role="tab"
      id={id}
      aria-selected={active}
      aria-controls={panel}
      className="segmented-option"
      onClick={onClick}
    >
      {children}
    </button>
  );
}
