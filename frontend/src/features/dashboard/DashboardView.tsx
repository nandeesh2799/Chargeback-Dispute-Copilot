import React from "react"
import { useQuery } from "@tanstack/react-query"
import { Link } from "react-router-dom"
import {
  AlertCircle,
  TrendingUp,
  ShieldAlert,
  Clock,
  CheckCircle2,
  FileCheck,
  ArrowRight,
  Sparkles,
  BarChart2,
  RefreshCw
} from "lucide-react"
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Cell,
  PieChart,
  Pie
} from "recharts"
import { api } from "../../lib/api"
import { formatCurrency, formatTimeRemaining, getStatusBadgeClass } from "../../lib/utils"

export const DashboardView: React.FC = () => {
  const { data: summary, isLoading, error, refetch } = useQuery({
    queryKey: ["dashboard-summary"],
    queryFn: api.getDashboardSummary,
    refetchInterval: 15000,
  })

  if (isLoading) {
    return (
      <div className="p-8 space-y-6 animate-pulse">
        <div className="h-8 bg-slate-900 rounded w-1/4"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-28 bg-slate-900 rounded-xl"></div>
          ))}
        </div>
        <div className="h-80 bg-slate-900 rounded-xl"></div>
      </div>
    )
  }

  if (error || !summary) {
    return (
      <div className="p-8">
        <div className="p-6 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400">
          <p className="font-medium">Failed to load dashboard metrics</p>
          <p className="text-xs text-rose-300 mt-1">{String(error)}</p>
          <button
            onClick={() => refetch()}
            className="mt-3 px-3 py-1.5 bg-rose-600 text-white rounded text-xs font-medium"
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  // Chart data formatting
  const reasonData = Object.entries(summary.disputes_by_reason).map(([key, count]) => ({
    name: key.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
    count,
  }))

  const outcomeData = [
    { name: "Won", value: summary.disputes_by_status.won || 0, color: "#10B981" },
    { name: "Lost", value: summary.disputes_by_status.lost || 0, color: "#EF4444" },
    { name: "Open / Review", value: (summary.disputes_by_status.open || 0) + (summary.disputes_by_status.under_review || 0), color: "#F59E0B" },
    { name: "Evidence Ready", value: summary.disputes_by_status.evidence_ready || 0, color: "#6366F1" },
  ]

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Top Banner Alert if urgent disputes exist */}
      {summary.urgent_disputes_count > 0 && (
        <div className="p-4 rounded-xl bg-gradient-to-r from-amber-950/40 via-slate-900 to-slate-900 border border-amber-500/30 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-amber-500/10 flex items-center justify-center text-amber-400 border border-amber-500/20">
              <Clock className="w-5 h-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">
                {summary.urgent_disputes_count} Urgent Dispute{summary.urgent_disputes_count > 1 ? "s" : ""} Requiring Response
              </div>
              <div className="text-xs text-slate-400">
                Action required within 72 hours to prevent automatic issuer default against RJ Kitchen.
              </div>
            </div>
          </div>
          <Link
            to="/disputes?status=open"
            className="px-3.5 py-1.5 rounded-lg bg-amber-500 text-slate-950 text-xs font-semibold hover:bg-amber-400 transition-colors flex items-center gap-1.5"
          >
            Review Urgent Queue
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>
      )}

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Amount at Risk */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Amount At Risk</div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5">
            {formatCurrency(summary.total_amount_at_risk)}
          </div>
          <div className="text-xs text-amber-400 mt-2 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
            <span>{summary.open_disputes} open disputes pending contest</span>
          </div>
        </div>

        {/* Historical Win Rate */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Dispute Win Rate</div>
          <div className="text-2xl font-bold font-mono text-emerald-400 mt-1.5">
            {summary.win_rate_percentage.toFixed(1)}%
          </div>
          <div className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
            <span>Recovered {formatCurrency(summary.won_amount)}</span>
          </div>
        </div>

        {/* Evidence Completeness Avg */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Avg. Evidence Completeness</div>
          <div className="text-2xl font-bold font-mono text-indigo-400 mt-1.5">
            {summary.average_evidence_completeness.toFixed(0)}%
          </div>
          <div className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
            <FileCheck className="w-3.5 h-3.5 text-indigo-400" />
            <span>{summary.evidence_ready_disputes} disputes ready for gateway submit</span>
          </div>
        </div>

        {/* Total Disputed Volume */}
        <div className="p-5 rounded-xl bg-slate-900/80 border border-slate-800 shadow-sm relative overflow-hidden">
          <div className="text-xs font-medium text-slate-400 uppercase tracking-wider">Dispute Caseload</div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5">
            {summary.total_disputes} Cases
          </div>
          <div className="text-xs text-slate-400 mt-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
            <span>100% ground-truth provenance audited</span>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Trend Area Chart */}
        <div className="lg:col-span-2 p-6 rounded-xl bg-slate-900/80 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-semibold text-white">Dispute Activity & Resolutions</h3>
              <p className="text-xs text-slate-400">Incoming disputes vs merchant win/loss determinations</p>
            </div>
            <div className="flex items-center gap-3 text-[11px] text-slate-400">
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-indigo-500"></span> Opened
              </span>
              <span className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span> Won
              </span>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={summary.recent_trend}>
                <defs>
                  <linearGradient id="colorOpened" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366F1" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#6366F1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorWon" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4} />
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="#64748B" fontSize={11} tickLine={false} />
                <YAxis stroke="#64748B" fontSize={11} tickLine={false} allowDecimals={false} />
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                />
                <Area type="monotone" dataKey="opened" stroke="#6366F1" fillOpacity={1} fill="url(#colorOpened)" />
                <Area type="monotone" dataKey="won" stroke="#10B981" fillOpacity={1} fill="url(#colorWon)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Outcome Donut Chart */}
        <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-semibold text-white">Resolution Distribution</h3>
            <p className="text-xs text-slate-400">Breakdown across all 50 dispute lifecycles</p>
          </div>
          <div className="h-48 my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={outcomeData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {outcomeData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: "#0F172A", borderColor: "#334155", borderRadius: "8px", fontSize: "12px" }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs text-slate-300">
            {outcomeData.map((item) => (
              <div key={item.name} className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                <span>{item.name}: <strong className="font-mono text-white">{item.value}</strong></span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Urgent Queue Table Preview */}
      <div className="p-6 rounded-xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Urgent Dispute Queue</h3>
            <p className="text-xs text-slate-400">Approaching contest deadlines ordered by urgency</p>
          </div>
          <Link
            to="/disputes"
            className="text-xs text-indigo-400 hover:text-indigo-300 flex items-center gap-1 font-medium"
          >
            View Full Queue
            <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                <th className="pb-3 font-medium">Dispute ID</th>
                <th className="pb-3 font-medium">Order Ref</th>
                <th className="pb-3 font-medium">Disputed Amount</th>
                <th className="pb-3 font-medium">Reason</th>
                <th className="pb-3 font-medium">Status</th>
                <th className="pb-3 font-medium">Est. Win-Score</th>
                <th className="pb-3 font-medium">Deadline</th>
                <th className="pb-3 font-medium text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 text-slate-300">
              {summary.urgent_queue.map((item) => {
                const rem = formatTimeRemaining(item.response_deadline)
                return (
                  <tr key={item.id} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 font-mono text-slate-200 font-medium">{item.id}</td>
                    <td className="py-3 font-mono text-slate-400">{item.order_number}</td>
                    <td className="py-3 font-mono font-semibold text-white">{formatCurrency(item.amount)}</td>
                    <td className="py-3 capitalize text-slate-300">{item.reason_code.replace(/_/g, " ")}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded-full text-[10px] border font-medium uppercase ${getStatusBadgeClass(item.status)}`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="py-3">
                      {item.win_probability_score ? (
                        <span className="font-mono font-semibold text-emerald-400">
                          {item.win_probability_score.toFixed(1)}%
                        </span>
                      ) : (
                        <span className="text-slate-500">Uncalculated</span>
                      )}
                    </td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-medium ${rem.isUrgent ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20' : 'text-slate-400'}`}>
                        {rem.text}
                      </span>
                    </td>
                    <td className="py-3 text-right">
                      <Link
                        to={`/disputes/${item.id}`}
                        className="px-2.5 py-1 rounded bg-indigo-600/20 text-indigo-400 hover:bg-indigo-600/30 border border-indigo-500/30 font-medium transition-colors"
                      >
                        Investigate
                      </Link>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
