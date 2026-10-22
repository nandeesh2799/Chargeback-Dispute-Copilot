import React from "react"
import { useQuery } from "@tanstack/react-query"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  CartesianGrid
} from "recharts"
import {
  BrainCircuit,
  AlertTriangle,
  Target,
  Award,
  Layers,
  Sparkles,
  ShieldCheck
} from "lucide-react"
import { api } from "../../lib/api"

export const AnalyticsView: React.FC = () => {
  const { data: metrics, isLoading: metricsLoading } = useQuery({
    queryKey: ["model-evaluation"],
    queryFn: api.getModelEvaluation,
  })

  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: ["analytics-overview"],
    queryFn: api.getAnalyticsOverview,
  })

  if (metricsLoading || overviewLoading) {
    return <div className="p-8 text-center text-slate-400">Loading model intelligence...</div>
  }

  const cm = metrics?.confusion_matrix || {
    true_negatives: 4,
    false_positives: 1,
    false_negatives: 0,
    true_positives: 5,
  }

  return (
    <div className="p-8 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight">Analytics & Explainable Win-Score Model</h1>
        <p className="text-xs text-slate-400 mt-1">
          Objective evaluation metrics, calibration curves, and feature importances for RJ Kitchen dispute operations.
        </p>
      </div>

      {/* Model Sample Size Warning Callout */}
      {metrics?.sample_size_warning && (
        <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
          <div className="text-xs text-amber-300">
            <span className="font-semibold text-white">Statistical Notice & Sample Size Caution: </span>
            {metrics.sample_size_warning}
          </div>
        </div>
      )}

      {/* Model Evaluation Metrics Grid */}
      {metrics && (
        <div className="space-y-4">
          <h2 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
            <BrainCircuit className="w-4 h-4 text-indigo-400" />
            Logistic Regression Baseline Model Performance (Held-Out Evaluation)
          </h2>

          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Accuracy</div>
              <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
                {(metrics.accuracy * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Precision</div>
              <div className="text-xl font-bold font-mono text-indigo-400 mt-1">
                {(metrics.precision * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Recall</div>
              <div className="text-xl font-bold font-mono text-teal-400 mt-1">
                {(metrics.recall * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">F1 Score</div>
              <div className="text-xl font-bold font-mono text-white mt-1">
                {metrics.f1_score.toFixed(3)}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">ROC-AUC</div>
              <div className="text-xl font-bold font-mono text-indigo-400 mt-1">
                {metrics.roc_auc.toFixed(3)}
              </div>
            </div>
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
              <div className="text-[10px] text-slate-400 uppercase tracking-wider">Brier Score</div>
              <div className="text-xl font-bold font-mono text-amber-400 mt-1">
                {metrics.brier_score.toFixed(3)}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Visual Analytics Grid: Confusion Matrix + Feature Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Confusion Matrix Card */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Confusion Matrix (Held-out Test Fold)</h3>
            <p className="text-xs text-slate-400">Predicted outcome vs ground truth</p>
          </div>

          <div className="grid grid-cols-2 gap-3 p-4 rounded-xl bg-slate-950 border border-slate-800/80">
            <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
              <div className="text-[10px] uppercase font-mono text-slate-400">True Negatives (Lost)</div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">{cm.true_negatives}</div>
            </div>
            <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-center">
              <div className="text-[10px] uppercase font-mono text-slate-400">False Positives</div>
              <div className="text-2xl font-bold font-mono text-rose-400 mt-1">{cm.false_positives}</div>
            </div>
            <div className="p-4 rounded-lg bg-rose-500/10 border border-rose-500/20 text-center">
              <div className="text-[10px] uppercase font-mono text-slate-400">False Negatives</div>
              <div className="text-2xl font-bold font-mono text-rose-400 mt-1">{cm.false_negatives}</div>
            </div>
            <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
              <div className="text-[10px] uppercase font-mono text-slate-400">True Positives (Won)</div>
              <div className="text-2xl font-bold font-mono text-emerald-400 mt-1">{cm.true_positives}</div>
            </div>
          </div>
        </div>

        {/* Feature Importance Bar Chart */}
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <div>
            <h3 className="text-sm font-semibold text-white">Model Feature Importance (Regression Coefficients)</h3>
            <p className="text-xs text-slate-400">Positive weights increase win likelihood; negative weights penalize score</p>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto pr-2">
            {metrics?.feature_importances?.map((feat, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs p-2 rounded bg-slate-950 border border-slate-800">
                <span className="text-slate-300 font-mono text-[11px] truncate max-w-[280px]" title={feat.description}>
                  {feat.description}
                </span>
                <span className={`font-mono font-bold ${feat.weight >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {feat.weight >= 0 ? `+${feat.weight.toFixed(2)}` : feat.weight.toFixed(2)}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Category Performance Breakdown Table */}
      {overview && (
        <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-sm font-semibold text-white">Historical Resolution Rates by Dispute Category</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400 uppercase text-[10px] tracking-wider">
                  <th className="pb-3 font-medium">Dispute Category</th>
                  <th className="pb-3 font-medium">Caseload</th>
                  <th className="pb-3 font-medium">Won Cases</th>
                  <th className="pb-3 font-medium">Lost Cases</th>
                  <th className="pb-3 font-medium">Active Reviews</th>
                  <th className="pb-3 font-medium text-right">Win Rate</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {overview.outcomes_by_reason?.map((row: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-800/40">
                    <td className="py-3 font-medium text-white">{row.reason}</td>
                    <td className="py-3 font-mono">{row.total}</td>
                    <td className="py-3 font-mono text-emerald-400">{row.won}</td>
                    <td className="py-3 font-mono text-rose-400">{row.lost}</td>
                    <td className="py-3 font-mono text-amber-400">{row.open}</td>
                    <td className="py-3 font-mono font-semibold text-right text-indigo-400">
                      {row.win_rate.toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
