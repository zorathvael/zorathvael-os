import React from "react";
import { INITIAL_WORKERS, INITIAL_MISSIONS, INITIAL_PLUGINS, INITIAL_LOGS } from "@/lib/mockData";
import { Activity, Users, Target, Puzzle, ArrowUpRight, ShieldCheck, Zap, Server } from "lucide-react";

export function DashboardView() {
  const activeWorkers = INITIAL_WORKERS.filter(w => w.status === "busy").length;
  const activeMissions = INITIAL_MISSIONS.filter(m => m.status === "executing").length;
  const enabledPlugins = INITIAL_PLUGINS.filter(p => p.status === "enabled").length;

  return (
    <div className="space-y-6">
      {/* Top Welcome Banner */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-blue-900/40 via-cyan-900/20 to-transparent border border-cyan-500/20 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            System Operational
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Mission Control Command Center</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Monitoring 8 AI departments, 15 active worker streams, and real-time mission telemetry.
          </p>
        </div>
        <div className="flex gap-3">
          <div className="text-right">
            <p className="text-[10px] font-mono text-zinc-400">UPTIME</p>
            <p className="text-sm font-mono font-bold text-emerald-400">99.998%</p>
          </div>
          <div className="h-8 w-px bg-white/10" />
          <div className="text-right">
            <p className="text-[10px] font-mono text-zinc-400">LATENCY</p>
            <p className="text-sm font-mono font-bold text-cyan-400">112ms</p>
          </div>
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-5 rounded-xl bg-[#0d0f17] border border-white/10 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl group-hover:bg-cyan-500/10 transition-all" />
          <div className="flex items-center justify-between">
            <p className="text-xs text-zinc-400 font-medium">Active AI Workers</p>
            <Users className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{activeWorkers} / {INITIAL_WORKERS.length}</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">Online</span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#0d0f17] border border-white/10 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/5 rounded-full blur-2xl group-hover:bg-blue-500/10 transition-all" />
          <div className="flex items-center justify-between">
            <p className="text-xs text-zinc-400 font-medium">Active Missions</p>
            <Target className="w-4 h-4 text-blue-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{activeMissions}</span>
            <span className="text-[10px] font-mono text-blue-400 bg-blue-500/10 px-1.5 py-0.5 rounded">Executing</span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#0d0f17] border border-white/10 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/5 rounded-full blur-2xl group-hover:bg-purple-500/10 transition-all" />
          <div className="flex items-center justify-between">
            <p className="text-xs text-zinc-400 font-medium">Active Plugins</p>
            <Puzzle className="w-4 h-4 text-purple-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">{enabledPlugins}</span>
            <span className="text-[10px] font-mono text-purple-400 bg-purple-500/10 px-1.5 py-0.5 rounded">Verified</span>
          </div>
        </div>

        <div className="p-5 rounded-xl bg-[#0d0f17] border border-white/10 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-2xl group-hover:bg-emerald-500/10 transition-all" />
          <div className="flex items-center justify-between">
            <p className="text-xs text-zinc-400 font-medium">System Health</p>
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-2xl font-bold font-mono text-white">100%</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded">Secured</span>
          </div>
        </div>
      </div>

      {/* Two Column Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Active Missions Stream */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#0d0f17] border border-white/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-cyan-400" /> Active Enterprise Missions
            </h3>
            <span className="text-xs text-cyan-400 font-mono">Live Telemetry</span>
          </div>
          <div className="space-y-3">
            {INITIAL_MISSIONS.map(m => (
              <div key={m.id} className="p-4 rounded-xl bg-white/5 border border-white/10 flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
                    <span className="text-xs font-bold text-white">{m.title}</span>
                  </div>
                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${
                    m.priority === 'Critical' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
                  }`}>
                    {m.priority}
                  </span>
                </div>
                <p className="text-[11px] text-zinc-400">{m.objective}</p>
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-white/5">
                  <span className="text-[10px] font-mono text-zinc-400">Lead: {m.lead} ({m.department})</span>
                  <div className="flex items-center gap-2 w-1/3">
                    <div className="flex-1 h-1.5 bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full bg-cyan-400" style={{ width: `${m.progress}%` }} />
                    </div>
                    <span className="text-[10px] font-mono text-cyan-400">{m.progress}%</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Live System Logs */}
        <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" /> Live Event Stream
            </h3>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          </div>
          <div className="flex-1 space-y-2.5 font-mono text-[11px] overflow-y-auto max-h-[380px]">
            {INITIAL_LOGS.map(log => (
              <div key={log.id} className="p-2.5 rounded bg-white/5 border border-white/5 flex flex-col gap-1">
                <div className="flex items-center justify-between">
                  <span className="text-cyan-400 font-bold">{log.source}</span>
                  <span className="text-zinc-500 text-[10px]">{log.timestamp}</span>
                </div>
                <p className="text-zinc-300">{log.message}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
