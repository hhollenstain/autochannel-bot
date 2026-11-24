import { Link, useParams } from 'react-router';
import GuildHeader from '../components/GuildHeader';
import Instructions from '../components/Instructions';
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
      <GuildHeader icon={guild?.icon}>{guild?.name}</GuildHeader>
      <h4 className="text-center my-3">
        AutoChannel bot was added:{' '}
        <Link className="btn btn-primary" to={`/dashboard/${guildId}`}>
          Dashboard
        </Link>
      </h4>
      <Instructions />
    </RequireLogin>
  );
}
