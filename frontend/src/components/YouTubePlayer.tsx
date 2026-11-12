import React, { useState, useRef, useEffect } from 'react';
import { 
  Play, ThumbsUp, Download, Smartphone, Monitor,
  CheckCircle, Sparkles, MessageSquare, Film
} from 'lucide-react';

export interface PlayableEpisode {
  id: string;
  title: string;
  studio_type: string;
  language: string;
  channel_name: string;
  description: string;
  views: string;
  duration: number;
  master_video_url: string;
  social_video_url: string;
}

interface Props {
  episodes: PlayableEpisode[];
  activeEpisode: PlayableEpisode | null;
  onSelectEpisode: (ep: PlayableEpisode) => void;
}

const studioColors: Record<string, string> = {
  entertainment: 'from-amber-500 to-rose-500',
  kids: 'from-emerald-400 to-teal-500',
  education: 'from-blue-500 to-indigo-600',
  podcast: 'from-purple-500 to-pink-500',
  news: 'from-red-500 to-orange-500',
  marketing: 'from-yellow-400 to-amber-600'
};

export const YouTubePlayer: React.FC<Props> = ({ episodes, activeEpisode, onSelectEpisode }) => {
  const [format, setFormat] = useState<'16:9' | '9:16'>('16:9');
  const [likes, setLikes] = useState<number>(342);
  const [hasLiked, setHasLiked] = useState<boolean>(false);
  const [isSubscribed, setIsSubscribed] = useState<boolean>(true);
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

  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.load();
      videoRef.current.play().catch(() => {});
    }
  }, [current?.id, format]);

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

  if (!current) return null;

  const currentVideoSrc = format === '16:9' ? current.master_video_url : current.social_video_url;

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-3xl p-6 shadow-2xl space-y-6">
      {/* Header bar */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-red-600 text-white shadow-lg shadow-red-600/30 flex items-center justify-center">
            <Film className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-white flex items-center gap-2">
              BhashaTube Cinema Player
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-red-500/20 text-red-400 border border-red-500/30 font-bold uppercase tracking-wider">
                LIVE
              </span>
            </h2>
            <p className="text-xs text-slate-400">Deterministic Multi-Studio Playback & Social Reframing</p>
          </div>
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

              {/* Action Buttons (Like, Share, Download, Badges) */}
              <div className="flex items-center gap-2">
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

                <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-slate-950 border border-slate-800 text-[11px] font-mono text-slate-400">
                  <span className="text-blue-400 font-bold">EBU R128</span> -14 LUFS
                </div>
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
              <span className="font-mono text-blue-400 uppercase">Lang: {current.language}</span>
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
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
};
