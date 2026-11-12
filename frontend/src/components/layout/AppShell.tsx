"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, FilePlus2, HelpCircle, LayoutDashboard, Menu, X, ClipboardList, ShieldCheck, Sparkles } from "lucide-react";
import { useState } from "react";

const links = [
  { href: "/dashboard", label: "Overview", icon: LayoutDashboard },
  { href: "/petitions/new", label: "Submit petition", icon: FilePlus2 },
  { href: "/petitions", label: "Track petitions", icon: ClipboardList },
  { href: "/help", label: "Help & about", icon: HelpCircle },
];
export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const active = links.find(x => pathname === x.href || pathname.startsWith(x.href + "/"));
  return <div className="min-h-screen md:flex">
    <aside className={`${open ? "translate-x-0" : "-translate-x-full"} fixed inset-y-0 left-0 z-40 flex w-[278px] flex-col border-r border-line bg-white px-5 py-6 transition-transform duration-300 md:sticky md:top-0 md:h-screen md:translate-x-0`}>
      <div className="flex items-center justify-between">
        <Link href="/dashboard" className="flex items-center gap-3" onClick={() => setOpen(false)}>
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-gradient-to-br from-[#214d7d] to-[#102d50] text-white shadow-lg shadow-blue-950/15"><BookOpen size={21}/></span>
          <span><span className="block text-[14px] font-extrabold tracking-tight text-ink">CampusResolve</span><span className="mt-0.5 block text-[11px] font-medium text-slate-500">Academic petition services</span></span>
        </Link>
        <button className="rounded-lg p-2 text-slate-500 hover:bg-mist md:hidden" onClick={() => setOpen(false)} aria-label="Close navigation"><X size={19}/></button>
      </div>
      <div className="mt-10"><p className="px-3 text-[10px] font-bold uppercase tracking-[.18em] text-slate-400">Workspace</p>
        <nav className="mt-3 space-y-1">{links.map(({ href, label, icon: Icon }) => {
          const selected = pathname === href || pathname.startsWith(href + "/");
          return <Link key={href} href={href} onClick={() => setOpen(false)} aria-current={selected ? "page" : undefined} className={`group flex items-center gap-3 rounded-xl px-3.5 py-3 text-[13px] font-semibold transition ${selected ? "bg-[#edf4fb] text-[#183b66] shadow-sm" : "text-slate-600 hover:bg-slate-50 hover:text-ink"}`}>
            <Icon size={18} className={selected ? "text-teal" : "text-slate-400 group-hover:text-slate-600"}/>{label}{selected && <span className="ml-auto h-1.5 w-1.5 rounded-full bg-teal"/>}
          </Link>;
        })}</nav>
      </div>
      <div className="mt-auto space-y-4">
        <div className="rounded-2xl border border-[#dcece9] bg-gradient-to-br from-[#f0f9f7] to-[#f7fbff] p-4">
          <div className="flex items-center gap-2 text-teal"><ShieldCheck size={16}/><span className="text-xs font-bold">Evidence-first workflow</span></div>
          <p className="mt-2 text-[11px] leading-5 text-slate-600">Every assessment shows its supporting provisions and flags cases needing human review.</p>
        </div>
        <div className="flex items-center gap-2 border-t border-line px-1 pt-4"><span className="grid h-8 w-8 place-items-center rounded-full bg-slate-100 text-slate-500"><Sparkles size={15}/></span><div><p className="text-[11px] font-bold text-slate-700">Demonstration environment</p><p className="text-[10px] text-slate-400">No student sign-in configured</p></div></div>
      </div>
    </aside>
    {open && <button className="fixed inset-0 z-30 bg-slate-950/35 backdrop-blur-[2px] md:hidden" onClick={() => setOpen(false)} aria-label="Close navigation overlay"/>}
    <div className="min-w-0 flex-1">
      <header className="sticky top-0 z-20 flex h-[70px] items-center justify-between border-b border-line/90 bg-white/90 px-5 backdrop-blur-xl md:px-9">
        <div className="flex items-center gap-3"><button className="rounded-lg p-2 text-slate-600 hover:bg-mist md:hidden" onClick={() => setOpen(true)} aria-label="Open navigation"><Menu size={21}/></button><div><p className="text-[13px] font-bold text-ink">{active?.label || "Petition workspace"}</p><p className="mt-0.5 hidden text-[11px] text-slate-400 sm:block">Transparent, regulation-grounded academic guidance</p></div></div>
        <div className="flex items-center gap-2 rounded-full border border-[#d9e9e6] bg-[#f2faf8] px-3 py-1.5"><span className="h-2 w-2 rounded-full bg-teal"/><span className="text-[11px] font-semibold text-teal">Advisory service</span></div>
      </header>
      <main className="mx-auto w-full max-w-[1440px] p-5 md:px-9 md:py-8 lg:px-11">{children}</main>
      <footer className="mx-auto flex max-w-[1440px] flex-wrap items-center justify-between gap-2 px-5 pb-7 text-[10px] text-slate-400 md:px-9 lg:px-11"><span>CampusResolve · Academic Petition Triage</span><span>Advisory only · Final decisions remain with authorised officials</span></footer>
    </div>
  </div>;
}
