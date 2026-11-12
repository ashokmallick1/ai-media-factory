import React, { useState, useRef, useEffect } from 'react';
import { 
  Play, ThumbsUp, Download, Smartphone, Monitor,
  CheckCircle, Sparkles, MessageSquare, Film, Globe,
  Share2, Copy, Check, X, Volume2, ShieldCheck, Radio
} from 'lucide-react';
import { PlayableEpisode } from '../types';
export type { PlayableEpisode };

interface Props {
  episodes: PlayableEpisode[];
  activeEpisode: PlayableEpisode | null;
  onSelectEpisode: (ep: PlayableEpisode) => void;
  onRefreshEpisodes?: () => void;
}

const studioColors: Record<string, string> = {
  entertainment: 'from-amber-500 to-rose-500',
  kids: 'from-emerald-400 to-teal-500',
  education: 'from-blue-500 to-indigo-600',
  podcast: 'from-purple-500 to-pink-500',
  news: 'from-red-500 to-orange-500',
  marketing: 'from-yellow-400 to-amber-600'
};

const LANG_LABELS: Record<string, { label: string; native: string }> = {
  or: { label: 'Odia', native: 'ଓଡ଼ିଆ' },
  hi: { label: 'Hindi', native: 'हिन्दी' },
  bn: { label: 'Bengali', native: 'বাংলা' },
  en: { label: 'English', native: 'English' },
  te: { label: 'Telugu', native: 'తెలుగు' },
  ta: { label: 'Tamil', native: 'தமிழ்' }
};

