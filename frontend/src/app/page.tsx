import Link from 'next/link';
import { Bot, Zap, Globe } from 'lucide-react';

export default function Home() {
  const features = [
    {
      icon: Bot,
      title: 'Agentic',
      description: 'Works with AI Agents to bring new capabilities to your AI.',
    },
    {
      icon: Zap,
      title: 'Rapid Development',
      description: 'Go from concept to a working collaboration in minutes, not months',
    },
    {
      icon: Globe,
      title: 'Web3',
      description: 'Built by Fetch.ai and the ASI Alliance.',
    },
  ];

  return (
<<<<<<< HEAD
    <div className="min-h-screen bg-slate-900">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-slate-800 via-slate-900 to-slate-950 text-slate-100 py-20 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 via-transparent to-emerald-500/10"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-emerald-400 to-emerald-600 bg-clip-text text-transparent">
            ASI:One Agentic AI
          </h1>
          <p className="text-xl md:text-2xl mb-8 text-slate-300 max-w-3xl mx-auto">
=======
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl md:text-6xl font-bold mb-6">
            ASI:One Agentic AI
          </h1>
          <p className="text-xl md:text-2xl mb-8 opacity-90 max-w-3xl mx-auto">
>>>>>>> 1d392c7 (mcp crude implementation)
            Build your next AI Agent using ASI:One to enable communication and collaboration with AI Agents.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
<<<<<<< HEAD
              href="/documentation"
              className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-4 rounded-lg font-semibold transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/25"
            >
              Get Started
            </Link>
            <Link
              href="/api-reference"
              className="border-2 border-emerald-500 text-emerald-400 px-8 py-4 rounded-lg font-semibold hover:bg-emerald-500 hover:text-slate-900 transition-all duration-300"
            >
              API Reference
=======
              href="/chat"
              className="bg-white text-indigo-600 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg"
            >
              Start Chatting with Dr.Doc
            </Link>
            <Link
              href="/documentation"
              className="border-2 border-white text-white px-8 py-4 rounded-lg font-semibold hover:bg-white hover:text-indigo-600 transition-all duration-300"
            >
              Documentation
>>>>>>> 1d392c7 (mcp crude implementation)
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
<<<<<<< HEAD
      <section className="py-20 bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16 text-slate-100">
=======
      <section className="py-20 bg-gray-50 dark:bg-slate-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16 text-gray-900 dark:text-white">
>>>>>>> 1d392c7 (mcp crude implementation)
            Key Features
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
<<<<<<< HEAD
                className="bg-slate-700 p-8 rounded-xl shadow-lg hover:shadow-xl hover:shadow-emerald-500/10 transition-all duration-300 transform hover:-translate-y-2 text-center border border-slate-600/50"
              >
                <div className="w-16 h-16 bg-emerald-600 rounded-full flex items-center justify-center mx-auto mb-6">
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4 text-slate-100">
                  {feature.title}
                </h3>
                <p className="text-slate-300 leading-relaxed">
=======
                className="bg-white dark:bg-slate-700 p-8 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-2 text-center"
              >
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-6">
                  <feature.icon className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-4 text-gray-900 dark:text-white">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
>>>>>>> 1d392c7 (mcp crude implementation)
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
<<<<<<< HEAD
      <section className="py-20 bg-slate-900 text-slate-100 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/5 via-transparent to-emerald-500/5"></div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold mb-6 text-slate-100">
            Build Your Next AI Agent Now
          </h2>
          <p className="text-xl mb-8 text-slate-300 max-w-3xl mx-auto">
=======
      <section className="py-20 bg-slate-800 dark:bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            Build Your Next AI Agent Now
          </h2>
          <p className="text-xl mb-8 opacity-90 max-w-3xl mx-auto">
>>>>>>> 1d392c7 (mcp crude implementation)
            Connect your agent across multiple marketplaces and chat interfaces to get it collaborating today
          </p>
          <Link
            href="/documentation"
<<<<<<< HEAD
            className="bg-emerald-600 hover:bg-emerald-700 text-white px-8 py-4 rounded-lg font-semibold transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg hover:shadow-emerald-500/25 inline-block"
=======
            className="bg-white text-slate-800 px-8 py-4 rounded-lg font-semibold hover:bg-gray-100 transition-all duration-300 transform hover:-translate-y-1 hover:shadow-lg inline-block"
>>>>>>> 1d392c7 (mcp crude implementation)
          >
            Get Started
          </Link>
        </div>
      </section>
    </div>
  );
}
