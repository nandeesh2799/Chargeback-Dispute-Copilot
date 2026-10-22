import React, { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { useNavigate } from "react-router-dom"
import {
  Search,
  Filter,
  Download,
  AlertTriangle,
  ArrowUpDown,
  ChevronLeft,
  ChevronRight,
  ShieldAlert,
  FileCheck2,
  Clock
} from "lucide-react"
import { api } from "../../lib/api"
import { formatCurrency, formatDate, formatTimeRemaining, getStatusBadgeClass, getTierBadgeClass } from "../../lib/utils"

export const DisputeQueueView: React.FC = () => {
  const navigate = useNavigate()
  const [search, setSearch] = useState("")
  const [statusFilter, setStatusFilter] = useState("")
  const [reasonFilter, setReasonFilter] = useState("")
  const [readinessFilter, setReadinessFilter] = useState("")
  const [page, setPage] = useState(0)
  const pageSize = 15

  const { data: disputes, isLoading, error } = useQuery({
    queryKey: ["disputes", { search, statusFilter, reasonFilter, readinessFilter, page }],
    queryFn: () =>
      api.getDisputes({
        search: search || undefined,
        status: statusFilter || undefined,
        reason: reasonFilter || undefined,
        readiness: readinessFilter || undefined,
        skip: page * pageSize,
        limit: pageSize,
      }),
  })

  return (
    <div className="p-8 space-y-6 max-w-7xl mx-auto">
      {/* Header with Title & Export Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Payment Dispute Queue</h1>
          <p className="text-xs text-slate-400 mt-1">
            Search, filter, and inspect incoming cardholder chargebacks and gateway claims for RJ Kitchen.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <a
            href="/api/disputes/export/csv"
            download="disputes_export.csv"
            className="px-3 py-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-xs text-slate-300 font-medium flex items-center gap-2 transition-colors"
          >
            <Download className="w-4 h-4 text-slate-400" />
            <span>Export CSV</span>
          </a>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-wrap items-center gap-3">
        {/* Search */}
        <div className="flex-1 min-w-[240px] relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search by Dispute ID, Order #, Customer, or Reason..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value)
              setPage(0)
            }}
            className="w-full pl-9 pr-4 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-indigo-500"
          />
        </div>

        {/* Status Dropdown */}
        <select
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value)
            setPage(0)
          }}
          className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Statuses</option>
          <option value="open">Open</option>
          <option value="under_review">Under Review</option>
          <option value="evidence_ready">Evidence Ready</option>
          <option value="contested">Contested</option>
          <option value="won">Won</option>
          <option value="lost">Lost</option>
        </select>

        {/* Reason Dropdown */}
        <select
          value={reasonFilter}
          onChange={(e) => {
            setReasonFilter(e.target.value)
            setPage(0)
          }}
          className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Reasons</option>
          <option value="product_not_received">Product Not Received</option>
          <option value="cancelled_charge">Order Cancelled But Charged</option>
          <option value="fraud_unauthorized">Fraud / Unauthorized Charge</option>
          <option value="not_as_described">Not As Described</option>
          <option value="duplicate_charge">Duplicate Charge</option>
        </select>

        {/* Readiness Dropdown */}
        <select
          value={readinessFilter}
          onChange={(e) => {
            setReadinessFilter(e.target.value)
            setPage(0)
          }}
          className="px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-indigo-500"
        >
          <option value="">All Readiness States</option>
          <option value="ready_to_submit">Ready To Submit</option>
          <option value="contradictions_detected">Contradictions Detected</option>
          <option value="gathering">Gathering Evidence</option>
          <option value="not_started">Not Started</option>
        </select>

        {/* Clear Filters */}
        {(search || statusFilter || reasonFilter || readinessFilter) && (
          <button
            onClick={() => {
              setSearch("")
              setStatusFilter("")
              setReasonFilter("")
              setReadinessFilter("")
              setPage(0)
            }}
            className="text-xs text-indigo-400 hover:text-indigo-300 underline font-medium px-2"
          >
            Reset
          </button>
        )}
      </div>

      {/* Main Table Container */}
      <div className="rounded-xl bg-slate-900/80 border border-slate-800 overflow-hidden shadow-sm">
        {isLoading ? (
          <div className="p-12 text-center text-slate-400 text-xs">
            Loading dispute queue...
          </div>
        ) : error ? (
          <div className="p-8 text-center text-rose-400 text-xs">
            Error loading disputes: {String(error)}
          </div>
        ) : !disputes || disputes.length === 0 ? (
          <div className="p-16 text-center text-slate-400">
            <ShieldAlert className="w-10 h-10 text-slate-600 mx-auto mb-3" />
            <div className="text-sm font-semibold text-slate-300">No disputes match your filters</div>
            <p className="text-xs text-slate-500 mt-1">Try resetting search keywords or category filters.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="bg-slate-950/60 border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider select-none">
                  <th className="py-3.5 px-4 font-medium">Dispute ID</th>
                  <th className="py-3.5 px-4 font-medium">Order / Customer</th>
                  <th className="py-3.5 px-4 font-medium">Amount</th>
                  <th className="py-3.5 px-4 font-medium">Reason Code</th>
                  <th className="py-3.5 px-4 font-medium">Status</th>
                  <th className="py-3.5 px-4 font-medium">Evidence Readiness</th>
                  <th className="py-3.5 px-4 font-medium">Win-Score</th>
                  <th className="py-3.5 px-4 font-medium">Deadline</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {disputes.map((d) => {
                  const rem = formatTimeRemaining(d.response_deadline)
                  return (
                    <tr
                      key={d.id}
                      onClick={() => navigate(`/disputes/${d.id}`)}
                      className="hover:bg-slate-800/50 cursor-pointer transition-colors group"
                    >
                      {/* ID */}
                      <td className="py-3.5 px-4 font-mono font-medium text-slate-200 group-hover:text-indigo-400 transition-colors">
                        {d.id}
                        {d.is_synthetic && (
                          <span className="block text-[9px] font-mono text-slate-500">SYNTHETIC</span>
                        )}
                      </td>

                      {/* Order & Customer */}
                      <td className="py-3.5 px-4">
                        <div className="font-mono text-slate-200 font-medium">{d.order_number}</div>
                        <div className="text-[11px] text-slate-400">{d.customer_name}</div>
                      </td>

                      {/* Amount */}
                      <td className="py-3.5 px-4 font-mono font-semibold text-white">
                        {formatCurrency(d.amount)}
                      </td>

                      {/* Reason */}
                      <td className="py-3.5 px-4 capitalize text-slate-300 max-w-[200px] truncate" title={d.reason_description}>
                        {d.reason_code.replace(/_/g, " ")}
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-4">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] border font-medium uppercase ${getStatusBadgeClass(d.status)}`}>
                          {d.status}
                        </span>
                      </td>

                      {/* Evidence Readiness */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-2">
                          <span className="text-[11px] text-slate-300 capitalize font-medium">
                            {d.evidence_readiness.replace(/_/g, " ")}
                          </span>
                          <span className="text-[10px] font-mono text-slate-400">
                            ({d.evidence_completeness_pct.toFixed(0)}%)
                          </span>
                        </div>
                        {d.evidence_readiness === "contradictions_detected" && (
                          <span className="inline-flex items-center gap-1 text-[10px] text-amber-400 font-medium mt-0.5">
                            <AlertTriangle className="w-3 h-3" /> Contradiction Alert
                          </span>
                        )}
                      </td>

                      {/* Win Score */}
                      <td className="py-3.5 px-4">
                        {d.win_probability_score ? (
                          <div className="flex items-center gap-1.5">
                            <span className="font-mono font-semibold text-white">
                              {d.win_probability_score.toFixed(1)}%
                            </span>
                            <span className={`text-[9px] uppercase px-1.5 py-0.5 rounded font-mono border ${getTierBadgeClass(d.win_score_tier)}`}>
                              {d.win_score_tier || "N/A"}
                            </span>
                          </div>
                        ) : (
                          <span className="text-slate-500 font-mono">--</span>
                        )}
                      </td>

                      {/* Deadline */}
                      <td className="py-3.5 px-4 font-mono">
                        <span className={`px-2 py-0.5 rounded text-[10px] font-medium ${rem.isUrgent ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'text-slate-400'}`}>
                          {rem.text}
                        </span>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="p-4 bg-slate-950/60 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing Page <strong>{page + 1}</strong>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={() => setPage((p) => p + 1)}
              disabled={!disputes || disputes.length < pageSize}
              className="p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-800"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
