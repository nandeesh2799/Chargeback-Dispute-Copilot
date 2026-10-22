import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(paise: number, currency = "INR"): string {
  const rupees = paise / 100
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(rupees)
}

export function formatDate(isoString: string): string {
  if (!isoString) return "N/A"
  try {
    const d = new Date(isoString)
    return d.toLocaleDateString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    })
  } catch {
    return isoString
  }
}

export function formatTimeRemaining(deadlineIso: string): { text: string; isUrgent: boolean } {
  if (!deadlineIso) return { text: "No deadline", isUrgent: false }
  const now = new Date().getTime()
  const deadline = new Date(deadlineIso).getTime()
  const diffMs = deadline - now

  if (diffMs <= 0) {
    return { text: "Expired", isUrgent: true }
  }

  const hours = Math.floor(diffMs / (1000 * 60 * 60))
  const days = Math.floor(hours / 24)

  if (days > 1) {
    return { text: `${days}d remaining`, isUrgent: days < 3 }
  }
  return { text: `${hours}h remaining`, isUrgent: true }
}

export function getStatusBadgeClass(status: string): string {
  switch (status.toLowerCase()) {
    case "won":
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
    case "lost":
      return "bg-rose-500/10 text-rose-400 border-rose-500/20"
    case "open":
      return "bg-amber-500/10 text-amber-400 border-amber-500/20"
    case "under_review":
      return "bg-indigo-500/10 text-indigo-400 border-indigo-500/20"
    case "evidence_ready":
      return "bg-teal-500/10 text-teal-400 border-teal-500/20"
    case "contested":
      return "bg-blue-500/10 text-blue-400 border-blue-500/20"
    default:
      return "bg-slate-800 text-slate-300 border-slate-700"
  }
}

export function getTierBadgeClass(tier?: string | null): string {
  switch (tier?.toLowerCase()) {
    case "very_high":
    case "high":
      return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
    case "medium":
      return "bg-amber-500/10 text-amber-400 border-amber-500/20"
    case "low":
    case "very_low":
      return "bg-rose-500/10 text-rose-400 border-rose-500/20"
    default:
      return "bg-slate-800 text-slate-400 border-slate-700"
  }
}
