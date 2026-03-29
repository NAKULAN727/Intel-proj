"use client";

import React, { useState } from "react";
import axios from "axios";
import { UploadCloud, File, Loader2 } from "lucide-react";
import { motion } from "framer-motion";

interface FileUploadProps {
  onUploadSuccess: (filename: string, chunksCount: number) => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://localhost:8000/api/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      onUploadSuccess(response.data.filename, response.data.chunks_count);
      setFile(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || "An error occurred during upload.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-xl p-8 bg-slate-900/50 backdrop-blur-md rounded-3xl shadow-xl border border-slate-800 relative group overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 blur-[50px] rounded-full group-hover:bg-indigo-500/20 transition-colors" />
      <h2 className="text-xl font-bold font-poppins text-white mb-6 flex items-center">
        <UploadCloud className="w-5 h-5 mr-2 text-indigo-400" /> Upload Document
      </h2>
      
      <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-700/80 rounded-2xl p-8 bg-slate-950/30 hover:bg-slate-800/60 hover:border-indigo-500/50 transition-all cursor-pointer relative group/upload">
        <input 
          type="file" 
          accept=".pdf" 
          onChange={(e) => {
             handleFileChange(e);
          }} 
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
          disabled={uploading}
        />
        {file ? (
          <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex flex-col items-center text-slate-200">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center mb-4 border border-indigo-500/30 shadow-inner">
              <File className="w-8 h-8 text-indigo-400" />
            </div>
            <span className="font-semibold text-lg truncate max-w-[250px] text-center">{file.name}</span>
            <span className="text-xs text-slate-500 mt-1">Ready to process</span>
          </motion.div>
        ) : (
          <div className="flex flex-col items-center text-slate-400">
            <div className="w-16 h-16 rounded-full bg-slate-800 flex items-center justify-center mb-4 group-hover/upload:scale-110 transition-transform shadow-inner">
              <UploadCloud className="w-6 h-6 text-slate-300 group-hover/upload:text-indigo-400 transition-colors" />
            </div>
            <span className="text-sm font-medium text-slate-200">Click or drag PDF to upload</span>
            <span className="text-xs font-medium text-slate-500 mt-1">Maximum file size: 50MB</span>
          </div>
        )}
      </div>

      {error && (
        <motion.div initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }} className="mt-4 text-red-400 text-sm font-medium bg-red-500/10 border border-red-500/20 p-3 rounded-xl flex items-center">
          <div className="w-1.5 h-1.5 rounded-full bg-red-400 mr-2" />
          {error}
        </motion.div>
      )}

      <button
        onClick={(e) => {
          e.preventDefault();
          handleUpload();
        }}
        disabled={!file || uploading}
        className="relative w-full mt-6 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 disabled:from-slate-800 disabled:to-slate-800 disabled:text-slate-500 text-white font-semibold py-3.5 rounded-xl transition-all flex justify-center items-center shadow-lg disabled:shadow-none hover:shadow-indigo-500/25 overflow-hidden group/btn"
      >
        {!uploading && !(!file) && (
          <span className="absolute inset-0 bg-white/20 translate-y-full group-hover/btn:translate-y-0 transition-transform duration-300 ease-out z-0" />
        )}
        <span className="relative z-10 flex items-center">
          {uploading ? (
            <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
              <Loader2 className="w-5 h-5 mr-2" />
            </motion.div>
          ) : null}
          {uploading ? "Indexing to Vector Store..." : "Build Knowledge Base"}
        </span>
      </button>
    </div>
  );
}
