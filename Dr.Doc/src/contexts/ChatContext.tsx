'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
}

interface ChatContextType {
  isChatOpen: boolean;
  toggleChat: () => void;
  messages: Message[];
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  sendMessage: (text: string) => Promise<void>;
  backendStatus: 'connected' | 'disconnected' | 'checking';
  checkBackendStatus: () => Promise<void>;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello! I\'m your AI agent. How can I help you today?',
      sender: 'agent',
      timestamp: new Date(),
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  const toggleChat = useCallback(() => {
    setIsChatOpen(prev => !prev);
  }, []);

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, newMessage]);
  }, []);

  const clearMessages = useCallback(() => {
    setMessages([
      {
        id: '1',
        text: 'Hello! I\'m your AI agent. How can I help you today?',
        sender: 'agent',
        timestamp: new Date(),
      },
    ]);
  }, []);

  const sendMessage = useCallback(async (text: string) => {
    if (!text.trim() || isLoading) return;

    // Add user message
    addMessage({
      text: text.trim(),
      sender: 'user',
      status: 'sending',
    });

    setIsLoading(true);

    try {
      // Connect to the actual backend agent API
      const response = await fetch('http://localhost:5003/api/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          question: text.trim(),
          user_id: 'frontend_user',
          session_id: Date.now().toString()
        }),
      });

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      
      // Check if we have a valid response (either success: true or an answer field)
      if (data.success || (data.answer && !data.error)) {
        // Add agent response with rich information
        let responseText = data.answer || 'No answer available';
        
        // Add sources if available
        if (data.sources && data.sources.length > 0) {
          const sourceNames = data.sources.map((source: any) => 
            typeof source === 'string' ? source : source.source || 'Unknown'
          );
          responseText += `\n\n📚 Sources: ${sourceNames.join(', ')}`;
        }
        
        // Add confidence score if available
        if (data.confidence) {
          responseText += `\n\n🎯 Confidence: ${(data.confidence * 100).toFixed(1)}%`;
        }
        
        // Add reasoning if available
        if (data.reasoning && data.reasoning !== 'No reasoning provided') {
          responseText += `\n\n💭 Reasoning: ${data.reasoning}`;
        }
        
        addMessage({
          text: responseText,
          sender: 'agent',
          status: 'sent',
        });
      } else {
        // Handle agent error response
        addMessage({
          text: `❌ Agent Error: ${data.error || 'Unknown error occurred'}`,
          sender: 'agent',
          status: 'error',
        });
      }
    } catch (error) {
      console.error('Error sending message to backend:', error);
      
      // Add error message with helpful information
      let errorMessage = 'Sorry, I encountered an error. ';
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        errorMessage += 'The backend agent is not running. Please start the backend system first.';
      } else {
        errorMessage += 'Please try again or check if the backend is running.';
      }
      
      addMessage({
        text: errorMessage,
        sender: 'agent',
        status: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  }, [addMessage, isLoading]);

  const checkBackendStatus = useCallback(async () => {
    setBackendStatus('checking');
    try {
      const response = await fetch('http://localhost:5003/api/health', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.status === 'healthy') {
          setBackendStatus('connected');
        } else {
          setBackendStatus('disconnected');
        }
      } else {
        setBackendStatus('disconnected');
      }
    } catch (error) {
      console.error('Backend health check failed:', error);
      setBackendStatus('disconnected');
    }
  }, []);

  // Check backend status on mount
  React.useEffect(() => {
    checkBackendStatus();
  }, [checkBackendStatus]);

  const value: ChatContextType = {
    isChatOpen,
    toggleChat,
    messages,
    addMessage,
    clearMessages,
    isLoading,
    setIsLoading,
    sendMessage,
    backendStatus,
    checkBackendStatus,
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat() {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
}
