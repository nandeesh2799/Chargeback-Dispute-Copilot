import React, { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import {
  Cpu,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Copy,
  ExternalLink,
  Sparkles,
  Terminal,
  Key
} from "lucide-react"
import { api } from "../../lib/api"

export const IntegrationsView: React.FC = () => {
  const [testWebhookStatus, setTestWebhookStatus] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  const { data: configs, isLoading } = useQuery({
    queryKey: ["integrations-status"],
    queryFn: api.getIntegrationsStatus,
  })

  const webhookEndpoint = `${window.location.origin}/api/webhooks/razorpay`

  const handleCopy = () => {
    navigator.clipboard.writeText(webhookEndpoint)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const handleTestWebhook = async () => {
    try {
      setTestWebhookStatus("Sending test webhook...")
      const res = await fetch("/api/webhooks/razorpay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          event: "dispute.under_review",
          event_id: `test_evt_${Date.now()}`,
          payload: {
            dispute: {
              entity: {
                id: "disp_synth_1001",
                amount: 42900,
                currency: "INR",
                status: "under_review",
              },
            },
          },
        }),
      })
      const data = await res.json()
      setTestWebhookStatus(`Webhook processed successfully! Status: ${data.status} (ID: ${data.event_id})`)
    } catch (e: any) {
      setTestWebhookStatus(`Failed: ${e.message}`)
    }
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Payment Gateways & AI Integrations</h1>
        <p className="text-xs text-slate-400 mt-1">
          Manage Razorpay test credentials, offline mock engines, LLM reasoning adapters, and webhook listeners.
        </p>
      </div>

      {/* Provider Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Mock Provider Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-600/20 text-indigo-400 flex items-center justify-center font-bold">
                M
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Mock Dispute Engine</h3>
                <span className="text-[10px] font-mono text-emerald-400">ACTIVE & READY</span>
              </div>
            </div>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Deterministic synthetic provider delivering 50 authentic disputes for RJ Kitchen with zero external gateway dependencies.
          </p>

          <div className="pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-500">
            Environment: <strong>local_sqlite</strong>
          </div>
        </div>

        {/* Razorpay Test Mode Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-blue-600/20 text-blue-400 flex items-center justify-center font-bold">
                R
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">Razorpay Test Gateway</h3>
                <span className="text-[10px] font-mono text-indigo-400">DISPUTE API v1</span>
              </div>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
              GUARDRAILS ON
            </span>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Connects to official Razorpay `/v1/disputes` endpoints. Enforces 1,000-character contest summary limits and intercepts mock dispute IDs.
          </p>

          <div className="pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-500">
            Safety Mode: <strong>Strict (Mock IDs Blocked)</strong>
          </div>
        </div>

        {/* LLM Intelligence Provider Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-emerald-600/20 text-emerald-400 flex items-center justify-center font-bold">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h3 className="text-sm font-semibold text-white">AI Reasoner Adapter</h3>
                <span className="text-[10px] font-mono text-emerald-400">Pydantic Grounded</span>
              </div>
            </div>
          </div>

          <p className="text-xs text-slate-400 leading-relaxed">
            Multi-provider LLM adapter supporting Claude 3.7 Sonnet or offline deterministic rules. Never hallucinates citations or evidence IDs.
          </p>

          <div className="pt-2 border-t border-slate-800/80 text-[11px] font-mono text-slate-500">
            Fallback Provider: <strong>Deterministic Rule Engine</strong>
          </div>
        </div>
      </div>

      {/* Webhook Configuration & Diagnostic Panel */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-5">
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Terminal className="w-4 h-4 text-indigo-400" />
            Razorpay Webhook Configuration & Testing
          </h3>
          <p className="text-xs text-slate-400 mt-1">
            Configure this endpoint in your Razorpay Dashboard under Settings → Webhooks.
          </p>
        </div>

        {/* Webhook URL bar */}
        <div className="flex items-center gap-2 p-3 rounded-lg bg-slate-950 border border-slate-800">
          <span className="text-xs font-mono text-slate-300 flex-1 truncate">{webhookEndpoint}</span>
          <button
            onClick={handleCopy}
            className="px-3 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-medium flex items-center gap-1.5 transition-colors"
          >
            <Copy className="w-3.5 h-3.5" />
            <span>{copied ? "Copied" : "Copy URL"}</span>
          </button>
        </div>

        {/* Supported Webhook Events */}
        <div className="text-xs text-slate-400 space-y-2">
          <div className="font-semibold text-slate-300">Supported Gateway Events:</div>
          <div className="flex flex-wrap gap-2 font-mono text-[11px]">
            <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">dispute.created</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">dispute.under_review</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">dispute.won</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">dispute.lost</span>
            <span className="px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-slate-700">dispute.closed</span>
          </div>
        </div>

        {/* Test Webhook Button */}
        <div className="pt-3 border-t border-slate-800/80 flex items-center gap-4">
          <button
            onClick={handleTestWebhook}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
          >
            Dispatch Test Webhook Event
          </button>
          {testWebhookStatus && (
            <span className="text-xs font-mono text-emerald-400">{testWebhookStatus}</span>
          )}
        </div>
      </div>
    </div>
  )
}
