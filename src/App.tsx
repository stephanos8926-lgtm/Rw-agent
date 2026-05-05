import React, { useState, useRef, useEffect } from 'react';
import { useAgent, ChatMessage } from './hooks/useAgent';
import { WorkspaceSidebar } from './components/WorkspaceSidebar';
import { SystemInfoModal } from './components/SystemInfoModal';
import { SwarmObserver } from './components/SwarmObserver';
import { MobileCommandBar } from './components/MobileCommandBar';
import { TypewriterMarkdown } from './components/TypewriterMarkdown';
import { Terminal, Send, Power, Code2, Cpu, Wrench, ChevronDown, ChevronRight, FileJson, Menu, X, Copy, Play, Info, Activity, BookOpen, AlertTriangle, Zap, Check, Maximize2, Minimize2 } from 'lucide-react';
import { AnimatePresence, motion } from 'motion/react';
import 'highlight.js/styles/github-dark.css';

export default function App() {
  const [input, setInput] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentWorkspace, setCurrentWorkspace] = useState('default');
  const [workspaces] = useState([{id: 'default', name: 'Default'}, {id: 'research', name: 'Research'}]);
  const [isDesktop, setIsDesktop] = useState(window.innerWidth >= 768);
  const [status, setStatus] = useState<any>(null);
  const [viewMode, setViewMode] = useState<'chat' | 'swarm'>('chat');
  const [activeTask, setActiveTask] = useState<string | null>(null);
  const [showCommandPalette, setShowCommandPalette] = useState(false);
  const [skills, setSkills] = useState<any[]>([]);
  const [skillFilter, setSkillFilter] = useState('');
  const [astData, setAstData] = useState<any>(null);
  const [isSystemInfoOpen, setIsSystemInfoOpen] = useState(false);
  const [systemDiagnostics, setSystemDiagnostics] = useState<{ type: 'error' | 'warning' | 'info', message: string }[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setShowCommandPalette(prev => !prev);
      }
      if (e.key === 'Escape') {
        setShowCommandPalette(false);
        setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);
  
  // Data Fetching Pollers
  useEffect(() => {
    const fetchMeta = async () => {
      try {
        const [statusRes, skillsRes, astRes] = await Promise.all([
          fetch('/api/status'),
          fetch('/api/skills'),
          fetch('/api/ast')
        ]);
        
        const statusData = await statusRes.json();
        const skillsData = await skillsRes.json();
        const astData = await astRes.json();
        
        setStatus(statusData);
        setSkills(skillsData.skills || []);
        setAstData(astData);
        
        // Check for diagnostics in result if they come from the message bus or previous messages
        // Here we'll just check if lsp errors exist in a dedicated field or parsed from messages
        if (statusData.errors) {
            setSystemDiagnostics([{ type: 'error', message: 'LSP Diagnostics Active' }]);
        } else {
            setSystemDiagnostics([]);
        }
        
        // Update active task if in progress
        if (statusData.in_progress?.length > 0) {
          setActiveTask(statusData.in_progress[0]);
        } else {
          setActiveTask(null);
        }
      } catch (err) {
        console.error("Meta poll failed:", err);
      }
    };

    fetchMeta();
    const interval = setInterval(fetchMeta, 5000);
    return () => clearInterval(interval);
  }, []);
  
  // Connect to the local FastAPI server
  const { messages, isConnected, isTyping, sendMessage, clearHistory } = useAgent('/ws/agent');

  // Global Error Listeners
  useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      setSystemDiagnostics(prev => [...prev, { 
        type: 'error', 
        message: `Runtime Fault: ${event.message}` 
      }]);
    };

    const handleRejection = (event: PromiseRejectionEvent) => {
      setSystemDiagnostics(prev => [...prev, { 
        type: 'error', 
        message: `Async Failure: ${event.reason?.message || 'Unhandled Rejection'}` 
      }]);
    };

    window.addEventListener('error', handleError);
    window.addEventListener('unhandledrejection', handleRejection);
    return () => {
      window.removeEventListener('error', handleError);
      window.removeEventListener('unhandledrejection', handleRejection);
    };
  }, []);

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
    <div className="flex h-screen bg-[#020617] text-slate-300 font-sans selection:bg-cyan-500/30 overflow-hidden">
      
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
        className="fixed md:static inset-y-0 left-0 z-50 w-72 bg-slate-925/90 backdrop-blur-2xl border-r border-slate-800/50 flex flex-col shadow-2xl md:shadow-none"
        initial={false}
        animate={{ 
          x: sidebarOpen || isDesktop ? 0 : "-100%" 
        }}
        transition={{ type: "spring", stiffness: 400, damping: 40 }}
      >
        <WorkspaceSidebar 
          workspaces={workspaces}
          currentWorkspace={currentWorkspace}
          onSelect={setCurrentWorkspace}
          status={status}
          viewMode={viewMode}
          setViewMode={setViewMode}
          skills={skills}
          skillFilter={skillFilter}
          onSkillFilterChange={setSkillFilter}
          astData={astData}
          onExport={exportChat}
          onImport={importChat}
          onOpenSystemInfo={() => setIsSystemInfoOpen(true)}
          onClearHistory={clearHistory}
          onReset={() => { localStorage.clear(); window.location.reload(); }}
          isConnected={isConnected}
        />

        <MobileCommandBar 
          onCommand={(cmd) => sendMessage(cmd)}
          isTyping={isTyping}
        />
        
        {/* Mobile Close Button - Floats inside sidebar top right */}
        {!isDesktop && sidebarOpen && (
          <button 
            className="absolute top-4 right-4 p-2 rounded-full bg-slate-800 text-slate-400 hover:text-white border border-slate-700 shadow-lg" 
            onClick={() => setSidebarOpen(false)}
          >
            <X size={18} />
          </button>
        )}
      </motion.aside>

      {/* Command Palette */}
      <AnimatePresence>
        {showCommandPalette && (
          <div className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] px-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-slate-950/60 backdrop-blur-sm"
              onClick={() => setShowCommandPalette(false)}
            />
            <motion.div 
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              className="w-full max-w-xl bg-slate-900/90 backdrop-blur-2xl border border-slate-700 shadow-2xl rounded-2xl overflow-hidden z-10"
            >
               <div className="p-4 border-b border-slate-800 flex items-center gap-3">
                  <Terminal size={18} className="text-cyan-500" />
                  <input 
                    autoFocus
                    placeholder="Search commands, skills, or codebase... (ESC to close)"
                    className="flex-1 bg-transparent border-none focus:outline-none text-slate-100 text-sm"
                    value={skillFilter}
                    onChange={(e) => setSkillFilter(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const val = (e.target as HTMLInputElement).value;
                        if (val.startsWith('/')) {
                          sendMessage(val);
                          setShowCommandPalette(false);
                          setSkillFilter('');
                        }
                      }
                    }}
                  />
               </div>
               <div className="p-2 max-h-80 overflow-y-auto custom-scrollbar">
                  {skillFilter ? (
                    <div className="space-y-4">
                      {/* Skills Results */}
                      <div>
                        <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold p-2">Intelligence Modules</div>
                        <div className="space-y-1">
                          {skills.filter(s => s.frontmatter.name.toLowerCase().includes(skillFilter.toLowerCase())).length > 0 ? (
                            skills.filter(s => s.frontmatter.name.toLowerCase().includes(skillFilter.toLowerCase())).map((skill, i) => (
                              <button 
                                key={i}
                                className="w-full px-3 py-2 flex items-center gap-3 text-xs text-slate-400 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition-all"
                              >
                                <BookOpen size={14} />
                                <span className="font-mono uppercase tracking-tighter">{skill.frontmatter.name}</span>
                              </button>
                            ))
                          ) : (
                            <div className="px-3 py-2 text-[10px] text-slate-600 italic">No skills found...</div>
                          )}
                        </div>
                      </div>
                      {/* Symbols Results if any */}
                      {astData && (
                        <div>
                          <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold p-2">Codebase Symbols</div>
                          <div className="space-y-1">
                            {Object.entries(astData).flatMap(([path, sym]: [any, any]) => 
                              (sym.functions || []).map((f: any) => ({ path, name: f.name, type: 'fn' }))
                            ).filter(s => s.name.toLowerCase().includes(skillFilter.toLowerCase())).slice(0, 5).map((sym, i) => (
                              <button 
                                key={i}
                                onClick={() => {
                                  sendMessage(`/explain symbol ${sym.name} in ${sym.path}`);
                                  setShowCommandPalette(false);
                                  setSkillFilter('');
                                }}
                                className="w-full px-3 py-2 flex items-center justify-between text-xs text-slate-400 hover:bg-slate-800 hover:text-cyan-400 rounded-lg transition-all"
                              >
                                <div className="flex items-center gap-3">
                                  <Code2 size={14} />
                                  <span className="font-mono">{sym.name}</span>
                                </div>
                                <span className="text-[9px] text-slate-600 truncate max-w-[200px]">{sym.path.split('/').pop()}</span>
                              </button>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ) : (
                    <>
                      <div className="text-[10px] uppercase tracking-widest text-slate-500 font-bold p-2">Quick Actions</div>
                      <div className="space-y-1">
                         <button 
                           onClick={() => { setViewMode('swarm'); setShowCommandPalette(false); }}
                           className="w-full px-3 py-2 flex items-center justify-between text-xs hover:bg-slate-800 rounded-lg transition-colors group"
                         >
                            <span className="flex items-center gap-3"><Activity size={14} className="text-slate-400 group-hover:text-cyan-400" /> Open Swarm Observer</span>
                            <span className="text-[10px] text-slate-600 font-mono">SWARM</span>
                         </button>
                         <button 
                           onClick={() => { setViewMode('chat'); setShowCommandPalette(false); }}
                           className="w-full px-3 py-2 flex items-center justify-between text-xs hover:bg-slate-800 rounded-lg transition-colors group"
                         >
                            <span className="flex items-center gap-3"><Terminal size={14} className="text-slate-400 group-hover:text-cyan-400" /> Open Chat</span>
                            <span className="text-[10px] text-slate-600 font-mono">CHAT</span>
                         </button>
                         <button 
                           onClick={() => { setIsSystemInfoOpen(true); setShowCommandPalette(false); }}
                           className="w-full px-3 py-2 flex items-center justify-between text-xs hover:bg-slate-800 rounded-lg transition-colors group"
                         >
                            <span className="flex items-center gap-3"><Info size={14} className="text-slate-400 group-hover:text-cyan-400" /> System Diagnostics</span>
                            <span className="text-[10px] text-slate-600 font-mono">DIAG</span>
                         </button>
                      </div>
                    </>
                  )}
               </div>
               <div className="p-3 bg-slate-950/50 border-t border-slate-800 text-[10px] text-slate-500 flex justify-between">
                  <span>TIP: START WITH / FOR DIRECT COMMANDS</span>
                  <span>CMD + K</span>
               </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>

      {/* Forge HUD Overlay */}
      <div className="fixed bottom-6 right-6 z-[60] flex flex-col items-end gap-3 pointer-events-none">
        <AnimatePresence>
          {systemDiagnostics.map((diag, i) => (
            <motion.div 
              key={i}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className={`px-4 py-2 rounded-xl border flex items-center gap-3 backdrop-blur-xl shadow-2xl pointer-events-auto ${diag.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' : 'bg-amber-500/10 border-amber-500/30 text-amber-400'}`}
            >
              <AlertTriangle size={14} className="animate-pulse" />
              <span className="text-[10px] font-bold uppercase tracking-widest">{diag.message}</span>
              <button className="hover:text-white" onClick={() => setSystemDiagnostics([])}><X size={12} /></button>
            </motion.div>
          ))}
        </AnimatePresence>

        <div className="bg-slate-950/80 backdrop-blur-2xl border border-slate-800 p-3 rounded-2xl flex items-center gap-6 shadow-2xl pointer-events-auto select-none">
           <div className="flex flex-col gap-1">
              <div className="text-[8px] text-slate-600 uppercase tracking-tighter">Neural Stream</div>
              <div className="flex items-center gap-2">
                 <div className="flex gap-0.5 items-end h-3 w-8">
                    {[...Array(5)].map((_, i) => (
                       <motion.div 
                         key={i}
                         animate={{ height: isTyping ? [4, 12, 6, 12, 4] : [4, 6, 4] }}
                         transition={{ repeat: Infinity, duration: 1, delay: i * 0.1 }}
                         className={`w-1 rounded-full ${isConnected ? 'bg-cyan-500' : 'bg-slate-700'}`}
                       />
                    ))}
                 </div>
                 <span className={`text-[10px] font-bold ${isConnected ? 'text-cyan-400' : 'text-slate-600'}`}>{isConnected ? 'LIVE' : 'IDLE'}</span>
              </div>
           </div>

           <div className="w-px h-8 bg-slate-800" />

           <div className="flex flex-col gap-1">
              <div className="text-[8px] text-slate-600 uppercase tracking-tighter">Memory Latency</div>
              <div className="flex items-center gap-2">
                 <Zap size={12} className={isConnected ? 'text-amber-500' : 'text-slate-700'} />
                 <span className="text-[10px] font-bold text-slate-400">12ms</span>
              </div>
           </div>

           <div className="w-px h-8 bg-slate-800" />

           <div className="flex flex-col gap-1">
              <div className="text-[8px] text-slate-600 uppercase tracking-tighter">Forge Heartbeat</div>
              <div className="h-1.5 w-16 bg-slate-900 rounded-full overflow-hidden">
                 <motion.div 
                    animate={{ x: [-64, 64] }}
                    transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
                    className="h-full w-16 bg-gradient-to-r from-transparent via-cyan-500 to-transparent"
                 />
              </div>
           </div>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col h-screen min-w-0 relative">
        
        {/* Background Grid */}
        <div className="absolute inset-0 grid-bg opacity-10 pointer-events-none" />

        {/* Header / Breadcrumbs */}
        <header className="glass-header h-14 flex items-center justify-between px-4 z-20">
          <div className="flex items-center gap-4">
            <button className="md:hidden text-slate-400 hover:text-cyan-400 p-1" onClick={() => setSidebarOpen(true)}>
              <Menu size={20} />
            </button>
            
        <nav className="flex items-center text-[11px] font-semibold text-slate-500 uppercase tracking-wider overflow-hidden">
          <span className="hover:text-cyan-400 cursor-pointer transition-colors" onClick={() => setViewMode('chat')}>FORGE</span>
          <ChevronRight size={14} className="mx-2 text-slate-800" />
          <span className="text-slate-400 font-medium">{workspaces.find(w => w.id === currentWorkspace)?.name || currentWorkspace}</span>
          <ChevronRight size={14} className="mx-2 text-slate-800" />
          <span className="text-cyan-500 font-bold truncate max-w-[120px] sm:max-w-none">
            {viewMode === 'chat' ? (activeTask || 'ACTIVE_SESSION') : 'SWARM_MONITOR'}
          </span>
        </nav>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-4 text-[10px] font-mono">
              <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-900/50 rounded border border-slate-800">
                <span className="text-slate-600">LSP</span>
                <span className="text-emerald-400">READY</span>
              </div>
              <div className="flex items-center gap-1.5 px-2 py-1 bg-slate-900/50 rounded border border-slate-800">
                <span className="text-slate-600">MEM</span>
                <span className="text-cyan-400">{messages.length}T</span>
              </div>
            </div>
            
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse shadow-[0_0_8px_rgba(16,185,129,0.5)]' : 'bg-red-500'}`} />
          </div>
        </header>

        {viewMode === 'chat' ? (
          <>
            {/* Main Terminal Area */}
            <main className="flex-1 overflow-y-auto p-4 md:p-8 custom-scrollbar relative z-10">
              <div className="max-w-4xl mx-auto space-y-6 pb-24">
                {messages.length === 0 && (
                  <div className="h-[60vh] flex flex-col items-center justify-center text-center space-y-4">
                    <div className="p-4 rounded-2xl bg-cyan-500/5 border border-cyan-500/10 mb-2">
                       <Cpu size={40} className="text-cyan-500/40" />
                    </div>
                    <h2 className="text-lg font-bold text-slate-200">System Initialized</h2>
                    <p className="text-sm text-slate-500 max-w-xs">Forge OS is ready for system directives. Connect to workspaces or deploy swarms to begin.</p>
                  </div>
                )}
                {messages.map((msg) => (
                  <MessageBubble key={msg.id} message={msg} />
                ))}
                {isTyping && (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex items-center space-x-3 text-cyan-500/60 ml-4 md:ml-12 pt-4 font-sans text-xs uppercase tracking-widest"
                  >
                    <Activity size={14} className="animate-spin-slow" />
                    <span>Processing Neural Streams...</span>
                  </motion.div>
                )}
                <div ref={messagesEndRef} />
              </div>
            </main>

            <div className="absolute bottom-0 inset-x-0 p-4 md:p-8 z-30 pointer-events-none">
              <form 
                onSubmit={handleSubmit} 
                className="max-w-4xl mx-auto relative flex items-center pointer-events-auto"
              >
                <div className="absolute left-4 p-1.5 rounded-lg bg-slate-900 border border-slate-800 text-cyan-500 shadow-lg z-10">
                  <Terminal size={14} />
                </div>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onPaste={handlePaste}
                  disabled={!isConnected}
                  autoFocus
                  placeholder={isConnected ? "Enter command or system directive..." : "Re-establishing connection..."}
                  className="w-full bg-slate-925/90 backdrop-blur-xl border border-slate-800 focus:border-cyan-500/50 rounded-2xl py-4 pl-14 pr-24 focus:outline-none focus:ring-4 focus:ring-cyan-500/5 transition-all text-sm shadow-2xl text-slate-100 placeholder:text-slate-600"
                />
                <div className="absolute right-3 flex items-center gap-2 z-10">
                  <button
                    type="button"
                    className="p-2 rounded-lg hover:bg-slate-800 text-slate-500 hover:text-cyan-400 transition-colors"
                    title="Voice Command"
                  >
                     <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" x2="12" y1="19" y2="22"/></svg>
                  </button>
                  <button 
                    type="submit"
                    disabled={!isConnected || !input.trim()}
                    className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600 hover:bg-cyan-500 text-white text-xs font-bold uppercase tracking-wider disabled:opacity-30 disabled:grayscale transition-all shadow-lg active:scale-95"
                  >
                     <Send size={14} />
                     <span className="hidden md:inline">Run</span>
                  </button>
                </div>
              </form>
            </div>
          </>
        ) : (
          <main className="flex-1 overflow-hidden relative">
            <SwarmObserver />
          </main>
        )}
        <SystemInfoModal 
          isOpen={isSystemInfoOpen} 
          onClose={() => setIsSystemInfoOpen(false)} 
          info="Forge OS Kernel v4.2.0-STABLE. System established. Neural streams active."
        />
      </div>
    </div>
  );
}

const MessageBubble: React.FC<{ message: ChatMessage }> = ({ message }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isCopied, setIsCopied] = useState(false);

  const copyToClipboard = () => {
    navigator.clipboard.writeText(message.content);
    setIsCopied(true);
    setTimeout(() => setIsCopied(false), 2000);
  };

  const getRoleConfig = () => {
    switch (message.role) {
      case 'user':
        return {
          container: 'items-end ml-auto',
          bubble: 'bg-slate-800/80 border-slate-700 ml-12 text-slate-100 shadow-xl',
          label: 'Operator',
          color: 'slate',
          icon: <Terminal size={10} className="text-slate-500" />
        };
      case 'agent':
        return {
          container: 'items-start mr-auto',
          bubble: 'bg-cyan-950/20 border-cyan-500/20 mr-12 text-cyan-50 shadow-[0_0_15px_rgba(6,182,212,0.05)]',
          label: 'Forge Intelligence',
          color: 'cyan',
          icon: <Cpu size={10} className="text-cyan-500" />
        };
      case 'tool_intent':
        return {
          container: 'items-center mx-auto',
          bubble: 'bg-amber-950/10 border-amber-900/30 text-amber-400/70 text-[10px] italic',
          label: 'Executing Sub-routine',
          color: 'amber',
          icon: <Activity size={10} className="text-amber-500" />
        };
      case 'tool_result':
        return {
          container: 'items-center mx-auto w-full max-w-2xl',
          bubble: 'bg-slate-950/60 border-slate-800/80 text-slate-400 text-[10px] font-mono',
          label: 'System Output',
          color: 'slate',
          icon: <FileJson size={10} className="text-slate-500" />
        };
      default:
        return {
          container: 'items-start',
          bubble: 'bg-slate-800 border-slate-700',
          label: 'Unknown',
          color: 'slate',
          icon: <Info size={10} />
        };
    }
  };

  const config = getRoleConfig();

  return (
    <motion.div 
      initial={{ opacity: 0, y: 10, scale: 0.98 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={`flex flex-col ${config.container} space-y-1 group`}
    >
      <div className="flex items-center gap-2 px-2 opacity-60 group-hover:opacity-100 transition-opacity">
        {config.icon}
        <span className="text-[10px] font-bold uppercase tracking-wider">{config.label}</span>
      </div>
      
      <div className={`relative p-3 sm:p-4 rounded-2xl border transition-all ${config.bubble}`}>
        {message.role === 'agent' ? (
          <TypewriterMarkdown content={message.content} className="text-sm sm:text-base" />
        ) : (
          <div className="text-sm sm:text-base whitespace-pre-wrap leading-relaxed">
            {message.content.length > 500 && !isExpanded && message.role === 'tool_result' ? (
              <>
                {message.content.slice(0, 500)}...
                <button 
                  onClick={() => setIsExpanded(true)}
                  className="block mt-2 text-cyan-500 hover:underline font-bold"
                >
                  EXPAND OUTPUT
                </button>
              </>
            ) : (
              message.content
            )}
            {isExpanded && (
               <button 
                onClick={() => setIsExpanded(false)}
                className="mt-4 text-slate-500 hover:text-slate-300 flex items-center gap-1"
              >
                <Minimize2 size={12} /> Hide
              </button>
            )}
          </div>
        )}

        {/* Actions bar inside bubble */}
        <div className="absolute top-2 right-2 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button 
            onClick={copyToClipboard}
            className="p-1.5 rounded-lg bg-slate-900/50 border border-slate-800 text-slate-500 hover:text-white"
          >
            {isCopied ? <Check size={12} className="text-emerald-500" /> : <Copy size={12} />}
          </button>
        </div>
      </div>
    </motion.div>
  );
};
