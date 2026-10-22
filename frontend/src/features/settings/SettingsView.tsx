import React, { useState, useEffect } from "react"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  Settings,
  RotateCcw,
  Shield,
  Key,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertTriangle,
  History,
  Store,
  Save,
  Cpu,
  Sparkles,
  PlugZap,
  Check
} from "lucide-react"
import { api } from "../../lib/api"
import { formatDate } from "../../lib/utils"

export const SettingsView: React.FC = () => {
  const queryClient = useQueryClient()

  // Integration Form State
  const [disputeSource, setDisputeSource] = useState("mock")
  const [razorpayKeyId, setRazorpayKeyId] = useState("")
  const [razorpayKeySecret, setRazorpayKeySecret] = useState("")
  const [razorpayWebhookSecret, setRazorpayWebhookSecret] = useState("")
  const [llmProvider, setLlmProvider] = useState("fallback")
  const [anthropicApiKey, setAnthropicApiKey] = useState("")
  const [showSecret, setShowSecret] = useState(false)

  // Status feedback
  const [saveSuccessMsg, setSaveSuccessMsg] = useState<string | null>(null)
  const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null)
  const [testingConnection, setTestingConnection] = useState(false)

  // Demo Reset Modal
  const [resetConfirmOpen, setResetConfirmOpen] = useState(false)
  const [resetSuccessMsg, setResetSuccessMsg] = useState<string | null>(null)

  // Fetch current configs
  const { data: configData } = useQuery({
    queryKey: ["integration-config"],
    queryFn: api.getIntegrationConfig,
  })

  useEffect(() => {
    if (configData) {
      setDisputeSource(configData.dispute_source)
      setRazorpayKeyId(configData.razorpay_key_id || "")
      setLlmProvider(configData.llm_provider || "fallback")
    }
  }, [configData])

  const { data: auditLogs, isLoading: logsLoading } = useQuery({
    queryKey: ["audit-logs"],
    queryFn: () => fetch("/api/settings/audit-logs").then((res) => res.json()),
  })

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: () =>
      api.updateIntegrationConfig({
        dispute_source: disputeSource,
        razorpay_key_id: razorpayKeyId,
        razorpay_key_secret: razorpayKeySecret || undefined,
        razorpay_webhook_secret: razorpayWebhookSecret || undefined,
        llm_provider: llmProvider,
        anthropic_api_key: anthropicApiKey || undefined,
      }),
    onSuccess: (res) => {
      setSaveSuccessMsg(res.message)
      setTimeout(() => setSaveSuccessMsg(null), 4000)
      queryClient.invalidateQueries()
    },
  })

  // Demo Reset mutation
  const resetMutation = useMutation({
    mutationFn: api.resetDemoData,
    onSuccess: (res) => {
      setResetSuccessMsg(res.message)
      setResetConfirmOpen(false)
      queryClient.invalidateQueries()
    },
  })

  const handleTestConnection = async () => {
    if (!razorpayKeyId || !razorpayKeySecret) {
      setTestResult({
        success: false,
        message: "Please enter both Key ID and Key Secret to test connection.",
      })
      return
    }

    setTestingConnection(true)
    setTestResult(null)
    try {
      const res = await api.testGatewayCredentials(razorpayKeyId, razorpayKeySecret)
      setTestResult({
        success: res.success,
        message: res.message,
      })
    } catch (e: any) {
      setTestResult({
        success: false,
        message: e.message || "Failed to reach gateway.",
      })
    } finally {
      setTestingConnection(false)
    }
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Platform Settings & Integrations</h1>
        <p className="text-xs text-slate-400 mt-1">
          Configure active dispute sources, Razorpay credentials, AI reasoning providers, and inspect operational audit logs.
        </p>
      </div>

      {/* Top Banner if settings saved */}
      {saveSuccessMsg && (
        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" />
          <span>{saveSuccessMsg}</span>
        </div>
      )}

      {/* Main Grid: Merchant Info & Gateway Setup */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Merchant Profile */}
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
              <span className="text-slate-500">Dispute Engine Status</span>
              <span className="font-mono font-medium text-emerald-400 uppercase">{disputeSource}</span>
            </div>
          </div>

          {/* Demo Reset Card inside left column */}
          <div className="pt-4 border-t border-slate-800/80 space-y-2">
            <div className="text-xs font-semibold text-slate-200">Demonstration Data</div>
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Reset the local database and restore the standard 50 RJ Kitchen dispute scenarios.
            </p>
            {resetSuccessMsg && (
              <div className="p-2.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
                {resetSuccessMsg}
              </div>
            )}
            <button
              onClick={() => setResetConfirmOpen(true)}
              className="w-full mt-2 px-3 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium flex items-center justify-center gap-2 transition-colors"
            >
              <RotateCcw className="w-3.5 h-3.5 text-amber-400" />
              <span>Reset Demo Database</span>
            </button>
          </div>
        </div>

        {/* Gateway & AI Integrations Panel (Takes 2 Columns) */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center">
                <PlugZap className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Payment Gateway & Provider Settings</h3>
                <p className="text-xs text-slate-400">Switch between offline demonstration mode and live Razorpay test sandbox</p>
              </div>
            </div>
          </div>

          {/* Provider Selection Radio */}
          <div className="space-y-2">
            <label className="text-xs font-semibold text-slate-300">Active Dispute Provider</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {/* Mock Option */}
              <div
                onClick={() => setDisputeSource("mock")}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  disputeSource === "mock"
                    ? "bg-indigo-600/10 border-indigo-500 text-white shadow-sm"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Mock Dispute Engine</span>
                  {disputeSource === "mock" && <Check className="w-4 h-4 text-indigo-400" />}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Offline mode with 50 realistic disputes for RJ Kitchen. Zero API keys required.
                </p>
              </div>

              {/* Razorpay Option */}
              <div
                onClick={() => setDisputeSource("razorpay")}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  disputeSource === "razorpay"
                    ? "bg-indigo-600/10 border-indigo-500 text-white shadow-sm"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white">Razorpay Test Mode</span>
                  {disputeSource === "razorpay" && <Check className="w-4 h-4 text-indigo-400" />}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">
                  Connects to Razorpay /v1/disputes API with safety guardrails active.
                </p>
              </div>
            </div>
          </div>

          {/* Razorpay Credentials Inputs */}
          <div className="space-y-4 pt-2 border-t border-slate-800/80">
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-slate-200 flex items-center gap-1.5">
                <Key className="w-3.5 h-3.5 text-indigo-400" />
                Razorpay API Credentials (Test Mode)
              </span>
              <span className="text-[10px] text-slate-500 font-mono">
                {configData?.razorpay_key_secret_masked ? `Secret: ${configData.razorpay_key_secret_masked}` : "No secret configured"}
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="text-[11px] font-medium text-slate-400 mb-1 block">Key ID</label>
                <input
                  type="text"
                  placeholder="rzp_test_..."
                  value={razorpayKeyId}
                  onChange={(e) => setRazorpayKeyId(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="text-[11px] font-medium text-slate-400 mb-1 block">Key Secret</label>
                <div className="relative">
                  <input
                    type={showSecret ? "text" : "password"}
                    placeholder="Enter secret (leave blank to keep existing)"
                    value={razorpayKeySecret}
                    onChange={(e) => setRazorpayKeySecret(e.target.value)}
                    className="w-full pl-3 pr-9 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecret(!showSecret)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300"
                  >
                    {showSecret ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>
            </div>

            <div>
              <label className="text-[11px] font-medium text-slate-400 mb-1 block">Webhook Secret</label>
              <input
                type="password"
                placeholder="Webhook secret for HMAC-SHA256 signature verification"
                value={razorpayWebhookSecret}
                onChange={(e) => setRazorpayWebhookSecret(e.target.value)}
                className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            {/* Test Connection Button & Result */}
            <div className="flex items-center gap-3 pt-1">
              <button
                type="button"
                onClick={handleTestConnection}
                disabled={testingConnection}
                className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
              >
                {testingConnection ? "Verifying..." : "Test Gateway Connection"}
              </button>
              {testResult && (
                <span
                  className={`text-xs font-medium flex items-center gap-1.5 ${
                    testResult.success ? "text-emerald-400" : "text-rose-400"
                  }`}
                >
                  {testResult.success ? <CheckCircle2 className="w-3.5 h-3.5" /> : <AlertTriangle className="w-3.5 h-3.5" />}
                  <span>{testResult.message}</span>
                </span>
              )}
            </div>
          </div>

          {/* AI Reasoner Provider Selection */}
          <div className="space-y-3 pt-4 border-t border-slate-800/80">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-200">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              AI Intelligence Engine
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div
                onClick={() => setLlmProvider("fallback")}
                className={`p-3 rounded-lg border cursor-pointer text-xs ${
                  llmProvider === "fallback"
                    ? "bg-emerald-500/10 border-emerald-500/30 text-white"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <div className="font-semibold text-white">Rule Engine (Deterministic)</div>
                <div className="text-[11px] text-slate-400 mt-0.5">100% offline, zero hallucinations, free</div>
              </div>

              <div
                onClick={() => setLlmProvider("claude")}
                className={`p-3 rounded-lg border cursor-pointer text-xs ${
                  llmProvider === "claude"
                    ? "bg-emerald-500/10 border-emerald-500/30 text-white"
                    : "bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <div className="font-semibold text-white">Anthropic Claude 3.7</div>
                <div className="text-[11px] text-slate-400 mt-0.5">Deep narrative extraction via API</div>
              </div>
            </div>

            {llmProvider === "claude" && (
              <div className="pt-2">
                <label className="text-[11px] font-medium text-slate-400 mb-1 block">Anthropic API Key</label>
                <input
                  type="password"
                  placeholder="sk-ant-..."
                  value={anthropicApiKey}
                  onChange={(e) => setAnthropicApiKey(e.target.value)}
                  className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
                />
              </div>
            )}
          </div>

          {/* Save Button */}
          <div className="pt-4 border-t border-slate-800 flex items-center justify-end">
            <button
              onClick={() => saveMutation.mutate()}
              disabled={saveMutation.isPending}
              className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold flex items-center gap-2 shadow-sm transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>{saveMutation.isPending ? "Saving..." : "Save Configuration"}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation Modal for Reset */}
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
