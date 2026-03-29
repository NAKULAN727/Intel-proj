"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, MessageSquare, UploadCloud, UserCircle, LogOut, ChevronRight } from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";

const navItems = [
  { name: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  { name: "Chat", href: "/chat", icon: MessageSquare },
  { name: "Upload PDF", href: "/upload", icon: UploadCloud },
  { name: "Profile", href: "/profile", icon: UserCircle },
];

export function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  return (
    <motion.aside 
      initial={{ x: -250 }} animate={{ x: 0 }} transition={{ duration: 0.4, ease: "easeOut" }}
      className="w-64 h-screen bg-slate-900/50 backdrop-blur-xl border-r border-slate-800 flex flex-col fixed left-0 top-0 z-40 hidden md:flex"
    >
      <div className="h-16 flex items-center px-6 border-b border-slate-800">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center mr-3 shadow-lg shadow-indigo-500/20">
          <span className="text-white font-bold font-poppins text-lg">AI</span>
        </div>
        <span className="text-slate-100 font-poppins font-semibold text-lg tracking-wide">Nexus<span className="text-indigo-400">RAG</span></span>
      </div>

      <nav className="flex-1 px-4 py-8 space-y-2 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link key={item.name} href={item.href} className="block relative">
              {isActive && (
                <motion.div layoutId="sidebar-active" className="absolute inset-0 bg-indigo-500/10 border border-indigo-500/20 rounded-xl" />
              )}
              <div className={`relative flex items-center px-4 py-3 rounded-xl transition-all duration-200 group ${isActive ? "text-indigo-400" : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"}`}>
                <Icon className={`w-5 h-5 mr-3 transition-transform duration-200 ${isActive ? "" : "group-hover:scale-110"}`} />
                <span className="font-medium">{item.name}</span>
                {isActive && <ChevronRight className="w-4 h-4 ml-auto" />}
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800">
        <button 
          onClick={logout}
          className="flex w-full items-center px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all duration-200 group"
        >
          <LogOut className="w-5 h-5 mr-3 group-hover:-translate-x-1 transition-transform" />
          <span className="font-medium">Sign Out</span>
        </button>
      </div>
    </motion.aside>
  );
}
