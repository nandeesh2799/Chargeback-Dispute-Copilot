import React from "react"
import { Routes, Route, Navigate } from "react-router-dom"
import { Sidebar } from "./components/Sidebar"
import { Header } from "./components/Header"
import { DashboardView } from "./features/dashboard/DashboardView"
import { DisputeQueueView } from "./features/disputes/DisputeQueueView"
import { DisputeWorkspaceView } from "./features/disputes/workspace/DisputeWorkspaceView"
import { AnalyticsView } from "./features/analytics/AnalyticsView"
import { IntegrationsView } from "./features/integrations/IntegrationsView"
import { SettingsView } from "./features/settings/SettingsView"

export const App: React.FC = () => {
  return (
    <div className="flex bg-slate-950 min-h-screen">
      {/* Fixed Navigation Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<DashboardView />} />
            <Route path="/disputes" element={<DisputeQueueView />} />
            <Route path="/disputes/:id" element={<DisputeWorkspaceView />} />
            <Route path="/analytics" element={<AnalyticsView />} />
            <Route path="/integrations" element={<IntegrationsView />} />
            <Route path="/settings" element={<SettingsView />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

export default App
