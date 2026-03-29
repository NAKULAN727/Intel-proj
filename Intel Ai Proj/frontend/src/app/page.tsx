"use client";

import React, { useState } from "react";
import FileUpload from "../components/FileUpload";
import ChatInterface from "../components/ChatInterface";

export default function Home() {
  const [isReady, setIsReady] = useState(false);
  const [documentDetails, setDocumentDetails] = useState<{ filename: string; chunksCount: number } | null>(null);

  const handleUploadSuccess = (filename: string, chunksCount: number) => {
    setIsReady(true);
    setDocumentDetails({ filename, chunksCount });
  };

  return (
    <main className="min-h-screen bg-[#0E1628] text-slate-200 font-sans">
      <div className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-[1fr,2fr] gap-8 h-screen items-start">
        
        {/* Left column - Setup & Info */}
        <div className="space-y-6 flex flex-col pt-10">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2 tracking-tight">Enterprise PDF Knowledge Base</h1>
            <p className="text-slate-400 text-sm leading-relaxed mb-6">
              A private, secure tool for asking questions intelligently against large PDF files. Runs models locally without external APIs.
            </p>
          </div>
          
          <FileUpload onUploadSuccess={handleUploadSuccess} />

          {documentDetails && (
            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg shadow-sm">
              <h3 className="text-green-400 font-medium mb-1">Knowledge Base Ready</h3>
              <p className="text-slate-300 text-sm">
                Indexed <span className="font-semibold">{documentDetails.filename}</span> with 
                <span className="font-semibold text-blue-400 mx-1">{documentDetails.chunksCount}</span> chunks.
              </p>
            </div>
          )}
        </div>

        {/* Right column - Chat Interface */}
        <div className="pt-10 pb-8 flex-1 h-[90vh]">
          <ChatInterface isReady={isReady} />
        </div>

      </div>
    </main>
  );
}
