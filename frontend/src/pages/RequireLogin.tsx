import type { ReactNode } from 'react';
import { useSession } from '../session';

export function RequireLogin({ children }: { children: ReactNode }) {
  const { me } = useSession();

  if (me === undefined) return <Loading />;
  if (me === null) {
    return (
      <div className="state-panel surface">
        <h1 className="h3">Log in with Discord to manage your servers</h1>
        <p>Auto-chan uses your Discord account to find the servers you can manage.</p>
        <a className="btn btn-primary btn-lg" href="/login">
          Login
        </a>
      </div>
    );
  }
  return <>{children}</>;
}

export function Loading() {
  return (
    <div className="loading">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
    </div>
  );
}
