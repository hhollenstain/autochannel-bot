import type { ReactNode } from 'react';
import { useSession } from '../session';

export function RequireLogin({ children }: { children: ReactNode }) {
  const { me } = useSession();

  if (me === undefined) return <Loading />;
  if (me === null) {
    return (
      <div className="text-center mt-5">
        <h3>Log in with Discord to manage your servers</h3>
        <a className="btn btn-primary mt-3" href="/login">
          Login
        </a>
      </div>
    );
  }
  return <>{children}</>;
}

export function Loading() {
  return (
    <div className="text-center mt-5">
      <div className="spinner-border" role="status">
        <span className="visually-hidden">Loading...</span>
      </div>
    </div>
  );
}
