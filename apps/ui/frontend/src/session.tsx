import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import { api, ApiError, type Me } from './api';

interface SessionState {
  /** undefined while loading, null when logged out. */
  me: Me | null | undefined;
}

const SessionContext = createContext<SessionState>({ me: undefined });

export function SessionProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null | undefined>(undefined);

  useEffect(() => {
    api
      .me()
      .then(setMe)
      .catch((e) => {
        if (!(e instanceof ApiError && e.status === 401)) console.error(e);
        setMe(null);
      });
  }, []);

  return <SessionContext.Provider value={{ me }}>{children}</SessionContext.Provider>;
}

export const useSession = () => useContext(SessionContext);
