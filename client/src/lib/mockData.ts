export interface Worker {
  id: string;
  name: string;
  role: string;
  department: string;
  status: "idle" | "busy" | "escalated" | "offline";
  currentTask?: string;
  successRate: string;
  latency: string;
  memoryUsage: string;
}

export interface Mission {
  id: string;
  title: string;
  objective: string;
  department: string;
  lead: string;
  status: "planning" | "executing" | "paused" | "completed" | "failed";
  progress: number;
  priority: "Low" | "Medium" | "High" | "Critical";
  startedAt: string;
}

export interface PluginItem {
  id: string;
  name: string;
  version: string;
  category: string;
  status: "enabled" | "disabled" | "update_available";
  permissions: string[];
  description: string;
}

export interface LogEntry {
  id: string;
  timestamp: string;
  level: "INFO" | "WARN" | "ERROR" | "SUCCESS";
  source: string;
  message: string;
}

export const INITIAL_WORKERS: Worker[] = [
  { id: "w_ceo", name: "Z-CEO v4", role: "Chief Executive Officer", department: "Executive Board", status: "busy", currentTask: "Supervising Q3 Enterprise Expansion", successRate: "99.8%", latency: "120ms", memoryUsage: "1.4 GB" },
  { id: "w_cto", name: "Z-CTO v4", role: "Chief Technology Officer", department: "Executive Board", status: "busy", currentTask: "Reviewing Microservice Architecture", successRate: "99.5%", latency: "110ms", memoryUsage: "1.8 GB" },
  { id: "w_coo", name: "Z-COO v4", role: "Chief Operating Officer", department: "Executive Board", status: "idle", currentTask: "Awaiting Next Mission Batch", successRate: "99.9%", latency: "95ms", memoryUsage: "1.2 GB" },
  { id: "w_eng_lead", name: "Apex-Eng", role: "Engineering Lead", department: "Engineering", status: "busy", currentTask: "Refactoring Core Rust & Python Bridges", successRate: "98.9%", latency: "140ms", memoryUsage: "2.1 GB" },
  { id: "w_sec_lead", name: "Sentinel-X", role: "Security Engineer", department: "Security", status: "idle", currentTask: "Continuous Vulnerability Scan", successRate: "100%", latency: "80ms", memoryUsage: "950 MB" },
  { id: "w_mkt_lead", name: "Growth-AI", role: "CMO & Growth Specialist", department: "Marketing", status: "busy", currentTask: "Generating Q3 AI Campaign Assets", successRate: "97.8%", latency: "160ms", memoryUsage: "1.6 GB" },
  { id: "w_fin_lead", name: "Ledger-Bot", role: "Financial Auditor", department: "Finance", status: "idle", currentTask: "Automated Invoice Reconciliation", successRate: "99.9%", latency: "105ms", memoryUsage: "1.1 GB" },
  { id: "w_res_lead", name: "Cognito-Res", role: "Research Analyst", department: "Research", status: "busy", currentTask: "Synthesizing Competitor LLM Benchmarks", successRate: "99.1%", latency: "180ms", memoryUsage: "2.4 GB" },
];

export const INITIAL_MISSIONS: Mission[] = [
  { id: "m_001", title: "Build Enterprise SaaS Platform", objective: "Develop full-stack SaaS with auth, billing, and multi-tenant DB.", department: "Engineering", lead: "Apex-Eng", status: "executing", progress: 78, priority: "Critical", startedAt: "2026-08-06 08:30" },
  { id: "m_002", title: "Global Q3 Product Launch Campaign", objective: "Execute multi-channel marketing, press releases, and social push.", department: "Marketing", lead: "Growth-AI", status: "executing", progress: 45, priority: "High", startedAt: "2026-08-06 09:15" },
  { id: "m_003", title: "Autonomous Security Penetration Audit", objective: "Run full fuzzing and vulnerability scan across all active plugins.", department: "Security", lead: "Sentinel-X", status: "completed", progress: 100, priority: "Critical", startedAt: "2026-08-05 14:00" },
  { id: "m_004", title: "Automated Financial Reconciliation & Tax Prep", objective: "Process global invoices and prepare tax ledger reports.", department: "Finance", lead: "Ledger-Bot", status: "planning", progress: 10, priority: "Medium", startedAt: "2026-08-06 11:00" },
];

export const INITIAL_PLUGINS: PluginItem[] = [
  { id: "p_github", name: "GitHub Integration", version: "2.1.0", category: "Version Control", status: "enabled", permissions: ["github", "network"], description: "Official GitHub sync, PR automation, and issue triage." },
  { id: "p_notion", name: "Notion Workspace Hub", version: "1.8.4", category: "Knowledge Base", status: "enabled", permissions: ["notion", "network"], description: "Sync organizational memory and documentation directly to Notion." },
  { id: "p_telegram", name: "Telegram Bot Gateway", version: "1.5.0", category: "Communication", status: "enabled", permissions: ["telegram", "network"], description: "Real-time alerts and executive command relay via Telegram." },
  { id: "p_openai", name: "OpenAI GPT-4o Provider", version: "3.0.1", category: "AI Providers", status: "enabled", permissions: ["ai.openai", "network"], description: "High-intelligence LLM provider for complex reasoning tasks." },
  { id: "p_anthropic", name: "Anthropic Claude 3.5 Sonnet", version: "2.9.0", category: "AI Providers", status: "enabled", permissions: ["ai.anthropic", "network"], description: "Advanced coding and analytical reasoning worker backend." },
  { id: "p_slack", name: "Slack Enterprise Relay", version: "1.2.0", category: "Communication", status: "disabled", permissions: ["network"], description: "Cross-departmental notifications and team alerts." },
];

export const INITIAL_LOGS: LogEntry[] = [
  { id: "l_1", timestamp: "12:04:22", level: "SUCCESS", source: "MissionEngine", message: "Mission 'Build Enterprise SaaS Platform' advanced to step 6 (Verification)." },
  { id: "l_2", timestamp: "12:04:18", level: "INFO", source: "WorkforceComm", message: "Worker z_cto delegated subtask to Apex-Eng successfully." },
  { id: "l_3", timestamp: "12:03:55", level: "SUCCESS", source: "PluginSandbox", message: "Plugin 'GitHub Integration' health check passed (0ms latency anomaly)." },
  { id: "l_4", timestamp: "12:02:10", level: "WARN", source: "MemorySystem", message: "Department memory threshold reached 82% capacity; auto-compaction queued." },
  { id: "l_5", timestamp: "11:58:30", level: "INFO", source: "SecurityManager", message: "RBAC token validated for Operator role [ID: 9942]." },
];
