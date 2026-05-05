import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Terminal, Code2, Wrench, Play, BookOpen, ChevronUp, Zap, ShieldCheck, Activity, X } from 'lucide-react';

interface MobileCommandBarProps {
  onCommand: (cmd: string) => void;
  isTyping: boolean;
}

export const MobileCommandBar: React.FC<MobileCommandBarProps> = ({ onCommand, isTyping }) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const actions = [
    { id: 'scan', label: 'Scan AST', icon: Code2, cmd: '/scan', color: 'cyan' },
    { id: 'refactor', label: 'Refactor', icon: Wrench, cmd: '/refactor', color: 'blue' },
    { id: 'security', label: 'Security', icon: ShieldCheck, cmd: '/security audit', color: 'red' },
    { id: 'reliability', label: 'SRE Check', icon: Activity, cmd: '/reliability check', color: 'emerald' },
    { id: 'test', label: 'Execute Tests', icon: Play, cmd: '/test', color: 'amber' },
    { id: 'docs', label: 'Explain', icon: BookOpen, cmd: '/explain code', color: 'slate' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[100] md:hidden px-4 pb-6 pt-4 bg-gradient-to-t from-slate-950 via-slate-950/90 to-transparent">
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ y: 20, opacity: 0, scale: 0.95 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 20, opacity: 0, scale: 0.95 }}
            className="mb-4 grid grid-cols-3 gap-2"
          >
            {actions.map((action) => (
              <button
                key={action.id}
                onClick={() => {
                  onCommand(action.cmd);
                  setIsOpen(false);
                }}
                className={`flex flex-col items-center justify-center gap-2 p-3 bg-slate-900/40 backdrop-blur-xl border border-slate-800/50 rounded-2xl active:bg-cyan-500/10 transition-all active:scale-95`}
                id={`btn-mobile-${action.id}`}
              >
                <div className={`p-2.5 rounded-xl bg-slate-950 border border-slate-800 text-${action.color}-400`}>
                  <action.icon size={20} />
                </div>
                <span className="text-[10px] sm:text-xs font-bold text-slate-400 uppercase tracking-widest text-center">{action.label}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center gap-3">
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className={`flex-1 h-14 rounded-2xl border flex items-center justify-center gap-3 transition-all duration-300 ${isOpen ? 'bg-cyan-500 border-cyan-400 text-white shadow-[0_0_20px_rgba(6,182,212,0.3)]' : 'bg-slate-900 bg-opacity-80 border-slate-800 text-slate-400 backdrop-blur-md'}`}
          id="btn-mobile-master"
        >
          <motion.div
            animate={{ rotate: isOpen ? 180 : 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          >
            {isOpen ? <X size={20} /> : <Zap size={20} className={isTyping ? "animate-pulse text-cyan-400" : ""} />}
          </motion.div>
          <span className="text-[10px] font-black uppercase tracking-[0.3em] font-mono">
            {isOpen ? 'Close Core' : 'Command Swarm'}
          </span>
        </button>
        
        <div className="w-14 h-14 bg-slate-900/80 border border-slate-800 rounded-2xl flex items-center justify-center backdrop-blur-md">
           <div className={`w-2 h-2 rounded-full transition-colors duration-500 ${isTyping ? 'bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.8)] animate-pulse' : 'bg-slate-700'}`} />
        </div>
      </div>
    </div>
  );
};
