import { Link } from 'react-router';
import GuildHeader from '../components/GuildHeader';
import { useTitle } from '../hooks';
import { useSession } from '../session';
import { RequireLogin } from './RequireLogin';

export default function Dashboard() {
  const { me } = useSession();
  useTitle(me ? `Guilds managed by ${me.user.username}` : 'Servers');

  return (
    <RequireLogin>
      <GuildHeader>{me?.user.username}: Guilds</GuildHeader>
      {me?.guilds.length === 0 ? (
        <p className="text-center">You don't manage any servers. You need the Manage Server permission.</p>
      ) : (
        <div className="d-flex justify-content-center flex-wrap animated bounceInUp">
          {me?.guilds.map((g) => (
            <Link key={g.id} to={`/dashboard/${g.id}`} title={g.name} className="select-server my-3">
              <img src={g.icon} width={128} height={128} className="img-circle" alt={g.name} />
            </Link>
          ))}
        </div>
      )}
    </RequireLogin>
  );
}
