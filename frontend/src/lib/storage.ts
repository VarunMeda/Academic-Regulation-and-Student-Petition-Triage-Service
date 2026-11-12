const key = "academic-petition-run-ids";
export function rememberRun(runId: string) { if (typeof window === "undefined") return; const ids = getRuns().filter((id) => id !== runId); window.localStorage.setItem(key, JSON.stringify([runId, ...ids].slice(0, 20))); }
export function getRuns(): string[] { if (typeof window === "undefined") return []; try { const value = JSON.parse(window.localStorage.getItem(key) || "[]"); return Array.isArray(value) ? value.filter((x): x is string => typeof x === "string") : []; } catch { return []; } }
