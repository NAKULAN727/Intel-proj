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
    <div className="w-full max-w-md p-6 bg-slate-800 rounded-xl shadow-lg border border-slate-700">
      <h2 className="text-xl font-semibold text-white mb-4">Knowledge Base Setup</h2>
      <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-600 rounded-lg p-6 bg-slate-900/50 hover:bg-slate-800/80 transition cursor-pointer relative">
        <input 
          type="file" 
          accept=".pdf" 
          onChange={handleFileChange} 
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        {file ? (
          <div className="flex items-center text-slate-300">
            <File className="w-8 h-8 text-blue-400 mr-2" />
            <span className="font-medium text-sm truncate max-w-[200px]">{file.name}</span>
          </div>
        ) : (
          <div className="flex flex-col items-center text-slate-400">
            <UploadCloud className="w-10 h-10 mb-2 text-slate-500" />
            <span className="text-sm font-medium">Click or drag PDF to upload</span>
          </div>
        )}
      </div>

      {error && <div className="mt-3 text-red-400 text-sm font-medium bg-red-900/20 p-2 rounded">{error}</div>}

      <button
        onClick={handleUpload}
        disabled={!file || uploading}
        className="w-full mt-4 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:text-slate-500 text-white font-medium py-2 rounded-lg transition flex justify-center items-center"
      >
        {uploading ? (
          <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
            <Loader2 className="w-5 h-5" />
          </motion.div>
        ) : (
          "Build Knowledge Base"
        )}
      </button>
    </div>
  );
}
