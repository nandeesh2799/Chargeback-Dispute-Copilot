import React from "react"
import { Bell, Search, ShieldCheck, CheckCircle2 } from "lucide-react"

interface HeaderProps {
  title?: string
  subtitle?: string
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle }) => {
  return (
    <header className="h-16 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-20 px-8 flex items-center justify-between">
      {/* Title / Breadcrumb */}
      <div>
        {title ? (
          <h1 className="text-base font-semibold text-white tracking-tight">{title}</h1>
        ) : (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span>RJ Kitchen</span>
            <span>/</span>
            <span className="text-slate-200 font-medium">Dispute Resolution Workspace</span>
          </div>
        )}
        {subtitle && <p className="text-xs text-slate-400 mt-0.5">{subtitle}</p>}
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-4">
        {/* Environment Badge */}
        <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-[11px] font-mono text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>DISPUTE_SOURCE=mock</span>
        </div>

        {/* Guardrail pill */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-[11px] text-indigo-400">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Gateway Safeguards Active</span>
        </div>

        {/* User profile */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-slate-800">
          <div className="w-8 h-8 rounded-full bg-indigo-600 flex items-center justify-center text-xs font-semibold text-white">
            RJ
          </div>
          <div className="hidden lg:block text-left">
            <div className="text-xs font-medium text-slate-200">Rohit Jain</div>
            <div className="text-[10px] text-slate-400">Risk Operations Lead</div>
          </div>
        </div>
      </div>
    </header>
  )
}
