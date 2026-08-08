import React from "react";
import { INITIAL_WORKERS, INITIAL_PLUGINS, INITIAL_LOGS } from "@/lib/mockData";
import { Users, Workflow, Puzzle, Database, Activity, ShieldCheck, Building2, Check, RefreshCw } from "lucide-react";

export function WorkforceMonitorView() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Workforce Telemetry
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Enterprise Workforce Monitor</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Real-time tracking of AI worker queues, success rates, latency, and memory utilization.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {INITIAL_WORKERS.map(w => (
          <div key={w.id} className="p-5 rounded-xl bg-[#0d0f17] border border-white/10 space-y-4">
            <div className="flex items-center justify-between">
              <span className={`w-2 h-2 rounded-full ${w.status === 'busy' ? 'bg-cyan-400 animate-pulse' : 'bg-emerald-400'}`} />
              <span className="text-[10px] font-mono text-zinc-400">{w.department}</span>
            </div>
            <div>
              <h4 className="text-sm font-bold text-white">{w.name}</h4>
              <p className="text-[11px] text-cyan-400">{w.role}</p>
            </div>
            <div className="space-y-1 font-mono text-[11px] pt-3 border-t border-white/5">
              <div className="flex justify-between text-zinc-400">
                <span>Success Rate:</span>
                <span className="text-emerald-400">{w.successRate}</span>
              </div>
              <div className="flex justify-between text-zinc-400">
                <span>Latency:</span>
                <span className="text-white">{w.latency}</span>
              </div>
              <div className="flex justify-between text-zinc-400">
                <span>Memory:</span>
                <span className="text-white">{w.memoryUsage}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function WorkflowVisualizerView() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Workflow Engine
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Visual Workflow Pipeline</h2>
          <p className="text-xs text-zinc-400 mt-1">
            End-to-end execution path for automated enterprise workflows and triggers.
          </p>
        </div>
      </div>

      <div className="p-8 rounded-2xl bg-[#0d0f17] border border-white/10 flex flex-col items-center justify-center space-y-6">
        <div className="flex flex-wrap items-center justify-center gap-4">
          <div className="p-4 rounded-xl bg-white/5 border border-cyan-500/30 text-center w-48">
            <p className="text-[10px] font-mono text-cyan-400">TRIGGER</p>
            <p className="text-xs font-bold text-white mt-1">Webhook / Event</p>
          </div>
          <div className="w-8 h-px bg-cyan-500/50" />
          <div className="p-4 rounded-xl bg-cyan-500/10 border border-cyan-500/50 text-center w-48">
            <p className="text-[10px] font-mono text-cyan-400">PLANNER</p>
            <p className="text-xs font-bold text-white mt-1">AI Router & Mission</p>
          </div>
          <div className="w-8 h-px bg-cyan-500/50" />
          <div className="p-4 rounded-xl bg-white/5 border border-cyan-500/30 text-center w-48">
            <p className="text-[10px] font-mono text-cyan-400">EXECUTION</p>
            <p className="text-xs font-bold text-white mt-1">Worker Delegation</p>
          </div>
          <div className="w-8 h-px bg-cyan-500/50" />
          <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/50 text-center w-48">
            <p className="text-[10px] font-mono text-emerald-400">VERIFICATION</p>
            <p className="text-xs font-bold text-white mt-1">Report & Approval</p>
          </div>
        </div>
        <p className="text-xs text-zinc-500 font-mono mt-4">All nodes synchronized with live backend Workflow Engine.</p>
      </div>
    </div>
  );
}

export function PluginControlView() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Plugin Ecosystem
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Plugin Control Center</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Manage installed official plugins, sandbox permissions, and runtime health.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {INITIAL_PLUGINS.map(p => (
          <div key={p.id} className="p-5 rounded-xl bg-[#0d0f17] border border-white/10 space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-white">{p.name}</span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded ${p.status === 'enabled' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-zinc-500/10 text-zinc-400'}`}>
                {p.status}
              </span>
            </div>
            <p className="text-xs text-zinc-400">{p.description}</p>
            <div className="flex flex-wrap gap-1 pt-2">
              {p.permissions.map(perm => (
                <span key={perm} className="text-[9px] font-mono bg-white/5 text-cyan-400 px-2 py-0.5 rounded border border-white/5">
                  {perm}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function MemoryExplorerView() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Memory Engine
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Shared Memory Explorer</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Inspect personal, department, project, and organization-wide AI memory layers.
          </p>
        </div>
      </div>

      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 space-y-4 font-mono text-xs">
        <div className="p-4 rounded-xl bg-white/5 border border-white/10 flex justify-between items-center">
          <div>
            <p className="text-cyan-400 font-bold">Organization Memory (Global)</p>
            <p className="text-[11px] text-zinc-400 mt-1">Enterprise vision, core policies, global compliance standards.</p>
          </div>
          <span className="text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">Synced</span>
        </div>
        <div className="p-4 rounded-xl bg-white/5 border border-white/10 flex justify-between items-center">
          <div>
            <p className="text-cyan-400 font-bold">Department Memory (Engineering)</p>
            <p className="text-[11px] text-zinc-400 mt-1">Code standards, architecture blueprints, repo schemas.</p>
          </div>
          <span className="text-emerald-400 bg-emerald-500/10 px-2 py-1 rounded">Synced</span>
        </div>
      </div>
    </div>
  );
}

export function ObservabilityView() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Telemetry & Logs
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Observability Platform</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Comprehensive audit logs, metrics, traces, and system performance telemetry.
          </p>
        </div>
      </div>

      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 space-y-3 font-mono text-xs">
        {INITIAL_LOGS.map(log => (
          <div key={log.id} className="p-3 rounded-xl bg-white/5 border border-white/5 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className={`px-2 py-0.5 rounded text-[10px] ${log.level === 'SUCCESS' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-cyan-500/10 text-cyan-400'}`}>
                {log.level}
              </span>
              <span className="text-white font-bold">{log.source}</span>
              <span className="text-zinc-400">{log.message}</span>
            </div>
            <span className="text-[10px] text-zinc-500">{log.timestamp}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SecurityView() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Enterprise Security
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Security & RBAC Access Control</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Role-Based Access Control, audit logs, and organization permissions matrix.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {["Administrator", "Operator", "Read-Only Viewer"].map(role => (
          <div key={role} className="p-5 rounded-xl bg-[#0d0f17] border border-white/10 space-y-3">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <h4 className="text-sm font-bold text-white">{role}</h4>
            <p className="text-xs text-zinc-400">Full cryptographic validation and permission inheritance for enterprise users.</p>
          </div>
        ))}
      </div>
    </div>
  );
}

export function WorkspacesView() {
  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Multi-Tenant
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Multi-Organization Workspaces</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Switch between isolated organizations, workspaces, and team environments.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {["Zorathvael Enterprise HQ", "Global SaaS Labs"].map(ws => (
          <div key={ws} className="p-6 rounded-xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Building2 className="w-6 h-6 text-cyan-400" />
              <div>
                <h4 className="text-sm font-bold text-white">{ws}</h4>
                <p className="text-xs text-zinc-400 font-mono mt-0.5">Isolated Memory & Plugins</p>
              </div>
            </div>
            <span className="text-xs font-mono bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 px-3 py-1 rounded-lg">
              Active
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
