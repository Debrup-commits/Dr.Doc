'use client';

import React, { createContext, useContext, useState, useCallback } from 'react';

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent' | 'system';
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  type?: 'message' | 'session-start' | 'session-end';
}

interface ChatContextType {
  isChatOpen: boolean;
  toggleChat: () => void;
  openChat: () => void;
  closeChat: () => void;
  messages: Message[];
  addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
  clearMessages: () => void;
  startNewChat: () => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  sendMessage: (text: string) => Promise<void>;
  backendStatus: 'connected' | 'disconnected' | 'checking';
  checkBackendStatus: () => Promise<void>;
  currentSessionId: string;
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export function ChatProvider({ children }: { children: React.ReactNode }) {
  // Initialize current session ID
  const [currentSessionId, setCurrentSessionId] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('currentSessionId') || Date.now().toString();
    }
    return Date.now().toString();
  });

  // Initialize chat state from localStorage or default to false
  const [isChatOpen, setIsChatOpen] = useState(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('chatOpen') === 'true';
    }
    return false;
  });
  
  // Initialize messages from localStorage or default
  const [messages, setMessages] = useState<Message[]>(() => {
    if (typeof window !== 'undefined') {
      const savedMessages = localStorage.getItem('chatMessages');
      const lastSessionId = localStorage.getItem('lastSessionId');
      const currentSessionId = localStorage.getItem('currentSessionId') || Date.now().toString();
      
      if (savedMessages) {
        try {
          const parsed = JSON.parse(savedMessages);
          // Convert timestamp strings back to Date objects
          const messages = parsed.map((msg: Message) => ({
            ...msg,
            timestamp: new Date(msg.timestamp)
          }));
          
          // Add session start message if this is a new session
          if (lastSessionId !== currentSessionId) {
            const sessionStartMessage: Message = {
              id: `session-${currentSessionId}`,
              text: `🔄 New session started at ${new Date().toLocaleString()}`,
              sender: 'system',
              timestamp: new Date(),
              type: 'session-start'
            };
            localStorage.setItem('lastSessionId', currentSessionId);
            return [sessionStartMessage, ...messages];
          }
          
          return messages;
        } catch (error) {
          console.error('Failed to parse saved messages:', error);
        }
      }
      
      // First time user - set session ID
      localStorage.setItem('lastSessionId', currentSessionId);
      localStorage.setItem('currentSessionId', currentSessionId);
    }
    
    return [
      {
        id: '1',
        text: 'Hello! I\'m your AI agent. How can I help you today?',
        sender: 'agent',
        timestamp: new Date(),
        type: 'message'
      },
    ];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState<'connected' | 'disconnected' | 'checking'>('checking');

  const toggleChat = useCallback(() => {
    setIsChatOpen(prev => {
      const newState = !prev;
      // Persist chat state to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('chatOpen', newState.toString());
      }
      return newState;
    });
  }, []);

  const openChat = useCallback(() => {
    setIsChatOpen(true);
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatOpen', 'true');
    }
  }, []);

  const closeChat = useCallback(() => {
    setIsChatOpen(false);
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatOpen', 'false');
    }
  }, []);

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    const newMessage: Message = {
      ...message,
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      timestamp: new Date(),
      type: message.type || 'message'
    };
    setMessages(prev => {
      const updatedMessages = [...prev, newMessage];
      // Persist messages to localStorage
      if (typeof window !== 'undefined') {
        localStorage.setItem('chatMessages', JSON.stringify(updatedMessages));
      }
      return updatedMessages;
    });
  }, []);

  const clearMessages = useCallback(() => {
    const newSessionId = Date.now().toString();
    const defaultMessages = [
      {
        id: `session-${newSessionId}`,
        text: `🔄 New session started at ${new Date().toLocaleString()}`,
        sender: 'system' as const,
        timestamp: new Date(),
        type: 'session-start' as const
      },
      {
        id: '1',
        text: 'Hello! I\'m your AI agent. How can I help you today?',
        sender: 'agent' as const,
        timestamp: new Date(),
        type: 'message' as const
      },
    ];
    setMessages(defaultMessages);
    setCurrentSessionId(newSessionId);
    // Clear messages from localStorage and set new session ID
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatMessages', JSON.stringify(defaultMessages));
      localStorage.setItem('lastSessionId', newSessionId);
      localStorage.setItem('currentSessionId', newSessionId);
    }
  }, []);

  const startNewChat = useCallback(() => {
    const newSessionId = Date.now().toString();
    const defaultMessages = [
      {
        id: `session-${newSessionId}`,
        text: `🆕 New chat started at ${new Date().toLocaleString()}`,
        sender: 'system' as const,
        timestamp: new Date(),
        type: 'session-start' as const
      },
      {
        id: '1',
        text: 'Hello! I\'m your AI agent. How can I help you today?',
        sender: 'agent' as const,
        timestamp: new Date(),
        type: 'message' as const
      },
    ];
    setMessages(defaultMessages);
    setCurrentSessionId(newSessionId);
    // Update localStorage with new session
    if (typeof window !== 'undefined') {
      localStorage.setItem('chatMessages', JSON.stringify(defaultMessages));
      localStorage.setItem('lastSessionId', newSessionId);
      localStorage.setItem('currentSessionId', newSessionId);
    }
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
          session_id: currentSessionId
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
          const sourceNames = data.sources.map((source: string | { source?: string }) => 
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
  }, [addMessage, isLoading, currentSessionId]);

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
    openChat,
    closeChat,
    messages,
    addMessage,
    clearMessages,
    startNewChat,
    isLoading,
    setIsLoading,
    sendMessage,
    backendStatus,
    checkBackendStatus,
    currentSessionId,
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
