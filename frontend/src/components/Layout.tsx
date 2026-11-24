import { useState } from 'react';
import { Link, Outlet } from 'react-router';
import { useSession } from '../session';
import { UserIcon } from './icons';

export default function Layout() {
  const [collapsed, setCollapsed] = useState(true);

  return (
    <>
      <TopNav collapsed={collapsed} onToggle={() => setCollapsed((c) => !c)} />
      <div className="wrapper">
        <Sidebar collapsed={collapsed} />
        <main id="content">
          <div className="container-fluid content-inner">
            <Outlet />
          </div>
        </main>
      </div>
      <Footer />
    </>
  );
}

function TopNav({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }) {
  const { me } = useSession();

  return (
    <nav className="navbar top-nav">
      <button
        type="button"
        id="sidebarCollapse"
        className={collapsed ? 'active' : ''}
        aria-label="Toggle sidebar"
        aria-expanded={!collapsed}
        onClick={onToggle}
      >
        <span />
        <span />
        <span />
      </button>
      <div className="d-flex align-items-center ms-auto gap-2">
        {me?.guilds.map((g) => (
          <Link key={g.id} to={`/dashboard/${g.id}`} className="hvrcenter top-guild" title={g.name}>
            <img src={g.icon} width={32} height={32} className="img-circle" alt={g.name} />
          </Link>
        ))}
        <Link className="hvrcenter ms-3" to="/instructions">
          How-To
        </Link>
      </div>
    </nav>
  );
}

function Sidebar({ collapsed }: { collapsed: boolean }) {
  const { me } = useSession();
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <nav id="sidebar" className={collapsed ? 'active' : ''}>
      <div className="sidebar-header">
        <Link to="/">
          <img width={35} src="/img/auto-chan-white.png" alt="" />
          <h3 className="expanded-text"> Auto-chan</h3>
        </Link>
      </div>

      <ul className="list-unstyled components">
        {me ? (
          <li className="mb-1">
            <button
              type="button"
              className="sidebar-link dropdown-toggle"
              aria-expanded={menuOpen}
              onClick={() => setMenuOpen((o) => !o)}
            >
              <UserIcon />
              <h6 className="expanded-text">{me.user.username}</h6>
            </button>
            {menuOpen && (
              <ul className="list-unstyled submenu">
                <li>
                  <Link to="/dashboard">Servers</Link>
                </li>
                <li>
                  <a href="/logout">Logout</a>
                </li>
              </ul>
            )}
          </li>
        ) : (
          <li className="mb-1">
            <a href="/login" className="sidebar-link">
              <UserIcon />
              <h6 className="expanded-text">Login</h6>
            </a>
          </li>
        )}
        {me?.guilds.map((g) => (
          <li key={g.id} className="py-2 select-server-hover animated bounceInUp">
            <Link className="select-server-hover sidebar-guild" to={`/dashboard/${g.id}`} title={g.name}>
              <img width={32} height={32} className="img-circle" src={g.icon} alt="" />
              <h6 className="expanded-text">{g.name}</h6>
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}

function Footer() {
  return (
    <footer className="navbar footer">
      <div className="row w-100 justify-content-center">
        <div className="col-lg-4 mb-4 mb-lg-0">
          <h6>Great Communities!</h6>
          <ul className="list-unstyled">
            <li>
              <a href="https://discord.gg/R7BFUd9" className="text-muted hvrcenter">
                Auto-chan's Discord
              </a>
            </li>
            <li>
              <a href="https://discord.gg/m8Ck3Ry" className="text-muted hvrcenter">
                24/7 Gaming
              </a>
            </li>
          </ul>
        </div>
        <div className="col-lg-4 col-md-6">
          <h6>Want to contribute?</h6>
          <p className="text-muted">Jump on discord!</p>
        </div>
        <div className="col-lg-4 col-md-6">
          <h6>Favorite Bots!</h6>
          <ul className="list-unstyled">
            <li>
              <a
                href="https://discord.com/oauth2/authorize?client_id=495481763821256705&scope=bot"
                className="text-muted hvrcenter"
              >
                Tamago
              </a>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
