'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ChevronRight, Info, AlertTriangle } from 'lucide-react';
import { useChat } from '@/contexts/ChatContext';
import DocumentationBlock from '@/components/DocumentationBlock';

export default function Documentation() {
  const [activeSection, setActiveSection] = useState('welcome');
  const { openChat } = useChat();

  const sidebarItems = [
    {
      title: 'Getting Started',
      items: [
        { id: 'welcome', label: 'Welcome' },
        { id: 'what-is-asi-one', label: 'What is ASI:One?' },
        { id: 'key-features', label: 'Key Features' },
        { id: 'getting-started', label: 'Getting Started' },
        { id: 'current-model', label: 'Current Model' },
      ],
    },
    {
      title: 'API Integration',
      items: [
        { id: 'api-key', label: 'How to Get an API Key' },
        { id: 'openai-compatibility', label: 'OpenAI Compatibility' },
        { id: 'chat-completion', label: 'Chat Completion Example' },
      ],
    },
    {
      title: 'Wallet Integration',
      items: [
        { id: 'link-account', label: 'Link Account' },
        { id: 'agent-chat-protocol', label: 'Agent Chat Protocol' },
      ],
    },
  ];

  const scrollToSection = (sectionId: string) => {
    setActiveSection(sectionId);
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  };

  // Auto-open chat when navigating to documentation
  useEffect(() => {
    // Check if we should keep chat open (e.g., when navigating from citations)
    const keepOpen = localStorage.getItem('keepChatOpen') === 'true';
    if (keepOpen) {
      openChat();
      // Clean up the flag after opening chat
      localStorage.removeItem('keepChatOpen');
    } else {
      // Only auto-open if chat was previously open
      const chatWasOpen = localStorage.getItem('chatOpen') === 'true';
      if (chatWasOpen) {
    openChat();
      }
    }
  }, [openChat]);

  return (
    <div className="min-h-screen bg-white dark:bg-slate-900">
      <div className="flex flex-col lg:flex-row">
        {/* Sidebar */}
        <aside className="w-full lg:w-64 bg-gray-50 dark:bg-slate-800 border-r border-gray-200 dark:border-slate-700 lg:min-h-screen lg:sticky lg:top-20">
          <div className="p-6">
            {sidebarItems.map((section) => (
              <div key={section.title} className="mb-8">
                <h3 className="text-sm font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-4">
                  {section.title}
                </h3>
                <ul className="space-y-2">
                  {section.items.map((item) => (
                    <li key={item.id}>
                      <button
                        onClick={() => scrollToSection(item.id)}
                        className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors duration-200 flex items-center ${
                          activeSection === item.id
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 border-l-4 border-blue-500'
                            : 'text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-slate-700'
                        }`}
                      >
                        <ChevronRight className="w-4 h-4 mr-2" />
                        {item.label}
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </aside>

        {/* Main Content */}
        <div className="flex-1 p-4 lg:p-8 max-w-4xl">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-8">
            ASI:One Documentation
          </h1>

          <section id="welcome" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Welcome to ASI:One Documentation
            </h2>
            <DocumentationBlock>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              ASI:One is an advanced AI platform designed to enable seamless communication and collaboration between AI agents in decentralized environments. Built by Fetch.ai and the ASI Alliance, it provides powerful tools for building and deploying agentic AI systems.
            </p>
            </DocumentationBlock>
          </section>

          <section id="what-is-asi-one" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              What is ASI:One?
            </h2>
            <DocumentationBlock>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              ASI:One is an LLM optimized for agentic AI within decentralized environments, integrating with the ASI wallet powered by the FET token. It provides a comprehensive platform for building, deploying, and managing AI agents that can communicate and collaborate effectively.
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-6">
              <div className="flex items-start">
                <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-blue-800 dark:text-blue-200 font-semibold mb-2">Key Characteristics</h4>
                  <ul className="text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• Optimized for agentic AI interactions</li>
                    <li>• Decentralized environment support</li>
                    <li>• ASI wallet integration</li>
                    <li>• FET token powered</li>
                  </ul>
                </div>
              </div>
            </div>
            </DocumentationBlock>
          </section>

          <section id="key-features" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-6">
              Key Features
            </h2>
            
            <div className="space-y-6">
              <DocumentationBlock>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Agentic Reasoning
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  ASI:One is specifically designed for agentic AI, enabling sophisticated reasoning and decision-making capabilities that allow AI agents to operate autonomously and make intelligent choices in complex environments.
                </p>
              </div>
              </DocumentationBlock>

              <DocumentationBlock>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Natural Language Understanding
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  Advanced natural language processing capabilities enable seamless communication between AI agents and human users, supporting complex conversations and context-aware interactions.
                </p>
              </div>
              </DocumentationBlock>

              <DocumentationBlock>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Multi-Step Task Execution
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  ASI:One can break down complex tasks into manageable steps, execute them systematically, and coordinate multiple operations to achieve desired outcomes efficiently.
                </p>
              </div>
              </DocumentationBlock>

              <DocumentationBlock>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  Contextual Memory
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  Maintains context across interactions, allowing AI agents to remember previous conversations, learn from past experiences, and provide more personalized and relevant responses.
                </p>
              </div>
              </DocumentationBlock>

              <DocumentationBlock>
              <div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  API-Driven Integration
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  RESTful API architecture makes it easy to integrate ASI:One into existing systems, applications, and workflows, providing flexible deployment options.
                </p>
              </div>
              </DocumentationBlock>
            </div>
          </section>

          <section id="getting-started" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Getting Started
            </h2>
            <DocumentationBlock>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              To begin using ASI:One, you&apos;ll need to sign up and obtain an API key. Follow these simple steps:
            </p>
            
            <ol className="list-decimal list-inside space-y-2 text-gray-600 dark:text-gray-300 mb-6">
              <li>Visit the <Link href="/login" className="text-blue-600 dark:text-blue-400 hover:underline">login page</Link> to create your account</li>
              <li>Verify your email address</li>
              <li>Generate your API key from the dashboard</li>
              <li>Start building with our API</li>
            </ol>

            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
              <div className="flex items-start">
                <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-yellow-800 dark:text-yellow-200 font-semibold mb-2">Important</h4>
                  <p className="text-yellow-700 dark:text-yellow-300">
                    Make sure to keep your API key secure and never share it publicly. Store it in environment variables or secure configuration files.
                  </p>
                </div>
              </div>
            </div>
            </DocumentationBlock>
          </section>

          <section id="current-model" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Current Model
            </h2>
            <DocumentationBlock>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              The current available model is <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm">asi1-mini</code>, which provides excellent performance for most agentic AI tasks while maintaining cost efficiency.
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
              <div className="flex items-start">
                <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-blue-800 dark:text-blue-200 font-semibold mb-2">Model Specifications</h4>
                  <ul className="text-blue-700 dark:text-blue-300 space-y-1">
                    <li><strong>Model Name:</strong> asi1-mini</li>
                    <li><strong>Type:</strong> Agentic AI Optimized</li>
                    <li><strong>Context Window:</strong> Large context support</li>
                    <li><strong>Specialization:</strong> Multi-agent collaboration</li>
                  </ul>
                </div>
              </div>
            </div>
            </DocumentationBlock>
          </section>

          <section id="api-key" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              How to Get an API Key
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Creating an API key is straightforward through the ASI1 dashboard:
            </p>
            
            <ol className="list-decimal list-inside space-y-2 text-gray-600 dark:text-gray-300 mb-6">
              <li>Log into your ASI:One account</li>
              <li>Navigate to the API Keys section in your dashboard</li>
              <li>Click &quot;Generate New API Key&quot;</li>
              <li>Copy and securely store your new API key</li>
              <li>Use the key in your API requests with the Authorization header</li>
            </ol>

            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto">
              Authorization: Bearer &lt;your-api-key&gt;
            </div>
          </section>

          <section id="openai-compatibility" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              OpenAI Compatibility
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              ASI:One&apos;s API conforms to the OpenAI API specification, making it easy to integrate with existing OpenAI client libraries and tools. This compatibility ensures seamless migration and familiar development experience.
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
              <div className="flex items-start">
                <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-blue-800 dark:text-blue-200 font-semibold mb-2">Compatible Features</h4>
                  <ul className="text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• Chat Completion API</li>
                    <li>• Standard request/response formats</li>
                    <li>• OpenAI client library support</li>
                    <li>• Familiar parameter structures</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          <section id="chat-completion" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Chat Completion Example
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Here&apos;s a simple example of how to obtain a chat completion using the <code className="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm">asi1-mini</code> model:
            </p>
            
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto mb-6">
              <pre>{`curl -X POST "https://api.asi1.ai/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "asi1-mini",
    "messages": [
      {
        "role": "user",
        "content": "Hello, how can you help me build an AI agent?"
      }
    ],
    "max_tokens": 150
  }'`}</pre>
            </div>

            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              This will return a response in the standard OpenAI format, making it easy to integrate with your existing applications.
            </p>
          </section>

          <section id="link-account" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Link Account
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              To unlock additional features and capabilities, you can link your ASI or Ethereum wallet to your ASI:One account. This enables:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-gray-600 dark:text-gray-300 mb-6">
              <li>Enhanced security features</li>
              <li>Access to premium models</li>
              <li>Decentralized identity verification</li>
              <li>Integration with Web3 ecosystems</li>
            </ul>

            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
              <div className="flex items-start">
                <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-blue-800 dark:text-blue-200 font-semibold mb-2">Supported Wallets</h4>
                  <ul className="text-blue-700 dark:text-blue-300 space-y-1">
                    <li>• ASI Wallet</li>
                    <li>• Ethereum-compatible wallets (MetaMask, WalletConnect, etc.)</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          <section id="agent-chat-protocol" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Agent Chat Protocol
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              The Agent Chat Protocol enables AI agents to understand natural language and interoperate across different ecosystems. This protocol provides:
            </p>
            
            <ul className="list-disc list-inside space-y-2 text-gray-600 dark:text-gray-300 mb-6">
              <li><strong>Standardized Communication:</strong> Common language for agent interactions</li>
              <li><strong>Cross-Platform Compatibility:</strong> Agents can communicate regardless of their platform</li>
              <li><strong>Rich Context Support:</strong> Complex information exchange between agents</li>
              <li><strong>Protocol Extensions:</strong> Customizable for specific use cases</li>
            </ul>

            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
              <div className="flex items-start">
                <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-yellow-800 dark:text-yellow-200 font-semibold mb-2">Protocol Benefits</h4>
                  <p className="text-yellow-700 dark:text-yellow-300">
                    This protocol is essential for building multi-agent systems that can collaborate effectively across different platforms and ecosystems.
                  </p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
