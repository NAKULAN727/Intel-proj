"use client";

import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Send, User, ChevronDown, FileText, Loader2, Bot, RefreshCw, Layers } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";

interface Source {
  page: string | number;
  source: string;
  rerank_score?: number;
  score?: number;
  text: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: Source[];
}

export default function ChatInterface({ isReady }: { isReady: boolean }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const clearChat = () => setMessages([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !isReady) return;

    const userMessage: Message = { id: Date.now().toString(), role: "user", content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post("http://localhost:8000/api/query", { query: userMessage.content });
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: response.data.answer,
          sources: response.data.sources,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: "assistant",
          content: "Sorry, I encountered an error while communicating with the server.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[85vh] md:h-[80vh] bg-slate-900/40 backdrop-blur-xl rounded-3xl shadow-2xl border border-slate-800 overflow-hidden relative">
      
      {/* Header */}
      <div className="flex justify-between items-center px-6 py-4 border-b border-slate-800/80 bg-slate-900/60 shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex justify-center items-center shadow-[0_0_15px_rgba(99,102,241,0.3)]">
            <Layers className="w-5 h-5 text-white" />
          </div>
          <div>
            <h3 className="text-slate-100 font-bold font-poppins">NexusRAG Chat</h3>
            <p className="text-xs text-indigo-400 font-medium">Enterprise Assistant</p>
          </div>
        </div>
        
        <button
          onClick={clearChat}
          disabled={messages.length === 0 || loading}
          className="flex items-center text-xs font-semibold text-slate-400 hover:text-white transition-all disabled:opacity-40 disabled:cursor-not-allowed bg-slate-800/80 hover:bg-slate-700 py-2 px-4 rounded-xl border border-slate-700 hover:border-slate-500 shadow-sm"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          New Chat
        </button>
      </div>

      {/* Messages Window */}
      <div className="flex-1 overflow-y-auto p-4 md:p-8 space-y-8 custom-scrollbar relative z-0">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} 
              className="flex items-center justify-center h-full flex-col text-center max-w-sm mx-auto"
            >
              <div className="w-20 h-20 rounded-3xl bg-slate-800/50 flex items-center justify-center mb-6 shadow-xl border border-slate-700/50">
                <Bot className="w-10 h-10 text-indigo-400 opacity-80" />
              </div>
              <h2 className="text-2xl font-bold font-poppins text-white mb-2">How can I help you today?</h2>
              <p className="text-slate-400 text-sm">Ask any question about the uploaded document, summarize data, or extract key metrics reliably.</p>
            </motion.div>
          )}

          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3, ease: "easeOut" }}
              className={`flex w-full ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`flex gap-4 max-w-[85%] md:max-w-[75%] ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}>
                
                {/* Avatar */}
                <div className="shrink-0 mt-1">
                  {msg.role === "user" ? (
                    <div className="w-8 h-8 rounded-full bg-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                      <User className="w-5 h-5 text-white" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
                      <Bot className="w-5 h-5 text-white" />
                    </div>
                  )}
                </div>

                {/* Bubble */}
                <div className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}>
                  <div className={`rounded-2xl px-5 py-3.5 shadow-sm text-[15px] leading-relaxed
                    ${msg.role === "user" 
                      ? "bg-indigo-600 text-white rounded-tr-sm" 
                      : "bg-slate-800 text-slate-200 rounded-tl-sm border border-slate-700" 
                    }`}
                  >
                    <div className="prose prose-invert max-w-none break-words">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>

                  {/* Sources Dropdown */}
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="mt-2 w-full max-w-xl">
                      <div className="space-y-2 mt-2">
                        {msg.sources.map((s, idx) => (
                          <details key={idx} className="bg-slate-900/60 border border-slate-700/60 rounded-xl overflow-hidden group">
                            <summary className="px-4 py-2.5 cursor-pointer hover:bg-slate-800 transition flex items-center justify-between outline-none">
                              <span className="flex items-center text-xs font-semibold text-slate-300 group-hover:text-indigo-300 transition-colors">
                                <FileText className="w-3.5 h-3.5 mr-2 text-indigo-400" />
                                Page {s.page} Match (Score: {s.rerank_score ?? s.score ?? 0})
                              </span>
                              <ChevronDown className="w-4 h-4 text-slate-500 group-hover:text-slate-300 group-open:rotate-180 transition-transform" />
                            </summary>
                            <div className="px-4 py-3 bg-slate-950/40 text-xs text-slate-400 border-t border-slate-800 leading-relaxed font-inter">
                              {s.text}
                            </div>
                          </details>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          ))}

          {/* Typing Indicator */}
          {loading && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="flex justify-start gap-4">
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5 text-white" />
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-2xl rounded-tl-sm px-5 py-4 flex items-center space-x-2">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.3s]" />
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce [animation-delay:-0.15s]" />
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" />
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} className="h-4" />
      </div>

      {/* Input Area */}
      <div className="p-4 md:p-6 bg-slate-900/80 backdrop-blur-md border-t border-slate-800 z-10">
        <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto flex items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!isReady || loading}
            placeholder={isReady ? "Ask anything about your document..." : "Please initialize knowledge base via Dashboard first."}
            rows={1}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            style={{ minHeight: "56px", maxHeight: "150px" }}
            className="w-full bg-slate-800 border-2 border-slate-700 rounded-2xl py-3.5 pl-6 pr-14 text-[15px] text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-4 focus:ring-indigo-500/10 transition-all resize-none shadow-[0_0_20px_rgba(0,0,0,0.2)] disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!isReady || loading || !input.trim()}
            className="absolute right-2 bottom-2 p-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all shadow-lg hover:shadow-indigo-500/25 disabled:opacity-40 disabled:hover:bg-indigo-600 disabled:shadow-none"
          >
            {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
          </button>
        </form>
        <p className="text-center text-[11px] text-slate-500 mt-3 hidden md:block">
          AI NexusRAG can make mistakes. Verify critical document extractions.
        </p>
      </div>
    </div>
  );
}
