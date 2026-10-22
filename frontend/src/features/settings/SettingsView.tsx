import React, { useState } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Settings,
  RotateCcw,
  Shield,
  FileSpreadsheet,
  CheckCircle2,
  AlertTriangle,
  History,
  Store
} from "lucide-react"
import { api } from "../../lib/api"
import { formatDate } from "../../lib/utils"

export const SettingsView: React.FC = () => {
  const queryClient = useQueryClient()
  const [resetConfirmOpen, setResetConfirmOpen] = useState(false)
  const [resetSuccessMsg, setResetSuccessMsg] = useState<string | null>(null)

  const { data: auditLogs, isLoading: logsLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => fetch("/api/settings/audit-logs").then((res) => res.json()),
  })

  const resetMutation = useMutation({
    mutationFn: api.resetDemoData,
    onSuccess: (res) => {
      setResetSuccessMsg(res.message)
      setResetConfirmOpen(false)
      queryClient.invalidateQueries()
    },
  })

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Settings & Operational Audit Log</h1>
        <p className="text-xs text-slate-400 mt-1">
          Merchant profile, demo data state management, and immutable audit history.
        </p>
      </div>

      {/* Merchant Profile & Demo Reset Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Merchant Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Store className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white">RJ Kitchen — Cyber Hub</h3>
              <p className="text-xs text-slate-400">RJ Gourmet Foods Pvt. Ltd.</p>
            </div>
          </div>

          <div className="space-y-2 text-xs text-slate-300 pt-2 border-t border-slate-800/80">
            <div className="flex justify-between">
              <span className="text-slate-500">Merchant Identifier</span>
              <span className="font-mono text-slate-300">mer_rjkitchen_01</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Operating Currency</span>
              <span className="font-mono text-slate-300">INR (₹)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">System Timezone</span>
              <span className="font-mono text-slate-300">Asia/Kolkata (IST)</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Industry Segment</span>
              <span className="text-slate-300">Cloud Kitchen / Food Delivery POS</span>
            </div>
          </div>
        </div>

        {/* Demo Reset Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4 flex flex-col justify-between">
          <div>
            <div className="flex items-center gap-2.5 text-amber-400 mb-2">
              <RotateCcw className="w-5 h-5" />
              <h3 className="text-sm font-semibold text-white">Reset Synthetic Demonstration State</h3>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Reseed the local database with the fresh 50-dispute synthetic dataset for RJ Kitchen. This cleanly clears all mock edits, investigations, and test uploads.
            </p>
          </div>

          {resetSuccessMsg && (
            <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
              {resetSuccessMsg}
            </div>
          )}

          <div>
            <button
              onClick={() => setResetConfirmOpen(true)}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-semibold flex items-center gap-2 transition-colors"
            >
              <RotateCcw className="w-4 h-4 text-amber-400" />
              <span>Reset Demo Database</span>
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation Modal */}
      {resetConfirmOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-md rounded-xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-amber-400">
              <AlertTriangle className="w-6 h-6" />
              <h3 className="text-base font-semibold text-white">Confirm Demo Data Reset</h3>
            </div>
            <p className="text-xs text-slate-300">
              This will re-initialize the local SQLite database and restore the standard 50 RJ Kitchen synthetic dispute scenarios.
            </p>
            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => setResetConfirmOpen(false)}
                className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
              >
                Cancel
              </button>
              <button
                onClick={() => resetMutation.mutate()}
                disabled={resetMutation.isPending}
                className="px-4 py-2 rounded-lg bg-amber-600 hover:bg-amber-500 text-white text-xs font-semibold"
              >
                {resetMutation.isPending ? "Resetting..." : "Confirm Reset"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Audit Trail Log Table */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
        <h3 className="text-sm font-semibold text-white flex items-center gap-2">
          <History className="w-4 h-4 text-indigo-400" />
          Consequential Operations Audit Trail
        </h3>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-medium">Action</th>
                <th className="pb-3 font-medium">Resource Type</th>
                <th className="pb-3 font-medium">Resource ID</th>
                <th className="pb-3 font-medium">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300 font-mono">
              {logsLoading ? (
                <tr>
                  <td colSpan={4} className="py-4 text-center text-slate-500">Loading audit history...</td>
                </tr>
              ) : !auditLogs || auditLogs.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-4 text-center text-slate-500">No audit events recorded yet.</td>
                </tr>
              ) : (
                auditLogs.map((log: any) => (
                  <tr key={log.id} className="hover:bg-slate-800/40">
                    <td className="py-2.5 font-bold text-indigo-300">{log.action}</td>
                    <td className="py-2.5 text-slate-400">{log.resource_type}</td>
                    <td className="py-2.5 text-slate-300">{log.resource_id}</td>
                    <td className="py-2.5 text-slate-400">{formatDate(log.created_at)}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
