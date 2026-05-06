import React, { useEffect, useRef, useState } from 'react';
import { Terminal, Copy, Maximize2, ArrowDown } from 'lucide-react';

interface MiniTerminalProps {
  content: string;
  onExpand: () => void;
}

export const MiniTerminal: React.FC<MiniTerminalProps> = ({ content, onExpand }) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  // Auto-scroll to bottom effect
  useEffect(() => {
    if (autoScroll && scrollContainerRef.current) {
        scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
  }, [content, autoScroll]);

  const handleCopy = () => {
    navigator.clipboard.writeText(content);
  };

  const handleScroll = () => {
    if (scrollContainerRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
        // Check if user is at the bottom (within 50px buffer)
        setAutoScroll(scrollHeight - scrollTop - clientHeight < 50);
    }
  };

  return (
    <div className="bg-slate-950 border border-slate-800 rounded-lg overflow-hidden flex flex-col font-mono text-xs w-full max-w-2xl">
      <div className="flex items-center justify-between px-3 py-2 bg-slate-900 border-b border-slate-800">
        <div className="flex items-center gap-2 text-slate-400">
          <Terminal size={12} />
          <span>Output</span>
        </div>
        <div className="flex items-center gap-2">
          <button onClick={handleCopy} className="p-1 hover:text-white text-slate-500" title="Copy to clipboard">
            <Copy size={12} />
          </button>
          <button onClick={onExpand} className="p-1 hover:text-white text-slate-500" title="Full Terminal">
            <Maximize2 size={12} />
          </button>
        </div>
      </div>
      <div 
        ref={scrollContainerRef}
        onScroll={handleScroll}
        className="p-3 overflow-y-auto max-h-64 custom-scrollbar text-slate-300 whitespace-pre-wrap break-all"
      >
        {content}
      </div>
      {!autoScroll && (
          <button 
            onClick={() => { setAutoScroll(true); scrollContainerRef.current?.scrollTo({top: scrollContainerRef.current.scrollHeight, behavior: 'smooth'}); }}
            className="absolute bottom-2 right-2 p-1 bg-slate-800 rounded-full text-slate-300 hover:bg-slate-700"
          >
              <ArrowDown size={12} />
          </button>
      )}
    </div>
  );
};
