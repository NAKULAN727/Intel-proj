"use client";

import { useAuth } from "@/context/AuthContext";
import { UserCircle, LogOut, ChevronDown, Bell, Search, Settings } from "lucide-react";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

export function TopNav() {
  const { user, logout } = useAuth();
  const [menuOpen, setMenuOpen] = useState(false);

  if (!user) return null;

  return (
    <header className="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-6">
      
      {/* Mobile brand - hidden on md+ */}
      <div className="md:hidden flex items-center">
        <span className="text-white font-bold font-poppins text-lg bg-gradient-to-br from-indigo-500 to-purple-600 rounded px-2 shadow-lg">AI</span>
      </div>

      {/* Global Search */}
      <div className="hidden md:flex flex-1 max-w-md relative group">
        <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2 group-focus-within:text-indigo-400 transition-colors" />
        <input 
          type="text" 
          placeholder="Search documents or history (Press / to focus)"
          className="w-full bg-slate-800/60 border border-slate-700/60 rounded-full py-2 pl-10 pr-4 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-inter shadow-inner"
        />
      </div>

      <div className="flex-1 md:hidden" />

      {/* Right Actions */}
      <div className="flex items-center space-x-4 pr-2">
        <button className="relative p-2 text-slate-400 hover:text-slate-200 hover:bg-slate-800 rounded-full transition-colors hidden sm:block">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-500 rounded-full border border-slate-900" />
        </button>

        <div className="relative">
          <button 
            onClick={() => setMenuOpen(!menuOpen)}
            className="flex items-center space-x-2 focus:outline-none group hover:bg-slate-800/80 p-1 pr-3 rounded-full transition-all border border-transparent hover:border-slate-700"
          >
            <motion.img 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              src={user.avatar} 
              alt={user.name} 
              className="w-8 h-8 rounded-full border border-slate-600 bg-slate-800 shadow-sm"
            />
            <span className="text-sm font-medium text-slate-300 group-hover:text-white hidden sm:block">
              {user.name.split(" ")[0]}
            </span>
            <ChevronDown className="w-4 h-4 text-slate-400 group-hover:text-slate-200 hidden sm:block transition-transform duration-200" style={{ transform: menuOpen ? "rotate(180deg)" : "rotate(0deg)" }} />
          </button>

          <AnimatePresence>
            {menuOpen && (
              <motion.div 
                initial={{ opacity: 0, y: 10, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 10, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 mt-2 w-56 rounded-xl border border-slate-700/80 bg-slate-800/95 backdrop-blur-xl shadow-2xl py-2 z-50 overflow-hidden shadow-black/40"
              >
                <div className="px-4 py-3 border-b border-slate-700/80 mb-1">
                  <p className="text-sm font-semibold text-white truncate">{user.name}</p>
                  <p className="text-xs text-slate-400 truncate mt-0.5">{user.email}</p>
                </div>
                
                <Link href="/profile" onClick={() => setMenuOpen(false)} className="flex items-center px-4 py-2.5 text-sm text-slate-300 hover:bg-indigo-500/10 hover:text-indigo-400 transition-colors">
                  <UserCircle className="w-4 h-4 mr-3" />
                  My Profile
                </Link>
                
                <Link href="/settings" onClick={() => setMenuOpen(false)} className="flex items-center px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-700/50 hover:text-white transition-colors">
                  <Settings className="w-4 h-4 mr-3" />
                  Account Settings
                </Link>

                <div className="h-px bg-slate-700/80 my-1 mx-2"></div>
                
                <button 
                  onClick={() => { setMenuOpen(false); logout(); }}
                  className="w-full flex items-center px-4 py-2.5 text-sm text-slate-400 hover:bg-red-500/10 hover:text-red-400 transition-colors font-medium group"
                >
                  <LogOut className="w-4 h-4 mr-3 group-hover:-translate-x-0.5 transition-transform" />
                  Sign Out
                </button>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
