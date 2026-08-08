import React, { useState } from "react";
import { INITIAL_WORKERS, Worker } from "@/lib/mockData";
import { Network, Users, Shield, Cpu, ChevronRight, CheckCircle2 } from "lucide-react";

export function OrgMapView() {
  const [selectedWorker, setSelectedWorker] = useState<Worker | null>(INITIAL_WORKERS[0]);

  const departments = Array.from(new Set(INITIAL_WORKERS.map(w => w.department)));

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex items-center justify-between">
        <div>
          <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
            Topology Map
          </span>
          <h2 className="text-xl font-bold text-white mt-2">Visual Organization Topology</h2>
          <p className="text-xs text-zinc-400 mt-1">
            Hierarchical structure of Executive Board, Departments, and Autonomous AI Workers.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Org Tree */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-[#0d0f17] border border-white/10 space-y-6">
          <div className="flex items-center gap-2 pb-4 border-b border-white/10">
            <Network className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Departmental Topology</h3>
          </div>

          <div className="space-y-4">
            {departments.map(dept => {
              const deptWorkers = INITIAL_WORKERS.filter(w => w.department === dept);
              return (
                <div key={dept} className="p-4 rounded-xl bg-white/5 border border-white/10 space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">{dept}</span>
                    <span className="text-[10px] font-mono text-zinc-400 bg-white/5 px-2 py-0.5 rounded">
                      {deptWorkers.length} Workers
                    </span>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {deptWorkers.map(worker => (
                      <button
                        key={worker.id}
                        onClick={() => setSelectedWorker(worker)}
                        className={`p-3 rounded-lg border text-left transition-all flex items-center justify-between ${
                          selectedWorker?.id === worker.id
                            ? "bg-cyan-500/10 border-cyan-500/40 text-white"
                            : "bg-white/5 border-white/5 text-zinc-300 hover:bg-white/10"
                        }`}
                      >
                        <div className="flex items-center gap-2.5">
                          <div className={`w-2 h-2 rounded-full ${worker.status === 'busy' ? 'bg-cyan-400 animate-pulse' : 'bg-emerald-400'}`} />
                          <div>
                            <p className="text-xs font-bold">{worker.name}</p>
                            <p className="text-[10px] text-zinc-400">{worker.role}</p>
                          </div>
                        </div>
                        <ChevronRight className="w-3.5 h-3.5 text-zinc-500" />
                      </button>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Worker Inspector */}
        <div className="p-6 rounded-2xl bg-[#0d0f17] border border-white/10 flex flex-col">
          <div className="flex items-center gap-2 pb-4 border-b border-white/10 mb-6">
            <Users className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white">Worker Inspector</h3>
          </div>

          {selectedWorker ? (
            <div className="space-y-5 flex-1">
              <div className="p-4 rounded-xl bg-gradient-to-br from-cyan-500/10 to-transparent border border-cyan-500/20 text-center">
                <div className="w-12 h-12 rounded-full bg-cyan-500/20 border border-cyan-500/40 flex items-center justify-center mx-auto mb-3 text-cyan-300 font-bold font-mono">
                  {selectedWorker.name.slice(0, 2)}
                </div>
                <h4 className="text-sm font-bold text-white">{selectedWorker.name}</h4>
                <p className="text-xs text-cyan-400 mt-0.5">{selectedWorker.role}</p>
                <span className="inline-block mt-3 text-[10px] font-mono px-2 py-0.5 rounded bg-white/10 text-zinc-300">
                  {selectedWorker.department}
                </span>
              </div>

              <div className="space-y-3 font-mono text-xs">
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-zinc-400">Status</span>
                  <span className="text-emerald-400 uppercase">{selectedWorker.status}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-zinc-400">Success Rate</span>
                  <span className="text-cyan-400">{selectedWorker.successRate}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-zinc-400">Latency</span>
                  <span className="text-white">{selectedWorker.latency}</span>
                </div>
                <div className="flex justify-between py-2 border-b border-white/5">
                  <span className="text-zinc-400">Memory Allocation</span>
                  <span className="text-white">{selectedWorker.memoryUsage}</span>
                </div>
              </div>

              {selectedWorker.currentTask && (
                <div className="p-3 rounded-lg bg-white/5 border border-white/10">
                  <p className="text-[10px] font-mono text-zinc-400 uppercase mb-1">Current Active Task</p>
                  <p className="text-xs text-zinc-200">{selectedWorker.currentTask}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center text-zinc-500 text-xs">
              Select a worker to inspect parameters
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
