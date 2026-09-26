import React, { useCallback, useEffect, useState } from "react";
import { Activity, RefreshCw, Radio, ShieldAlert, TrendingDown, TrendingUp } from "lucide-react";

type Result = {
  symbol: string; interval: string; status: string; side?: string | null; score?: number;
  price?: number; entry?: number | null; stop_loss?: number | null; take_profit?: number[];
  leverage?: number | null; live_data?: boolean; error?: string;
  metrics?: { rsi14?: number; volume_ratio?: number; order_book_imbalance?: number; funding_rate?: number };
};

const API_BASE = (import.meta as any).env?.VITE_SCANNER_API_URL || "";

const fmt = (n?: number | null) => n == null ? "—" : Number(n).toLocaleString(undefined, {maximumFractionDigits: 6});

export function ScannerView() {
  const [results, setResults] = useState<Result[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [lastScan, setLastScan] = useState("");

  const scan = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const response = await fetch(`${API_BASE}/scan/universe`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      setResults(data.results || []);
      setLastScan(new Date().toLocaleTimeString());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scanner API unavailable");
      setResults([]);
    } finally { setLoading(false); }
  }, []);

  useEffect(() => { scan(); const id = setInterval(scan, 30000); return () => clearInterval(id); }, [scan]);

  const entries = results.filter(r => r.status === "ENTRY NOW");

  return (
    <div className="space-y-6">
      <div className="p-6 rounded-2xl bg-gradient-to-r from-cyan-900/30 via-blue-900/10 to-transparent border border-cyan-500/20 flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-cyan-400 animate-pulse" />
            <span className="text-[10px] font-mono text-cyan-400 uppercase tracking-widest">LIVE FUTURES SCANNER</span>
          </div>
          <h2 className="text-xl font-bold text-white mt-2">Zorathvael 15m Altcoin Scanner</h2>
          <p className="text-xs text-zinc-400 mt-1">Public Binance USDT-M Futures data. No mock market data.</p>
        </div>
        <button onClick={scan} disabled={loading} className="flex items-center gap-2 px-4 py-2 rounded-lg bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 text-xs font-mono hover:bg-cyan-500/20 disabled:opacity-50">
          <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} /> SCAN NOW
        </button>
      </div>

      {error && <div className="p-4 rounded-xl border border-red-500/30 bg-red-500/5 text-red-400 text-xs font-mono"><ShieldAlert className="inline w-4 h-4 mr-2" />API ERROR: {error}</div>}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-5 rounded-xl bg-[#0d0f17] border border-white/10"><p className="text-xs text-zinc-400">ENTRY NOW</p><p className="text-3xl font-bold font-mono text-emerald-400 mt-2">{entries.length}</p></div>
        <div className="p-5 rounded-xl bg-[#0d0f17] border border-white/10"><p className="text-xs text-zinc-400">PAIRS SCANNED</p><p className="text-3xl font-bold font-mono text-white mt-2">{results.length}</p></div>
        <div className="p-5 rounded-xl bg-[#0d0f17] border border-white/10"><p className="text-xs text-zinc-400">LAST SCAN</p><p className="text-lg font-bold font-mono text-cyan-400 mt-3">{lastScan || "—"}</p></div>
      </div>

      {entries.length > 0 && <div className="space-y-3">
        <h3 className="text-sm font-bold text-white">ENTRY NOW — 15m</h3>
        {entries.map(r => <SignalCard key={r.symbol} r={r} />)}
      </div>}

      <div className="p-5 rounded-2xl bg-[#0d0f17] border border-white/10 overflow-x-auto">
        <h3 className="text-sm font-bold text-white mb-4">Full Universe</h3>
        <table className="w-full text-xs font-mono">
          <thead><tr className="text-zinc-500 border-b border-white/10"><th className="text-left p-2">PAIR</th><th>STATUS</th><th>SCORE</th><th>PRICE</th><th>RSI</th><th>VOL</th><th>OB IMB</th></tr></thead>
          <tbody>{results.map(r => <tr key={r.symbol} className="border-b border-white/5">
            <td className="p-3 text-white font-bold">{r.symbol}</td>
            <td className={`text-center ${r.status === "ENTRY NOW" ? "text-emerald-400" : "text-zinc-500"}`}>{r.status}</td>
            <td className="text-center text-cyan-400">{r.score ?? "—"}</td><td className="text-center">{fmt(r.price)}</td>
            <td className="text-center">{fmt(r.metrics?.rsi14)}</td><td className="text-center">{fmt(r.metrics?.volume_ratio)}x</td>
            <td className="text-center">{fmt(r.metrics?.order_book_imbalance)}</td>
          </tr>)}</tbody>
        </table>
      </div>
    </div>
  );
}

function SignalCard({r}:{r:Result}) {
  const long = r.side === "LONG";
  return <div className="p-5 rounded-2xl bg-[#0d0f17] border border-emerald-500/30">
    <div className="flex items-center justify-between">
      <div className="flex items-center gap-3"><span className="text-lg font-bold text-white">{r.symbol}</span>
        <span className={`text-[10px] font-mono px-2 py-1 rounded border ${long ? "text-emerald-400 border-emerald-500/30 bg-emerald-500/10" : "text-red-400 border-red-500/30 bg-red-500/10"}`}>{long ? <TrendingUp className="inline w-3 h-3"/> : <TrendingDown className="inline w-3 h-3"/>} {r.side}</span>
      </div><span className="text-emerald-400 text-xs font-mono">SCORE {r.score}</span>
    </div>
    <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-5 text-xs font-mono">
      <Metric label="ENTRY" value={fmt(r.entry)} /><Metric label="SL" value={fmt(r.stop_loss)} />
      <Metric label="TP1" value={fmt(r.take_profit?.[0])} /><Metric label="TP2" value={fmt(r.take_profit?.[1])} />
      <Metric label="LEV" value={r.leverage ? `${r.leverage}x` : "—"} />
    </div>
  </div>;
}
function Metric({label,value}:{label:string,value:string}) { return <div><p className="text-zinc-500">{label}</p><p className="text-white mt-1">{value}</p></div>; }
