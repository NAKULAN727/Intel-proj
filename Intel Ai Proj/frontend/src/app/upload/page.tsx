"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import { motion } from "framer-motion";
import { Database, FileCheck } from "lucide-react";

export default function UploadPage() {
  const [documentDetails, setDocumentDetails] = useState<{ filename: string; chunksCount: number } | null>(null);

  const handleUploadSuccess = (filename: string, chunksCount: number) => {
    setDocumentDetails({ filename, chunksCount });
  };

  return (
    <div className="max-w-3xl mx-auto w-full pb-10">
      <header className="mb-10 text-center">
        <h1 className="text-3xl font-bold font-poppins text-white mb-3">Upload PDF Document</h1>
        <p className="text-slate-400">Index new material to your Enterprise RAG cluster.</p>
      </header>

      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900/40 border border-slate-800 rounded-3xl p-8 shadow-2xl backdrop-blur-xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500" />
        
        <div className="mb-8">
          <FileUpload onUploadSuccess={handleUploadSuccess} />
        </div>

        {documentDetails && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}
            className="p-5 rounded-2xl bg-gradient-to-r from-emerald-500/10 to-emerald-500/5 border border-emerald-500/20 flex items-start gap-4"
          >
            <div className="w-10 h-10 rounded-xl bg-emerald-500/20 flex items-center justify-center shrink-0">
              <Database className="w-5 h-5 text-emerald-400" />
            </div>
            <div>
              <h3 className="text-emerald-400 text-lg font-bold font-poppins mb-1 flex items-center">
                Knowledge Base Indexed <FileCheck className="w-4 h-4 ml-2" />
              </h3>
              <p className="text-slate-300 text-sm leading-relaxed">
                Successfully processed <span className="text-white font-medium">{documentDetails.filename}</span> safely routing 
                <span className="text-emerald-300 font-bold mx-1">{documentDetails.chunksCount}</span> semantic chunks into the local vector space.
              </p>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
