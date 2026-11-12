import React from 'react';
import { Character } from '../types';
import { User, Volume2, Mic } from 'lucide-react';

interface Props {
  characters: Character[];
}

export const CharacterVoiceLibrary: React.FC<Props> = ({ characters }) => {
  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 shadow-xl">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <User className="w-5 h-5 text-amber-400" />
          <h2 className="text-base font-bold text-white">Recurring Character & Voice Registry</h2>
        </div>
        <span className="text-xs text-slate-400">Maya3 Native Voice IDs</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {characters.map((char) => (
          <div key={char.id} className="bg-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 capitalize">
                  {char.role}
                </span>
                <span className="text-[11px] text-slate-500 font-mono">Maya3 Indic</span>
              </div>
              <h3 className="text-sm font-bold text-white mb-1">{char.name}</h3>
              <p className="text-xs text-slate-400 line-clamp-2 mb-3 leading-relaxed">{char.bio}</p>
            </div>

            <div className="pt-2 border-t border-slate-900 flex items-center justify-between text-xs text-slate-300">
              <span className="flex items-center gap-1.5 text-slate-400">
                <Mic className="w-3.5 h-3.5 text-rose-400" />
                <span className="font-mono text-[11px]">{char.name === 'Gulu Owl' ? 'Voice: Ahana' : 'Voice: Bikram'}</span>
              </span>
              <button className="p-1.5 rounded-lg bg-slate-900 hover:bg-slate-800 text-amber-400 transition-colors">
                <Volume2 className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
