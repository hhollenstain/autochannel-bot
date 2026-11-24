import { Navigate, Route, Routes, useParams } from 'react-router';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import GuildAdded from './pages/GuildAdded';
import GuildCategories from './pages/GuildCategories';
import Home from './pages/Home';
import InstructionsPage from './pages/InstructionsPage';
import NotFound from './pages/NotFound';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Home />} />
        <Route path="instructions" element={<InstructionsPage />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="dashboard/:guildId" element={<GuildCategories />} />
        {/* The Jinja UI put the user id in the URL; keep old bookmarks working. */}
        <Route path="dashboard/:userId/:guildId" element={<LegacyGuildRedirect />} />
        <Route path="guild-added/:guildId" element={<GuildAdded />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}

function LegacyGuildRedirect() {
  const { guildId } = useParams();
  return <Navigate to={`/dashboard/${guildId}`} replace />;
}
