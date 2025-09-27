'use client';

import { useState } from 'react';
import { ChevronRight, Info, AlertTriangle, Code, Database, Zap } from 'lucide-react';

export default function ApiReference() {
  const [activeSection, setActiveSection] = useState('introduction');

  const sidebarItems = [
    {
      title: 'Authentication',
      items: [
        { id: 'introduction', label: 'Introduction' },
        { id: 'authentication', label: 'Authentication' },
        { id: 'base-url', label: 'Base URL' },
      ],
    },
    {
      title: 'Endpoints',
      items: [
        { id: 'chat-completions', label: 'Chat Completions' },
        { id: 'models', label: 'Models' },
        { id: 'embeddings', label: 'Embeddings' },
      ],
    },
    {
      title: 'Examples',
      items: [
        { id: 'python-example', label: 'Python Example' },
        { id: 'curl-example', label: 'cURL Example' },
        { id: 'javascript-example', label: 'JavaScript Example' },
      ],
    },
    {
      title: 'Error Handling',
      items: [
        { id: 'error-codes', label: 'Error Codes' },
        { id: 'rate-limits', label: 'Rate Limits' },
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
            ASI:One API Reference
          </h1>

          <section id="introduction" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Introduction
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              The ASI:One API provides programmatic access to our agentic AI models. Our API conforms to the OpenAI API specification, making it easy to integrate with existing OpenAI client libraries and tools.
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-6">
              <div className="flex items-start">
                <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-blue-800 dark:text-blue-200 font-semibold mb-2">OpenAI Compatibility</h4>
                  <p className="text-blue-700 dark:text-blue-300">
                    ASI:One's API is fully compatible with the OpenAI API specification, ensuring seamless integration with existing applications and tools.
                  </p>
                </div>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Key Features</h3>
            <ul className="space-y-2 text-gray-600 dark:text-gray-300">
              <li><strong>OpenAI Compatible:</strong> Drop-in replacement for OpenAI API</li>
              <li><strong>Agentic AI Optimized:</strong> Specialized for multi-agent interactions</li>
              <li><strong>Web3 Integration:</strong> Built for decentralized environments</li>
              <li><strong>High Performance:</strong> Optimized for speed and reliability</li>
            </ul>
          </section>

          <section id="authentication" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Authentication
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              All API requests require authentication using an API key. You can create API keys from your account dashboard.
            </p>
            
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Include your API key in the Authorization header of your requests:
            </p>
            
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto mb-6">
              Authorization: Bearer &lt;your-api-key&gt;
            </div>

            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6 mb-6">
              <div className="flex items-start">
                <AlertTriangle className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-yellow-800 dark:text-yellow-200 font-semibold mb-2">Security Note</h4>
                  <p className="text-yellow-700 dark:text-yellow-300">
                    Keep your API key secure and never expose it in client-side code. Store it in environment variables or secure configuration files.
                  </p>
                </div>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Getting Your API Key</h3>
            <ol className="list-decimal list-inside space-y-2 text-gray-600 dark:text-gray-300">
              <li>Sign up for an ASI:One account</li>
              <li>Navigate to the API Keys section in your dashboard</li>
              <li>Click "Generate New API Key"</li>
              <li>Copy and securely store your API key</li>
            </ol>
          </section>

          <section id="base-url" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Base URL
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              All API requests should be made to:
            </p>
            
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto mb-6">
              https://api.asi1.ai/v1/
            </div>

            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              All endpoints are relative to this base URL.
            </p>
          </section>

          <section id="chat-completions" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Chat Completions
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Create a completion for a chat conversation. This is the primary endpoint for interacting with ASI:One models.
            </p>
            
            <div className="bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-6 mb-6">
              <div className="flex items-center gap-4 mb-2">
                <span className="bg-green-600 text-white px-3 py-1 rounded text-sm font-bold">POST</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">/chat/completions</span>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Request Parameters</h3>
            <div className="overflow-x-auto mb-6">
              <table className="w-full border-collapse border border-gray-300 dark:border-gray-600">
                <thead>
                  <tr className="bg-gray-50 dark:bg-slate-800">
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Parameter</th>
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Type</th>
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Required</th>
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">model</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">string</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2"><span className="text-red-600 dark:text-red-400 font-semibold">Required</span></td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">The model to use for completion (e.g., "asi1-mini")</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">messages</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">array</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2"><span className="text-red-600 dark:text-red-400 font-semibold">Required</span></td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Array of message objects representing the conversation</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">max_tokens</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">integer</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2"><span className="text-green-600 dark:text-green-400">Optional</span></td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Maximum number of tokens to generate</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">temperature</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">number</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2"><span className="text-green-600 dark:text-green-400">Optional</span></td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Controls randomness (0.0 to 2.0, default: 1.0)</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Example Request</h3>
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto mb-6">
              <pre>{`curl -X POST "https://api.asi1.ai/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "asi1-mini",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful AI assistant specialized in agentic AI."
      },
      {
        "role": "user",
        "content": "How can I build a multi-agent system?"
      }
    ],
    "max_tokens": 500,
    "temperature": 0.7
  }'`}</pre>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Example Response</h3>
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto">
              <pre>{`{
  "id": "chatcmpl-123",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "asi1-mini",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "Building a multi-agent system involves several key components..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 150,
    "total_tokens": 175
  }
}`}</pre>
            </div>
          </section>

          <section id="models" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Models
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              List all available models that can be used with the API.
            </p>
            
            <div className="bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-6 mb-6">
              <div className="flex items-center gap-4 mb-2">
                <span className="bg-blue-600 text-white px-3 py-1 rounded text-sm font-bold">GET</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">/models</span>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Example Request</h3>
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto mb-6">
              <pre>{`curl -X GET "https://api.asi1.ai/v1/models" \\
  -H "Authorization: Bearer YOUR_API_KEY"`}</pre>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Example Response</h3>
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto">
              <pre>{`{
  "object": "list",
  "data": [
    {
      "id": "asi1-mini",
      "object": "model",
      "created": 1677610602,
      "owned_by": "asi-one"
    }
  ]
}`}</pre>
            </div>
          </section>

          <section id="embeddings" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Embeddings
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Generate embeddings for text using ASI:One models.
            </p>
            
            <div className="bg-gray-50 dark:bg-slate-800 border border-gray-200 dark:border-slate-700 rounded-lg p-6 mb-6">
              <div className="flex items-center gap-4 mb-2">
                <span className="bg-green-600 text-white px-3 py-1 rounded text-sm font-bold">POST</span>
                <span className="font-mono text-gray-700 dark:text-gray-300">/embeddings</span>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Request Parameters</h3>
            <div className="overflow-x-auto mb-6">
              <table className="w-full border-collapse border border-gray-300 dark:border-gray-600">
                <thead>
                  <tr className="bg-gray-50 dark:bg-slate-800">
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Parameter</th>
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Type</th>
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Required</th>
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">model</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">string</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2"><span className="text-red-600 dark:text-red-400 font-semibold">Required</span></td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">The embedding model to use</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">input</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">string/array</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2"><span className="text-red-600 dark:text-red-400 font-semibold">Required</span></td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Text or array of texts to embed</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <section id="python-example" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Python Example
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Here's how to use the ASI:One API with Python:
            </p>
            
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto">
              <pre>{`import openai

# Configure the client
openai.api_key = "your-api-key"
openai.api_base = "https://api.asi1.ai/v1"

# Make a chat completion request
response = openai.ChatCompletion.create(
    model="asi1-mini",
    messages=[
        {"role": "user", "content": "Hello, how can you help me?"}
    ],
    max_tokens=150
)

print(response.choices[0].message.content)`}</pre>
            </div>
          </section>

          <section id="curl-example" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              cURL Example
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Simple cURL request to test the API:
            </p>
            
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto">
              <pre>{`curl -X POST "https://api.asi1.ai/v1/chat/completions" \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "asi1-mini",
    "messages": [
      {"role": "user", "content": "What is agentic AI?"}
    ]
  }'`}</pre>
            </div>
          </section>

          <section id="javascript-example" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              JavaScript Example
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              Using the ASI:One API with JavaScript/Node.js:
            </p>
            
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto">
              <pre>{`const OpenAI = require('openai');

const openai = new OpenAI({
  apiKey: 'your-api-key',
  baseURL: 'https://api.asi1.ai/v1'
});

async function chatCompletion() {
  const completion = await openai.chat.completions.create({
    model: "asi1-mini",
    messages: [
      { role: "user", content: "Explain agentic AI in simple terms." }
    ],
    max_tokens: 200
  });

  console.log(completion.choices[0].message.content);
}

chatCompletion();`}</pre>
            </div>
          </section>

          <section id="error-codes" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Error Codes
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              The API uses standard HTTP status codes and returns detailed error information.
            </p>
            
            <div className="overflow-x-auto mb-6">
              <table className="w-full border-collapse border border-gray-300 dark:border-gray-600">
                <thead>
                  <tr className="bg-gray-50 dark:bg-slate-800">
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Status Code</th>
                    <th className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-left font-semibold text-gray-900 dark:text-white">Description</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">400</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Bad Request - Invalid parameters</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">401</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Unauthorized - Invalid API key</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">403</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Forbidden - Insufficient permissions</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">429</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Too Many Requests - Rate limit exceeded</td>
                  </tr>
                  <tr>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 font-mono text-sm">500</td>
                    <td className="border border-gray-300 dark:border-gray-600 px-4 py-2 text-gray-600 dark:text-gray-300">Internal Server Error</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Error Response Format</h3>
            <div className="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto">
              <pre>{`{
  "error": {
    "message": "Invalid API key",
    "type": "invalid_request_error",
    "code": "invalid_api_key"
  }
}`}</pre>
            </div>
          </section>

          <section id="rate-limits" className="mb-12">
            <h2 className="text-3xl font-semibold text-gray-900 dark:text-white mb-4">
              Rate Limits
            </h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed mb-6">
              API requests are subject to rate limits to ensure fair usage and system stability.
            </p>
            
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6 mb-6">
              <div className="flex items-start">
                <Info className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 mr-3 flex-shrink-0" />
                <div>
                  <h4 className="text-blue-800 dark:text-blue-200 font-semibold mb-2">Rate Limit Headers</h4>
                  <ul className="text-blue-700 dark:text-blue-300 space-y-1">
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded text-xs">X-RateLimit-Limit</code>: Maximum requests per minute</li>
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded text-xs">X-RateLimit-Remaining</code>: Remaining requests in current window</li>
                    <li><code className="bg-blue-100 dark:bg-blue-800 px-1 rounded text-xs">X-RateLimit-Reset</code>: Timestamp when the rate limit resets</li>
                  </ul>
                </div>
              </div>
            </div>

            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Default Limits</h3>
            <ul className="space-y-2 text-gray-600 dark:text-gray-300">
              <li><strong>Free Tier:</strong> 60 requests per minute</li>
              <li><strong>Pro Tier:</strong> 300 requests per minute</li>
              <li><strong>Enterprise:</strong> Custom limits available</li>
            </ul>
          </section>
        </div>
      </div>
    </div>
  );
}
