import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
    // Future: send to telemetry endpoint
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 font-sans">
          <div className="max-w-md w-full bg-slate-900 border border-red-500/30 rounded-2xl p-8 shadow-2xl text-center">
            <div className="inline-flex p-4 rounded-full bg-red-500/10 text-red-500 mb-6">
              <AlertTriangle size={48} />
            </div>
            <h1 className="text-xl font-bold text-white mb-2 uppercase tracking-wider">Kernel Panic</h1>
            <p className="text-slate-400 text-sm mb-8 leading-relaxed">
              The Forge OS UI has encountered a critical failure. System state has been preserved, but the interface needs a reset.
            </p>
            
            <div className="bg-slate-950 rounded-xl p-4 mb-8 text-left border border-slate-800">
                <div className="text-[10px] text-slate-500 font-mono mb-2 uppercase">Error Context:</div>
                <div className="text-xs text-red-400 font-mono break-all line-clamp-3">
                    {this.state.error?.message || 'Unknown system fault'}
                </div>
            </div>

            <button
              onClick={() => window.location.reload()}
              className="w-full h-12 flex items-center justify-center gap-3 bg-red-500 text-white rounded-xl font-bold hover:bg-red-400 transition-all shadow-lg shadow-red-500/20 active:scale-[0.98]"
            >
              <RefreshCw size={18} />
              REBOOT_INTERFACE
            </button>
          </div>
        </div>
      );
    }

    return this.children;
  }
}
