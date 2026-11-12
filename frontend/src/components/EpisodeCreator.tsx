import React, { useState } from 'react';
import { Play, Sparkles, Sliders, DollarSign, Globe2 } from 'lucide-react';

interface Props {
  selectedStudio: string;
  onTriggerRun: (params: { title: string; brief: string; target_language: string; budget_limit_usd: number }) => void;
  isLoading: boolean;
}

export const EpisodeCreator: React.FC<Props> = ({ selectedStudio, onTriggerRun, isLoading }) => {
  const [title, setTitle] = useState(selectedStudio === 'kids' ? 'Gulu Owl Star Counting' : 'Bikram Baboo Village Comedy');
  const [brief, setBrief] = useState(
    selectedStudio === 'kids'
      ? 'Preschool counting numbers 1 and 2 with joyful forest animation'
      : 'Village square market arrival and hilarious sweet shop incident'
  );
  const [language, setLanguage] = useState(selectedStudio === 'kids' ? 'en' : 'or');
  const [budget, setBudget] = useState(1.5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onTriggerRun({
      title,
      brief,
      target_language: language,
      budget_limit_usd: budget
    });
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-bold text-white">Autonomous Episode Production Wizard</h2>
        </div>
        <span className="text-xs text-slate-400 flex items-center gap-1">
          <Sliders className="w-3.5 h-3.5" /> 1-Click Generation Mode
        </span>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold text-slate-300 mb-1.5">Episode Title</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500 focus:ring-1 focus:ring-amber-500"
              placeholder="e.g. Bikram Baboo & the Magic Umbrella"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
                <Globe2 className="w-3.5 h-3.5 text-amber-400" /> Target Language
              </label>
              <select
                value={language}
                onChange={(e) => setLanguage(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
              >
                <option value="or">Odia (ଓଡ଼ିଆ)</option>
                <option value="hi">Hindi (हिन्दी)</option>
                <option value="bn">Bengali (বাংলা)</option>
                <option value="en">English</option>
                <option value="te">Telugu (తెలుగు)</option>
                <option value="ta">Tamil (தமிழ்)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1.5 flex items-center gap-1">
                <DollarSign className="w-3.5 h-3.5 text-emerald-400" /> Budget Cap
              </label>
              <input
                type="number"
                step="0.1"
                min="0.5"
                max="5.0"
                value={budget}
                onChange={(e) => setBudget(parseFloat(e.target.value))}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2.5 text-sm text-white focus:outline-none focus:border-amber-500"
              />
            </div>
          </div>
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-300 mb-1.5">Creative Brief / Topic</label>
          <textarea
            value={brief}
            onChange={(e) => setBrief(e.target.value)}
            rows={2}
            className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-amber-500"
            placeholder="Describe the comedic premise or educational goal..."
          />
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="w-full py-3 px-5 rounded-xl bg-gradient-to-r from-amber-500 to-rose-500 hover:from-amber-600 hover:to-rose-600 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 shadow-lg shadow-amber-500/20 transition-all disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <span className="w-4 h-4 border-2 border-slate-950 border-t-transparent rounded-full animate-spin"></span>
              <span>Autonomous Production in Progress...</span>
            </>
          ) : (
            <>
              <Play className="w-4 h-4 fill-slate-950" />
              <span>Launch Autonomous Production Pipeline</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
