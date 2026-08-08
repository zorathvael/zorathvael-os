import React from "react";
import { 
  LayoutDashboard, 
  Network, 
  Target, 
  Users, 
  Workflow, 
  Puzzle, 
  Database, 
  Activity, 
  ShieldCheck, 
  Building2, 
  FileText,
  Terminal,
  Settings,
  Bell
} from "lucide-react";

interface NavigationProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export function Sidebar({ currentTab, setCurrentTab }: NavigationProps) {
  const menuItems = [
    { id: "dashboard", label: "Executive Dashboard", icon: LayoutDashboard },
    { id: "org_map", label: "Visual Org Map", icon: Network },
    { id: "mission_center", label: "Mission Center", icon: Target },
    { id: "workforce", label: "Workforce Monitor", icon: Users },
    { id: "workflows", label: "Workflow Visualizer", icon: Workflow },
    { id: "plugins", label: "Plugin Control Center", icon: Puzzle },
    { id: "memory", label: "Memory Explorer", icon: Database },
    { id: "observability", label: "Observability Platform", icon: Activity },
    { id: "security", label: "Security & RBAC", icon: ShieldCheck },
    { id: "workspaces", label: "Multi-Organization", icon: Building2 },
  ];

  return (
    <aside className="w-64 bg-[#0d0f17] border-r border-white/10 flex flex-col h-screen sticky top-0">
      <div className="p-5 border-b border-white/10 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
          <Terminal className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-sm tracking-wide text-white">ZORATHVAEL OS</h1>
          <p className="text-[10px] text-cyan-400 font-mono tracking-widest uppercase">Mission Control v3.0</p>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-4 px-3 space-custom space-y-1">
        <p className="px-3 text-[10px] font-mono text-zinc-400 uppercase tracking-wider mb-2">Navigation</p>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentTab(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-inner"
                  : "text-zinc-400 hover:text-zinc-100 hover:bg-white/5"
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? "text-cyan-400" : "text-zinc-400"}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="p-4 border-t border-white/10 bg-[#090a0f]">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[11px] font-mono text-emerald-400">System Nominal</span>
          </div>
          <span className="text-[10px] font-mono text-zinc-400">99.99%</span>
        </div>
      </div>
    </aside>
  );
}

export function Topbar({ currentWorkspace, setWorkspace }: { currentWorkspace: string; setWorkspace: (w: string) => void }) {
  return (
    <header className="h-16 border-b border-white/10 bg-[#0d0f17]/80 backdrop-blur-xl px-6 flex items-center justify-between sticky top-0 z-20">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-white/5 border border-white/10 px-3 py-1.5 rounded-lg">
          <Building2 className="w-4 h-4 text-cyan-400" />
          <select 
            value={currentWorkspace} 
            onChange={(e) => setWorkspace(e.target.value)}
            className="bg-transparent text-xs font-medium text-white focus:outline-none cursor-pointer"
          >
            <option value="Enterprise HQ" className="bg-[#11131a] text-white">Zorathvael Enterprise HQ</option>
            <option value="Global SaaS Labs" className="bg-[#11131a] text-white">Global SaaS Labs</option>
            <option value="AI Research Division" className="bg-[#11131a] text-white">AI Research Division</option>
          </select>
        </div>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative">
          <button className="w-9 h-9 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center text-zinc-300 hover:text-white hover:bg-white/10 transition-colors relative">
            <Bell className="w-4 h-4" />
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
            <span className="absolute top-2 right-2 w-2 h-2 rounded-full bg-cyan-400" />
          </button>
        </div>

        <div className="flex items-center gap-3 pl-4 border-l border-white/10">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-cyan-500 to-indigo-500 flex items-center justify-center text-white font-bold text-xs shadow">
            ZA
          </div>
          <div>
            <p className="text-xs font-medium text-white">Zorathvael Admin</p>
            <p className="text-[10px] text-zinc-400 font-mono">Administrator Role</p>
          </div>
        </div>
      </div>
    </header>
  );
}
