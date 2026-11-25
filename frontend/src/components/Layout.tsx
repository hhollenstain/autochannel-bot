import { useEffect, useId, useRef, useState } from 'react';
import { Link, NavLink, Outlet, useLocation } from 'react-router';
import type { Me } from '../api';
import { useSession } from '../session';
import { useTheme } from '../theme';
import { ChevronDownIcon, MoonIcon, SunIcon } from './icons';

export default function Layout() {
  return (
    <div className="app">
      <a className="skip-link" href="#content">
        Skip to content
      </a>
      <Header />
      <main id="content" className="app-main" tabIndex={-1}>
        <div className="container-app">
          <Outlet />
        </div>
      </main>
      <Footer />
    </div>
  );
}

function Header() {
  const { me } = useSession();

  return (
    <header className="app-header">
      <nav aria-label="Main" className="container-app app-nav">
        <Link to="/" className="brand">
          <span className="brand-logo">
            <img src="/img/auto-chan-white.png" alt="" width={24} height={24} />
          </span>
          <span className="visually-hidden-sm">Auto-chan</span>
        </Link>
        <ul className="nav-links">
          <li>
            <NavLink to="/dashboard" className="nav-link-item">
              Servers
            </NavLink>
          </li>
          <li>
            <NavLink to="/instructions" className="nav-link-item">
              How-To
            </NavLink>
          </li>
        </ul>
        <div className="nav-actions">
          <ThemeToggle />
          {me ? (
            <UserMenu me={me} />
          ) : (
            // Hidden while the session loads so it doesn't flash for logged-in users.
            me === null && (
              <a href="/login" className="btn btn-primary btn-sm">
                Login
              </a>
            )
          )}
        </div>
      </nav>
    </header>
  );
}

function ThemeToggle() {
  const [theme, setTheme] = useTheme();
  const dark = theme === 'dark';

  return (
    <button
      type="button"
      className="icon-button"
      aria-label="Dark theme"
      aria-pressed={dark}
      title={dark ? 'Switch to light theme' : 'Switch to dark theme'}
      onClick={() => setTheme(dark ? 'light' : 'dark')}
    >
      {dark ? <MoonIcon /> : <SunIcon />}
    </button>
  );
}

function UserMenu({ me }: { me: Me }) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const panelId = useId();
  const { pathname } = useLocation();

  useEffect(() => setOpen(false), [pathname]);

  useEffect(() => {
    if (!open) return;
    const onPointer = (e: PointerEvent) => {
      if (!ref.current?.contains(e.target as Node)) setOpen(false);
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false);
    };
    document.addEventListener('pointerdown', onPointer);
    document.addEventListener('keydown', onKey);
    return () => {
      document.removeEventListener('pointerdown', onPointer);
      document.removeEventListener('keydown', onKey);
    };
  }, [open]);

  return (
    <div className="user-menu" ref={ref}>
      <button
        type="button"
        className="user-menu-button"
        aria-expanded={open}
        aria-controls={panelId}
        onClick={() => setOpen((o) => !o)}
      >
        <img src={me.user.avatar} width={28} height={28} className="avatar" alt="" />
        <span className="visually-hidden-sm">{me.user.username}</span>
        <ChevronDownIcon />
      </button>
      {open && (
        <div className="user-menu-panel" id={panelId}>
          <div className="user-menu-meta">
            Signed in as <strong>{me.user.username}</strong>
          </div>
          <a href="/logout">Logout</a>
        </div>
      )}
    </div>
  );
}

function Footer() {
  return (
    <footer className="app-footer">
      <div className="container-app footer-grid">
        <div>
          <h2>Great communities</h2>
          <ul>
            <li>
              <a href="https://discord.gg/R7BFUd9">Auto-chan's Discord</a>
            </li>
            <li>
              <a href="https://discord.gg/m8Ck3Ry">24/7 Gaming</a>
            </li>
          </ul>
        </div>
        <div>
          <h2>Want to contribute?</h2>
          <p>Jump on Discord!</p>
        </div>
        <div>
          <h2>Favorite bots</h2>
          <ul>
            <li>
              <a href="https://discord.com/oauth2/authorize?client_id=495481763821256705&scope=bot">Tamago</a>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
