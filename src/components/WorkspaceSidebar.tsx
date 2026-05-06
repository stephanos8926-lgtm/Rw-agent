import React from 'react';
import { 
  Plus, 
  Folder, 
  Database, 
  Settings, 
  Activity, 
  Terminal, 
  GitBranch, 
  BookOpen, 
  Download, 
  Upload, 
  ShieldAlert, 
  Cpu,
  Info,
  Power,
  Layers,
  Search,
  ChevronRight,
  Code2,
  Zap,
  Share2,
  FileUp,
  History,
  Layout
} from 'lucide-react';
import { motion } from 'motion/react';

interface WorkspaceSidebarProps {
  workspaces: any[];
  currentWorkspace: string;
  onSelect: (id: string) => void;
  status: any;
  viewMode: 'chat' | 'swarm';
  setViewMode: (mode: 'chat' | 'swarm') => void;
  skills: any[];
  skillFilter: string;
  onSkillFilterChange: (val: string) => void;
  astData: any;
  astError?: string | null;
  onRetryAst: () => void;
  onExport: () => void;
  onImport: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onOpenSystemInfo: () => void;
  onClearHistory: () => void;
  onReset: () => void;
  isConnected: boolean;
}

export const WorkspaceSidebar: React.FC<WorkspaceSidebarProps> = ({ 
  workspaces, 
  currentWorkspace, 
  onSelect, 
  status, 
  viewMode, 
  setViewMode,
  skills,
  skillFilter,
  onSkillFilterChange,
  astData,
  astError,
  onRetryAst,
  onExport,
  onImport,
  onOpenSystemInfo,
  onClearHistory,
  onReset,
  isConnected
}) => {
  const [symbolFilter, setSymbolFilter] = React.useState('');
  const [selectedSymbol, setSelectedSymbol] = React.useState<string | null>(null);
  const [symbolUsages, setSymbolUsages] = React.useState<any[]>([]);
  
  const filteredSkills = React.useMemo(() => 
    skills.filter(s => s.frontmatter.name.toLowerCase().includes(skillFilter.toLowerCase())), 
    [skills, skillFilter]
  );

  const filteredAst = React.useMemo(() => {
    if (!astData) return {};
    const filtered: any = {};
    Object.entries(astData).forEach(([path, sym]: [any, any]) => {
      const fns = sym.functions?.filter((f: any) => f.name.toLowerCase().includes(symbolFilter.toLowerCase())) || [];
      const classes = sym.classes?.filter((c: any) => c.name.toLowerCase().includes(symbolFilter.toLowerCase())) || [];
      if (fns.length > 0 || classes.length > 0) {
        filtered[path] = { functions: fns, classes: classes };
      }
    });
    return filtered;
  }, [astData, symbolFilter]);

  const handleSelectSymbol = async (symbolName: string) => {
    setSelectedSymbol(symbolName);
    try {
      const response = await fetch(`/api/ast/usages/${symbolName}`);
      const data = await response.json();
      setSymbolUsages(data.usages || []);
    } catch (e) {
      console.error("Failed to fetch usages", e);
      setSymbolUsages([]);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden text-slate-400">
      
      {/* OS Branding */}
      <div className="p-5 flex items-center justify-between border-b border-slate-800/50 bg-slate-950/20">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-xl bg-slate-900 border ${isConnected ? 'border-cyan-500/50 text-cyan-400' : 'border-red-500/50 text-red-500'}`}>
            <Cpu size={22} />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-100 tracking-[0.15em] uppercase">Forge OS</h1>
            <div className="flex items-center gap-1.5 mt-0.5">
              <span className={`w-1.5 h-1.5 rounded-full ${isConnected ? 'bg-emerald-500' : 'bg-red-500'}`} />
              <span className="text-[10px] font-mono uppercase text-slate-600">
                {isConnected ? 'NODE_ACTIVE' : 'NODE_OFFLINE'}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar">
        
        {/* Navigation Section */}
        <div className="px-4 py-6 border-b border-slate-800/30">
          <h3 className="text-[11px] uppercase tracking-widest text-slate-500 font-bold mb-4 px-2">Primary Interface</h3>
          <div className="space-y-1.5">
            <button 
              onClick={() => setViewMode('chat')}
              className={`w-full h-11 flex items-center justify-between px-4 rounded-xl transition-all group ${viewMode === 'chat' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'hover:bg-slate-800/50 text-slate-500 hover:text-slate-300'}`}
            >
              <div className="flex items-center gap-3">
                <Terminal size={18} />
                <span className="text-sm font-bold uppercase tracking-wide">Command Chat</span>
              </div>
            </button>
            <button 
              onClick={() => setViewMode('swarm')}
              className={`w-full h-11 flex items-center justify-between px-4 rounded-xl transition-all group ${viewMode === 'swarm' ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20' : 'hover:bg-slate-800/50 text-slate-500 hover:text-slate-300'}`}
            >
              <div className="flex items-center gap-3">
                <Activity size={18} />
                <span className="text-sm font-bold uppercase tracking-wide">Swarm Monitor</span>
              </div>
            </button>
          </div>
        </div>

        {/* Mission Status Section */}
        {status && (
          <div className="px-4 py-6 border-b border-slate-800/30 bg-cyan-500/[0.02]">
            <h3 className="text-[10px] uppercase tracking-widest text-cyan-500/70 font-bold flex items-center gap-2 mb-4 px-2">
              <Zap size={12} /> Intelligence Status
            </h3>
            <div className="space-y-3 px-2">
              <div className="flex justify-between items-center text-[10px]">
                <span className="text-slate-500 uppercase tracking-tighter">Tasks Completed</span>
                <span className="text-cyan-400 font-mono font-bold bg-cyan-950/50 px-1.5 py-0.5 rounded border border-cyan-500/20">{status.completed?.length || 0}</span>
              </div>
              <div className="flex justify-between items-center text-[10px]">
                <span className="text-slate-500 uppercase tracking-tighter">In Progress</span>
                <span className="text-amber-400 font-mono font-bold bg-amber-950/50 px-1.5 py-0.5 rounded border border-amber-500/20">{status.in_progress?.length || 0}</span>
              </div>
              
              <div className="mt-4">
                <div className="flex justify-between text-[8px] uppercase tracking-widest text-slate-600 mb-1.5">
                   <span>Capacity</span>
                   <span>{Math.min(100, ((status.completed?.length || 0) / ((status.completed?.length || 0) + (status.in_progress?.length || 0) + (status.blocked?.length || 0) || 1)) * 100).toFixed(0)}%</span>
                </div>
                <div className="h-1 w-full bg-slate-900 rounded-full overflow-hidden">
                  <motion.div 
                    initial={{ width: 0 }}
                    animate={{ width: `${Math.min(100, ((status.completed?.length || 0) / ((status.completed?.length || 0) + (status.in_progress?.length || 0) + (status.blocked?.length || 0) || 1)) * 100)}%` }}
                    className="h-full bg-cyan-500 transition-all duration-1000 shadow-[0_0_8px_rgba(34,211,238,0.5)]" 
                  />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Agent Registry */}
        <div className="px-4 py-6 border-b border-slate-800/30">
          <h3 className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold mb-4 px-2 flex items-center gap-2">
            <Cpu size={12} /> Agent Registry
          </h3>
          <div className="space-y-1.5 max-h-48 overflow-y-auto custom-scrollbar px-1">
            {/* Will fetch and map agents here */}
          </div>
        </div>

        {/* Intelligence / Skills Section */}
        <div className="px-4 py-6 border-b border-slate-800/30">
          <h3 className="text-[11px] uppercase tracking-widest text-slate-500 font-bold mb-4 px-2 flex items-center gap-2">
            <BookOpen size={14} /> Intelligence
          </h3>
          <div className="relative mb-4 flex items-center">
             <input 
              type="text" 
              placeholder="Search Intelligence..." 
              value={skillFilter} 
              onChange={(e) => onSkillFilterChange(e.target.value)}
              className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-2.5 pl-4 pr-10 text-xs focus:outline-none focus:border-cyan-500/50 transition-all"
            />
            <div className="absolute right-4 text-slate-700">
               <Search size={14} />
            </div>
          </div>
          <div className="space-y-1 max-h-48 overflow-y-auto custom-scrollbar px-1">
            {filteredSkills.map((skill, i) => (
              <div key={i} className="text-xs text-slate-500 hover:text-cyan-400 cursor-pointer py-2 px-3 hover:bg-cyan-500/5 rounded-xl border border-transparent hover:border-cyan-500/10 transition-all flex items-center gap-3 group">
                <div className="w-1.5 h-1.5 rounded-full bg-slate-800 group-hover:bg-cyan-400 transition-colors" />
                <span className="truncate uppercase tracking-tight font-medium">{skill.frontmatter.name}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Codebase Map Section */}
        <div className="px-4 py-6 border-b border-slate-800/30">
          <h3 className="text-[10px] uppercase tracking-[0.2em] text-slate-500 font-bold mb-4 px-2 flex items-center gap-2">
            <Database size={12} /> Project Index
          </h3>
          <div className="relative mb-4 flex items-center">
            <input 
              type="text" 
              placeholder="Search symbols..." 
              value={symbolFilter} 
              onChange={(e) => setSymbolFilter(e.target.value)}
              className="w-full bg-slate-950/50 border border-slate-800 rounded-xl py-2.5 pl-4 pr-10 text-xs focus:outline-none focus:border-cyan-500/50 transition-all"
            />
            <div className="absolute right-4 text-slate-700">
               <Search size={14} />
            </div>
          </div>
          
          {astError ? (
            <div className="px-2 py-3 mb-4 rounded-xl bg-red-950/30 border border-red-900/50 text-[10px] text-red-400 flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <ShieldAlert size={14} />
                <span>{astError}</span>
              </div>
              <button 
                onClick={onRetryAst}
                className="w-full py-1.5 rounded-lg bg-red-900/50 hover:bg-red-900 text-white font-bold transition-all"
              >
                Retry Load
              </button>
            </div>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto custom-scrollbar px-2">
              {Object.entries(filteredAst).map(([path, symbols]: [any, any]) => (
                  <div key={path} className="group">
                      <div className="text-[10px] font-bold text-slate-400 truncate mb-1 hover:text-cyan-400 transition-colors cursor-pointer">{path.split('/').pop()}</div>
                      <div className="ml-2 border-l border-slate-800 pl-2 space-y-0.5">
                          {symbols.functions && symbols.functions.map((fn: any) => (
                            <div 
                              key={fn.name} 
                              onClick={() => handleSelectSymbol(fn.name)}
                              className={`text-[9px] truncate flex items-center gap-1.5 cursor-pointer ${selectedSymbol === fn.name ? 'text-cyan-400' : 'text-slate-600 hover:text-slate-400'}`}
                            >
                              <span className="text-amber-500/50">fn</span> {fn.name}
                            </div>
                          ))}
                      </div>
                  </div>
              ))}
              
              {selectedSymbol && (
                 <div className="mt-4 pt-4 border-t border-slate-800">
                    <h4 className="text-[10px] font-bold text-slate-300 mb-2">Usages of {selectedSymbol}:</h4>
                    {symbolUsages.length > 0 ? (
                      <div className="space-y-1">
                        {symbolUsages.map(([path, line]: [string, number], i) => (
                          <div key={i} className="text-[9px] text-slate-500 font-mono truncate">
                            {path.split('/').pop()}:{line}
                          </div>
                      ))}
                      </div>
                    ) : <div className="text-[9px] text-slate-600 italic">No usages found</div>}
                 </div>
              )}
              
              {Object.keys(filteredAst).length === 0 && <div className="text-[10px] text-slate-600 italic">No symbols found...</div>}
            </div>
          )}
        </div>
      </div>
      
      {/* Footer Controls */}
      <div className="p-4 bg-slate-950/40 border-t border-slate-800/50">
        <div className="grid grid-cols-2 gap-2 mb-4">
           <button onClick={onExport} className="flex items-center gap-2 justify-center p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 hover:text-cyan-400 transition-all text-[10px] font-bold uppercase">
             <Share2 size={12} /> Export
           </button>
           <label className="flex items-center gap-2 justify-center p-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 hover:text-cyan-400 transition-all text-[10px] font-bold uppercase cursor-pointer">
             <FileUp size={12} /> Import
             <input type="file" onChange={onImport} className="hidden" />
           </label>
        </div>
        
        <div className="space-y-1">
          <button onClick={onOpenSystemInfo} className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 transition-all">
            <Info size={14} /> System Diagnostics
          </button>
          <button onClick={onClearHistory} className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest text-slate-500 hover:text-red-400 hover:bg-red-400/5 transition-all">
            <History size={14} /> Wipe Session
          </button>
          <button onClick={onReset} className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-[10px] font-bold uppercase tracking-widest text-slate-600 hover:text-amber-400 hover:bg-amber-400/5 transition-all">
            <Power size={14} /> Factory Reset
          </button>
        </div>
      </div>
    </div>
  );
};
