'use client';

import React from 'react';

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

export default function MarkdownRenderer({ content, className = '' }: MarkdownRendererProps) {
  // Simple markdown parser for basic formatting
  const parseMarkdown = (text: string) => {
    let html = text
      // Headers
      .replace(/^### (.*$)/gim, '<h3 class="text-xl font-semibold text-gray-900 dark:text-white mb-4">$1</h3>')
      .replace(/^## (.*$)/gim, '<h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-6">$1</h2>')
      .replace(/^# (.*$)/gim, '<h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-8">$1</h1>')
      
      // Code blocks
      .replace(/```([\s\S]*?)```/g, '<pre class="bg-gray-900 dark:bg-gray-800 text-gray-100 p-6 rounded-lg font-mono text-sm overflow-x-auto mb-6"><code>$1</code></pre>')
      
      // Inline code
      .replace(/`([^`]+)`/g, '<code class="bg-gray-100 dark:bg-gray-800 px-2 py-1 rounded text-sm font-mono text-red-600 dark:text-red-400">$1</code>')
      
      // Bold
      .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-gray-900 dark:text-white">$1</strong>')
      
      // Italic
      .replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
      
      // Lists
      .replace(/^\* (.*$)/gim, '<li class="ml-4 mb-2">• $1</li>')
      .replace(/^- (.*$)/gim, '<li class="ml-4 mb-2">• $1</li>')
      
      // Links
      .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" class="text-blue-600 dark:text-blue-400 hover:underline" target="_blank" rel="noopener noreferrer">$1</a>')
      
      // Line breaks
      .replace(/\n\n/g, '</p><p class="mb-4 text-gray-600 dark:text-gray-300 leading-relaxed">')
      .replace(/\n/g, '<br>');

    // Wrap in paragraph tags
    html = `<p class="mb-4 text-gray-600 dark:text-gray-300 leading-relaxed">${html}</p>`;
    
    // Clean up empty paragraphs
    html = html.replace(/<p class="mb-4 text-gray-600 dark:text-gray-300 leading-relaxed"><\/p>/g, '');
    
    return html;
  };

  return (
    <div 
      className={`prose prose-lg max-w-none ${className}`}
      dangerouslySetInnerHTML={{ __html: parseMarkdown(content) }}
    />
  );
}
