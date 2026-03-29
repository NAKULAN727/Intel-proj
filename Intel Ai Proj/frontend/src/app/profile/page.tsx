"use client";

import { useState } from "react";
import { useAuth } from "@/context/AuthContext";
import { motion } from "framer-motion";
import { Camera, Save, User, Mail, Shield } from "lucide-react";

export default function ProfilePage() {
  const { user, updateProfile } = useAuth();
  const [name, setName] = useState(user?.name || "");
  const [email, setEmail] = useState(user?.email || "");
  const [saving, setSaving] = useState(false);

  if (!user) return null;

  const handleSave = () => {
    setSaving(true);
    setTimeout(() => {
      updateProfile(name, email);
      setSaving(false);
    }, 800);
  };

  return (
    <div className="max-w-3xl mx-auto w-full pb-10">
      <header className="mb-10">
        <h1 className="text-3xl font-bold font-poppins text-white mb-2">Profile Settings</h1>
        <p className="text-slate-400">Manage your account details and preferences.</p>
      </header>

      <motion.div 
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900/50 border border-slate-800 rounded-3xl p-8 shadow-xl backdrop-blur-sm"
      >
        <div className="flex flex-col sm:flex-row items-center sm:items-start gap-8 border-b border-slate-800 pb-8 mb-8">
          <div className="relative group cursor-pointer">
            <motion.img 
              whileHover={{ scale: 1.05 }}
              src={user.avatar} 
              alt="Avatar" 
              className="w-32 h-32 rounded-full border-4 border-slate-800 shadow-xl object-cover bg-slate-800"
            />
            <div className="absolute inset-0 rounded-full bg-black/50 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
              <Camera className="w-8 h-8 text-white" />
            </div>
          </div>
          <div className="flex-1 text-center sm:text-left">
            <h2 className="text-2xl font-bold text-white font-poppins">{user.name}</h2>
            <p className="text-slate-400 mb-4">{user.email}</p>
            <div className="inline-flex items-center px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-medium border border-emerald-500/20">
              <Shield className="w-3 h-3 mr-1.5" /> Enterprise Plan
            </div>
          </div>
        </div>

        <div className="space-y-6 max-w-xl">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center">
              <User className="w-4 h-4 mr-2 text-slate-500" /> Full Name
            </label>
            <input 
              type="text" 
              value={name}
              onChange={e => setName(e.target.value)}
              className="w-full bg-slate-950/50 border border-slate-700 rounded-xl py-3 px-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-medium"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-300 flex items-center">
              <Mail className="w-4 h-4 mr-2 text-slate-500" /> Email Address
            </label>
            <input 
              type="email" 
              value={email}
              onChange={e => setEmail(e.target.value)}
              className="w-full bg-slate-950/50 border border-slate-700 rounded-xl py-3 px-4 text-slate-200 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all font-medium"
            />
          </div>

          <div className="pt-4 flex justify-end">
            <button 
              onClick={handleSave}
              disabled={saving}
              className="flex items-center px-6 py-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-medium transition-colors disabled:opacity-50"
            >
              {saving ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-2" />
              ) : (
                <Save className="w-5 h-5 mr-2" />
              )}
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
