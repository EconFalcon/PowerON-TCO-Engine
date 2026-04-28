import { Link, useLocation } from 'react-router-dom';
import { ReactNode } from 'react';

interface AppShellProps {
  children: ReactNode;
}

export default function AppShell({ children }: AppShellProps) {
  const loc = useLocation();
  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-56 bg-green-800 text-white flex flex-col shrink-0">
        <div className="px-5 py-5 border-b border-green-700">
          <div className="text-lg font-bold tracking-tight">PowerOn Energy</div>
          <div className="text-xs text-green-300 mt-0.5">Fleet TCO Calculator</div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          <NavLink to="/" active={loc.pathname === '/'}>Calculator</NavLink>
          <NavLink to="/scenarios" active={loc.pathname === '/scenarios'}>Saved Scenarios</NavLink>
        </nav>
        <div className="px-5 py-4 text-xs text-green-400 border-t border-green-700">
          v1.0 &copy; {new Date().getFullYear()}
        </div>
      </aside>
      {/* Main */}
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}

function NavLink({ to, active, children }: { to: string; active: boolean; children: ReactNode }) {
  return (
    <Link
      to={to}
      className={`block px-3 py-2 rounded-md text-sm font-medium transition-colors ${
        active ? 'bg-green-700 text-white' : 'text-green-200 hover:bg-green-700 hover:text-white'
      }`}
    >
      {children}
    </Link>
  );
}
