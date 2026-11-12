import React from 'react';
import { Clapperboard, Activity, ShieldCheck } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-6 py-4">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-gradient-to-tr from-amber-500 to-rose-500 text-white shadow-lg shadow-amber-500/20">
            <Clapperboard className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-white">AI Media Factory</h1>
              <span className="text-xs px-2 py-0.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/30 font-medium">OS v1.0</span>
            </div>
            <p className="text-xs text-slate-400">Autonomous Multi-Brand, Multi-Studio, Multilingual Production</p>
          </div>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium text-slate-300">
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span>Maya3 TTS Engine: <strong className="text-emerald-400">12 Indic Langs</strong></span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
            <ShieldCheck className="w-4 h-4 text-blue-400" />
            <span>FFmpeg QA: <strong className="text-blue-400">EBU R128 (-14 LUFS)</strong></span>
          </div>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
            <Activity className="w-4 h-4 text-amber-400" />
            <span>Budget Cap: <strong className="text-amber-400">&lt;$0.10 / min</strong></span>
          </div>
        </div>
      </div>
    </header>
  );
};
