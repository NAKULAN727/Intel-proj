"use client";

import { useState } from "react";
import ChatInterface from "@/components/ChatInterface";
import { useAuth } from "@/context/AuthContext";
import { motion } from "framer-motion";

export default function ChatPage() {
  const { user } = useAuth();
  // Assume for this simplified demo that isReady is true to allow chatting immediately
  // Or we can connect it to global state later. True for demonstration.
  const [isReady] = useState(true);

  if (!user) return null;

  return (
    <div className="max-w-4xl mx-auto w-full h-full flex flex-col pt-4 pb-2">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="w-full flex-1"
      >
        <ChatInterface isReady={isReady} />
      </motion.div>
    </div>
  );
}
