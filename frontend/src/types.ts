export interface LocalizedEdition {
  master_video_url: string;
  social_video_url: string;
}

export interface PlayableEpisode {
  id: string;
  title: string;
  studio_type: string;
  language: string;
  available_languages?: string[];
  channel_name: string;
  description: string;
  views: string;
  duration: number;
  master_video_url: string;
  social_video_url: string;
  localized_versions?: Record<string, LocalizedEdition>;
}

export interface Studio {
  id: string;
  name: string;
  description: string;
  render_engine: string;
  primary_language: string;
  status: 'active' | 'ready' | 'beta';
}

export interface Character {
  id: string;
  name: string;
  role: string;
  bio: string;
  personality: string;
}

export interface ProductionRunResponse {
  episode_id: string;
  status: string;
  title: string;
  studio_type: string;
  language: string;
  master_video_path?: string;
  social_video_path?: string;
  duration_seconds: number;
  total_cost_usd: number;
  qa_passed: boolean;
  qa_report: {
    duration_seconds?: number;
    video_codec?: string;
    audio_codec?: string;
    passed?: boolean;
    format?: string;
  };
  cost_summary: {
    finished_duration_seconds?: number;
    total_cost_usd?: number;
    cost_per_minute_usd?: number;
    target_ceiling_usd?: number;
    within_budget?: boolean;
    breakdown?: Record<string, number>;
  };
  logs: string[];
}
