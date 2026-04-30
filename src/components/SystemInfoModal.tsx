import React from 'react';
import { X } from 'lucide-react';

export const SystemInfoModal = ({ isOpen, onClose, info }: { isOpen: boolean, onClose: () => void, info: string | null }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-lg w-full max-w-sm p-4 relative">
         <button onClick={onClose} className="absolute top-2 right-2 text-slate-400 hover:text-white"><X size={18} /></button>
         <h2 className="text-sm font-semibold text-slate-100 mb-4">System Information</h2>
         <pre className="text-[10px] text-slate-300 font-mono bg-slate-950 p-2 rounded whitespace-pre-wrap">{info || 'Loading...'}</pre>
      </div>
    </div>
  );
};
