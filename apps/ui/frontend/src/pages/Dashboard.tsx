import { Link } from 'react-router';
import { ChevronRightIcon, ServerIcon } from '../components/icons';
import PageHeader from '../components/PageHeader';
import { useTitle } from '../hooks';
import { useSession } from '../session';
import { RequireLogin } from './RequireLogin';

export default function Dashboard() {
  const { me } = useSession();
  useTitle(me ? `Guilds managed by ${me.user.username}` : 'Servers');

  return (
    <RequireLogin>
      <PageHeader
        title="Your servers"
        description={me && `Signed in as ${me.user.username}. Pick a server to set up Auto-chan.`}
      />
      {me?.guilds.length === 0 ? (
        <div className="state-panel surface">
          <div className="state-panel-icon">
            <ServerIcon />
          </div>
          <h2>No servers to manage yet</h2>
          <p className="mb-0">
            Servers appear here when you have the <strong>Manage Server</strong> permission in
            them. Ask a server owner for it, or create your own server in Discord.
          </p>
        </div>
      ) : (
        <ul className="server-grid">
          {me?.guilds.map((g) => (
            <li key={g.id}>
              <Link className="server-card" to={`/dashboard/${g.id}`}>
                <img src={g.icon} width={56} height={56} className="avatar" alt="" />
                <span className="server-card-name">{g.name}</span>
                <ChevronRightIcon />
              </Link>
            </li>
          ))}
        </ul>
      )}
    </RequireLogin>
  );
}
