import { Link } from 'react-router';
import GuildHeader from '../components/GuildHeader';
import { useTitle } from '../hooks';

export default function Home() {
  useTitle('Welcome to Autochannel Bot!');

  return (
    <>
      <GuildHeader>
        Welcome to AutoChannel{' '}
        <Link to="/dashboard" className="btn btn-primary">
          Add Auto-chan!
        </Link>
      </GuildHeader>
      <div className="row">
        <div className="col-md-6 mx-auto">
          <h4>What is AutoChannel?</h4>
          <p>
            AutoChannel is here for Admins/moderators/channel managers to facilitate managing voice
            channels. This can help you moderate small to large discord servers with over 1 million+
            active users.
          </p>
          <p>
            Auto-chan (AutoChannels friendly bot!) does this by watching categories you specified to
            always have empty channels. You can tell Auto-chan to watch specific categories and
            always make sure it has 1-10 empty channels and you can set how many users can be in
            each channel generated. You might think but how does this make my life easier? This
            means you will no longer have excess channels and not have to scroll endless looking for
            groups or see how many rooms are occupied.
          </p>
          <p>
            Auto-chan also checks to make sure you don't have too many channels in your categories.
            If people leave it will automatically clean up empty channels.
          </p>
        </div>
        <div className="col-md-6 mx-auto">
          <h4>Auto-chan dashboards</h4>
          <p>
            <img className="img-fluid" width={400} src="/img/autochannels-guild.png" alt="AutoChannel settings" />
          </p>
          <p>
            <img className="img-fluid" width={400} src="/img/autochannel-custom.png" alt="Custom channel settings" />
          </p>
        </div>
      </div>
    </>
  );
}
