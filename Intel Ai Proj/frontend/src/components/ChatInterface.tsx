"use client";

import React, { useState, useRef, useEffect } from "react";
import axios from "axios";
import { Send, User, ChevronDown, FileText, Loader2, Bot, RefreshCw } from "lucide-react";
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

  const clearChat = () => {
    setMessages([]);
  };

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
          content: "Sorry, I encountered an error while processing your request.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[80vh] bg-slate-900 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
      {/* Header with Clear button */}
      <div className="flex justify-between items-center p-4 border-b border-slate-700 bg-slate-800/80">
        <h3 className="text-slate-200 font-semibold flex items-center">
          <Bot className="w-5 h-5 mr-2 text-blue-400" /> Assistant
        </h3>
        <button
          onClick={clearChat}
          disabled={messages.length === 0 || loading}
          className="flex items-center text-xs font-medium text-slate-400 hover:text-slate-200 transition disabled:opacity-50 disabled:cursor-not-allowed bg-slate-800 py-1.5 px-3 rounded-lg border border-slate-600 hover:bg-slate-700"
          title="Refresh chat when you change documents"
        >
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh Chat
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6">
        <AnimatePresence>
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} 
              className="flex items-center justify-center h-full text-slate-500 flex-col space-y-3"
            >
              <Bot className="w-16 h-16 opacity-50" />
              <p>Hello! Ask me anything about the uploaded document.</p>
            </motion.div>
          )}

          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div className={`max-w-[80%] rounded-2xl p-4 ${msg.role === "user" ? "bg-blue-600 text-white" : "bg-slate-800 text-slate-200"}`}>
                <div className="flex items-center space-x-2 mb-2">
                  {msg.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-blue-400" />}
                  <span className="text-xs font-semibold opacity-70 uppercase tracking-wider">{msg.role}</span>
                </div>
                
                <div className="prose prose-invert max-w-none text-sm leading-relaxed">
                  <ReactMarkdown>{msg.content}</ReactMarkdown>
                </div>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 border-t border-slate-700 pt-3">
                    <p className="text-xs text-slate-400 font-medium mb-2 flex items-center">
                      <FileText className="w-3 h-3 mr-1" />
                      Sources Used ({msg.sources.length})
                    </p>
                    <div className="space-y-2">
                      {msg.sources.map((s, idx) => (
                        <details key={idx} className="bg-slate-900 rounded-md overflow-hidden text-xs">
                          <summary className="p-2 cursor-pointer hover:bg-slate-700 transition flex items-center justify-between">
                            <span className="font-medium text-slate-300 truncate">
                              Page {s.page} • Score: {s.rerank_score ?? s.score ?? 0}
                            </span>
                            <ChevronDown className="w-3 h-3 opacity-50" />
                          </summary>
                          <div className="p-2 border-t border-slate-700 text-slate-400">
                            {s.text}
                          </div>
                        </details>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}
          {loading && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-start">
              <div className="bg-slate-800 rounded-2xl p-4 flex items-center space-x-2">
                <Loader2 className="w-5 h-5 text-blue-400 animate-spin" />
                <span className="text-slate-400 text-sm">Thinking...</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 bg-slate-800 border-t border-slate-700">
        <form onSubmit={handleSubmit} className="flex relative items-center">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={!isReady || loading}
            placeholder={isReady ? "Ask a question..." : "Please upload a document first"}
            className="flex-1 bg-slate-900 border border-slate-600 rounded-full py-3 px-5 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500 transition disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!isReady || loading || !input.trim()}
            className="absolute right-2 p-2 bg-blue-600 hover:bg-blue-500 text-white rounded-full transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </button>
        </form>
      </div>
    </div>
  );
}
