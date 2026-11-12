import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import { YouTubePlayer, PlayableEpisode } from './components/YouTubePlayer';
import { StudioSelector } from './components/StudioSelector';
import { EpisodeCreator } from './components/EpisodeCreator';
import { ProductionMonitor } from './components/ProductionMonitor';
import { CostLedger } from './components/CostLedger';
import { CharacterVoiceLibrary } from './components/CharacterVoiceLibrary';
import { Studio, Character, ProductionRunResponse } from './types';

export const App: React.FC = () => {
  const [studios, setStudios] = useState<Studio[]>([]);
  const [selectedStudio, setSelectedStudio] = useState<string>('entertainment');
  const [characters, setCharacters] = useState<Character[]>([]);
  const [episodes, setEpisodes] = useState<PlayableEpisode[]>([]);
  const [activeEpisode, setActiveEpisode] = useState<PlayableEpisode | null>(null);
  const [productionData, setProductionData] = useState<ProductionRunResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const fetchEpisodes = () => {
    fetch('/api/v1/episodes')
      .then((res) => res.json())
      .then((data: PlayableEpisode[]) => {
        setEpisodes(data);
        if (data.length > 0 && !activeEpisode) {
          setActiveEpisode(data[0]);
        }
      })
      .catch((err) => console.error('Failed to load episodes', err));
  };

  useEffect(() => {
    // Initial data fetch
    fetch('/api/v1/studios')
      .then((res) => res.json())
      .then((data) => setStudios(data))
      .catch((err) => console.error('Failed to load studios', err));

    fetch('/api/v1/characters')
      .then((res) => res.json())
      .then((data) => setCharacters(data))
      .catch((err) => console.error('Failed to load characters', err));

    fetchEpisodes();
  }, []);

  const handleSelectStudio = (studioId: string) => {
    setSelectedStudio(studioId);
    // Find matching episode in playlist
    const match = episodes.find((e) => e.studio_type === studioId);
    if (match) {
      setActiveEpisode(match);
    }
  };

  const handleTriggerRun = async (params: {
    title: string;
    brief: string;
    target_language: string;
    budget_limit_usd: number;
  }) => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/v1/production/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          brand_id: 'default_brand',
          studio_type: selectedStudio,
          title: params.title,
          brief: params.brief,
          target_language: params.target_language,
          budget_limit_usd: params.budget_limit_usd
        })
      });
      const data: ProductionRunResponse = await res.json();
      setProductionData(data);

      // Refresh episodes and set newly generated video active
      fetch('/api/v1/episodes')
        .then((r) => r.json())
        .then((allEps: PlayableEpisode[]) => {
          setEpisodes(allEps);
          const newlyCreated = allEps.find((e) => e.id === data.episode_id);
          if (newlyCreated) {
            setActiveEpisode(newlyCreated);
          } else if (allEps.length > 0) {
            setActiveEpisode(allEps[0]);
          }
        });
    } catch (err) {
      console.error('Production execution failed', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Header />

      <main className="flex-1 max-w-7xl w-full mx-auto px-6 py-8 space-y-8">
        {/* Cinema Video Player (YouTube style) */}
        <section>
          <YouTubePlayer
            episodes={episodes}
            activeEpisode={activeEpisode}
            onSelectEpisode={setActiveEpisode}
          />
        </section>

        {/* Studio Selection */}
        <section>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-400">Production Studio Hub</h2>
            <span className="text-xs text-slate-500">6 Autonomous Studios Available</span>
          </div>
          <StudioSelector
            studios={studios}
            selectedStudio={selectedStudio}
            onSelectStudio={handleSelectStudio}
          />
        </section>

        {/* Episode Creation & Cost Controls */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <EpisodeCreator
              selectedStudio={selectedStudio}
              onTriggerRun={handleTriggerRun}
              isLoading={isLoading}
            />
          </div>
          <div>
            <CostLedger costSummary={productionData?.cost_summary} />
          </div>
        </div>

        {/* Real-time Production Monitor */}
        <section>
          <ProductionMonitor data={productionData} isLoading={isLoading} />
        </section>

        {/* Character and Voice Library */}
        <section>
          <CharacterVoiceLibrary characters={characters} />
        </section>
      </main>

      <footer className="border-t border-slate-900 py-6 px-6 text-center text-xs text-slate-500">
        AI Media Factory OS • Powered by Google Antigravity • LangGraph Stateful Architecture • Maya3 Indic Speech
      </footer>
    </div>
  );
};

export default App;
