import { describe, it, expect } from "vitest"
import {
  formatCurrency,
  formatDate,
  formatTimeRemaining,
  getStatusBadgeClass,
  getTierBadgeClass,
  cn,
} from "./utils"

describe("Frontend Utility Functions", () => {
  it("formats paise into INR correctly", () => {
    expect(formatCurrency(100000)).toContain("1,000.00")
    expect(formatCurrency(49900)).toContain("499.00")
    expect(formatCurrency(0)).toContain("0.00")
  })

  it("handles empty or invalid dates gracefully", () => {
    expect(formatDate("")).toBe("N/A")
    const formatted = formatDate("2026-10-29T10:00:00Z")
    expect(formatted).not.toBe("N/A")
    expect(formatted).toContain("2026")
  })

  it("formats deadline and urgency levels correctly", () => {
    const emptyResult = formatTimeRemaining("")
    expect(emptyResult.text).toBe("No deadline")
    expect(emptyResult.isUrgent).toBe(false)

    // Expired deadline
    const pastIso = new Date(Date.now() - 1000000).toISOString()
    const expiredResult = formatTimeRemaining(pastIso)
    expect(expiredResult.text).toBe("Expired")
    expect(expiredResult.isUrgent).toBe(true)

    // Future deadline (> 2 days)
    const futureIso = new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString()
    const futureResult = formatTimeRemaining(futureIso)
    expect(futureResult.text).toContain("d remaining")
  })

  it("returns appropriate badge classes for dispute status", () => {
    expect(getStatusBadgeClass("won")).toContain("emerald")
    expect(getStatusBadgeClass("lost")).toContain("rose")
    expect(getStatusBadgeClass("open")).toContain("amber")
    expect(getStatusBadgeClass("unknown_status")).toContain("slate")
  })

  it("returns appropriate badge classes for win probability tiers", () => {
    expect(getTierBadgeClass("VERY_HIGH")).toContain("emerald")
    expect(getTierBadgeClass("MEDIUM")).toContain("amber")
    expect(getTierBadgeClass("LOW")).toContain("rose")
    expect(getTierBadgeClass(null)).toContain("slate")
  })

  it("merges Tailwind classes without conflicts via cn()", () => {
    const result = cn("px-2 py-1", "px-4")
    expect(result).toBe("py-1 px-4")
  })
})
