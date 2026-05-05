import React from 'react';

interface DiffViewerProps {
  files: { path: string, content: string, status: 'modified' | 'added' | 'deleted' }[];
  onAccept: () => void;
  onReject: () => void;
}

export const DiffViewer: React.FC<DiffViewerProps> = ({ files, onAccept, onReject }) => {
  return (
    <div className="bg-slate-900 border border-slate-700 rounded-lg overflow-hidden flex flex-col font-mono text-xs shadow-2xl">
      <div className="bg-slate-800 px-4 py-2 flex justify-between items-center text-slate-300 font-bold border-b border-slate-700">
        <span>Atomic Commit Request</span>
        <span className="text-cyan-400">{files.length} file(s) changed</span>
      </div>
      <div className="p-4 overflow-y-auto max-h-64 custom-scrollbar">
        {files.map((file, idx) => (
          <div key={idx} className="mb-4 last:mb-0">
            <div className="text-slate-400 font-bold mb-1 flex items-center gap-2">
              <span className={`w-2 h-2 rounded-full ${file.status === 'added' ? 'bg-emerald-400' : file.status === 'deleted' ? 'bg-red-400' : 'bg-amber-400'}`}></span>
              {file.path}
            </div>
            <pre className="bg-slate-950 p-2 rounded border border-slate-800 text-slate-300">
              {file.content.substring(0, 150)}...
            </pre>
          </div>
        ))}
      </div>
      <div className="p-3 bg-slate-800 border-t border-slate-700 flex justify-end gap-3">
        <button onClick={onReject} className="px-4 py-1.5 rounded bg-slate-700 hover:bg-slate-600 text-slate-200 transition-colors">Reject</button>
        <button onClick={onAccept} className="px-4 py-1.5 rounded bg-cyan-600 hover:bg-cyan-500 text-white font-bold transition-colors shadow-lg">Accept Changes</button>
      </div>
    </div>
  );
};
