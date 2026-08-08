import React, { useState } from "react";
import { INITIAL_MISSIONS, Mission } from "@/lib/mockData";
import { Target, Plus, Play, Pause, CheckCircle2, AlertCircle } from "lucide-react";

export function MissionCenterView() {
  const [missions, setMissions] = useState<Mission[]>(INITIAL_MISSIONS);
  const [newTitle, setNewTitle] = useState("");
  const [newObjective, setNewObjective] = useState("");

  const handleCreateMission = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTitle) return;
    const newM: Mission = {
      id: `m_00${missions.length + 1}`,
      title: newTitle,
      objective: newObjective || "Custom assigned enterprise mission.",
      department: "Engineering",
      lead: "Apex-Eng",
      status: "executing",
      progress: 0,
      priority: "High",
      startedAt: new Date().toISOString().replace('T', ' ').slice(0, 16)
    };
    setMissions([newM, ...missions]);
    setNewTitle("");
    setNewObjective("");
  };

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Mission Control
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Mission Center & Pipeline</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Create, deploy, monitor, and pause enterprise missions executed by AI workforce departments.
          </p>
        </div>
      </div>

      {/* New Mission Form */}
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10">
        <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-4">
          <Plus className="w-4 h-4 text-cyan-400" /> Dispatch New Mission
        </h3>
        <form onSubmit={handleCreateMission} className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <input
            type="text"
            placeholder="Mission Title..."
            value={newTitle}
            onChange={e => setNewTitle(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
          />
          <input
            type="text"
            placeholder="Mission Objective & Scope..."
            value={newObjective}
            onChange={e => setNewObjective(e.target.value)}
            className="bg-white/5 border border-white/10 rounded-lg px-4 py-2 text-xs text-white focus:outline-none focus:border-cyan-500"
          />
          <button
            type="submit"
            className="bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold text-xs rounded-lg px-4 py-2 transition-colors flex items-center justify-center gap-2"
          >
            <Play className="w-3.5 h-3.5 fill-slate-950" /> Launch Mission
          </button>
        </form>
      </div>

      {/* Mission List */}
      <div className="space-y-4">
        {missions.map(m => (
          <div key={m.id} className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="space-y-1.5 flex-1">
              <div className="flex items-center gap-3">
                <span className={`w-2.5 h-2.5 rounded-full ${m.status === 'executing' ? 'bg-cyan-400 animate-pulse' : 'bg-emerald-400'}`} />
                <h4 className="text-sm font-bold text-white">{m.title}</h4>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-white/5 text-zinc-300">
                  {m.department}
                </span>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                  {m.priority}
                </span>
              </div>
              <p className="text-xs text-zinc-400">{m.objective}</p>
              <p className="text-[10px] font-mono text-zinc-500">Started: {m.startedAt} | Lead: {m.lead}</p>
            </div>

            <div className="flex items-center gap-6 w-full md:w-auto justify-between md:justify-end">
              <div className="w-32">
                <div className="flex justify-between text-[10px] font-mono text-zinc-400 mb-1">
                  <span>Progress</span>
                  <span className="text-cyan-400">{m.progress}%</span>
                </div>
                <div className="h-1.5 bg-white/10 rounded-full overflow-hidden">
                  <div className="h-full bg-cyan-400" style={{ width: `${m.progress}%` }} />
                </div>
              </div>
              <div className="flex gap-2">
                <button 
                  onClick={() => {
                    setMissions(missions.map(item => item.id === m.id ? { ...item, status: item.status === 'executing' ? 'paused' : 'executing' } : item));
                  }}
                  className="p-2 rounded-lg bg-white/5 hover:bg-white/10 text-zinc-300 transition-colors"
                >
                  {m.status === 'executing' ? <Pause className="w-4 h-4 text-amber-400" /> : <Play className="w-4 h-4 text-emerald-400" />}
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
