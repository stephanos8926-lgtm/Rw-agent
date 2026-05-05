import React from 'react';
import { useSwarmEvents } from '../hooks/useSwarmEvents';
import { motion, AnimatePresence } from 'motion/react';
import { Activity, Cpu, Code2, AlertTriangle, CheckCircle, Clock, Info, Terminal } from 'lucide-react';

export const SwarmObserver: React.FC = () => {
  const { events } = useSwarmEvents('/ws/events');
  const [isCondensed, setIsCondensed] = React.useState(window.innerWidth < 768);
  const [persistentAgents, setPersistentAgents] = React.useState<any[]>([]);
  const [selectedAgentId, setSelectedAgentId] = React.useState<string | null>(null);
  const [auditLog, setAuditLog] = React.useState<any[]>([]);
  const [isAuditing, setIsAuditing] = React.useState(false);

  React.useEffect(() => {
    const handleResize = () => setIsCondensed(window.innerWidth < 768);
    window.addEventListener('resize', handleResize);
    fetchAgents();
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const fetchAgents = async () => {
    try {
      const res = await fetch('/api/swarm/agents');
      const data = await res.json();
      setPersistentAgents(data.agents || []);
    } catch (e) {
      console.error("Failed to fetch persistent agents", e);
    }
  };

  const fetchAuditLog = async (agentId: string) => {
    setIsAuditing(true);
    setSelectedAgentId(agentId);
    try {
      const res = await fetch(`/api/swarm/audit/${agentId}`);
      const data = await res.json();
      setAuditLog(data.history || []);
    } catch (e) {
      console.error("Audit failed", e);
    }
  };
  
  // Create a reversed array so newest is at the top
  const displayEvents = [...events].reverse().slice(0, 50);

  const getEventIcon = (type: string) => {
    if (type.includes('error') || type.includes('fail')) return <AlertTriangle size={isCondensed ? 12 : 14} className="text-red-400" />;
    if (type.includes('complete') || type.includes('success')) return <CheckCircle size={isCondensed ? 12 : 14} className="text-emerald-400" />;
    if (type.includes('spawn') || type.includes('start')) return <Cpu size={isCondensed ? 12 : 14} className="text-amber-400" />;
    return <Activity size={isCondensed ? 12 : 14} className="text-cyan-400" />;
  };

  return (
    <div className={`flex flex-col h-full bg-[#020617] text-slate-300 font-sans ${isCondensed ? 'p-3' : 'p-4 md:p-8'} overflow-hidden relative`}>
      {/* Background Effect */}
      <div className="absolute inset-0 grid-bg opacity-5 pointer-events-none" />
      
      <div className={`flex flex-row items-center justify-between gap-4 ${isCondensed ? 'mb-4' : 'mb-8'} z-10`}>
        <div className="flex items-center gap-3">
          <Activity size={isCondensed ? 20 : 24} className="text-cyan-500 animate-pulse" />
          <h2 className={`${isCondensed ? 'text-base' : 'text-xl'} font-bold text-slate-100`}>
            {isCondensed ? 'Ops' : 'Swarm Operations'}
          </h2>
        </div>
        
        <div className="flex items-center gap-2 sm:gap-4">
          <button 
            onClick={() => setIsCondensed(!isCondensed)}
            className="px-3 py-1.5 bg-slate-900 border border-slate-800 rounded-lg text-[10px] font-bold text-slate-400 hover:text-cyan-400 hover:border-cyan-500/50 transition-all uppercase tracking-wider shadow-lg"
          >
            {isCondensed ? 'Expand' : 'Collapse'}
          </button>
          {!isCondensed && (
            <div className="hidden sm:flex items-center gap-4 text-[10px]">
              <div className="flex flex-col items-end">
                <span className="text-slate-600 font-bold uppercase tracking-widest">Bus Status</span>
                <span className="text-emerald-400 flex items-center gap-2">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                  ONLINE
                </span>
              </div>
              <div className="h-8 w-px bg-slate-800" />
              <div className="flex flex-col items-end">
                <span className="text-slate-600 font-bold uppercase tracking-widest">Events</span>
                <span className="text-cyan-400 font-bold">{events.length}</span>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Persistent Audit Log Overlay */}
      <AnimatePresence>
        {selectedAgentId && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[100] bg-slate-950/80 backdrop-blur-md p-4 md:p-8 flex items-center justify-center"
          >
            <motion.div 
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="w-full max-w-2xl h-[80vh] terminal-card bg-slate-900 flex flex-col overflow-hidden border-2 border-cyan-500/30"
            >
              <div className="p-4 border-b border-slate-800 flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                    <Terminal size={16} className="text-cyan-400" /> AGENT_AUDIT_LOG
                  </h3>
                  <p className="text-[10px] text-slate-500 font-mono mt-1">{selectedAgentId}</p>
                </div>
                <button 
                  onClick={() => setSelectedAgentId(null)}
                  className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors"
                >
                  <X size={20} /> 
                </button>
              </div>

              <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar bg-slate-950/30">
                {auditLog.map((log, i) => (
                  <div key={log.event_id || i} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      <div className="w-2 h-2 rounded-full bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.5)]" />
                      {i < auditLog.length - 1 && <div className="flex-1 w-[1px] bg-slate-800 my-1" />}
                    </div>
                    <div className="flex-1 pb-4">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-bold text-cyan-400 uppercase tracking-widest">{log.event_type}</span>
                        <span className="text-[9px] text-slate-600">{new Date(log.timestamp).toLocaleString()}</span>
                      </div>
                      <div className="text-[12px] text-slate-300 font-mono bg-slate-900/80 p-3 rounded-xl border border-slate-800 overflow-x-auto custom-scrollbar shadow-inner">
                        {log.payload ? (
                          <pre className="whitespace-pre-wrap break-all md:break-normal">
                            {JSON.stringify(JSON.parse(log.payload), null, 2)}
                          </pre>
                        ) : (
                          <span className="italic text-slate-600">NULL_PAYLOAD</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
                
                {auditLog.length === 0 && !isAuditing && (
                  <div className="h-full flex items-center justify-center text-slate-600 text-[10px] uppercase">
                    No logs found for this agent
                  </div>
                )}
              </div>
              
              <div className="p-3 bg-slate-950 border-t border-slate-800 flex justify-between items-center">
                <span className="text-[9px] text-slate-500 uppercase">Audit Mode: PERSISTENT_RECOVERY</span>
                <button 
                  onClick={() => fetchAuditLog(selectedAgentId)}
                  className="px-3 py-1 bg-cyan-500/10 border border-cyan-500/30 rounded text-[10px] text-cyan-400 font-bold hover:bg-cyan-500/20 transition-all uppercase"
                >
                  Sync Audit
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <div className={`grid grid-cols-1 ${isCondensed ? '' : 'lg:grid-cols-4'} gap-6 flex-1 overflow-hidden z-10`}>
        {/* Intelligence Briefing - Hidden in Condensed Mode */}
        {!isCondensed && (
          <div className="lg:col-span-1 space-y-6 flex flex-col">
            <div className="terminal-card p-4 border-l-2 border-l-cyan-500">
              <h3 className="text-[11px] font-bold text-slate-200 mb-3 flex items-center gap-2">
                <Info size={14} className="text-cyan-400" /> SYSTEM_PRIMER
              </h3>
              <p className="text-[10px] leading-relaxed text-slate-400">
                The Swarm architecture uses distributed worker nodes to perform horizontal scaling of tasks. 
              </p>
            </div>

            <div className="terminal-card p-4 flex-1 flex flex-col overflow-hidden">
               <div className="flex items-center justify-between mb-4">
                 <h3 className="text-[11px] font-bold text-slate-200 uppercase tracking-widest">Agent Registry</h3>
                 <button onClick={fetchAgents} className="text-[9px] text-cyan-500 hover:text-cyan-400">REFRESH</button>
               </div>
               
               <div className="flex-1 flex flex-col space-y-4 overflow-y-auto custom-scrollbar">
                  {persistentAgents.map((agent) => (
                    <button 
                      key={agent.agent_id} 
                      onClick={() => fetchAuditLog(agent.agent_id)}
                      className={`p-3 rounded-lg border flex items-center gap-4 text-left transition-all ${selectedAgentId === agent.agent_id ? 'bg-cyan-500/10 border-cyan-500/50' : 'bg-slate-900/50 border-slate-800 hover:border-slate-700'}`}
                    >
                       <div className={`p-2 rounded-lg ${agent.status === 'active' ? 'bg-cyan-500/10 text-cyan-500' : 'bg-slate-800 text-slate-600'}`}>
                          <Cpu size={16} />
                       </div>
                       <div className="flex-1 overflow-hidden">
                          <div className="flex justify-between items-center mb-1">
                             <span className="text-[10px] font-bold text-slate-300 truncate">{agent.role}</span>
                             <span className={`text-[8px] px-1 rounded uppercase ${agent.status === 'active' ? 'bg-cyan-500/20 text-cyan-400' : 'bg-slate-800 text-slate-500'}`}>{agent.status}</span>
                          </div>
                          <div className="text-[8px] text-slate-500 font-mono truncate">{agent.agent_id}</div>
                       </div>
                    </button>
                  ))}
                  
                  {persistentAgents.length === 0 && (
                    <div className="flex-1 flex items-center justify-center text-[10px] text-slate-600 italic uppercase">
                      Registry Empty
                    </div>
                  )}
               </div>
            </div>
          </div>
        )}

        {/* Live Stream */}
        <div className={`${isCondensed ? 'col-span-1' : 'lg:col-span-3'} flex flex-col overflow-hidden`}>
          {!isCondensed && (
            <div className="flex items-center justify-between px-2 mb-2">
              <span className="text-[10px] font-bold text-slate-500 uppercase flex items-center gap-2">
                <Terminal size={12} /> Sequence_Log
              </span>
              <span className="text-[9px] text-slate-700">Last 50 cycles</span>
            </div>
          )}
          
          <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-2">
            <AnimatePresence mode="popLayout">
              {displayEvents.map((evt, idx) => (
                <motion.div
                  key={evt.timestamp + idx}
                  initial={{ opacity: 0, x: isCondensed ? 5 : 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  className={`terminal-card ${isCondensed ? 'p-2' : 'p-4'} flex flex-col gap-2 relative group`}
                >
                  <div className="flex justify-between items-center w-full">
                    <div className="flex items-center gap-3">
                      <div className={`rounded-md bg-slate-950/50 border border-slate-800 ${isCondensed ? 'p-1' : 'p-1.5'}`}>
                        {getEventIcon(evt.type)}
                      </div>
                      <div>
                        <span className={`${isCondensed ? 'text-[11px]' : 'text-[13px]'} font-bold text-slate-200 tracking-wide uppercase`}>{evt.type}</span>
                        {!isCondensed && (
                          <div className="text-[11px] text-slate-500 font-mono">
                            {new Date(evt.timestamp).toLocaleTimeString()}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    {isCondensed && (
                      <div className="text-[10px] text-slate-600 font-mono">
                        {new Date(evt.timestamp).toLocaleTimeString()}
                      </div>
                    )}
                  </div>
                  
                  {!isCondensed && (
                    <div className="text-[11px] text-cyan-400/70 bg-slate-950/40 p-3 rounded border border-slate-900 overflow-x-auto custom-scrollbar font-mono">
                      <pre>{JSON.stringify(evt.payload, null, 2)}</pre>
                    </div>
                  )}
                </motion.div>
              ))}
            </AnimatePresence>
            
            {displayEvents.length === 0 && (
              <div className="h-full flex items-center justify-center text-slate-800 text-sm italic border-2 border-dashed border-slate-900 rounded-2xl">
                Awaiting peripheral handshake...
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
