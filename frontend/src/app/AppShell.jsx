import { Bell, Calendar, LayoutDashboard, LogOut, Menu, Settings } from "lucide-react";
import PropTypes from "prop-types";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { Drawer } from "../components/primitives/Drawer";
import { IconButton } from "../components/primitives/IconButton";
import { PipelineStatusStrip } from "../domain/PipelineStatusStrip";
import { usePipelineStatus } from "../domain/usePipelineStatus";
import { useAuth } from "./AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/alerts", label: "Alerts", icon: Bell },
  { to: "/weekly", label: "Weekly", icon: Calendar },
];

function NavLinks({ isAdmin, onNavigate }) {
  return (
    <nav className="flex flex-col gap-1">
      {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
        <NavLink
          key={to}
          to={to}
          end={end}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium
             focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent
             ${isActive ? "bg-accent-weak text-accent" : "text-ink-muted hover:bg-accent-weak hover:text-accent"}`
          }
        >
          <Icon size={18} aria-hidden="true" />
          {label}
        </NavLink>
      ))}
      {isAdmin ? (
        <NavLink
          to="/admin/sources"
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium
             focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent
             ${isActive ? "bg-accent-weak text-accent" : "text-ink-muted hover:bg-accent-weak hover:text-accent"}`
          }
        >
          <Settings size={18} aria-hidden="true" />
          Admin
        </NavLink>
      ) : null}
    </nav>
  );
}

NavLinks.propTypes = {
  isAdmin: PropTypes.bool.isRequired,
  onNavigate: PropTypes.func,
};

export function AppShell() {
  const { user, logout } = useAuth();
  const { data: pipelineStatus } = usePipelineStatus();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const isAdmin = user?.role === "admin";

  return (
    <div className="flex min-h-screen">
      <aside className="hidden w-56 flex-col border-r border-rule bg-surface-raised p-4 md:flex">
        <NavLinks isAdmin={isAdmin} />
      </aside>

      <div className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-rule bg-surface-raised px-4 py-3">
          <div className="flex items-center gap-3">
            <IconButton
              label="Open navigation"
              icon={Menu}
              className="md:hidden"
              onClick={() => setDrawerOpen(true)}
            />
            <PipelineStatusStrip
              lastRunAt={pipelineStatus?.last_run_at ?? null}
              silentSourceCount={pipelineStatus?.silent_source_count ?? 0}
            />
          </div>
          <div className="flex items-center gap-3">
            <span className="text-sm text-ink">{user?.username}</span>
            <IconButton label="Log out" icon={LogOut} onClick={() => logout()} />
          </div>
        </header>

        <main className="flex-1 bg-surface">
          <Outlet />
        </main>
      </div>

      <Drawer title="Navigation" isOpen={drawerOpen} onClose={() => setDrawerOpen(false)}>
        <NavLinks isAdmin={isAdmin} onNavigate={() => setDrawerOpen(false)} />
      </Drawer>
    </div>
  );
}
