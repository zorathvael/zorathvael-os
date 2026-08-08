import React, { useState } from "react";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import { Sidebar, Topbar } from "./components/Navigation";
import { DashboardView } from "./components/views/DashboardView";
import { OrgMapView } from "./components/views/OrgMapView";
import { MissionCenterView } from "./components/views/MissionCenterView";
import { 
  WorkforceMonitorView, 
  WorkflowVisualizerView, 
  PluginControlView, 
  MemoryExplorerView, 
  ObservabilityView, 
  SecurityView, 
  WorkspacesView 
} from "./components/views/AdditionalViews";

function MainApp() {
  const [currentTab, setCurrentTab] = useState("dashboard");
  const [currentWorkspace, setWorkspace] = useState("Enterprise HQ");

  const renderView = () => {
    switch (currentTab) {
      case "dashboard": return <DashboardView />;
      case "org_map": return <OrgMapView />;
      case "mission_center": return <MissionCenterView />;
      case "workforce": return <WorkforceMonitorView />;
      case "workflows": return <WorkflowVisualizerView />;
      case "plugins": return <PluginControlView />;
      case "memory": return <MemoryExplorerView />;
      case "observability": return <ObservabilityView />;
      case "security": return <SecurityView />;
      case "workspaces": return <WorkspacesView />;
      default: return <DashboardView />;
    }
  };

  return (
    <div className="min-h-screen bg-[#090a0f] text-zinc-100 flex font-sans selection:bg-cyan-500 selection:text-slate-950">
      <Sidebar currentTab={currentTab} setCurrentTab={setCurrentTab} />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar currentWorkspace={currentWorkspace} setWorkspace={setWorkspace} />
        <main className="flex-1 p-8 overflow-y-auto">
          {renderView()}
        </main>
      </div>
    </div>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <TooltipProvider>
          <Toaster />
          <MainApp />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}
