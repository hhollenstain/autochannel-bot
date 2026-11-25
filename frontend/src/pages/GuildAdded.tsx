import { Link, useParams } from 'react-router';
import Instructions from '../components/Instructions';
import PageHeader from '../components/PageHeader';
import { useTitle } from '../hooks';
import { useSession } from '../session';
import { RequireLogin } from './RequireLogin';

export default function GuildAdded() {
  const { guildId = '' } = useParams();
  const { me } = useSession();
  const guild = me?.guilds.find((g) => g.id === guildId);
  useTitle(guild ? `Auto-chan added to ${guild.name}` : undefined);

  return (
    <RequireLogin>
      <PageHeader
        icon={guild?.icon}
        title={guild?.name ?? 'Server'}
        description="AutoChannel bot was added. Next, choose its settings for each category."
        actions={
          <Link className="btn btn-primary btn-lg" to={`/dashboard/${guildId}`}>
            Dashboard
          </Link>
        }
      />
      <Instructions />
    </RequireLogin>
  );
}
