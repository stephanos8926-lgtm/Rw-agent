import React, { useState, useRef, useEffect } from 'react';
import { useAgent, ChatMessage } from './hooks/useAgent';
import { WorkspaceSidebar } from './components/WorkspaceSidebar';
import { SystemInfoModal } from './components/SystemInfoModal';
import { Terminal, Send, Power, Code2, Cpu, Wrench, ChevronDown, ChevronRight, FileJson, Menu, X, Copy, Play, Info } from 'lucide-react';
import Markdown from 'react-markdown';
import rehypeHighlight from 'rehype-highlight';
import 'highlight.js/styles/github-dark.css';
import { motion, AnimatePresence } from 'motion/react';

export default function App() {
  const [input, setInput] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentWorkspace, setCurrentWorkspace] = useState('default');
  const [workspaces] = useState([{id: 'default', name: 'Default'}, {id: 'research', name: 'Research'}]);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 768);
  const [status, setStatus] = useState<any>(null);
  
  useEffect(() => {
    const handleResize = () => setIsDesktop(window.innerWidth >= 768);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);
  const [skills, setSkills] = useState<any[]>([]);
  const [astData, setAstData] = useState<any>(null);
  const [isSystemInfoOpen, setIsSystemInfoOpen] = useState(false);
  const [systemInfo, setSystemInfo] = useState<string | null>(null);
  const [skillFilter, setSkillFilter] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch('/api/os-info')
      .then(res => res.json())
      .then(data => setSystemInfo(data.info))
      .catch(err => console.error("Failed to fetch OS info:", err));
  }, []);

  useEffect(() => {
    fetch('/api/ast')
        .then(res => res.json())
        .then(data => setAstData(data))
        .catch(err => console.error("Failed to fetch AST:", err));
  }, []);
  
  // Connect to the local FastAPI server
  const { messages, isConnected, isTyping, sendMessage, clearHistory } = useAgent('/ws/agent');

  const filteredSkills = skills.filter(s => s.frontmatter.name.toLowerCase().includes(skillFilter.toLowerCase()));

  // Persistence
  useEffect(() => {
    const saved = localStorage.getItem('forge-chat-history');
    if (saved) {
      // For now, allow merging or just replacing. Replacing is simpler.
    }
  }, []);

  useEffect(() => {
    localStorage.setItem('forge-chat-history', JSON.stringify(messages));
  }, [messages]);

  const exportChat = () => {
    const blob = new Blob([JSON.stringify(messages, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forge-chat-${new Date().toISOString()}.json`;
    a.click();
  };

  const importChat = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const data = JSON.parse(event.target?.result as string);
      // In a real app, we would need to push these to the useAgent hook's state. 
      // For now, this is a placeholder for the logic.
    };
    reader.readAsText(file);
  };

  const handlePaste = (e: React.ClipboardEvent) => {
    if (e.clipboardData.files.length > 0) {
        // Handle file
    } else if (e.clipboardData.getData('text').length > 1000) {
        const text = e.clipboardData.getData('text');
        // Show in-line text paste object
        console.log("Large paste detected:", text.length, "chars");
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !isConnected) return;
    sendMessage(input.trim());
    setInput('');
  };

  return (
    <div className="flex h-screen bg-[#0f172a] text-slate-300 font-mono selection:bg-cyan-900 selection:text-cyan-50 overflow-hidden">
      
      {/* Mobile Sidebar Overlay */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/50 z-40 md:hidden"
            onClick={() => setSidebarOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside 
        className="fixed md:static inset-y-0 left-0 z-50 w-64 bg-slate-900 border-r border-slate-800 flex flex-col"
        initial={false}
        animate={{ 
          x: sidebarOpen || isDesktop ? 0 : "-100%" 
        }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
      >
        <div className="p-4 border-b border-slate-800 flex justify-between items-center bg-slate-950/50">
          <div className="flex items-center space-x-3">
             <div className={`p-2 rounded-md bg-slate-800 border ${isConnected ? 'border-cyan-500/50 text-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.2)]' : 'border-red-500/50 text-red-400'}`}>
               <Cpu size={20} />
             </div>
             <h1 className="text-sm font-semibold text-slate-200 tracking-wide">FORGE OS</h1>
          </div>
          <button className="md:hidden text-slate-400 hover:text-slate-200" onClick={() => setSidebarOpen(false)}>
            <X size={20} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-4">
          <WorkspaceSidebar workspaces={workspaces} currentWorkspace={currentWorkspace} onSelect={setCurrentWorkspace} />
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-4 font-semibold mt-2">Project Progress</div>
          {status ? (
            <div className="space-y-1 bg-slate-950/50 p-3 rounded-lg border border-slate-800">
              <div className="flex justify-between text-[11px] text-slate-400"><span>Completed:</span><span className="text-cyan-400 font-mono">{status.completed?.length || 0}</span></div>
              <div className="flex justify-between text-[11px] text-slate-400"><span>In Progress:</span><span className="text-amber-400 font-mono">{status.in_progress?.length || 0}</span></div>
            </div>
          ) : (
            <div className="text-[11px] text-slate-500 italic">No project data yet.</div>
          )}

          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2 font-semibold mt-6">Available Skills</div>
          <input 
            type="text" 
            placeholder="Filter skills..." 
            value={skillFilter} 
            onChange={(e) => setSkillFilter(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-md py-1.5 px-3 text-xs mb-3 focus:outline-none focus:border-cyan-500/50"
          />
          <div className="space-y-1">
            {filteredSkills.map((skill, i) => (
              <div key={i} className="text-xs text-slate-400 truncate hover:text-cyan-400 cursor-pointer py-1 px-2 hover:bg-slate-800 rounded">{skill.frontmatter.name}</div>
            ))}
          </div>

          <div className="text-xs text-slate-500 uppercase tracking-widest mb-2 font-semibold mt-6">Codebase Map</div>
          <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar">
            {astData && Object.entries(astData).map(([path, symbols]: [any, any]) => (
                <div key={path} className="text-[10px] text-slate-400">
                    <div className="font-semibold text-slate-500 truncate">{path.split('/').pop()}</div>
                    <div className="ml-2">
                        {symbols.classes && symbols.classes.map((cls: any) => <div key={cls.name} className="truncate">cls: {cls.name}</div>)}
                        {symbols.functions && symbols.functions.map((fn: any) => <div key={fn.name} className="truncate">fn: {fn.name}</div>)}
                    </div>
                </div>
            ))}
          </div>
          
          <div className="text-xs text-slate-500 uppercase tracking-widest mb-4 font-semibold mt-6">Session</div>
          <div className="space-y-1">
            <button onClick={exportChat} className="w-full text-left text-xs text-slate-400 hover:text-cyan-400 py-1 px-2 hover:bg-slate-800 rounded">Export Conversation</button>
            <button onClick={() => setIsSystemInfoOpen(true)} className="w-full text-left text-xs text-slate-400 hover:text-cyan-400 py-1 px-2 hover:bg-slate-800 rounded flex items-center gap-2"><Info size={12} />System Info</button>
            <label className="block w-full text-left text-xs text-slate-400 hover:text-cyan-400 cursor-pointer py-1 px-2 hover:bg-slate-800 rounded">
              Import Conversation
              <input type="file" onChange={importChat} className="hidden" />
            </label>
            <button onClick={clearHistory} className="w-full text-left text-xs text-slate-400 hover:text-red-400 py-1 px-2 hover:bg-slate-800 rounded">Clear History</button>
          </div>
        </div>
        
        <div className="p-4 border-t border-slate-800">
           <button onClick={() => { localStorage.clear(); window.location.reload(); }} className="flex items-center justify-center w-full p-2 hover:bg-slate-800 rounded-md transition-colors text-slate-400 hover:text-red-400 text-sm">
             <Power size={16} className="mr-2" /> Reset Session
           </button>
        </div>
        <SystemInfoModal isOpen={isSystemInfoOpen} onClose={() => setIsSystemInfoOpen(false)} info={systemInfo} />
      </motion.aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen min-w-0">
        
        {/* Header */}
        <header className="flex items-center justify-between p-4 bg-slate-900 md:bg-transparent border-b border-slate-800 md:border-transparent z-10 sticky top-0">
          <div className="flex items-center md:hidden">
            <button className="text-slate-400 hover:text-slate-200 p-1" onClick={() => setSidebarOpen(true)}>
              <Menu size={24} />
            </button>
          </div>
          <h2 className="text-sm font-semibold text-slate-200 tracking-wide md:hidden">FORGE OS</h2>
          <div className="w-6 md:hidden"></div> {/* Spacer for centering */}
        </header>

        {/* Main Terminal Area */}
        <main className="flex-1 overflow-y-auto p-2 md:p-4 space-y-4">
          <div className="max-w-4xl mx-auto space-y-4 pb-20">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isTyping && (
              <div className="flex items-center space-x-3 text-slate-500 animate-pulse ml-4 md:ml-12 pt-4">
                <Terminal size={16} />
                <span className="text-xs">Agent OS is reasoning...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </main>

        {/* Input Area */}
        <div className="p-4 bg-slate-900 md:bg-transparent border-t border-slate-800 md:border-transparent">
          <form onSubmit={handleSubmit} className="max-w-4xl mx-auto relative flex items-center shadow-lg md:shadow-none">
            <Terminal size={18} className="absolute left-4 text-cyan-500 z-10" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onPaste={handlePaste}
              disabled={!isConnected}
              placeholder={isConnected ? "Enter command or system directive..." : "Waiting for WebSocket connection..."}
              className="w-full bg-slate-950/80 md:bg-slate-900 border border-slate-800 rounded-xl py-3.5 pl-12 pr-12 focus:outline-none focus:border-cyan-500/50 focus:ring-1 focus:ring-cyan-500/50 transition-all text-sm disabled:opacity-50 shadow-inner"
            />
            <button 
              type="submit"
              disabled={!isConnected || !input.trim()}
              className="absolute right-2 p-2 rounded-lg hover:bg-slate-800 text-cyan-500 disabled:opacity-50 disabled:hover:bg-transparent transition-colors z-10"
            >
               <Send size={16} />
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}

const MessageBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const [isExpanded, setIsExpanded] = useState(false);

  const getStyle = () => {
    switch (message.role) {
      case 'user':
        return 'bg-slate-800/80 border-slate-700 ml-12 text-slate-200';
      case 'agent':
        return 'bg-cyan-950/20 border-cyan-900/50 mr-12 text-cyan-100 shadow-[inset_0_1px_0_rgba(255,255,255,0.05)]';
      case 'tool_intent':
        return 'bg-amber-950/20 border-amber-900/50 text-amber-200/80 text-xs italic mx-8';
      case 'tool_result':
        return 'bg-slate-950/80 border-slate-800 text-slate-400 text-xs font-mono mx-8 w-full';
      case 'system':
        return 'bg-transparent border-transparent text-slate-500 text-xs text-center justify-center';
      default:
        return 'bg-slate-800 border-slate-700';
    }
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const isVerbose = message.content.length > 200 || message.content.includes('\n');

  const renderToolResult = (content: string) => {
    try {
      const parsed = JSON.parse(content);
      return (
        <pre className="bg-slate-900 p-2 rounded text-blue-300 font-mono text-xs overflow-x-auto">
          <code>{JSON.stringify(parsed, null, 2)}</code>
        </pre>
      );
    } catch {
      return <div className="whitespace-pre-wrap font-mono text-xs">{content}</div>;
    }
  };

  if (message.role === 'tool_result') {
    return (
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex flex-col items-start w-full pr-12 pl-8`}
      >
        <div className={`flex flex-col space-y-2 w-full p-3 rounded-xl border ${getStyle()} relative group`}>
           <div className="flex justify-between items-center w-full">
             <button 
               onClick={() => setIsExpanded(!isExpanded)}
               className="flex items-center space-x-2 text-slate-500 hover:text-slate-300 transition-colors w-full focus:outline-none"
             >
               {isExpanded ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
               <FileJson size={14} className="text-slate-600" />
               <span className="font-semibold uppercase tracking-wider text-[10px]">Tool Output</span>
             </button>
             <div className="flex space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                <button onClick={() => copyToClipboard(message.content)} className="p-1 hover:bg-slate-700 rounded transition-colors"><Copy size={12} /></button>
             </div>
           </div>
           
           {(isExpanded || !isVerbose) && (
             <div className="mt-2 pt-2 border-t border-slate-800/50 overflow-x-auto max-h-96 custom-scrollbar">
                {renderToolResult(message.content)}
             </div>
           )}
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div 
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        className={`flex flex-col ${message.role === 'user' ? 'items-end' : 'items-start'}`}
    >
      <div className={`flex items-start space-x-3 max-w-[90%] p-4 rounded-xl border ${getStyle()} relative group`}>
        {message.role === 'agent' && (
          <div className="absolute -left-3 -top-3 p-1.5 bg-cyan-950 border border-cyan-800 rounded-lg text-cyan-400 shadow-md">
            <Code2 size={14} />
          </div>
        )}
        <div className="flex-1 whitespace-pre-wrap leading-relaxed min-w-0 break-words">
          {message.role === 'agent' ? (
            <div className="text-sm prose prose-invert max-w-none">
              <Markdown rehypePlugins={[rehypeHighlight]}>{message.content}</Markdown>
            </div>
          ) : (
            message.content
          )}
        </div>
      </div>
    </motion.div>
  );
}
