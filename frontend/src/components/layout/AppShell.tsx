"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BookOpen, FilePlus2, HelpCircle, LayoutDashboard, Menu, X, ClipboardList } from "lucide-react";
import { useState } from "react";

const links = [{href:"/dashboard",label:"Dashboard",icon:LayoutDashboard},{href:"/petitions/new",label:"Submit Petition",icon:FilePlus2},{href:"/petitions",label:"My Petitions",icon:ClipboardList},{href:"/help",label:"Help & About",icon:HelpCircle}];
export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname=usePathname(); const [open,setOpen]=useState(false);
  return <div className="min-h-screen md:flex">
    <aside className={`${open?"translate-x-0":"-translate-x-full"} fixed inset-y-0 left-0 z-40 w-72 border-r border-line bg-white p-5 transition-transform md:static md:translate-x-0`}>
      <div className="flex items-center justify-between"><Link href="/dashboard" className="flex items-center gap-3" onClick={()=>setOpen(false)}><span className="grid h-10 w-10 place-items-center rounded-xl bg-navy text-white"><BookOpen size={21}/></span><span><span className="block text-sm font-bold text-ink">Academic Petition</span><span className="block text-xs text-slate-500">Student services</span></span></Link><button className="md:hidden" onClick={()=>setOpen(false)} aria-label="Close navigation"><X size={20}/></button></div>
      <nav className="mt-10 space-y-1">{links.map(({href,label,icon:Icon})=><Link key={href} href={href} onClick={()=>setOpen(false)} className={`flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold ${pathname===href||pathname.startsWith(href+"/")?"bg-blue-50 text-navy":"text-slate-600 hover:bg-mist hover:text-ink"}`}><Icon size={18}/>{label}</Link>)}</nav>
      <div className="absolute bottom-5 left-5 right-5 rounded-2xl bg-mist p-4"><p className="text-xs font-bold text-ink">Demo student-reference mode</p><p className="mt-1 text-xs leading-5 text-slate-500">No authentication is configured. Track submissions from this browser only.</p></div>
    </aside>
    {open&&<button className="fixed inset-0 z-30 bg-ink/30 md:hidden" onClick={()=>setOpen(false)} aria-label="Close navigation overlay"/>}
    <div className="min-w-0 flex-1"><header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-line bg-white/95 px-5 backdrop-blur md:px-10"><div className="flex items-center gap-3"><button className="md:hidden" onClick={()=>setOpen(true)} aria-label="Open navigation"><Menu size={22}/></button><div><p className="text-sm font-bold text-ink">{links.find(x=>pathname===x.href||pathname.startsWith(x.href+"/"))?.label||"Petition services"}</p><p className="hidden text-xs text-slate-500 sm:block">Evidence-backed academic guidance</p></div></div><span className="rounded-full border border-line px-3 py-1.5 text-xs font-semibold text-slate-600">Advisory service</span></header><main className="mx-auto max-w-7xl p-5 md:p-10">{children}</main></div>
  </div>;
}
