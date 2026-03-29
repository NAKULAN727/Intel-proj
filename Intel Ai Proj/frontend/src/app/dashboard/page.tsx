"use client";

import { useAuth } from "@/context/AuthContext";
import { motion } from "framer-motion";
import { FileText, Clock, ArrowUpRight, TrendingUp, Users } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <div className="max-w-6xl mx-auto w-full pb-10">
      <header className="mb-10">
        <motion.h1 
          initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          className="text-3xl font-bold font-poppins text-white mb-2"
        >
          Welcome back, {user?.name?.split(" ")[0]} 🚀
        </motion.h1>
        <motion.p 
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.1 }}
          className="text-slate-400"
        >
          Here's an overview of your Enterprise Knowledge Base operations.
        </motion.p>
      </header>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
        {[
          { label: "Total Documents", value: "14", change: "+2 this week", icon: FileText, color: "text-blue-400", bg: "bg-blue-500/10" },
          { label: "Queries Answered", value: "1,248", change: "+148 today", icon: TrendingUp, color: "text-emerald-400", bg: "bg-emerald-500/10" },
          { label: "Active Users", value: "3", change: "Stable", icon: Users, color: "text-purple-400", bg: "bg-purple-500/10" }
        ].map((stat, i) => (
          <motion.div 
            key={i}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="p-6 rounded-2xl bg-slate-900/50 border border-slate-800 shadow-xl backdrop-blur-sm hover:-translate-y-1 transition-transform duration-300"
          >
            <div className="flex justify-between items-start mb-4">
              <div className={`p-3 rounded-xl ${stat.bg}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
              <span className="text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-full">
                {stat.change}
              </span>
            </div>
            <h3 className="text-3xl font-bold text-white font-poppins mb-1">{stat.value}</h3>
            <p className="text-sm text-slate-400 font-medium">{stat.label}</p>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Quick Actions */}
        <motion.div 
          initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
          className="col-span-1 border border-slate-800 bg-slate-900/30 rounded-3xl p-6"
        >
          <h3 className="text-lg font-semibold text-white mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <Link href="/upload" className="flex items-center justify-between p-4 rounded-2xl bg-gradient-to-r from-indigo-500/10 to-indigo-500/5 hover:from-indigo-500/20 hover:to-indigo-500/10 border border-indigo-500/20 transition-all group">
              <div>
                <p className="text-indigo-300 font-medium mb-0.5">Upload Document</p>
                <p className="text-xs text-indigo-400/60">Index a new PDF into memory</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-indigo-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <ArrowUpRight className="w-4 h-4 text-indigo-300" />
              </div>
            </Link>
            
            <Link href="/chat" className="flex items-center justify-between p-4 rounded-2xl bg-gradient-to-r from-purple-500/10 to-purple-500/5 hover:from-purple-500/20 hover:to-purple-500/10 border border-purple-500/20 transition-all group">
              <div>
                <p className="text-purple-300 font-medium mb-0.5">Start New Chat</p>
                <p className="text-xs text-purple-400/60">Query the knowledge base</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-purple-500/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                <ArrowUpRight className="w-4 h-4 text-purple-300" />
              </div>
            </Link>
          </div>
        </motion.div>

        {/* Recent Documents */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
          className="col-span-1 lg:col-span-2 border border-slate-800 bg-slate-900/30 rounded-3xl p-6"
        >
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-lg font-semibold text-white">Recent Documents</h3>
            <button className="text-sm text-indigo-400 hover:text-indigo-300">View all</button>
          </div>

          <div className="space-y-4">
            {[
              { name: "Q4_Financial_Report_2024.pdf", time: "2 hours ago", size: "2.4 MB" },
              { name: "Employee_Handbook_v3.pdf", time: "Yesterday", size: "1.1 MB" },
              { name: "Technical_Architecture_Spec.pdf", time: "3 days ago", size: "4.8 MB" }
            ].map((doc, i) => (
              <div key={i} className="flex items-center p-4 rounded-2xl hover:bg-slate-800/50 transition-colors border border-transparent hover:border-slate-700">
                <div className="w-10 h-10 rounded-lg bg-slate-800 flex items-center justify-center mr-4 shrink-0">
                  <FileText className="w-5 h-5 text-slate-400" />
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">{doc.name}</p>
                  <div className="flex items-center text-xs text-slate-500 mt-1">
                    <Clock className="w-3 h-3 mr-1" /> {doc.time} • {doc.size}
                  </div>
                </div>
                <div className="ml-4 flex gap-2">
                  <button className="px-3 py-1.5 text-xs font-medium text-indigo-400 bg-indigo-400/10 rounded-lg hover:bg-indigo-400/20 transition-colors">Analyze</button>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

    </div>
  );
}
