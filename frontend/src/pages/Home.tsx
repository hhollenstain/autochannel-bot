import { Link } from 'react-router';
import PageHeader from '../components/PageHeader';
import { useTitle } from '../hooks';

export default function Home() {
  useTitle('Welcome to Autochannel Bot!');

  return (
    <>
      <PageHeader
        title="Welcome to AutoChannel"
        description="Voice channels that open and close on their own, so your server always has a free room."
        actions={
          <>
            <Link to="/dashboard" className="btn btn-primary btn-lg">
              Add Auto-chan!
            </Link>
            <Link to="/instructions" className="btn btn-secondary btn-lg">
              How it works
            </Link>
          </>
        }
      />
      <div className="home-grid">
        <section className="surface prose" aria-labelledby="home-what">
          <h2 id="home-what" className="section-title">
            What is AutoChannel?
          </h2>
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
          <p className="mb-0">
            Auto-chan also checks to make sure you don't have too many channels in your categories.
            If people leave it will automatically clean up empty channels.
          </p>
        </section>
        <section className="surface" aria-labelledby="home-dashboards">
          <h2 id="home-dashboards" className="section-title">
            Auto-chan dashboards
          </h2>
          <img className="screenshot" width={560} src="/img/autochannels-guild.png" alt="AutoChannel settings" />
          <img className="screenshot" width={560} src="/img/autochannel-custom.png" alt="Custom channel settings" />
        </section>
      </div>
    </>
  );
}
