import React, { useState } from "react"
import { useParams, Link } from "react-router-dom"
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query"
import {
  ArrowLeft,
  Sparkles,
  Calculator,
  Download,
  Send,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ShieldAlert,
  FileText,
  Truck,
  MessageSquare,
  Paperclip,
  Check,
  AlertCircle,
  ExternalLink,
  ChevronRight,
  Info
} from "lucide-react"
import { api } from "../../../lib/api"
import {
  formatCurrency,
  formatDate,
  formatTimeRemaining,
  getStatusBadgeClass,
  getTierBadgeClass
} from "../../../lib/utils"

export const DisputeWorkspaceView: React.FC = () => {
  const { id } = useParams<{ id: string }>()
  const queryClient = useQueryClient()
  const [activeTab, setActiveTab] = useState<"overview" | "evidence" | "investigation" | "draft" | "scoring">("overview")
  const [contestModalOpen, setContestModalOpen] = useState(false)
  const [contestSuccessMsg, setContestSuccessMsg] = useState<string | null>(null)

  // Draft editing state
  const [draftSummary, setDraftSummary] = useState("")
  const [draftLetter, setDraftLetter] = useState("")
  const [isDraftDirty, setIsDraftDirty] = useState(false)

  // Upload evidence state
  const [eviTitle, setEviTitle] = useState("")
  const [eviDesc, setEviDesc] = useState("")
  const [eviType, setEviType] = useState("delivery_proof")

  const { data: dispute, isLoading, error } = useQuery({
    queryKey: ["dispute-detail", id],
    queryFn: () => api.getDisputeDetail(id!),
    enabled: !!id,
  })

  React.useEffect(() => {
    if (dispute?.latest_draft && !isDraftDirty) {
      setDraftSummary(dispute.latest_draft.contest_summary)
      setDraftLetter(dispute.latest_draft.representation_letter)
    }
  }, [dispute, isDraftDirty])

  // Mutations
  const investigateMutation = useMutation({
    mutationFn: () => api.triggerInvestigation(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dispute-detail", id] })
      setActiveTab("investigation")
    }
  })

  const scoreMutation = useMutation({
    mutationFn: () => api.calculateScore(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dispute-detail", id] })
      setActiveTab("scoring")
    }
  })

  const saveDraftMutation = useMutation({
    mutationFn: () =>
      api.updateDraft(id!, {
        contest_summary: draftSummary,
        representation_letter: draftLetter,
      }),
    onSuccess: () => {
      setIsDraftDirty(false)
      queryClient.invalidateQueries({ queryKey: ["dispute-detail", id] })
    }
  })

  const approveDraftMutation = useMutation({
    mutationFn: () => api.approveDraft(id!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dispute-detail", id] })
    }
  })

  const submitContestMutation = useMutation({
    mutationFn: () => api.submitContest(id!),
    onSuccess: (res) => {
      setContestSuccessMsg(res.message)
      queryClient.invalidateQueries({ queryKey: ["dispute-detail", id] })
    }
  })

  if (isLoading) {
    return <div className="p-8 text-center text-slate-400">Loading dispute workspace...</div>
  }

  if (error || !dispute) {
    return (
      <div className="p-8">
        <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
          Dispute not found or failed to load.
        </div>
      </div>
    )
  }

  const rem = formatTimeRemaining(dispute.response_deadline)
  const isSummaryTooLong = draftSummary.length > 1000

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Back button */}
      <div>
        <Link
          to="/disputes"
          className="inline-flex items-center gap-2 text-xs text-slate-400 hover:text-slate-200 transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Dispute Queue</span>
        </Link>
      </div>

      {/* Main Dispute Header Banner */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 shadow-sm relative">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
          {/* Dispute Core Info */}
          <div className="space-y-2">
            <div className="flex items-center gap-3">
              <h1 className="text-xl font-bold font-mono text-white tracking-tight">{dispute.id}</h1>
              <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border uppercase ${getStatusBadgeClass(dispute.status)}`}>
                {dispute.status}
              </span>
              {dispute.is_synthetic && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                  SYNTHETIC FIXTURE
                </span>
              )}
            </div>

            <div className="text-xs text-slate-300 flex flex-wrap items-center gap-4">
              <span>Order Ref: <strong className="font-mono text-white">{dispute.order.order_number}</strong></span>
              <span>•</span>
              <span>Customer: <strong className="text-white">{dispute.customer.name}</strong></span>
              <span>•</span>
              <span>Amount: <strong className="font-mono text-white">{formatCurrency(dispute.amount)}</strong></span>
              <span>•</span>
              <span>Reason: <strong className="capitalize text-indigo-300">{dispute.reason_code.replace(/_/g, " ")}</strong></span>
            </div>

            <p className="text-xs text-slate-400 max-w-3xl leading-relaxed">
              {dispute.reason_description}
            </p>
          </div>

          {/* Action Buttons & Countdown */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            {/* Deadline Countdown Box */}
            <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-left">
              <div className="text-[10px] text-slate-500 uppercase tracking-wider">Response Window</div>
              <div className={`text-xs font-mono font-bold mt-0.5 ${rem.isUrgent ? 'text-rose-400' : 'text-slate-200'}`}>
                {rem.text}
              </div>
            </div>

            {/* Run Investigation */}
            <button
              onClick={() => investigateMutation.mutate()}
              disabled={investigateMutation.isPending}
              className="px-3.5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm disabled:opacity-50"
            >
              <Sparkles className="w-4 h-4" />
              <span>{investigateMutation.isPending ? "Investigating..." : "AI Investigation"}</span>
            </button>

            {/* Calculate Score */}
            <button
              onClick={() => scoreMutation.mutate()}
              disabled={scoreMutation.isPending}
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors disabled:opacity-50"
            >
              <Calculator className="w-4 h-4 text-emerald-400" />
              <span>Win-Score</span>
            </button>

            {/* Export PDF */}
            <a
              href={`/api/disputes/${dispute.id}/report`}
              target="_blank"
              rel="noopener noreferrer"
              className="px-3.5 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 text-xs font-semibold flex items-center gap-1.5 transition-colors"
            >
              <Download className="w-4 h-4 text-slate-400" />
              <span>PDF Report</span>
            </a>

            {/* Contest Dispute (Guarded) */}
            <button
              onClick={() => setContestModalOpen(true)}
              className="px-3.5 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-sm"
            >
              <Send className="w-4 h-4" />
              <span>Contest Dispute</span>
            </button>
          </div>
        </div>
      </div>

      {/* Contest Confirmation Modal */}
      {contestModalOpen && (
        <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="w-full max-w-lg rounded-xl bg-slate-900 border border-slate-800 p-6 space-y-4 shadow-2xl">
            <div className="flex items-center gap-3 text-amber-400">
              <ShieldAlert className="w-6 h-6" />
              <h3 className="text-base font-semibold text-white">Confirm Gateway Contest Submission</h3>
            </div>

            <div className="text-xs text-slate-300 space-y-2">
              <p>
                You are about to submit a formal contest package for dispute <strong className="text-white font-mono">{dispute.id}</strong> ({formatCurrency(dispute.amount)}).
              </p>
              <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 font-mono text-[11px] text-slate-400 space-y-1">
                <div>Provider: <strong>{dispute.is_synthetic ? "MOCK PROVIDER" : "RAZORPAY TEST"}</strong></div>
                <div>Contest Summary Length: <strong className={isSummaryTooLong ? "text-rose-400" : "text-emerald-400"}>{draftSummary.length} / 1000 chars</strong></div>
                <div>Attached Exhibits: <strong>{dispute.evidence_links.length} documents</strong></div>
              </div>
              {isSummaryTooLong && (
                <div className="text-rose-400 font-medium">
                  Cannot submit: Summary exceeds strict 1,000-character limit. Please shorten it in the Response Studio.
                </div>
              )}
            </div>

            {contestSuccessMsg && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs">
                {contestSuccessMsg}
              </div>
            )}

            <div className="flex items-center justify-end gap-3 pt-2">
              <button
                onClick={() => {
                  setContestModalOpen(false)
                  setContestSuccessMsg(null)
                }}
                className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700"
              >
                Close
              </button>
              {!contestSuccessMsg && (
                <button
                  onClick={() => submitContestMutation.mutate()}
                  disabled={submitContestMutation.isPending || isSummaryTooLong}
                  className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-semibold disabled:opacity-50"
                >
                  {submitContestMutation.isPending ? "Submitting..." : "Confirm & Submit Contest"}
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Tabs Navigation */}
      <div className="flex items-center border-b border-slate-800 gap-6 text-xs font-medium">
        {[
          { id: "overview", label: "Overview & Timeline", icon: Clock },
          { id: "evidence", label: `Evidence Vault (${dispute.evidence_links.length})`, icon: Paperclip },
          { id: "investigation", label: "AI Investigation", icon: Sparkles },
          { id: "draft", label: "Response Studio", icon: FileText },
          { id: "scoring", label: "Explainable Win-Score", icon: Calculator },
        ].map((t) => {
          const Icon = t.icon
          const isActive = activeTab === t.id
          return (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id as any)}
              className={`pb-3 flex items-center gap-2 border-b-2 transition-all ${
                isActive
                  ? "border-indigo-500 text-indigo-400"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Icon className="w-4 h-4" />
              <span>{t.label}</span>
            </button>
          )
        })}
      </div>

      {/* TAB CONTENT 1: OVERVIEW & TIMELINE */}
      {activeTab === "overview" && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Timeline & Flow */}
          <div className="lg:col-span-2 space-y-6">
            {/* Visual Timeline Card */}
            <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
              <h3 className="text-sm font-semibold text-white mb-4">Transaction & Dispute Milestones</h3>
              <div className="relative border-l-2 border-slate-800 ml-4 pl-6 space-y-6">
                {/* 1. Order Placed */}
                <div className="relative">
                  <div className="absolute -left-[31px] top-0 w-3 h-3 rounded-full bg-indigo-500 ring-4 ring-slate-950"></div>
                  <div className="text-xs font-semibold text-white">Order Placed (#{dispute.order.order_number})</div>
                  <div className="text-[11px] text-slate-400">{formatDate(dispute.order.ordered_at)}</div>
                  <div className="mt-1 text-xs text-slate-300">
                    Billed: {formatCurrency(dispute.order.amount)} for {dispute.order.item_summary?.items?.length || 1} kitchen items.
                  </div>
                </div>

                {/* 2. Payment Captured */}
                <div className="relative">
                  <div className="absolute -left-[31px] top-0 w-3 h-3 rounded-full bg-emerald-500 ring-4 ring-slate-950"></div>
                  <div className="text-xs font-semibold text-white">Payment Captured via {dispute.payment.method.toUpperCase()}</div>
                  <div className="text-[11px] text-slate-400">{formatDate(dispute.payment.captured_at || dispute.order.ordered_at)}</div>
                  <div className="mt-1 text-xs text-slate-300 font-mono">
                    Gateway Ref: {dispute.payment.gateway_payment_id} ({dispute.payment.provider.toUpperCase()})
                  </div>
                </div>

                {/* 3. Delivery Drop-Off */}
                {dispute.fulfilment && (
                  <div className="relative">
                    <div className="absolute -left-[31px] top-0 w-3 h-3 rounded-full bg-teal-500 ring-4 ring-slate-950"></div>
                    <div className="text-xs font-semibold text-white">Courier Fulfilment ({dispute.fulfilment.carrier})</div>
                    <div className="text-[11px] text-slate-400">{formatDate(dispute.fulfilment.delivered_at || "")}</div>
                    <div className="mt-1 text-xs text-slate-300">
                      Proof: <strong className="text-teal-400 uppercase">{dispute.fulfilment.delivery_proof_type}</strong> to {dispute.fulfilment.delivery_address}
                    </div>
                  </div>
                )}

                {/* 4. Dispute Filed */}
                <div className="relative">
                  <div className="absolute -left-[31px] top-0 w-3 h-3 rounded-full bg-amber-500 ring-4 ring-slate-950"></div>
                  <div className="text-xs font-semibold text-amber-400">Chargeback Filed by Issuer</div>
                  <div className="text-[11px] text-slate-400">{formatDate(dispute.created_at)}</div>
                  <div className="mt-1 text-xs text-slate-300">
                    Reason: {dispute.reason_description}
                  </div>
                </div>

                {/* 5. Response Deadline */}
                <div className="relative">
                  <div className="absolute -left-[31px] top-0 w-3 h-3 rounded-full bg-rose-500 ring-4 ring-slate-950"></div>
                  <div className="text-xs font-semibold text-rose-400">Response Window Closes</div>
                  <div className="text-[11px] text-slate-400">{formatDate(dispute.response_deadline)}</div>
                </div>
              </div>
            </div>

            {/* Customer Message History */}
            <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
              <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
                <MessageSquare className="w-4 h-4 text-indigo-400" />
                Customer Support Communication
              </h3>
              {dispute.messages.length === 0 ? (
                <div className="text-xs text-slate-500 italic">No inbound customer messages recorded for this order.</div>
              ) : (
                <div className="space-y-3">
                  {dispute.messages.map((m) => (
                    <div key={m.id} className="p-3 rounded-lg bg-slate-950 border border-slate-800">
                      <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                        <span className="font-semibold text-slate-200">{m.sender_name} ({m.channel.toUpperCase()})</span>
                        <span>{formatDate(m.sent_at)}</span>
                      </div>
                      <p className="text-xs text-slate-300">{m.content}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Right Sidebar: Customer & Payment Details */}
          <div className="space-y-6">
            <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
              <h3 className="text-sm font-semibold text-white">Order & Customer Card</h3>
              <div className="text-xs space-y-2 text-slate-300">
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span className="text-slate-500">Customer Name</span>
                  <span className="font-medium text-white">{dispute.customer.name}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span className="text-slate-500">Email</span>
                  <span className="font-mono text-slate-300">{dispute.customer.email}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span className="text-slate-500">Phone</span>
                  <span className="font-mono text-slate-300">{dispute.customer.phone}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span className="text-slate-500">Payment ID</span>
                  <span className="font-mono text-slate-300">{dispute.payment.id}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span className="text-slate-500">Payment Method</span>
                  <span className="uppercase font-medium text-indigo-300">{dispute.payment.method}</span>
                </div>
                <div className="flex justify-between border-b border-slate-800/60 pb-1.5">
                  <span className="text-slate-500">Refund Status</span>
                  <span className="font-medium text-slate-300">{dispute.payment.refund_status || "None"}</span>
                </div>
              </div>

              {/* Order Items */}
              {dispute.order.item_summary?.items && (
                <div className="pt-2">
                  <div className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider mb-2">
                    Line Items
                  </div>
                  <div className="space-y-1.5 text-xs text-slate-300">
                    {dispute.order.item_summary.items.map((item, idx) => (
                      <div key={idx} className="flex justify-between">
                        <span>{item.name}</span>
                        <span className="font-mono text-slate-400">{formatCurrency(item.price)}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 2: EVIDENCE VAULT */}
      {activeTab === "evidence" && (
        <div className="space-y-6">
          {/* Upload New Evidence Panel */}
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
            <h3 className="text-sm font-semibold text-white mb-2">Upload & Attach Supporting Document</h3>
            <p className="text-xs text-slate-400 mb-4">
              Attach carrier telematics, proof of delivery slips, customer chat transcripts, or merchant policies to strengthen this case.
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <input
                type="text"
                placeholder="Document Title (e.g. Courier Drop-Off Photo)"
                value={eviTitle}
                onChange={(e) => setEviTitle(e.target.value)}
                className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
              />
              <select
                value={eviType}
                onChange={(e) => setEviType(e.target.value)}
                className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200"
              >
                <option value="delivery_proof">Delivery Proof</option>
                <option value="order_invoice">Order Invoice / KOT</option>
                <option value="customer_chat_log">Customer Chat Transcript</option>
                <option value="cancellation_policy">Merchant Policy</option>
                <option value="ip_geo_log">IP & Geo Authentication Log</option>
              </select>
              <button
                onClick={async () => {
                  if (!eviTitle) return
                  const form = new FormData()
                  form.append("title", eviTitle)
                  form.append("evidence_type", eviType)
                  form.append("description", eviDesc || "Manual merchant evidence upload")
                  await fetch(`/api/disputes/${dispute.id}/evidence`, { method: "POST", body: form })
                  queryClient.invalidateQueries({ queryKey: ["dispute-detail", id] })
                  setEviTitle("")
                }}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
              >
                Attach Evidence
              </button>
            </div>
          </div>

          {/* Attached Evidence List */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {dispute.evidence_links.map((link) => {
              const ei = link.evidence_item
              if (!ei) return null
              return (
                <div key={link.id} className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <div className="text-xs font-bold text-white flex items-center gap-2">
                        {ei.title}
                        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                          {ei.verification_status.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-[10px] font-mono text-slate-500 mt-0.5">
                        {ei.evidence_type.toUpperCase()} • Source: {ei.source.toUpperCase()}
                      </div>
                    </div>
                    <span className="text-[10px] text-slate-500 font-mono">{formatDate(ei.created_at)}</span>
                  </div>

                  <p className="text-xs text-slate-400 leading-relaxed">{ei.description}</p>

                  <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-xs">
                    <span className="font-mono text-[11px] text-slate-500">{ei.file_name || "Record #verified"}</span>
                    <button
                      onClick={async () => {
                        await fetch(`/api/disputes/${dispute.id}/evidence/${ei.id}`, { method: "DELETE" })
                        queryClient.invalidateQueries({ queryKey: ["dispute-detail", id] })
                      }}
                      className="text-[11px] text-rose-400 hover:text-rose-300 font-medium"
                    >
                      Unlink
                    </button>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* TAB CONTENT 3: AI INVESTIGATION */}
      {activeTab === "investigation" && (
        <div className="space-y-6">
          {!dispute.investigation ? (
            <div className="p-12 text-center rounded-xl bg-slate-900 border border-slate-800">
              <Sparkles className="w-8 h-8 text-indigo-400 mx-auto mb-2" />
              <div className="text-sm font-semibold text-white">No investigation on record yet</div>
              <p className="text-xs text-slate-400 mt-1 max-w-md mx-auto">
                Trigger the 10-step AI investigation agent to inspect fulfilment records, detect contradictions, and audit evidence requirements.
              </p>
              <button
                onClick={() => investigateMutation.mutate()}
                className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold"
              >
                Start Investigation
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Summary finding */}
              <div className="p-5 rounded-xl bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-indigo-500/20">
                <div className="text-xs font-semibold text-indigo-300 uppercase tracking-wider mb-1">
                  Investigation Executive Summary
                </div>
                <p className="text-xs text-slate-200 leading-relaxed">
                  {dispute.investigation.findings_summary}
                </p>
                <div className="text-[10px] text-slate-500 font-mono mt-3">
                  Engine: {dispute.investigation.model_provider} • Latency: {dispute.investigation.execution_duration_ms}ms
                </div>
              </div>

              {/* Contradictions & Inconsistencies Alert Box */}
              {dispute.investigation.contradictions.length > 0 && (
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-amber-400 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4" />
                    Identified Record Inconsistencies ({dispute.investigation.contradictions.length})
                  </h3>
                  {dispute.investigation.contradictions.map((c, idx) => (
                    <div key={idx} className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 space-y-1.5">
                      <div className="text-xs font-bold text-amber-300 flex items-center gap-2">
                        <span>[{c.severity.toUpperCase()}] {c.title}</span>
                      </div>
                      <p className="text-xs text-slate-300">{c.description}</p>
                      <div className="text-[10px] font-mono text-slate-400">
                        Conflicting Entities: {c.conflicting_records.join(", ")}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* Checklist Requirements Audit */}
              <div className="p-6 rounded-xl bg-slate-900 border border-slate-800">
                <h3 className="text-sm font-semibold text-white mb-3">
                  Reason-Specific Evidence Checklist ({dispute.reason_code})
                </h3>
                <div className="space-y-2">
                  {dispute.investigation.checklist_audit.items?.map((item, idx) => (
                    <div key={idx} className="p-3 rounded-lg bg-slate-950 border border-slate-800/80 flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        {item.status === "fulfilled" ? (
                          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                        ) : (
                          <AlertCircle className="w-4 h-4 text-rose-400" />
                        )}
                        <div>
                          <div className="text-xs font-medium text-slate-200">{item.label}</div>
                          <div className="text-[10px] text-slate-500">
                            {item.is_mandatory ? "Mandatory scheme criterion" : "Optional supporting exhibit"}
                          </div>
                        </div>
                      </div>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono uppercase font-semibold ${item.status === 'fulfilled' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-rose-500/10 text-rose-400'}`}>
                        {item.status}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* TAB CONTENT 4: RESPONSE STUDIO */}
      {activeTab === "draft" && (
        <div className="space-y-6">
          <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-white">Razorpay Contest Summary</h3>
                <p className="text-xs text-slate-400">
                  Transmitted directly in the contest API payload. Enforces Razorpay 1,000-character ceiling.
                </p>
              </div>
              <div className="text-right">
                <span className={`text-xs font-mono font-bold ${isSummaryTooLong ? "text-rose-400" : "text-slate-400"}`}>
                  {draftSummary.length} / 1000 characters
                </span>
                {isSummaryTooLong && (
                  <div className="text-[10px] text-rose-400">Exceeds limit by {draftSummary.length - 1000} chars</div>
                )}
              </div>
            </div>

            <textarea
              rows={4}
              value={draftSummary}
              onChange={(e) => {
                setDraftSummary(e.target.value)
                setIsDraftDirty(true)
              }}
              className={`w-full p-3 bg-slate-950 border rounded-lg text-xs font-mono text-slate-200 focus:outline-none ${
                isSummaryTooLong ? "border-rose-500 focus:border-rose-500" : "border-slate-800 focus:border-indigo-500"
              }`}
            />

            <div>
              <h3 className="text-sm font-semibold text-white mb-1">Formal Dispute Representation Letter</h3>
              <p className="text-xs text-slate-400 mb-3">
                Comprehensive representation included in the formal PDF arbitration packet.
              </p>
              <textarea
                rows={10}
                value={draftLetter}
                onChange={(e) => {
                  setDraftLetter(e.target.value)
                  setIsDraftDirty(true)
                }}
                className="w-full p-3 bg-slate-950 border border-slate-800 rounded-lg text-xs font-mono text-slate-200 focus:outline-none focus:border-indigo-500"
              />
            </div>

            <div className="flex items-center justify-between pt-3 border-t border-slate-800">
              <div className="text-xs text-slate-500">
                {dispute.latest_draft?.is_approved ? (
                  <span className="text-emerald-400 font-medium flex items-center gap-1.5">
                    <Check className="w-3.5 h-3.5" /> Approved by Risk Lead
                  </span>
                ) : (
                  <span>Draft pending operator approval</span>
                )}
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => saveDraftMutation.mutate()}
                  disabled={saveDraftMutation.isPending || isSummaryTooLong}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-xs font-semibold disabled:opacity-50"
                >
                  {saveDraftMutation.isPending ? "Saving..." : "Save Draft"}
                </button>
                <button
                  onClick={() => approveDraftMutation.mutate()}
                  disabled={approveDraftMutation.isPending || isSummaryTooLong}
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg text-xs font-semibold disabled:opacity-50"
                >
                  {approveDraftMutation.isPending ? "Approving..." : "Approve Response"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* TAB CONTENT 5: EXPLAINABLE WIN-SCORE */}
      {activeTab === "scoring" && (
        <div className="space-y-6">
          {!dispute.scoring ? (
            <div className="p-12 text-center rounded-xl bg-slate-900 border border-slate-800">
              <Calculator className="w-8 h-8 text-emerald-400 mx-auto mb-2" />
              <div className="text-sm font-semibold text-white">No score calculated yet</div>
              <button
                onClick={() => scoreMutation.mutate()}
                className="mt-4 px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg text-xs font-semibold"
              >
                Run Scoring Pipeline
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {/* Score Highlight Box */}
              <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-between">
                <div>
                  <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    Estimated Probability of Winning
                  </div>
                  <div className="text-4xl font-extrabold font-mono text-emerald-400 mt-2">
                    {dispute.scoring.score.toFixed(1)}%
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Calibrated Logistic Regression baseline model ({dispute.scoring.model_name})
                  </p>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 rounded-full text-xs font-mono font-bold uppercase border ${getTierBadgeClass(dispute.scoring.tier)}`}>
                    {dispute.scoring.tier} Likelihood
                  </span>
                </div>
              </div>

              {/* Factors Breakdown: Positive & Negative */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Positive Drivers */}
                <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <h3 className="text-sm font-semibold text-emerald-400">Top Positive Evidence Drivers</h3>
                  <div className="space-y-2">
                    {dispute.scoring.top_positive_factors.map((f, idx) => (
                      <div key={idx} className="p-3 rounded-lg bg-emerald-500/5 border border-emerald-500/20 text-xs flex items-center justify-between">
                        <span className="text-slate-200">{f.description}</span>
                        <span className="font-mono font-bold text-emerald-400">+{f.impact_points.toFixed(1)} pts</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Negative Drivers */}
                <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
                  <h3 className="text-sm font-semibold text-rose-400">Negative Penalty Factors</h3>
                  <div className="space-y-2">
                    {dispute.scoring.top_negative_factors.length === 0 ? (
                      <div className="text-xs text-slate-500 italic p-3">No negative factor penalties detected.</div>
                    ) : (
                      dispute.scoring.top_negative_factors.map((f, idx) => (
                        <div key={idx} className="p-3 rounded-lg bg-rose-500/5 border border-rose-500/20 text-xs flex items-center justify-between">
                          <span className="text-slate-200">{f.description}</span>
                          <span className="font-mono font-bold text-rose-400">{f.impact_points.toFixed(1)} pts</span>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
