import React from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Terminal, Code2, Wrench, Play, BookOpen, ChevronUp, Zap, ShieldCheck, Activity, X, Pause, StopCircle } from 'lucide-react';

interface MobileCommandBarProps {
  onCommand: (cmd: string) => void;
  isTyping: boolean;
}

export const MobileCommandBar: React.FC<MobileCommandBarProps> = ({ onCommand, isTyping }) => {
  const [isOpen, setIsOpen] = React.useState(false);

  const actions = [
    { id: 'scan', label: 'Scan AST', icon: Code2, cmd: '/scan', color: 'text-cyan-400' },
    { id: 'refactor', label: 'Refactor', icon: Wrench, cmd: '/refactor', color: 'text-blue-400' },
    { id: 'security', label: 'Security', icon: ShieldCheck, cmd: '/security audit', color: 'text-red-400' },
    { id: 'reliability', label: 'SRE Check', icon: Activity, cmd: '/reliability check', color: 'text-emerald-400' },
    { id: 'test', label: 'Tests', icon: Play, cmd: '/test', color: 'text-amber-400' },
    { id: 'docs', label: 'Explain', icon: BookOpen, cmd: '/explain code', color: 'text-slate-400' },
    { id: 'swarm-pause', label: 'Pause', icon: Pause, cmd: '/swarm pause', color: 'text-zinc-400' },
    { id: 'swarm-resume', label: 'Resume', icon: Play, cmd: '/swarm resume', color: 'text-zinc-400' },
    { id: 'swarm-stop', label: 'Stop', icon: StopCircle, cmd: '/swarm stop', color: 'text-rose-400' },
  ];

  return (
    <div className="fixed bottom-0 left-0 right-0 z-[100] md:hidden px-4 pb-6 pt-4 bg-gradient-to-t from-slate-950 via-slate-950/95 to-transparent">
      <AnimatePresence>
        {isOpen && (
          <motion.div 
            initial={{ y: 20, opacity: 0, scale: 0.95 }}
            animate={{ y: 0, opacity: 1, scale: 1 }}
            exit={{ y: 20, opacity: 0, scale: 0.95 }}
            className="mb-4 grid grid-cols-3 gap-3"
          >
            {actions.map((action) => (
              <button
                key={action.id}
                onClick={() => {
                  onCommand(action.cmd);
                  setIsOpen(false);
                }}
                className={`flex flex-col items-center justify-center gap-2 p-4 bg-slate-900 border border-slate-700 rounded-2xl active:bg-slate-800 transition-all active:scale-95 shadow-xl`}
                id={`btn-mobile-${action.id}`}
              >
                <action.icon size={22} className={`${action.color}`} />
                <span className="text-[10px] font-bold text-slate-300 uppercase tracking-wider text-center">{action.label}</span>
              </button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="flex items-center gap-3">
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className={`flex-1 min-h-[56px] rounded-2xl border flex items-center justify-center gap-3 transition-all duration-300 shadow-xl ${isOpen ? 'bg-cyan-600 border-cyan-500 text-white' : 'bg-slate-900 border-slate-700 text-slate-300'}`}
          id="btn-mobile-master"
        >
          <motion.div
            animate={{ rotate: isOpen ? 180 : 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 20 }}
          >
            {isOpen ? <X size={22} /> : <Zap size={22} className={isTyping ? "animate-pulse text-cyan-400" : ""} />}
          </motion.div>
          <span className="text-xs font-black uppercase tracking-[0.2em] font-mono">
            {isOpen ? 'Core Locked' : 'Command Swarm'}
          </span>
        </button>
        
        <div className="w-14 h-14 bg-slate-900 border border-slate-700 rounded-2xl flex items-center justify-center shadow-lg">
           <div className={`w-3 h-3 rounded-full transition-all duration-300 ${isTyping ? 'bg-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.8)] animate-pulse' : 'bg-slate-600'}`} />
        </div>
      </div>
    </div>
  );
};
