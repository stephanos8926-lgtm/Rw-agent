import React, { useState, useEffect } from 'react';
import Markdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import rehypeRaw from 'rehype-raw';
import 'highlight.js/styles/github-dark.css';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface TypewriterMarkdownProps {
  content: string;
  speed?: number;
  className?: string;
}

export const TypewriterMarkdown: React.FC<TypewriterMarkdownProps> = ({ 
  content, 
  speed = 5,
  className 
}) => {
  const [displayedContent, setDisplayedContent] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (content.length <= displayedContent.length) {
      if (content !== displayedContent) {
        setDisplayedContent(content);
      }
      setIsComplete(true);
      return;
    }

    const timer = setTimeout(() => {
      // Chunking for speed if it's very long
      const nextChunk = content.slice(0, displayedContent.length + 5); 
      setDisplayedContent(nextChunk);
    }, speed);

    return () => clearTimeout(timer);
  }, [content, displayedContent, speed]);

  return (
    <div className={cn("markdown-body font-sans text-[13px] sm:text-sm leading-relaxed", className)}>
      <Markdown 
        rehypePlugins={[rehypeHighlight, rehypeRaw]}
        components={{
          code({ node, inline, className, children, ...props }: any) {
            const match = /language-(\w+)/.exec(className || '');
            return !inline && match ? (
              <pre className={cn("rounded-xl bg-slate-950 p-4 border border-slate-800 my-4 overflow-x-auto custom-scrollbar font-mono", className)}>
                <code {...props} className={cn("text-[12px] text-cyan-50", className)}>
                  {children}
                </code>
              </pre>
            ) : (
              <code {...props} className={cn("bg-slate-800 px-1.5 py-0.5 rounded text-cyan-400 font-mono text-[0.95em]", className)}>
                {children}
              </code>
            );
          },
          p: ({children}) => <p className="mb-4 last:mb-0">{children}</p>,
          ul: ({children}) => <ul className="list-disc pl-5 mb-4 space-y-1.5">{children}</ul>,
          ol: ({children}) => <ol className="list-decimal pl-5 mb-4 space-y-1.5">{children}</ol>,
          h1: ({children}) => <h1 className="text-lg font-bold mb-4 text-white border-b border-slate-800 pb-2">{children}</h1>,
          h2: ({children}) => <h2 className="text-md font-bold mb-3 text-slate-100 uppercase tracking-tight">{children}</h2>,
          h3: ({children}) => <h3 className="text-sm font-bold mb-2 text-slate-200">{children}</h3>,
          blockquote: ({children}) => <blockquote className="border-l-2 border-cyan-500 pl-4 py-1 italic bg-cyan-500/5 mb-4 rounded-r">{children}</blockquote>,
        }}
      >
        {displayedContent}
      </Markdown>
      {!isComplete && (
        <span className="inline-block w-2 h-4 ml-1 bg-cyan-500 animate-pulse align-middle" />
      )}
    </div>
  );
};
