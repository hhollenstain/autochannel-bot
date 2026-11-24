import { createContext, useCallback, useContext, useRef, useState, type ReactNode } from 'react';

type Kind = 'success' | 'error';

interface Toast {
  id: number;
  kind: Kind;
  title: string;
  message: string;
}

type Notify = (kind: Kind, title: string, message: string) => void;

const ToastContext = createContext<Notify>(() => {});

const DISMISS_MS = 4000;

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);
  const nextId = useRef(0);

  const dismiss = useCallback((id: number) => {
    setToasts((ts) => ts.filter((t) => t.id !== id));
  }, []);

  const notify = useCallback<Notify>(
    (kind, title, message) => {
      const id = nextId.current++;
      setToasts((ts) => [...ts, { id, kind, title, message }]);
      setTimeout(() => dismiss(id), DISMISS_MS);
    },
    [dismiss],
  );

  return (
    <ToastContext.Provider value={notify}>
      {children}
      <div className="toast-stack" aria-live="polite">
        {toasts.map((t) => (
          <div key={t.id} className={`ac-toast ac-toast-${t.kind}`} role="status">
            <button className="btn-close btn-close-white" aria-label="Close" onClick={() => dismiss(t.id)} />
            <strong>{t.title}</strong>
            <div>{t.message}</div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export const useToast = () => useContext(ToastContext);
