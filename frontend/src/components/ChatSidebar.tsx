'use client';

import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, X, Bot, User, Minimize2, Maximize2, Loader2, Plus, Copy, Check, ChevronDown, ChevronRight } from 'lucide-react';
import { useChat } from '@/contexts/ChatContext';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

export default function ChatSidebar() {
  const { isChatOpen, toggleChat, openChat, messages, isLoading, sendMessage, clearMessages, startNewChat, backendStatus, checkBackendStatus } = useChat();
  const [inputText, setInputText] = useState('');
  const [isMinimized, setIsMinimized] = useState(false);
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
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

  // Clean up navigation flags when chat is manually closed
  useEffect(() => {
    if (!isChatOpen) {
      // Only clean up if chat was manually closed (not due to navigation)
      const wasNavigating = localStorage.getItem('navigatingToDocs') === 'true';
      if (!wasNavigating) {
        localStorage.removeItem('keepChatOpen');
        localStorage.removeItem('navigatingToDocs');
      }
    }
  }, [isChatOpen]);

  // Auto-open chat when clicking on citation links and prevent chat from closing
  useEffect(() => {
    const handleLinkClick = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      const link = target.closest('a');
      
      if (link && link.getAttribute('href')?.startsWith('/documentation')) {
        // Ensure chat stays open when clicking on documentation links
        openChat();
        
        // Store that we're navigating to documentation to keep chat open
        localStorage.setItem('keepChatOpen', 'true');
        localStorage.setItem('navigatingToDocs', 'true');
      }
    };

    // Handle navigation events to keep chat open
    const handleBeforeUnload = () => {
      if (localStorage.getItem('navigatingToDocs') === 'true') {
        localStorage.setItem('keepChatOpen', 'true');
      }
    };

    // Handle page load to restore chat state
    const handlePageLoad = () => {
      if (localStorage.getItem('keepChatOpen') === 'true') {
        openChat();
        localStorage.removeItem('keepChatOpen');
        localStorage.removeItem('navigatingToDocs');
      }
    };

    document.addEventListener('click', handleLinkClick);
    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('load', handlePageLoad);
    
    return () => {
      document.removeEventListener('click', handleLinkClick);
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('load', handlePageLoad);
    };
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

  const copyToClipboard = async (text: string, codeId: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedCode(codeId);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const toggleSection = (sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  };

  if (!isChatOpen) {
    return (
      <button
        onClick={toggleChat}
        className="fixed bottom-8 right-8 bg-gradient-to-br from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 text-white p-5 rounded-2xl shadow-2xl transition-all duration-300 z-50"
        aria-label="Open chat"
      >
        <div className="relative">
          <MessageCircle size={26} className="drop-shadow-sm" />
          <div className="absolute -top-1 -right-1 w-4 h-4 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
        </div>
      </button>
    );
  }

  return (
    <div className={`fixed right-0 top-0 h-full bg-slate-900/95 backdrop-blur-xl shadow-2xl border-l border-slate-700/30 z-50 transition-all duration-500 ease-out chat-slide-in flex flex-col ${
      isMinimized ? 'w-16' : 'w-[600px]'
    }`}>
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700/30 bg-gradient-to-r from-slate-800/90 to-slate-700/90 backdrop-blur-xl">
        <div className="flex items-center space-x-3">
          <div className="relative">
            <div className="p-2.5 bg-gradient-to-br from-emerald-500/20 to-emerald-600/30 rounded-xl shadow-lg">
              <Bot size={20} className="text-emerald-400 drop-shadow-sm" />
            </div>
            <div className="absolute -top-1 -right-1 w-3 h-3 bg-emerald-500 rounded-full animate-pulse shadow-lg shadow-emerald-500/50"></div>
          </div>
          {!isMinimized && (
            <div className="flex items-center space-x-3">
              <div className="flex flex-col">
                <span className="font-bold text-white text-lg tracking-tight">Dr.Doc Agent</span>
                <div className="flex items-center space-x-2">
                  {backendStatus === 'connected' && (
                    <>
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                      <span className="text-xs text-emerald-400 font-medium">Online</span>
                    </>
                  )}
                  {backendStatus === 'disconnected' && (
                    <>
                      <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                      <span className="text-xs text-red-400 font-medium">Offline</span>
                    </>
                  )}
                  {backendStatus === 'checking' && (
                    <>
                      <Loader2 size={12} className="text-amber-400 animate-spin" />
                      <span className="text-xs text-amber-400 font-medium">Connecting...</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
                <div className="flex items-center space-x-1">
                  {!isMinimized && (
                    <button
                      onClick={startNewChat}
                      className="p-2.5 hover:bg-emerald-500/20 rounded-xl transition-all duration-300"
                      aria-label="Start new chat"
                      title="Start a new chat session"
                    >
                      <Plus size={16} className="text-emerald-400" />
                    </button>
                  )}
                  {!isMinimized && backendStatus === 'disconnected' && (
                    <button
                      onClick={checkBackendStatus}
                      className="p-2.5 hover:bg-slate-700/50 rounded-xl transition-all duration-300"
                      aria-label="Retry connection"
                      title="Retry connection to backend"
                    >
                      <Loader2 size={16} className="animate-spin text-amber-400" />
                    </button>
                  )}
                  <button
                    onClick={() => setIsMinimized(!isMinimized)}
                    className="p-2.5 hover:bg-slate-700/50 rounded-xl transition-all duration-300"
                    aria-label={isMinimized ? 'Expand chat' : 'Minimize chat'}
                  >
                    {isMinimized ? <Maximize2 size={16} className="text-slate-300" /> : <Minimize2 size={16} className="text-slate-300" />}
                  </button>
                  <button
                    onClick={toggleChat}
                    className="p-2.5 hover:bg-red-500/20 rounded-xl transition-all duration-300"
                    aria-label="Close chat"
                  >
                    <X size={16} className="text-slate-300" />
                  </button>
                </div>
      </div>

      {!isMinimized && (
        <>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-600 scrollbar-track-transparent" style={{ wordWrap: 'break-word', overflowWrap: 'break-word' }}>
            {messages.map((message) => {
              const isUser = message.sender === 'user';
              const isAgent = message.sender === 'agent';
              const isSystem = message.sender === 'system';
              const isSessionStart = message.type === 'session-start';
              
              // Special styling for session start messages
              if (isSystem && isSessionStart) {
                return (
                  <div key={message.id} className="flex justify-center mb-6 message-fade-in">
                    <div className="bg-gradient-to-r from-emerald-500/10 to-emerald-600/10 border border-emerald-400/30 rounded-2xl px-6 py-4 text-center backdrop-blur-sm shadow-lg shadow-emerald-500/10">
                      <div className="flex items-center justify-center space-x-3">
                        <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
                        <span className="text-sm text-emerald-300 font-semibold tracking-wide">{message.text}</span>
                        <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse shadow-lg shadow-emerald-400/50"></div>
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
                            className={`max-w-md lg:max-w-xl px-6 py-5 rounded-3xl ${
                              isUser
                                ? 'bg-gradient-to-br from-emerald-600/90 to-emerald-700/90 text-white border border-emerald-500/30 shadow-xl'
                                : 'bg-slate-800/70 text-slate-100 border border-slate-700/40 shadow-lg backdrop-blur-sm'
                            }`}
                            style={{ wordWrap: 'break-word', overflowWrap: 'break-word' }}
                          >
                            <div className="flex items-start space-x-3">
                              {isAgent && (
                                <div className="p-2.5 bg-gradient-to-br from-emerald-500/20 to-emerald-600/30 rounded-xl mt-0.5 shadow-sm">
                                  <Bot size={16} className="text-emerald-400 drop-shadow-sm" />
                                </div>
                              )}
                              {isUser && (
                                <div className="p-2.5 bg-white/20 rounded-xl mt-0.5 shadow-sm">
                                  <User size={16} className="text-white drop-shadow-sm" />
                                </div>
                              )}
                      <div className="flex-1 min-w-0">
                        <div className="text-sm leading-relaxed break-words overflow-hidden chat-message">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            rehypePlugins={[rehypeRaw]}
                            components={{
                              // Custom component overrides for styling
                              h1: ({ children }) => <h1 className={`text-xl font-bold mb-5 border-b pb-3 mt-0 break-words ${isUser ? 'text-white border-white/30' : 'text-white border-slate-600/50'}`}>{children}</h1>,
                              h2: ({ children }) => <h2 className={`text-lg font-semibold mb-4 mt-5 first:mt-0 break-words ${isUser ? 'text-white' : 'text-white'}`}>{children}</h2>,
                              h3: ({ children }) => {
                                const sectionId = `section-${Math.random().toString(36).substr(2, 9)}`;
                                const isExpanded = expandedSections.has(sectionId);
                                const isCollapsible = typeof children === 'string' && (
                                  children.includes('Code Example') || 
                                  children.includes('Request') || 
                                  children.includes('Response') ||
                                  children.includes('Example')
                                );
                                
                                return (
                                  <div className="mb-3 mt-4">
                                    <button
                                      onClick={() => isCollapsible && toggleSection(sectionId)}
                                      className={`flex items-center space-x-2 text-base font-semibold break-words transition-colors ${
                                        isUser ? 'text-emerald-200 hover:text-emerald-100' : 'text-emerald-300 hover:text-emerald-200'
                                      } ${isCollapsible ? 'cursor-pointer' : ''}`}
                                    >
                                      {isCollapsible && (
                                        isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />
                                      )}
                                      <span>{children}</span>
                                    </button>
                                  </div>
                                );
                              },
                              h4: ({ children }) => <h4 className={`text-sm font-medium mb-3 mt-3 break-words ${isUser ? 'text-emerald-100' : 'text-emerald-200'}`}>{children}</h4>,
                              p: ({ children }) => <p className={`mb-4 last:mb-0 leading-relaxed text-sm break-words ${isUser ? 'text-white/90' : 'text-slate-200'}`}>{children}</p>,
                              ul: ({ children }) => <ul className={`list-disc list-inside mb-5 space-y-2 ml-4 break-words ${isUser ? 'text-white/90' : 'text-slate-200'}`}>{children}</ul>,
                              ol: ({ children }) => <ol className={`list-decimal list-inside mb-5 space-y-2 ml-4 break-words ${isUser ? 'text-white/90' : 'text-slate-200'}`}>{children}</ol>,
                              li: ({ children }) => <li className={`text-sm leading-relaxed break-words ${isUser ? 'text-white/90' : 'text-slate-200'}`}>{children}</li>,
                              code: ({ children }) => <code className={`px-2 py-1 rounded text-xs font-mono border break-all ${isUser ? 'bg-white/20 text-emerald-200 border-white/30' : 'bg-slate-700/60 text-emerald-300 border-slate-600/30'}`}>{children}</code>,
                              pre: ({ children }) => {
                                const codeId = `code-${Math.random().toString(36).substr(2, 9)}`;
                                const codeText = typeof children === 'string' ? children : children?.toString() || '';
                                return (
                                  <div className="relative group mb-5">
                                    <pre className={`p-4 pr-12 rounded-lg text-xs font-mono overflow-x-auto border shadow-inner whitespace-pre-wrap break-words ${isUser ? 'bg-white/10 text-white/90 border-white/20' : 'bg-slate-800/90 text-slate-200 border-slate-700/50'}`}>
                                      {children}
                                    </pre>
                                    <button
                                      onClick={() => copyToClipboard(codeText, codeId)}
                                      className={`absolute top-3 right-3 p-2 rounded-md transition-all duration-200 opacity-0 group-hover:opacity-100 ${
                                        isUser 
                                          ? 'bg-white/20 hover:bg-white/30 text-white' 
                                          : 'bg-slate-700/60 hover:bg-slate-600/80 text-slate-200'
                                      }`}
                                      title={copiedCode === codeId ? "Copied!" : "Copy code"}
                                    >
                                      {copiedCode === codeId ? (
                                        <Check size={14} className="text-green-500" />
                                      ) : (
                                        <Copy size={14} />
                                      )}
                                    </button>
                                  </div>
                                );
                              },
                              blockquote: ({ children }) => <blockquote className={`border-l-4 pl-4 italic mb-5 py-3 rounded-r break-words ${isUser ? 'border-emerald-300 text-white/80 bg-white/10' : 'border-emerald-400/60 text-slate-300 bg-slate-800/30'}`}>{children}</blockquote>,
                              strong: ({ children }) => <strong className={`font-semibold break-words ${isUser ? 'text-white' : 'text-white'}`}>{children}</strong>,
                              em: ({ children }) => <em className={`italic break-words ${isUser ? 'text-white/80' : 'text-slate-300'}`}>{children}</em>,
                              a: ({ children, href }) => <a href={href} className={`underline transition-colors font-medium break-words ${isUser ? 'text-emerald-200 hover:text-emerald-100 decoration-emerald-200/50 hover:decoration-emerald-100' : 'text-emerald-400 hover:text-emerald-300 decoration-emerald-400/50 hover:decoration-emerald-300'}`}>{children}</a>,
                              table: ({ children }) => <div className="overflow-x-auto mb-5"><table className={`min-w-full border rounded-lg overflow-hidden ${isUser ? 'border-white/30' : 'border-slate-600/50'}`}>{children}</table></div>,
                              thead: ({ children }) => <thead className={isUser ? 'bg-white/10' : 'bg-slate-800/50'}>{children}</thead>,
                              tbody: ({ children }) => <tbody className={isUser ? 'bg-white/5' : 'bg-slate-800/20'}>{children}</tbody>,
                              tr: ({ children }) => <tr className={isUser ? 'border-b border-white/20' : 'border-b border-slate-600/30'}>{children}</tr>,
                              th: ({ children }) => <th className={`px-3 py-2 text-left text-xs font-semibold uppercase tracking-wider break-words ${isUser ? 'text-white/90' : 'text-slate-200'}`}>{children}</th>,
                              td: ({ children }) => <td className={`px-3 py-2 text-sm break-words ${isUser ? 'text-white/90' : 'text-slate-200'}`}>{children}</td>,
                              hr: () => <hr className={`my-5 ${isUser ? 'border-white/30' : 'border-slate-600/50'}`} />,
                            }}
                          >
                            {message.text}
                          </ReactMarkdown>
                        </div>
                                <p className={`text-xs mt-4 font-medium opacity-70 ${isUser ? 'text-white/60' : 'text-slate-400'}`}>
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
              <div className="flex justify-start message-fade-in">
                <div className="bg-slate-800/70 text-slate-100 px-5 py-4 rounded-2xl border border-slate-700/40 backdrop-blur-sm shadow-lg">
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-gradient-to-br from-emerald-500/20 to-emerald-600/30 rounded-xl shadow-sm">
                      <Bot size={14} className="text-emerald-400 drop-shadow-sm" />
                    </div>
                    <div className="flex space-x-1.5">
                      <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full typing-indicator shadow-lg shadow-emerald-400/30"></div>
                      <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full typing-indicator shadow-lg shadow-emerald-400/30" style={{ animationDelay: '0.2s' }}></div>
                      <div className="w-2.5 h-2.5 bg-emerald-400 rounded-full typing-indicator shadow-lg shadow-emerald-400/30" style={{ animationDelay: '0.4s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="px-4 py-6 border-t border-slate-700/30 bg-gradient-to-r from-slate-800/90 to-slate-700/90 backdrop-blur-xl mt-auto" style={{ wordWrap: 'break-word', overflowWrap: 'break-word' }}>
            <div className="flex space-x-3">
              <div className="flex-1 relative">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={backendStatus === 'disconnected' ? 'Backend not connected...' : 'Ask Dr.Doc anything...'}
                  className="w-full px-5 py-4 border border-slate-600/40 rounded-2xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500/50 bg-slate-700/60 text-slate-100 placeholder-slate-400 backdrop-blur-sm transition-all duration-300 break-words"
                  disabled={isLoading || backendStatus === 'disconnected'}
                />
                <div className="absolute inset-y-0 right-0 flex items-center pr-4">
                  <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse opacity-50"></div>
                </div>
              </div>
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() || isLoading || backendStatus === 'disconnected'}
                className="bg-gradient-to-br from-emerald-600 to-emerald-700 hover:from-emerald-500 hover:to-emerald-600 disabled:from-slate-600 disabled:to-slate-700 disabled:cursor-not-allowed text-white p-4 rounded-2xl transition-all duration-300 shadow-lg"
                aria-label="Send message"
              >
                <Send size={18} className="drop-shadow-sm" />
              </button>
            </div>
                    <div className="mt-4 flex space-x-4">
                      <button
                        onClick={startNewChat}
                        className="text-xs text-emerald-400 hover:text-emerald-300 transition-colors font-medium flex items-center space-x-1"
                      >
                        <Plus size={12} />
                        <span>New Chat</span>
                      </button>
                      <button
                        onClick={clearMessages}
                        className="text-xs text-slate-400 hover:text-slate-300 transition-colors font-medium"
                      >
                        Clear conversation
                      </button>
                    </div>
          </div>
        </>
      )}
    </div>
  );
}
