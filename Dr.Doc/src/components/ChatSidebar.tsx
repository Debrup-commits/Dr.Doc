'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, X, Bot, User, Minimize2, Maximize2, Wifi, WifiOff, Loader2 } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useChat } from '@/contexts/ChatContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

export default function ChatSidebar() {
  const { theme } = useTheme();
  const { isChatOpen, toggleChat, openChat, messages, isLoading, sendMessage, clearMessages, backendStatus, checkBackendStatus } = useChat();
  const [inputText, setInputText] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isChatOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isChatOpen]);

  // Auto-open chat when clicking on citation links
  useEffect(() => {
    const handleLinkClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const link = target.closest('a');
      
      if (link && link.getAttribute('href')?.startsWith('/documentation')) {
        // Open chat when clicking on documentation links
        openChat();
      }
    };

    document.addEventListener('click', handleLinkClick);
    return () => document.removeEventListener('click', handleLinkClick);
  }, [openChat]);

  const handleSendMessage = async () => {
    if (!inputText.trim() || isLoading) return;

    const messageText = inputText.trim();
    setInputText('');
    await sendMessage(messageText);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!isChatOpen) {
    return (
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 bg-blue-600 hover:bg-blue-700 text-white p-4 rounded-full shadow-lg transition-all duration-300 transform hover:scale-110 z-50"
        aria-label="Open chat"
      >
        <MessageCircle size={24} />
      </button>
    );
  }

  return (
    <div className={`fixed right-0 top-0 h-full bg-white dark:bg-slate-800 shadow-2xl border-l border-gray-200 dark:border-slate-700 z-50 transition-all duration-300 chat-slide-in ${
      isMinimized ? 'w-16' : 'w-96'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-slate-700 bg-blue-600 text-white">
        <div className="flex items-center space-x-2">
          <Bot size={20} />
          {!isMinimized && (
            <div className="flex items-center space-x-2">
              <span className="font-semibold">AI Agent</span>
              <div className="flex items-center space-x-1">
                {backendStatus === 'connected' && <Wifi size={14} className="text-green-300" />}
                {backendStatus === 'disconnected' && <WifiOff size={14} className="text-red-300" />}
                {backendStatus === 'checking' && <Loader2 size={14} className="text-yellow-300 animate-spin" />}
                {!isMinimized && (
                  <span className="text-xs opacity-75">
                    {backendStatus === 'connected' && 'Connected'}
                    {backendStatus === 'disconnected' && 'Disconnected'}
                    {backendStatus === 'checking' && 'Checking...'}
                  </span>
                )}
              </div>
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2">
          {!isMinimized && backendStatus === 'disconnected' && (
            <button
              onClick={checkBackendStatus}
              className="p-1 hover:bg-blue-700 rounded transition-colors"
              aria-label="Retry connection"
              title="Retry connection to backend"
            >
              <Loader2 size={16} className="animate-spin" />
            </button>
          )}
          <button
            onClick={() => setIsMinimized(!isMinimized)}
            className="p-1 hover:bg-blue-700 rounded transition-colors"
            aria-label={isMinimized ? 'Expand chat' : 'Minimize chat'}
          >
            {isMinimized ? <Maximize2 size={16} /> : <Minimize2 size={16} />}
          </button>
          <button
            onClick={toggleChat}
            className="p-1 hover:bg-blue-700 rounded transition-colors"
            aria-label="Close chat"
          >
            <X size={16} />
          </button>
        </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 h-96">
            {messages.map((message) => {
              const isUser = message.sender === 'user';
              const isAgent = message.sender === 'agent';
              const isSystem = message.sender === 'system';
              const isSessionStart = message.type === 'session-start';
              
              // Special styling for session start messages
              if (isSystem && isSessionStart) {
                return (
                  <div key={message.id} className="flex justify-center mb-4 message-fade-in">
                    <div className="bg-blue-500/20 border border-blue-400/30 rounded-lg px-4 py-2 text-center">
                      <div className="flex items-center justify-center space-x-2">
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                        <span className="text-sm text-blue-600 dark:text-blue-300 font-medium">{message.text}</span>
                        <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
                      </div>
                    </div>
                  </div>
                );
              }
              
              return (
                <div
                  key={message.id}
                  className={`flex ${isUser ? 'justify-end' : 'justify-start'} message-fade-in`}
                >
                  <div
                    className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                      isUser
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-100 dark:bg-slate-700 text-gray-900 dark:text-gray-100'
                    }`}
                  >
                    <div className="flex items-start space-x-2">
                      {isAgent && (
                        <Bot size={16} className="mt-1 flex-shrink-0" />
                      )}
                      {isUser && (
                        <User size={16} className="mt-1 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <div className="text-sm prose prose-sm max-w-none dark:prose-invert">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeRaw]}
                            components={{
                              // Custom component overrides for styling
                              h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                              h2: ({ children }) => <h2 className="text-base font-semibold mb-2">{children}</h2>,
                              h3: ({ children }) => <h3 className="text-sm font-semibold mb-1">{children}</h3>,
                              p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                              ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                              ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                              li: ({ children }) => <li className="text-sm">{children}</li>,
                              code: ({ children }) => <code className="bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-xs font-mono">{children}</code>,
                              pre: ({ children }) => <pre className="bg-gray-100 dark:bg-gray-700 p-2 rounded text-xs font-mono overflow-x-auto mb-2">{children}</pre>,
                              blockquote: ({ children }) => <blockquote className="border-l-4 border-gray-300 dark:border-gray-600 pl-3 italic mb-2">{children}</blockquote>,
                              strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                              em: ({ children }) => <em className="italic">{children}</em>,
                            }}
                          >
                            {message.text}
                          </ReactMarkdown>
                        </div>
                        <p className="text-xs opacity-70 mt-1">
                          {message.timestamp.toLocaleTimeString([], { 
                            hour: '2-digit', 
                            minute: '2-digit' 
                          })}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-slate-700 text-gray-900 dark:text-gray-100 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <Bot size={16} />
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-indicator"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-indicator" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full typing-indicator" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 dark:border-slate-700">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={backendStatus === 'disconnected' ? 'Backend not connected...' : 'Type your message...'}
                className="flex-1 px-3 py-2 border border-gray-300 dark:border-slate-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-slate-700 text-gray-900 dark:text-gray-100"
                disabled={isLoading || backendStatus === 'disconnected'}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() || isLoading || backendStatus === 'disconnected'}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white p-2 rounded-lg transition-colors"
                aria-label="Send message"
              >
                <Send size={16} />
              </button>
            </div>
            <button
              onClick={clearMessages}
              className="mt-2 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            >
              Clear chat
            </button>
          </div>
        </>
      )}
    </div>
  );
}
