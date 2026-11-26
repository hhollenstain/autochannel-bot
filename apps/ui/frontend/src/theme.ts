import { useEffect, useSyncExternalStore } from 'react';

// The inline script in index.html sets `data-bs-theme` on <html> before first paint.
// That attribute is the single source of truth; this module only reads and updates it.

export type Theme = 'light' | 'dark';

const STORAGE_KEY = 'ac-theme';
const DARK_QUERY = '(prefers-color-scheme: dark)';

function currentTheme(): Theme {
  return document.documentElement.getAttribute('data-bs-theme') === 'dark' ? 'dark' : 'light';
}

function subscribe(onChange: () => void) {
  const observer = new MutationObserver(onChange);
  observer.observe(document.documentElement, { attributes: true, attributeFilter: ['data-bs-theme'] });
  return () => observer.disconnect();
}

function savedTheme(): Theme | null {
  try {
    const value = localStorage.getItem(STORAGE_KEY);
    return value === 'light' || value === 'dark' ? value : null;
  } catch {
    return null;
  }
}

function applyTheme(theme: Theme) {
  document.documentElement.setAttribute('data-bs-theme', theme);
}

/** The active theme plus a setter that also remembers the choice. */
export function useTheme(): [Theme, (theme: Theme) => void] {
  const theme = useSyncExternalStore(subscribe, currentTheme, () => 'light' as const);

  // Until the user picks a theme, keep following the OS setting.
  useEffect(() => {
    const media = window.matchMedia?.(DARK_QUERY);
    if (!media) return;
    const follow = (e: MediaQueryListEvent) => {
      if (!savedTheme()) applyTheme(e.matches ? 'dark' : 'light');
    };
    media.addEventListener('change', follow);
    return () => media.removeEventListener('change', follow);
  }, []);

  function setTheme(next: Theme) {
    applyTheme(next);
    try {
      localStorage.setItem(STORAGE_KEY, next);
    } catch {
      // Private mode or storage disabled: the choice lasts for this page only.
    }
  }

  return [theme, setTheme];
}
