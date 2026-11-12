import "./globals.css";
import { AppShell } from "@/components/layout/AppShell";
export const metadata = { title: "Academic Petition Services", description: "Advisory academic petition triage portal" };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body><AppShell>{children}</AppShell></body></html>; }