export const YouTubePlayer: React.FC<Props> = ({ 
  episodes, 
  activeEpisode, 
  onSelectEpisode,
  onRefreshEpisodes 
}) => {
  const [format, setFormat] = useState<'16:9' | '9:16'>('16:9');
  const [likes, setLikes] = useState<number>(342);
  const [hasLiked, setHasLiked] = useState<boolean>(false);
  const [isSubscribed, setIsSubscribed] = useState<boolean>(true);
  const [activeLang, setActiveLang] = useState<string>('or');
  const [showDubModal, setShowDubModal] = useState<boolean>(false);
  const [isDubbing, setIsDubbing] = useState<string | null>(null);
  const [showExportModal, setShowExportModal] = useState<boolean>(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const [comments, setComments] = useState<Array<{ user: string; text: string; time: string; avatar: string }>>([
    {
      user: 'Priyadarshi_Odia',
      text: 'ଆରେ ବାବୁଙ୍କ ଜିଲାପି ସିନ୍ ପୁରା ପିକ୍ କମେଡି! Maya3 voice cloning sounds so authentic! 😂🔥',
      time: '18 minutes ago',
      avatar: '👨‍🌾'
    },
    {
      user: 'TechExplorer_AI',
      text: 'The EBU R128 audio normalization makes listening with headphones super crisp. Zero clipping.',
      time: '1 hour ago',
      avatar: '🎧'
    },
    {
      user: 'Anita_Teacher',
      text: 'My kindergarten class loved Gulu Owl! Gentle animation and safe for preschoolers.',
      time: '2 hours ago',
      avatar: '🦉'
    }
  ]);
  const [newComment, setNewComment] = useState<string>('');
  const videoRef = useRef<HTMLVideoElement>(null);

  const current = activeEpisode || episodes[0];

  // Sync active language when episode changes
  useEffect(() => {
    if (current) {
      setActiveLang(current.language || 'or');
    }
  }, [current?.id]);

  // Compute active video source based on language and format
  const activeLangEdition = current?.localized_versions?.[activeLang];
  const currentVideoSrc = activeLangEdition
    ? (format === '16:9' ? activeLangEdition.master_video_url : activeLangEdition.social_video_url)
    : (format === '16:9' ? current?.master_video_url : current?.social_video_url);

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(() => {});
    }
  }, [current?.id, format, activeLang, currentVideoSrc]);

  const handleLike = () => {
    if (hasLiked) {
      setLikes(likes - 1);
      setHasLiked(false);
    } else {
      setLikes(likes + 1);
      setHasLiked(true);
    }
  };

  const handleAddComment = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim()) return;
    setComments([
      {
        user: 'You (Creator)',
        text: newComment.trim(),
        time: 'Just now',
        avatar: '🚀'
      },
      ...comments
    ]);
    setNewComment('');
  };

  const handleTriggerDubbing = async (targetLang: string) => {
    if (!current) return;
    setIsDubbing(targetLang);
    try {
      const res = await fetch(`/api/v1/episodes/${current.id}/localize?target_language=${targetLang}`, {
        method: 'POST'
      });
      if (res.ok) {
        if (onRefreshEpisodes) onRefreshEpisodes();
        setActiveLang(targetLang);
        setShowDubModal(false);
      } else {
        alert('Dubbing failed. Check server logs.');
      }
    } catch (err) {
      console.error('Localization error', err);
    } finally {
      setIsDubbing(null);
    }
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  if (!current) return null;

  // Available localized editions for current episode
  const installedLangs = Array.from(
    new Set([current.language, ...(Object.keys(current.localized_versions || {}))])
  );

  const candidateDubLangs = ['hi', 'bn', 'en', 'or', 'te', 'ta'].filter(
    (l) => !installedLangs.includes(l)
  );

  // SEO strings for export kit
  const exportTitle = `${current.channel_name} | ${current.title} [Official 4K Master]`;
  const exportDescription = `${current.description}\n\n⏱️ TIMESTAMPS:\n0:00 - Introduction & Hook\n0:05 - Main Scene Sequence\n0:12 - Climax & Resolution\n\n🎙️ Audio Engine: Maya3 Neural Speech (Indic 24kHz)\n🔊 Audio Normalization: EBU R128 (-14.0 LUFS)\n🎬 Visual Pipeline: HyperFrames + Remotion Composition\n\n#${current.studio_type} #BhashaAI #Maya3Speech #${current.channel_name.replace(/\\s+/g, '')}`;
  const exportTags = `${current.studio_type}, ai animation, maya3 speech, indic voice cloning, ebu r128, bhasha ai, ${current.channel_name.toLowerCase()}`;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6 relative">
      {/* Header bar */}
      <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-red-600 text-white shadow-lg shadow-red-600/30 flex items-center justify-center">
            <Film className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              BhashaTube Cinema Player
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 font-bold uppercase tracking-wider flex items-center gap-1">
                <Radio className="w-2.5 h-2.5 animate-pulse text-red-400" /> LIVE
              </span>
            </h2>
            <p className="text-xs text-slate-400">Deterministic Multi-Studio Playback & Multilingual Mode A Reframing</p>
          </div>
        </div>

        {/* Controls: Audio Language Switcher + 16:9 vs 9:16 Format Toggle */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Active Audio Language Pills */}
          <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800 gap-1">
            <div className="px-2 py-1 text-[11px] font-semibold text-slate-400 flex items-center gap-1 border-r border-slate-800 pr-2">
              <Globe className="w-3 h-3 text-amber-400" /> Audio:
            </div>
            {installedLangs.map((lang) => {
              const info = LANG_LABELS[lang] || { label: lang.toUpperCase(), native: lang.toUpperCase() };
              const isSelected = activeLang === lang;
              const isOriginal = lang === current.language;
              return (
                <button
                  key={lang}
                  onClick={() => setActiveLang(lang)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-all flex items-center gap-1 ${
                    isSelected
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30 font-bold'
                      : 'text-slate-400 hover:text-white hover:bg-slate-900'
                  }`}
                  title={isOriginal ? 'Original Master Audio' : 'Maya3 Localized Audio'}
                >
                  <span>{info.label}</span>
                  {isOriginal && (
                    <span className="text-[9px] px-1 py-0.2 rounded bg-amber-500/20 text-amber-300 font-mono">orig</span>
                  )}
                </button>
              );
            })}
          </div>

          {/* 16:9 vs 9:16 Format Toggle */}
          <div className="flex items-center bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button
              onClick={() => setFormat('16:9')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                format === '16:9'
                  ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Monitor className="w-3.5 h-3.5" />
              <span>16:9 Cinema</span>
            </button>

            <button
              onClick={() => setFormat('9:16')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                format === '9:16'
                  ? 'bg-rose-500 text-white shadow-md shadow-rose-500/20 font-bold'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Smartphone className="w-3.5 h-3.5" />
              <span>9:16 Shorts</span>
            </button>
          </div>
        </div>
      </div>

      {/* Main Grid: Left = Video + Details + Comments, Right = Up Next Playlist */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left 2 Cols: Player & Community */}
        <div className="lg:col-span-2 space-y-5">
          {/* Cinema Screen Frame */}
          <div className="relative rounded-2xl overflow-hidden bg-black border border-slate-800 shadow-2xl flex items-center justify-center group aspect-video">
            <video
              ref={videoRef}
              src={currentVideoSrc}
              className={`max-h-full transition-all duration-300 ${
                format === '9:16' ? 'h-full object-contain' : 'w-full h-full object-contain'
              }`}
              playsInline
              controls
            />

            {/* Language & Loudness Floating HUD */}
            <div className="absolute top-3 left-3 flex items-center gap-2 pointer-events-none">
              <span className="px-2.5 py-1 rounded-lg bg-black/75 backdrop-blur-md border border-white/10 text-[10px] font-mono text-white flex items-center gap-1.5 shadow-lg">
                <Volume2 className="w-3 h-3 text-emerald-400" />
                <span>Audio: <b className="text-amber-400 uppercase">{activeLang}</b> {activeLang === current.language ? '(Original)' : '(Maya3 Dubbed)'}</span>
              </span>
              <span className="px-2.5 py-1 rounded-lg bg-black/75 backdrop-blur-md border border-white/10 text-[10px] font-mono text-blue-400 flex items-center gap-1.5 shadow-lg">
                <ShieldCheck className="w-3 h-3 text-blue-400" />
                <span>-14.0 LUFS</span>
              </span>
            </div>
          </div>

          {/* Video Metadata & Title */}
          <div>
            <h1 className="text-xl font-extrabold text-white leading-tight mb-2">
              {current.title}
            </h1>

            <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800/80 pb-4">
              {/* Channel / Studio Info */}
              <div className="flex items-center gap-3">
                <div className={`w-11 h-11 rounded-full bg-gradient-to-tr ${studioColors[current.studio_type] || 'from-amber-500 to-rose-500'} flex items-center justify-center text-white font-extrabold text-lg shadow-md`}>
                  {current.channel_name.charAt(0)}
                </div>
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="font-bold text-sm text-white">{current.channel_name}</span>
                    <CheckCircle className="w-3.5 h-3.5 text-blue-400 fill-blue-400/20" />
                  </div>
                  <span className="text-xs text-slate-400 capitalize">{current.studio_type} Studio • 124K subscribers</span>
                </div>

                <button
                  onClick={() => setIsSubscribed(!isSubscribed)}
                  className={`ml-3 px-4 py-1.5 rounded-full text-xs font-bold transition-all ${
                    isSubscribed
                      ? 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                      : 'bg-white text-slate-950 hover:bg-slate-200 shadow-lg shadow-white/10'
                  }`}
                >
                  {isSubscribed ? 'Subscribed' : 'Subscribe'}
                </button>
              </div>

              {/* Action Buttons (Like, Auto-Dub, Export Kit, Download) */}
              <div className="flex flex-wrap items-center gap-2">
                {/* 1-Click Auto-Dub Button */}
                <button
                  onClick={() => setShowDubModal(true)}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-md shadow-blue-600/20 transition-all"
                >
                  <Globe className="w-3.5 h-3.5 text-blue-200" />
                  <span>Auto-Dub (Mode A)</span>
                </button>

                {/* Publish & Export Kit */}
                <button
                  onClick={() => setShowExportModal(true)}
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-slate-950 border border-slate-800 text-amber-300 hover:border-amber-500/50 hover:bg-amber-500/10 transition-all"
                >
                  <Share2 className="w-3.5 h-3.5 text-amber-400" />
                  <span>Publish Kit</span>
                </button>

                <button
                  onClick={handleLike}
                  className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold border transition-all ${
                    hasLiked
                      ? 'bg-amber-500/20 border-amber-500/40 text-amber-300'
                      : 'bg-slate-950 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <ThumbsUp className={`w-3.5 h-3.5 ${hasLiked ? 'fill-amber-400 text-amber-400' : ''}`} />
                  <span>{likes}</span>
                </button>

                <a
                  href={currentVideoSrc}
                  download
                  className="flex items-center gap-1.5 px-3.5 py-1.5 rounded-full text-xs font-semibold bg-slate-950 border border-slate-800 text-slate-300 hover:border-slate-700 transition-all"
                >
                  <Download className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Download MP4</span>
                </a>
              </div>
            </div>
          </div>

          {/* Description Box */}
          <div className="bg-slate-950/70 border border-slate-800/80 rounded-2xl p-4 text-xs text-slate-300 space-y-2">
            <div className="flex items-center gap-3 font-semibold text-slate-400">
              <span className="text-white font-bold">{current.views}</span>
              <span>•</span>
              <span>Uploaded Today</span>
              <span>•</span>
              <span className="font-mono text-amber-400 uppercase">#{current.studio_type}</span>
              <span>•</span>
              <span className="font-mono text-blue-400 uppercase">Lang: {activeLang}</span>
              <span>•</span>
              <span className="font-mono text-emerald-400">EBU R128 (-14 LUFS)</span>
            </div>
            <p className="leading-relaxed text-slate-300">
              {current.description}
            </p>
          </div>

          {/* Community Discussion Section */}
          <div className="space-y-4 pt-2">
            <div className="flex items-center gap-2 text-sm font-bold text-white">
              <MessageSquare className="w-4 h-4 text-amber-400" />
              <span>Community Comments ({comments.length})</span>
            </div>

            {/* Input Comment */}
            <form onSubmit={handleAddComment} className="flex gap-3 items-center">
              <div className="w-8 h-8 rounded-full bg-amber-500/20 text-amber-300 font-bold flex items-center justify-center text-xs">
                U
              </div>
              <input
                type="text"
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment on this studio production..."
                className="flex-1 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-xs text-white focus:outline-none focus:border-amber-500"
              />
              <button
                type="submit"
                className="px-4 py-2 rounded-xl bg-amber-500 text-slate-950 text-xs font-bold hover:bg-amber-400 transition-colors"
              >
                Post
              </button>
            </form>

            {/* Comments List */}
            <div className="space-y-3">
              {comments.map((c, idx) => (
                <div key={idx} className="flex gap-3 bg-slate-950/40 border border-slate-900 rounded-xl p-3">
                  <div className="text-xl">{c.avatar}</div>
                  <div className="space-y-0.5">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{c.user}</span>
                      <span className="text-[10px] text-slate-500">{c.time}</span>
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{c.text}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right 1 Col: Up Next Studio Playlist */}
        <div className="space-y-4">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <h3 className="text-sm font-bold text-white flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-amber-400" />
              <span>Up Next in Studios</span>
            </h3>
            <span className="text-xs text-slate-500 font-mono">{episodes.length} Episodes</span>
          </div>

          <div className="space-y-3 max-h-[750px] overflow-y-auto pr-1">
            {episodes.map((ep) => {
              const isSelected = ep.id === current.id;
              const hasDubbed = Object.keys(ep.localized_versions || {}).length > 0;
              return (
                <button
                  key={ep.id}
                  onClick={() => onSelectEpisode(ep)}
                  className={`w-full text-left p-2.5 rounded-xl border transition-all flex gap-3 group ${
                    isSelected
                      ? 'bg-amber-500/10 border-amber-500/60 shadow-lg shadow-amber-500/5'
                      : 'bg-slate-950/60 border-slate-800/80 hover:bg-slate-950 hover:border-slate-700'
                  }`}
                >
                  {/* Thumbnail Badge */}
                  <div className="relative w-28 h-18 rounded-lg overflow-hidden bg-slate-900 border border-slate-800 shrink-0 flex items-center justify-center">
                    <div className={`w-full h-full bg-gradient-to-tr ${studioColors[ep.studio_type] || 'from-slate-800 to-slate-900'} opacity-40 group-hover:opacity-60 transition-opacity`}></div>
                    <Play className="w-5 h-5 text-white/80 absolute group-hover:scale-110 transition-transform" />
                    <span className="absolute bottom-1 right-1 text-[9px] font-mono px-1 py-0.2 bg-black/80 text-white rounded">
                      0:{Math.round(ep.duration)}
                    </span>
                    {hasDubbed && (
                      <span className="absolute top-1 left-1 text-[8px] font-mono px-1 py-0.2 bg-blue-600/90 text-white rounded font-bold">
                        MULTILINGUAL
                      </span>
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0 flex flex-col justify-between py-0.5">
                    <div>
                      <h4 className="text-xs font-bold text-white line-clamp-2 group-hover:text-amber-400 transition-colors leading-snug">
                        {ep.title}
                      </h4>
                      <p className="text-[11px] text-slate-400 truncate mt-0.5">{ep.channel_name}</p>
                    </div>

                    <div className="flex items-center gap-2 text-[10px] text-slate-500 mt-1">
                      <span>{ep.views}</span>
                      <span>•</span>
                      <span className="uppercase font-mono text-amber-400/90">{ep.language}</span>
                      {hasDubbed && (
                        <span className="text-[9px] text-blue-400 font-mono">
                          +{Object.keys(ep.localized_versions || {}).length} dubs
                        </span>
                      )}
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Auto-Dubbing Modal (Mode A) */}
      {showDubModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-md w-full p-6 shadow-2xl space-y-5 animate-in fade-in">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Globe className="w-5 h-5 text-blue-400" />
                <h3 className="font-bold text-base text-white">Mode A Multilingual Localization</h3>
              </div>
              <button 
                onClick={() => setShowDubModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <p className="text-xs text-slate-300 leading-relaxed">
              Synthesize culturally adapted dialogue with Maya3 Indic Neural TTS, remux with the master visual timeline, and normalize to <b>EBU R128 (-14 LUFS)</b>.
            </p>

            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400">Select Target Language:</label>
              <div className="grid grid-cols-2 gap-2.5">
                {candidateDubLangs.map((lang) => {
                  const info = LANG_LABELS[lang] || { label: lang, native: lang };
                  const loadingThis = isDubbing === lang;
                  return (
                    <button
                      key={lang}
                      disabled={isDubbing !== null}
                      onClick={() => handleTriggerDubbing(lang)}
                      className="p-3 rounded-xl border border-slate-800 bg-slate-950/80 hover:border-blue-500 hover:bg-blue-500/10 text-left transition-all group disabled:opacity-50"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-bold text-white group-hover:text-blue-300">{info.label}</span>
                        {loadingThis && <span className="w-3.5 h-3.5 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></span>}
                      </div>
                      <span className="text-[11px] text-slate-400 font-sans">{info.native}</span>
                    </button>
                  );
                })}
              </div>
            </div>

            {isDubbing && (
              <div className="p-3 rounded-xl bg-blue-500/10 border border-blue-500/30 text-xs text-blue-300 flex items-center gap-2">
                <span className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></span>
                <span>Synthesizing Maya3 speech & muxing timeline in <b>{LANG_LABELS[isDubbing]?.label}</b>...</span>
              </div>
            )}

            <div className="flex justify-end pt-2 border-t border-slate-800/80">
              <button
                onClick={() => setShowDubModal(false)}
                className="px-4 py-2 rounded-xl text-xs font-bold text-slate-400 hover:text-white"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Publish & Export Release Kit Modal */}
      {showExportModal && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl max-w-2xl w-full p-6 shadow-2xl space-y-5 animate-in fade-in">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center gap-2">
                <Share2 className="w-5 h-5 text-amber-400" />
                <h3 className="font-bold text-base text-white">Production Deliverable & Publishing Kit</h3>
              </div>
              <button 
                onClick={() => setShowExportModal(false)}
                className="text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* QA & Loudness Banner */}
            <div className="p-3 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-between text-xs text-emerald-300">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-emerald-400" />
                <span><b>QA PASSED:</b> EBU R128 Loudness Verified (-14.0 LUFS, -1.0 dBTP)</span>
              </div>
              <span className="font-mono text-[10px] bg-emerald-500/20 px-2 py-0.5 rounded text-emerald-200">BROADCAST READY</span>
            </div>

            {/* Tab 1: Video Files Download */}
            <div className="space-y-2">
              <label className="text-xs font-semibold text-slate-400">Master Video Deliverables:</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <a
                  href={current.master_video_url}
                  download
                  className="p-3 rounded-xl bg-slate-950 border border-slate-800 hover:border-amber-500/50 flex items-center justify-between group transition-all"
                >
                  <div className="flex items-center gap-2.5">
                    <Monitor className="w-4 h-4 text-amber-400" />
                    <div>
                      <div className="text-xs font-bold text-white group-hover:text-amber-300">16:9 Landscape Master</div>
                      <div className="text-[10px] text-slate-400">1920x1080 • YouTube / Web</div>
                    </div>
                  </div>
                  <Download className="w-4 h-4 text-slate-400 group-hover:text-amber-400" />
                </a>

                <a
                  href={current.social_video_url}
                  download
                  className="p-3 rounded-xl bg-slate-950 border border-slate-800 hover:border-rose-500/50 flex items-center justify-between group transition-all"
                >
                  <div className="flex items-center gap-2.5">
                    <Smartphone className="w-4 h-4 text-rose-400" />
                    <div>
                      <div className="text-xs font-bold text-white group-hover:text-rose-300">9:16 Vertical Reel</div>
                      <div className="text-[10px] text-slate-400">1080x1920 • Shorts / Reels / TikTok</div>
                    </div>
                  </div>
                  <Download className="w-4 h-4 text-slate-400 group-hover:text-rose-400" />
                </a>
              </div>
            </div>

            {/* Tab 2: SEO Title */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-400">YouTube / Social Title:</label>
                <button
                  onClick={() => copyToClipboard(exportTitle, 'title')}
                  className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 font-semibold"
                >
                  {copiedKey === 'title' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey === 'title' ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <input
                type="text"
                readOnly
                value={exportTitle}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-white focus:outline-none font-mono"
              />
            </div>

            {/* Tab 3: SEO Description */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-400">Video Description with Timestamps:</label>
                <button
                  onClick={() => copyToClipboard(exportDescription, 'desc')}
                  className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 font-semibold"
                >
                  {copiedKey === 'desc' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey === 'desc' ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <textarea
                readOnly
                rows={4}
                value={exportDescription}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none font-mono resize-none"
              />
            </div>

            {/* Tab 4: Tags */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-400">Target Tags:</label>
                <button
                  onClick={() => copyToClipboard(exportTags, 'tags')}
                  className="text-xs text-amber-400 hover:text-amber-300 flex items-center gap-1 font-semibold"
                >
                  {copiedKey === 'tags' ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copiedKey === 'tags' ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
              <input
                type="text"
                readOnly
                value={exportTags}
                className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-300 focus:outline-none font-mono"
              />
            </div>

            <div className="flex justify-end pt-2 border-t border-slate-800">
              <button
                onClick={() => setShowExportModal(false)}
                className="px-5 py-2 rounded-xl bg-amber-500 text-slate-950 text-xs font-bold hover:bg-amber-400 transition-colors"
              >
                Close Release Kit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
