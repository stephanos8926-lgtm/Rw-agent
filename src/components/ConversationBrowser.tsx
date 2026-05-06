import React from 'react';
import { GitBranch, CornerDownRight, RotateCcw, MessageSquare } from 'lucide-react';
import { ChatMessage } from '../hooks/useAgent';

interface ConversationBrowserProps {
  messages: ChatMessage[];
  onRevert: (messageId: string) => void;
  onBranch: (messageId: string) => void;
}

export const ConversationBrowser: React.FC<ConversationBrowserProps> = ({ messages, onRevert, onBranch }) => {
  const canRevert = (index: number) => {
    for (let i = index + 1; i < messages.length; i++) {
        if (messages[i].isToolAction) return false;
    }
    return true;
  };

  return (
    <div className="w-64 bg-slate-925 border-l border-slate-800 flex flex-col h-full">
      <div className="p-4 border-b border-slate-800">
        <h3 className="text-[11px] uppercase tracking-widest text-slate-500 font-bold flex items-center gap-2">
          <GitBranch size={14} /> Conversation History
        </h3>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
        {messages.map((msg, idx) => (
          <div key={msg.id} className="group p-2 rounded-lg hover:bg-slate-900 border border-transparent hover:border-slate-800 transition-all">
            <div className="flex items-center gap-2 text-[10px] text-slate-500 mb-1">
              <MessageSquare size={10} />
              <span className="uppercase">{msg.role}</span>
              <span className="ml-auto">{new Date(msg.timestamp).toLocaleTimeString()}</span>
            </div>
            <div className="text-[11px] text-slate-300 truncate font-mono">{msg.content}</div>
            
            <div className="flex gap-2 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
              <button 
                onClick={() => canRevert(idx) && onRevert(msg.id)}
                disabled={!canRevert(idx)}
                className={`text-[10px] flex items-center gap-1 ${canRevert(idx) ? 'text-amber-500 hover:text-amber-400' : 'text-slate-700 cursor-not-allowed'}`}
              >
                <RotateCcw size={10} /> {canRevert(idx) ? 'Revert' : 'Locked'}
              </button>
              <button 
                onClick={() => onBranch(msg.id)}
                className="text-[10px] text-cyan-500 hover:text-cyan-400 flex items-center gap-1"
              >
                <CornerDownRight size={10} /> Branch
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
