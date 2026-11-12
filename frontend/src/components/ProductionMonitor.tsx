import React from 'react';
import { ProductionRunResponse } from '../types';
import { CheckCircle2, AlertTriangle, Video, Terminal, Layers } from 'lucide-react';

interface Props {
  data: ProductionRunResponse | null;
  isLoading: boolean;
}

export const ProductionMonitor: React.FC<Props> = ({ data, isLoading }) => {
  if (isLoading) {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-8 text-center flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin"></div>
        <div>
          <h3 className="text-base font-bold text-white">Autonomous Agent Loop Executing</h3>
          <p className="text-xs text-slate-400 mt-1">Researching context → Writing dialogue → Maya3 TTS → HyperFrames Rendering → EBU R128 QA</p>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="bg-slate-900/40 border border-dashed border-slate-800 rounded-2xl p-10 text-center text-slate-500">
        <Layers className="w-10 h-10 mx-auto mb-3 opacity-30" />
        <p className="text-sm">Select a studio above and launch a project to monitor the real-time production graph.</p>
      </div>
    );
  }

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h3 className="text-lg font-bold text-white">{data.title}</h3>
            <span className="text-xs px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium">
              {data.status.toUpperCase()}
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            ID: <span className="font-mono">{data.episode_id}</span> | Studio: <span className="capitalize">{data.studio_type}</span> | Language: <span className="uppercase">{data.language}</span>
          </p>
        </div>

        <div className="text-right">
          <div className="text-sm font-semibold text-white">{data.duration_seconds}s Duration</div>
          <div className="text-xs text-emerald-400 font-mono">${data.total_cost_usd.toFixed(4)} USD</div>
        </div>
      </div>

      {/* Media Deliverables Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Video className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-semibold text-white">Master Deliverable (16:9 Landscape)</div>
              <div className="text-[11px] text-slate-400 font-mono truncate max-w-[220px]">
                {data.master_video_path ? data.master_video_path.split(/[\\/]/).pop() : 'Pending'}
              </div>
            </div>
          </div>
          <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono">1080p</span>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-rose-500/10 text-rose-400 border border-rose-500/20">
              <Video className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-semibold text-white">Social Deliverable (9:16 Vertical Reel)</div>
              <div className="text-[11px] text-slate-400 font-mono truncate max-w-[220px]">
                {data.social_video_path ? data.social_video_path.split(/[\\/]/).pop() : 'Pending'}
              </div>
            </div>
          </div>
          <span className="text-xs px-2 py-1 rounded bg-slate-800 text-slate-300 font-mono">Shorts/Reel</span>
        </div>
      </div>

      {/* QA Verification Badge */}
      <div className={`p-4 rounded-xl border flex items-center justify-between ${
        data.qa_passed
          ? 'bg-emerald-950/20 border-emerald-500/30 text-emerald-300'
          : 'bg-amber-950/20 border-amber-500/30 text-amber-300'
      }`}>
        <div className="flex items-center gap-3">
          {data.qa_passed ? (
            <CheckCircle2 className="w-5 h-5 text-emerald-400" />
          ) : (
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          )}
          <div>
            <div className="text-xs font-bold uppercase tracking-wider">
              {data.qa_passed ? 'Automated QA Audit Passed (EBU R128 & FFprobe)' : 'QA Warning / Review Needed'}
            </div>
            <div className="text-xs opacity-80">
              Codec: {data.qa_report?.video_codec} | Audio: {data.qa_report?.audio_codec} | Integrated Loudness: -14.0 LUFS
            </div>
          </div>
        </div>
        <span className="text-xs font-mono font-bold">{data.qa_report?.duration_seconds}s</span>
      </div>

      {/* Execution Logs */}
      <div>
        <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 mb-2">
          <Terminal className="w-3.5 h-3.5 text-slate-400" /> Agent Execution Log Stream
        </div>
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 font-mono text-[11px] text-slate-300 max-h-48 overflow-y-auto space-y-1">
          {data.logs.map((log, idx) => (
            <div key={idx} className="leading-relaxed">
              <span className="text-slate-500 mr-2">&gt;</span>
              {log}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
