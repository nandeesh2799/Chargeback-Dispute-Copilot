import React from "react"
import { NavLink } from "react-router-dom"
import {
  LayoutDashboard,
  ShieldAlert,
  BarChart3,
  FileCheck2,
  Cpu,
  Settings,
  Sparkles,
  ExternalLink,
  Store
} from "lucide-react"

export const Sidebar: React.FC = () => {
  const navItems = [
    { to: "/", label: "Executive Dashboard", icon: LayoutDashboard },
    { to: "/disputes", label: "Dispute Queue", icon: ShieldAlert },
    { to: "/analytics", label: "Analytics & ML Model", icon: BarChart3 },
    { to: "/integrations", label: "Integrations & Gateway", icon: Cpu },
    { to: "/settings", label: "Settings & Audit", icon: Settings },
  ]

  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-950 flex flex-col h-screen fixed left-0 top-0 z-30 select-none">
      {/* Brand Header */}
      <div className="p-5 border-b border-slate-800">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-lg bg-indigo-600 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <div className="font-semibold text-sm tracking-tight text-white flex items-center gap-1.5">
              Dispute Copilot
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                PRO
              </span>
            </div>
            <div className="text-[11px] text-slate-400">Payment Evidence Intelligence</div>
          </div>
        </div>

        {/* Merchant Selector Card */}
        <div className="mt-4 p-2.5 rounded-lg bg-slate-900 border border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400">
              <Store className="w-4 h-4" />
            </div>
            <div>
              <div className="text-xs font-medium text-slate-200">RJ Kitchen</div>
              <div className="text-[10px] text-slate-500">Cyber Hub Cloud Kitchen</div>
            </div>
          </div>
          <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.5 rounded border border-emerald-500/20">
            TEST MODE
          </span>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <div className="text-[10px] font-semibold tracking-wider text-slate-500 uppercase px-3 mb-2">
          Operations
        </div>
        {navItems.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? "bg-indigo-600/10 text-indigo-400 border border-indigo-500/20 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-900/60"
                }`
              }
            >
              <Icon className="w-4 h-4" />
              <span>{item.label}</span>
            </NavLink>
          )
        })}
      </nav>

      {/* Footer Info Box */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950">
        <div className="rounded-lg p-3 bg-gradient-to-br from-indigo-950/40 to-slate-900 border border-indigo-500/20">
          <div className="flex items-center justify-between text-xs text-indigo-300 font-medium mb-1">
            <span>Synthetic DisputeVault</span>
            <FileCheck2 className="w-3.5 h-3.5 text-indigo-400" />
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            Seeded with 50 realistic disputes & courier evidence proofs for RJ Kitchen.
          </p>
        </div>
      </div>
    </aside>
  )
}
