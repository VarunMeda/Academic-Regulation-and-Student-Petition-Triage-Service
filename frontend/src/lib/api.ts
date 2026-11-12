import type { PetitionPayload, RunStatusResponse, SubmitResponse, TriageResult } from "./types";

const base = (process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");
async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const controller = new AbortController(); const timer = window.setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${base}${path}`, { ...init, signal: controller.signal, headers: { "Content-Type": "application/json", ...(init?.headers || {}) } });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) { const detail = body?.detail || body?.error || `Request failed (${response.status})`; throw new Error(detail); }
    return body as T;
  } catch (error) { if (error instanceof DOMException && error.name === "AbortError") throw new Error("The request timed out. Please try again."); throw error; }
  finally { window.clearTimeout(timer); }
}
export const api = {
  submitPetition: (payload: PetitionPayload, idempotencyKey: string) => request<SubmitResponse>("/api/petitions", { method: "POST", headers: { "Idempotency-Key": idempotencyKey }, body: JSON.stringify(payload) }),
  getRunStatus: (runId: string) => request<RunStatusResponse>(`/api/runs/${encodeURIComponent(runId)}`),
  getRunResult: (runId: string) => request<TriageResult>(`/api/runs/${encodeURIComponent(runId)}/result`),
  health: () => request<{ status: string; queue_backend: string; retrieval_backend: string }>("/health/ready"),
};
