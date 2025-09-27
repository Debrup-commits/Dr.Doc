'use client';

import React, { useState, useRef, useEffect } from 'react';
import AskAgentButton from './AskAgentButton';

interface DocumentationBlockProps {
  children: React.ReactNode;
  className?: string;
  enableAskAgent?: boolean;
}

export default function DocumentationBlock({ 
  children, 
  className = '', 
  enableAskAgent = true 
}: DocumentationBlockProps) {
  const [isHovered, setIsHovered] = useState(false);
  const [extractedText, setExtractedText] = useState('');
  const blockRef = useRef<HTMLDivElement>(null);

  // Extract text content from the block
  useEffect(() => {
    if (blockRef.current && enableAskAgent) {
      // Extract text content, excluding the AskAgentButton itself
      const textContent = blockRef.current.innerText || blockRef.current.textContent || '';
      // Clean up the text (remove extra whitespace, limit length)
      const cleanedText = textContent
        .replace(/\s+/g, ' ')
        .trim()
        .substring(0, 500); // Limit to 500 characters to avoid overly long queries
      setExtractedText(cleanedText);
    }
  }, [children, enableAskAgent]);

  // Only show Ask Agent button if we have meaningful text content
  const shouldShowButton = enableAskAgent && 
    extractedText.length > 20 && // At least 20 characters
    !extractedText.includes('Ask Agent') && // Don't show on the button itself
    !extractedText.match(/^\s*$/) && // Not just whitespace
    !extractedText.match(/^[\d\s\-•]+$/); // Not just list markers or numbers

  return (
    <div
      ref={blockRef}
      className={`
        relative group
        ${className}
      `}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}
      
      {shouldShowButton && (
        <AskAgentButton 
          text={extractedText}
          className={`
            transition-all duration-200 ease-in-out
            ${isHovered ? 'opacity-100' : 'opacity-0'}
          `}
        />
      )}
    </div>
  );
}
