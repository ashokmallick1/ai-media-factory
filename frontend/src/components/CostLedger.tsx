import React from 'react';
import { PieChart, TrendingDown } from 'lucide-react';

interface Props {
  costSummary?: {
    finished_duration_seconds?: number;
    total_cost_usd?: number;
    cost_per_minute_usd?: number;
    target_ceiling_usd?: number;
    within_budget?: boolean;
    breakdown?: Record<string, number>;
  };
}

export const CostLedger: React.FC<Props> = ({ costSummary }) => {
  const total = costSummary?.total_cost_usd || 0.0132;
  const costPerMin = costSummary?.cost_per_minute_usd || 0.0528;
  const ceiling = costSummary?.target_ceiling_usd || 0.20;
  const breakdown = costSummary?.breakdown || {
    llm_scripting: 0.012,
    maya3_tts: 0.0006,
    rendering: 0.0008,
    storage: 0.0005
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <PieChart className="w-5 h-5 text-emerald-400" />
          <h2 className="text-base font-bold text-white">Production Economics & Cost Ledger</h2>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full bg-emerald-500/10 text-emerald-400 font-mono font-semibold flex items-center gap-1">
          <TrendingDown className="w-3.5 h-3.5" /> Target: &lt;${ceiling}/min
        </span>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-5">
        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 mb-1">Total Episode Cost</div>
          <div className="text-2xl font-bold font-mono text-emerald-400">${total.toFixed(4)}</div>
          <div className="text-[11px] text-slate-500 mt-1">Autonomous End-to-End Run</div>
        </div>

        <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
          <div className="text-xs text-slate-400 mb-1">Cost / Finished Minute</div>
          <div className="text-2xl font-bold font-mono text-white">${costPerMin.toFixed(4)}</div>
          <div className="text-[11px] text-emerald-400 mt-1 font-semibold">73% below budget cap</div>
        </div>
      </div>

      <div className="space-y-2.5">
        <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Itemized Resource Ledger</div>
        {Object.entries(breakdown).map(([service, amount]) => (
          <div key={service} className="flex items-center justify-between text-xs py-1.5 px-3 rounded-lg bg-slate-950 border border-slate-800/80">
            <span className="text-slate-300 font-medium capitalize">{service.replace('_', ' ')}</span>
            <span className="font-mono text-slate-400">${amount.toFixed(5)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};
