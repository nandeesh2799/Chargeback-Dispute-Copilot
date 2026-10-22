import {
  DashboardSummary,
  DisputeSummaryItem,
  DisputeDetail,
  AIInvestigation,
  ScoringResult,
  ResponseDraft,
  ModelEvaluationMetrics,
} from "../types"

const BASE_URL = "/api"

async function request<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  })

  if (!res.ok) {
    let errorMsg = `API request failed: ${res.status} ${res.statusText}`
    try {
      const errorJson = await res.json()
      if (errorJson.detail) {
        errorMsg = typeof errorJson.detail === "string" ? errorJson.detail : JSON.stringify(errorJson.detail)
      }
    } catch {}
    throw new Error(errorMsg)
  }

  return res.json()
}

export const api = {
  getDashboardSummary: () => request<DashboardSummary>("/dashboard/summary"),

  getDisputes: (params?: {
    status?: string
    reason?: string
    readiness?: string
    search?: string
    skip?: number
    limit?: number
  }) => {
    const q = new URLSearchParams()
    if (params?.status) q.append("status", params.status)
    if (params?.reason) q.append("reason", params.reason)
    if (params?.readiness) q.append("readiness", params.readiness)
    if (params?.search) q.append("search", params.search)
    if (params?.skip !== undefined) q.append("skip", params.skip.toString())
    if (params?.limit !== undefined) q.append("limit", params.limit.toString())

    return request<DisputeSummaryItem[]>(`/disputes?${q.toString()}`)
  },

  getDisputeDetail: (id: string) => request<DisputeDetail>(`/disputes/${id}`),

  triggerInvestigation: (id: string) =>
    request<AIInvestigation>(`/disputes/${id}/investigate`, { method: "POST" }),

  calculateScore: (id: string) =>
    request<ScoringResult>(`/disputes/${id}/score`, { method: "POST" }),

  updateDraft: (
    id: string,
    payload: { contest_summary: string; representation_letter: string; cited_evidence_ids?: string[] }
  ) =>
    request<ResponseDraft>(`/disputes/${id}/draft`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    }),

  approveDraft: (id: string) =>
    request<ResponseDraft>(`/disputes/${id}/draft/approve`, { method: "POST" }),

  submitContest: (id: string) =>
    request<{ success: boolean; status: string; message: string }>(`/disputes/${id}/contest`, {
      method: "POST",
    }),

  getAnalyticsOverview: () => request<any>("/analytics/overview"),

  getModelEvaluation: () => request<ModelEvaluationMetrics>("/analytics/model-evaluation"),

  getIntegrationsStatus: () => request<any[]>("/integrations/status"),

  resetDemoData: () => request<{ success: boolean; message: string; disputes_seeded: number }>("/settings/demo-reset", {
    method: "POST",
  }),

  getPdfReportUrl: (id: string) => `/api/disputes/${id}/report`,
}
