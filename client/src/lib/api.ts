import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
const AUDIO_BASE_URL = import.meta.env.VITE_AUDIO_BASE_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface VideoMetadata {
  video_id: string;
  title: string;
  duration: number;
  uploader?: string;
  description?: string;
  upload_date?: string;
  thumbnail?: string;
  url?: string;
  [key: string]: unknown;
}

export interface ClipData {
  clip_name: string;
  duration: number;
  start_time: number;
  end_time: number;
  padded_duration: number;
}

export interface AudioSplitResponse {
  success: boolean;
  message: string;
  video_id: string;
  domain: string;
  video_metadata: VideoMetadata;
  clips: ClipData[];
  total_clips: number;
  start_padding: number;
  end_padding: number;
}

export interface TranscribedClip {
  clip_name: string;
  transcription: string | null;  // Allow null for failed transcriptions
}

export interface TranscriptionResponse {
  success: boolean;
  message: string;
  video_id: string;
  transcribed_clips: TranscribedClip[];
  total_transcribed: number;
  failed_clips: string[];
}

export interface ProcessedClip {
  clip_name: string;
  cloud_url: string | null;
  database_id: string | null;
}

export interface CloudStorageResponse {
  success: boolean;
  message: string;
  video_id: string;
  processed_clips: ProcessedClip[];
  total_processed: number;
  failed_clips: string[];
}

export const audioApi = {
  splitAudio: async (
    youtubeUrl: string,
    domain: string,
    vadAggressiveness: number = 2,
    startPadding: number = 1.0,
    endPadding: number = 0.5
  ): Promise<AudioSplitResponse> => {
    const response = await api.post('/split-audio', {
      youtube_url: youtubeUrl,
      domain: domain,
      vad_aggressiveness: vadAggressiveness,
      start_padding: startPadding,
      end_padding: endPadding,
    });
    return response.data;
  },

  transcribeClips: async (videoId: string, clipNames?: string[]): Promise<TranscriptionResponse> => {
    const response = await api.post('/transcribe-clips', {
      video_id: videoId,
      clip_names: clipNames,
    });
    return response.data;
  },

  saveToCloud: async (videoId: string, clipNames?: string[]): Promise<CloudStorageResponse> => {
    const response = await api.post('/save-clips', {
      video_id: videoId,
      clip_names: clipNames,
      upload_to_cloud_bucket: true,
      add_to_transcription_service: true,
    });
    return response.data;
  },

  deleteAudioFiles: async (videoId: string): Promise<{ success: boolean; message: string; deleted_files: string[]; total_deleted: number }> => {
    const response = await api.delete(`/delete-audio/${videoId}`);
    return response.data;
  },

  cleanNullTranscriptions: async (videoId: string): Promise<{ success: boolean; message: string; deleted_files: string[]; total_deleted: number; remaining_clips: number }> => {
    const response = await api.post(`/clean-transcriptions/${videoId}`);
    return response.data;
  },

  getAudioFile: (videoId: string, clipName: string): string => {
    return `${AUDIO_BASE_URL}/output/${videoId}/${clipName}`;
  },
};
