"use client";
import Link from "next/link";
import { ArrowRight, ArrowUpRight, ClipboardCheck, FilePlus2, GitBranch, ShieldCheck, Loader2, Activity, BookOpenCheck, Clock3 } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { getRuns } from "@/lib/storage";
import type { RunStatus } from "@/lib/types";
import { StatusBadge } from "@/components/common/StatusBadge";
import { Notice } from "@/components/common/Notice";

export function Dashboard() {
  const [runs, setRuns] = useState<{ id: string; status: RunStatus }[]>([]);
  const [health, setHealth] = useState<"checking" | "available" | "unavailable">("checking");
  useEffect(() => {
    let live = true;
    api.health().then(() => live && setHealth("available")).catch(() => live && setHealth("unavailable"));
    Promise.all(getRuns().slice(0, 8).map(async id => {
      try { return { id, status: (await api.getRunStatus(id)).status }; }
      catch { return { id, status: "failed" as RunStatus }; }
    })).then(items => live && setRuns(items));
    return () => { live = false; };
  }, []);
  const processing = runs.filter(x => x.status === "pending" || x.status === "running").length;
  const escalated = runs.filter(x => x.status === "escalated").length;
  const completed = runs.filter(x => x.status === "completed").length;
  return <div className="space-y-7">
    <section className="relative isolate overflow-hidden rounded-[28px] bg-gradient-to-br from-[#173b66] via-[#17365b] to-[#102641] px-7 py-9 text-white shadow-xl shadow-blue-950/10 md:px-10 md:py-11">
      <div className="absolute -right-20 -top-28 -z-10 h-80 w-80 rounded-full border-[1px] border-white/10"/><div className="absolute -right-5 -top-14 -z-10 h-56 w-56 rounded-full border-[34px] border-white/[.045]"/><div className="absolute bottom-[-100px] right-[25%] -z-10 h-52 w-52 rounded-full bg-teal/10 blur-3xl"/>
      <div className="max-w-2xl"><div className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/[.08] px-3 py-1.5"><span className="h-1.5 w-1.5 rounded-full bg-emerald-300"/><span className="text-[10px] font-bold uppercase tracking-[.16em] text-blue-100">Student services portal</span></div>
        <h1 className="mt-5 max-w-xl text-[30px] font-extrabold leading-[1.15] tracking-tight md:text-[42px]">Academic guidance, <span className="text-teal-200">grounded in evidence.</span></h1>
        <p className="mt-4 max-w-xl text-sm leading-7 text-blue-100/85 md:text-[15px]">Submit and track academic petitions through a transparent triage workflow that retrieves relevant provisions, verifies citations and flags cases for human review.</p>
        <div className="mt-7 flex flex-wrap gap-3"><Link href="/petitions/new" className="inline-flex items-center gap-2 rounded-xl bg-white px-5 py-3 text-sm font-bold text-[#173b66] shadow-lg transition hover:-translate-y-0.5 hover:bg-blue-50">Start a petition <ArrowRight size={16}/></Link><Link href="/help" className="inline-flex items-center gap-2 rounded-xl border border-white/20 bg-white/[.07] px-5 py-3 text-sm font-semibold text-white transition hover:bg-white/[.13]">Explore the process <ArrowUpRight size={16}/></Link></div>
      </div>
      <div className="mt-9 flex flex-wrap gap-x-6 gap-y-2 border-t border-white/10 pt-5 text-[11px] text-blue-100/80"><span className="flex items-center gap-2"><ShieldCheck size={14}/> Evidence verification</span><span className="flex items-center gap-2"><GitBranch size={14}/> Human-review routing</span><span className="flex items-center gap-2"><BookOpenCheck size={14}/> Clause-level citations</span></div>
    </section>
    {health === "unavailable" && <Notice kind="error">The API is currently unavailable. You can explore the guidance pages, but petition submission requires the backend to be running.</Notice>}
    <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
      <Link href="/petitions/new" className="card group p-5"><span className="grid h-11 w-11 place-items-center rounded-xl bg-blue-50 text-[#214d7d]"><FilePlus2 size={21}/></span><div className="mt-4 flex items-center justify-between"><h2 className="text-[15px] font-bold">Submit a petition</h2><ArrowUpRight size={17} className="text-slate-300 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-navy"/></div><p className="mt-2 text-[12px] leading-6 text-slate-500">Share your concern and the facts needed for a careful assessment.</p></Link>
      <Link href="/petitions" className="card group p-5"><span className="grid h-11 w-11 place-items-center rounded-xl bg-teal-50 text-teal"><ClipboardCheck size={21}/></span><div className="mt-4 flex items-center justify-between"><h2 className="text-[15px] font-bold">Track petitions</h2><ArrowUpRight size={17} className="text-slate-300 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-navy"/></div><p className="mt-2 text-[12px] leading-6 text-slate-500">Reopen submissions saved in this browser and check their latest status.</p></Link>
      <Link href="/help" className="card group p-5 sm:col-span-2 xl:col-span-1"><span className="grid h-11 w-11 place-items-center rounded-xl bg-violet-50 text-violet-700"><ShieldCheck size={21}/></span><div className="mt-4 flex items-center justify-between"><h2 className="text-[15px] font-bold">Understand the process</h2><ArrowUpRight size={17} className="text-slate-300 transition group-hover:-translate-y-0.5 group-hover:translate-x-0.5 group-hover:text-navy"/></div><p className="mt-2 text-[12px] leading-6 text-slate-500">Learn how retrieval, citation checks and committee review work.</p></Link>
    </section>
    <section className="grid gap-5 xl:grid-cols-[1.15fr_.85fr]">
      <div className="card p-6 md:p-7"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="eyebrow">Your workspace</p><h2 className="mt-1 text-xl font-extrabold tracking-tight">Submission activity</h2><p className="mt-1 text-xs text-slate-500">A snapshot of run references saved in this browser</p></div>{health === "checking" ? <span className="flex items-center gap-2 text-xs text-slate-400"><Loader2 className="animate-spin" size={15}/> Checking API</span> : <span className={`flex items-center gap-2 rounded-full px-3 py-1.5 text-[10px] font-bold ${health === "available" ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700"}`}><span className={`h-1.5 w-1.5 rounded-full ${health === "available" ? "bg-emerald-500" : "bg-rose-500"}`}/>{health === "available" ? "API connected" : "API offline"}</span>}</div>
        <div className="mt-6 grid grid-cols-3 gap-3"><div className="rounded-2xl bg-slate-50 p-4"><span className="text-slate-400"><Activity size={17}/></span><p className="mt-3 text-2xl font-extrabold tabular-nums">{runs.length}</p><p className="mt-1 text-[10px] font-medium text-slate-500">Tracked runs</p></div><div className="rounded-2xl bg-amber-50/70 p-4"><span className="text-amber-600"><Clock3 size={17}/></span><p className="mt-3 text-2xl font-extrabold tabular-nums">{processing}</p><p className="mt-1 text-[10px] font-medium text-slate-500">Processing</p></div><div className="rounded-2xl bg-emerald-50/70 p-4"><span className="text-emerald-700"><ClipboardCheck size={17}/></span><p className="mt-3 text-2xl font-extrabold tabular-nums">{completed}</p><p className="mt-1 text-[10px] font-medium text-slate-500">Completed</p></div></div>
        {runs.length > 0 ? <div className="mt-5 space-y-2">{runs.slice(0, 3).map(run => <Link href={`/petitions/${run.id}`} key={run.id} className="flex items-center justify-between gap-3 rounded-xl border border-line px-4 py-3 transition hover:bg-slate-50"><span className="min-w-0"><span className="block text-xs font-bold">Petition run</span><span className="mt-1 block truncate font-mono text-[10px] text-slate-400">{run.id}</span></span><StatusBadge status={run.status}/></Link>)}</div> : <div className="mt-5 rounded-xl border border-dashed border-slate-200 p-5 text-center"><p className="text-xs font-semibold text-slate-600">No submissions in this browser yet</p><p className="mt-1 text-[11px] text-slate-400">Your petition references will appear here.</p></div>}
        <p className="mt-4 text-[10px] leading-5 text-slate-400">{escalated} case(s) currently require authorised review. Counts are limited to locally saved run IDs; this is not an authenticated student-history service.</p>
      </div>
      <div className="card p-6 md:p-7"><p className="eyebrow">Workflow overview</p><h2 className="mt-1 text-xl font-extrabold tracking-tight">From request to assessment</h2><div className="mt-6 space-y-5">{[["01","Submit petition","Student provides category and relevant facts."],["02","Retrieve provisions","Search the configured academic corpus."],["03","Verify evidence","Check passages and citation references."],["04","Route responsibly","Return an advisory result or request human review."]].map(([n,title,desc],i)=><div className="flex gap-3" key={n}><span className={`grid h-9 w-9 shrink-0 place-items-center rounded-xl text-[11px] font-extrabold ${i===3?"bg-teal-50 text-teal":"bg-blue-50 text-[#214d7d]"}`}>{n}</span><div className="min-w-0"><p className="text-[13px] font-bold">{title}</p><p className="mt-1 text-[11px] leading-5 text-slate-500">{desc}</p></div></div>)}</div><div className="mt-6 flex gap-3 rounded-xl border border-amber-100 bg-amber-50/70 p-3.5 text-[11px] leading-5 text-amber-900"><GitBranch size={16} className="mt-0.5 shrink-0"/><span>Final academic decisions always remain with authorised university officials.</span></div></div>
    </section>
    <div className="rounded-2xl border border-slate-200/80 bg-white/65 px-5 py-4 text-[11px] leading-5 text-slate-500"><strong className="text-slate-700">Demo data notice:</strong> The included regulation clauses are synthetic examples for software demonstration only, not official university policy. Do not use this service to make real eligibility decisions.</div>
  </div>;
}
