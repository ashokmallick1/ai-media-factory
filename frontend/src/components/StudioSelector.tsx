import React from 'react';
import { Studio } from '../types';
import { Film, Baby, GraduationCap, Mic, Newspaper, Megaphone } from 'lucide-react';

interface Props {
  studios: Studio[];
  selectedStudio: string;
  onSelectStudio: (id: string) => void;
}

const icons: Record<string, React.ReactNode> = {
  entertainment: <Film className="w-5 h-5" />,
  kids: <Baby className="w-5 h-5" />,
  education: <GraduationCap className="w-5 h-5" />,
  podcast: <Mic className="w-5 h-5" />,
  news: <Newspaper className="w-5 h-5" />,
  marketing: <Megaphone className="w-5 h-5" />
};

export const StudioSelector: React.FC<Props> = ({ studios, selectedStudio, onSelectStudio }) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
      {studios.map((studio) => {
        const isSelected = selectedStudio === studio.id;
        return (
          <button
            key={studio.id}
            onClick={() => onSelectStudio(studio.id)}
            className={`p-4 rounded-xl text-left border transition-all duration-200 relative overflow-hidden flex flex-col justify-between ${
              isSelected
                ? 'bg-amber-500/10 border-amber-500 text-white shadow-lg shadow-amber-500/10'
                : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700 hover:bg-slate-900'
            }`}
          >
            <div>
              <div className={`p-2 rounded-lg inline-block mb-3 ${
                isSelected ? 'bg-amber-500 text-slate-950 font-bold' : 'bg-slate-800 text-slate-400'
              }`}>
                {icons[studio.id] || <Film className="w-5 h-5" />}
              </div>
              <h3 className="font-semibold text-sm mb-1">{studio.name}</h3>
              <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed">{studio.description}</p>
            </div>

            <div className="mt-3 pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-400">
              <span className="font-mono uppercase">{studio.primary_language}</span>
              <span className="px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">{studio.render_engine.split(' ')[0]}</span>
            </div>
          </button>
        );
      })}
    </div>
  );
};
