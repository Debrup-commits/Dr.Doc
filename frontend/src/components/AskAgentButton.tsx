'use client';

import React, { useState } from 'react';
import { MessageCircle, Loader2 } from 'lucide-react';
import { useChat } from '@/contexts/ChatContext';

interface AskAgentButtonProps {
  text: string;
  className?: string;
}

export default function AskAgentButton({ text, className = '' }: AskAgentButtonProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { openChat, sendMessage } = useChat();

  const handleAskAgent = async () => {
    if (!text.trim() || isLoading) return;

    setIsLoading(true);
    
    try {
      // Open chat if it's closed
      openChat();
      
      // Send the extracted text as a query to the agent
      await sendMessage(`Can you explain this part of the documentation: "${text.trim()}"`);
    } catch (error) {
      console.error('Error asking agent:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      onClick={handleAskAgent}
      disabled={isLoading}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      className={`
        absolute top-2 right-2 z-10
        px-3 py-1.5
        bg-white/90 dark:bg-slate-800/90
        border border-slate-200 dark:border-slate-600
        rounded-full
        shadow-sm hover:shadow-md
        text-xs font-medium
        text-slate-600 dark:text-slate-300
        hover:text-emerald-600 dark:hover:text-emerald-400
        hover:border-emerald-300 dark:hover:border-emerald-500
        transition-all duration-200 ease-in-out
        backdrop-blur-sm
        flex items-center space-x-1.5
        ${isHovered ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}
        ${isLoading ? 'cursor-not-allowed opacity-70' : 'cursor-pointer'}
        ${className}
      `}
      title="Ask the AI agent about this section"
    >
      {isLoading ? (
        <>
          <Loader2 size={12} className="animate-spin" />
          <span>Asking...</span>
        </>
      ) : (
        <>
          <MessageCircle size={12} />
          <span>Ask Agent</span>
        </>
      )}
    </button>
  );
}
