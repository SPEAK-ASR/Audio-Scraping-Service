import { useState, useRef, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  IconButton,
  Slider,
  Box,
  Button,
  Chip,
  LinearProgress,
  CircularProgress
} from '@mui/material';
import {
  PlayArrow,
  Pause,
  VolumeUp,
  Transcribe,
  CloudUpload,
  Storage,
  Refresh
} from '@mui/icons-material';
import { audioApi, type ClipData, type TranscribedClip, type ProcessedClip, type VideoMetadata } from '../lib/api';
import type { ProcessingStep } from '../App';

interface AudioClipsDisplayProps {
  videoId: string;
  clips: ClipData[];
  videoMetadata: VideoMetadata | null;
  onTranscriptionComplete: (transcriptions: TranscribedClip[]) => void;
  onTranscriptionStart: () => void;
  onStorageStart: () => void;
  onStorageComplete: () => void;
  onRevert: () => void;
  currentStep: ProcessingStep;
  isTranscribing: boolean;
}

interface AudioPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
}

export function AudioClipsDisplay({ 
  videoId, 
  clips, 
  videoMetadata,
  onTranscriptionComplete,
  onTranscriptionStart,
  onStorageStart,
  onStorageComplete,
  onRevert,
  currentStep,
  isTranscribing
}: AudioClipsDisplayProps) {
  const [selectedClip, setSelectedClip] = useState<ClipData | null>(null);
  const [currentlyPlaying, setCurrentlyPlaying] = useState<string | null>(null);
  const [playerState, setPlayerState] = useState<AudioPlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: 1
  });
  const [isReverting, setIsReverting] = useState(false);
  const [, setTranscriptions] = useState<TranscribedClip[]>([]);
  const [, setProcessedClips] = useState<ProcessedClip[]>([]);
  
  const audioRef = useRef<HTMLAudioElement>(null);

  // Helper functions - defined before use
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const videoTitle = videoMetadata?.title ?? 'Video title unavailable';
  const videoAuthor = videoMetadata?.uploader ?? 'Unknown creator';
  const totalDurationSeconds = typeof videoMetadata?.duration === 'number' ? videoMetadata.duration : 0;
  const formattedVideoDuration = totalDurationSeconds > 0 ? formatTime(totalDurationSeconds) : '–';

  // Select first clip on component mount
  useEffect(() => {
    if (clips.length > 0 && !selectedClip) {
      setSelectedClip(clips[0]);
    }
  }, [clips, selectedClip]);

  const formatDuration = (seconds: number) => {
    return `${seconds.toFixed(1)}s`;
  };

  const handlePlayPause = () => {
    const audio = audioRef.current;
    if (!audio || !selectedClip) return;

    if (currentlyPlaying === selectedClip.clip_name) {
      audio.pause();
      setCurrentlyPlaying(null);
    } else {
      setCurrentlyPlaying(selectedClip.clip_name);
      audio.play();
    }
  };

  const handleVolumeChange = (volume: number) => {
    const audio = audioRef.current;
    if (audio) {
      audio.volume = volume;
      setPlayerState(prev => ({ ...prev, volume }));
    }
  };

  const handleTimeUpdate = (audio: HTMLAudioElement) => {
    setPlayerState(prev => ({
      ...prev,
      currentTime: audio.currentTime,
      duration: audio.duration || 0,
      isPlaying: !audio.paused
    }));
  };

  const handleAudioEnded = () => {
    setCurrentlyPlaying(null);
    setPlayerState(prev => ({ ...prev, isPlaying: false, currentTime: 0 }));
    
    // Auto-play next clip if available
    const currentIndex = clips.findIndex(clip => clip.clip_name === selectedClip?.clip_name);
    if (currentIndex >= 0 && currentIndex < clips.length - 1) {
      setSelectedClip(clips[currentIndex + 1]);
    }
  };

  const handleClipSelect = (clip: ClipData) => {
    const audio = audioRef.current;
    if (audio) {
      audio.pause();
    }
    setSelectedClip(clip);
    setCurrentlyPlaying(null);
    setPlayerState(prev => ({ ...prev, isPlaying: false, currentTime: 0 }));
  };

  const handleTranscribe = async () => {
    // Immediately move to transcription stage with loading state
    onTranscriptionStart();
    
    try {
      const response = await audioApi.transcribeClips(videoId);
      if (response.success) {
        setTranscriptions(response.transcribed_clips);
        onTranscriptionComplete(response.transcribed_clips);
      }
    } catch (error) {
      console.error('Transcription failed:', error);
      // On error, reset transcribing state
      onTranscriptionComplete([]);
    }
  };

  const handleSaveToCloud = async () => {
    // Immediately move to storage stage with loading state
    onStorageStart();
    
    try {
      const response = await audioApi.saveToCloud(videoId);
      if (response.success) {
        setProcessedClips(response.processed_clips);
        onStorageComplete();
      }
    } catch (error) {
      console.error('Cloud storage failed:', error);
      // On error, could handle going back or staying on transcription
      onStorageComplete(); // This will move to complete even on error - you might want different handling
    }
  };

  const handleRevert = async () => {
    setIsReverting(true);
    try {
      await audioApi.deleteAudioFiles(videoId);
      onRevert();
    } catch (error) {
      console.error('Revert failed:', error);
    } finally {
      setIsReverting(false);
    }
  };

  return (
    <div>
      {/* Audio Playlist - Only show when not in transcription, storage, or complete step */}
      {currentStep !== 'transcription' && currentStep !== 'storage' && currentStep !== 'complete' && (
        <Box sx={{ 
          maxWidth: 800, 
          mx: 'auto',
          bgcolor: 'background.paper',
          borderRadius: 2,
          boxShadow: 3,
          p: 2
        }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box>
            <Typography variant="h6" component="h4" fontWeight="600" sx={{ mb: 1, fontSize: '1.2rem' }}>
              {videoTitle}
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 4, fontSize: '0.875rem' }}>
              <Typography variant="caption" color="text.secondary">
                {videoAuthor} • {formattedVideoDuration} • {clips.length} clips
              </Typography>
            </Box>
          </Box>
            <Button
              onClick={handleRevert}
              disabled={isReverting}
              startIcon={
                isReverting ? (
                  <CircularProgress size={16} color="inherit" />
                ) : (
                  <Refresh />
                )
              }
              variant="outlined"
              size="small"
              color="warning"
              sx={{ 
                textTransform: 'none',
              }}
            >
              {isReverting ? 'Reverting...' : 'Start Over'}
            </Button>
          </Box>

          <Box sx={{ display: 'flex', gap: 2, height: 320 }}>
            {/* Main Audio Player - Left Side */}
            <Box sx={{ flex: '0 0 400px', display: 'flex', flexDirection: 'column' }}>
              <Box sx={{ 
                flex: 1, 
                display: 'flex', 
                flexDirection: 'column',
                bgcolor: '#151515',
                borderRadius: 2,
                boxShadow: 2,
                p: 3
              }}>
                {selectedClip ? (
                    <>
                      {/* Current Track Info */}
                      <Box sx={{ mb: 3 }}>
                        <Typography variant="h6" fontWeight="600" sx={{ fontSize: '1rem', mb: 1 }}>
                          {selectedClip.clip_name}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 2 }}>
                          <Chip 
                            label={`${formatTime(selectedClip.start_time)} - ${formatTime(selectedClip.end_time)}`}
                            size="small"
                            variant="outlined"
                            color="primary"
                            sx={{ fontSize: '0.7rem' }}
                          />
                          <Chip 
                            label={formatDuration(selectedClip.duration)}
                            size="small"
                            color="primary"
                            sx={{ fontSize: '0.7rem' }}
                          />
                        </Box>
                      </Box>

                      {/* Audio Element */}
                      <audio
                        ref={audioRef}
                        src={audioApi.getAudioFile(videoId, selectedClip.clip_name)}
                        onTimeUpdate={(e) => handleTimeUpdate(e.currentTarget)}
                        onEnded={handleAudioEnded}
                        onLoadedMetadata={(e) => handleTimeUpdate(e.currentTarget)}
                      />

                      {/* Progress Section */}
                      <Box sx={{ mb: 3 }}>
                        <LinearProgress
                          variant="determinate"
                          value={playerState.duration > 0 ? (playerState.currentTime / playerState.duration) * 100 : 0}
                          sx={{ 
                            height: 6,
                            borderRadius: 3,
                            mb: 1,
                          }}
                        />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" color="text.secondary">
                            {formatTime(playerState.currentTime)}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            {formatTime(playerState.duration)}
                          </Typography>
                        </Box>
                      </Box>

                      {/* Main Controls */}
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 3 }}>
                        <IconButton
                          onClick={handlePlayPause}
                          size="large"
                          sx={{
                            backgroundColor: 'primary.main',
                            color: 'primary.contrastText',
                            width: 64,
                            height: 64,
                            '&:hover': {
                              backgroundColor: 'primary.dark',
                              transform: 'scale(1.05)',
                            },
                            transition: 'all 0.2s ease',
                          }}
                        >
                          {currentlyPlaying === selectedClip.clip_name && playerState.isPlaying ? (
                            <Pause sx={{ fontSize: 32 }} />
                          ) : (
                            <PlayArrow sx={{ fontSize: 32 }} />
                          )}
                        </IconButton>
                      </Box>

                      {/* Volume Control */}
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <VolumeUp sx={{ color: 'primary.main' }} />
                        <Slider
                          value={playerState.volume}
                          min={0}
                          max={1}
                          step={0.05}
                          onChange={(_, value) => handleVolumeChange(value as number)}
                          sx={{ flex: 1 }}
                        />
                        <Typography variant="body2" color="text.secondary" sx={{ minWidth: 36 }}>
                          {Math.round(playerState.volume * 100)}%
                        </Typography>
                      </Box>
                    </>
                  ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', flex: 1 }}>
                      <Typography variant="body1" color="text.secondary">
                        Select a clip to play
                      </Typography>
                    </Box>
                  )}
              </Box>
            </Box>

            {/* Playlist - Right Side */}
            <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', bgcolor: '#151515', borderRadius: 1, p: 2 }}>
              <Typography variant="subtitle1" fontWeight="600" sx={{ mb: 1 }}>
                Playlist
              </Typography>
              <Box 
                sx={{ 
                  flex: 1,
                  overflowY: 'auto',
                  pr: 1,
                  '&::-webkit-scrollbar': {
                    width: '6px',
                  },
                  '&::-webkit-scrollbar-track': {
                    background: 'rgba(255, 255, 255, 0.1)',
                    borderRadius: '3px',
                  },
                  '&::-webkit-scrollbar-thumb': {
                    background: '#4F8EFF',
                    borderRadius: '3px',
                    '&:hover': {
                      background: '#7BA8FF',
                    },
                  },
                }}
              >
                {clips.map((clip, index) => (
                  <Card 
                    key={clip.clip_name}
                    onClick={() => handleClipSelect(clip)}
                    sx={{ 
                      mb: 1,
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      backgroundColor: selectedClip?.clip_name === clip.clip_name 
                        ? 'rgba(79, 142, 255, 0.2)' 
                        : 'transparent',
                      border: selectedClip?.clip_name === clip.clip_name 
                        ? '1px solid #4F8EFF' 
                        : '1px solid transparent',
                      '&:hover': {
                        backgroundColor: 'rgba(79, 142, 255, 0.1)',
                      }
                    }}
                  >
                    <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Typography variant="body2" color="text.secondary" sx={{ minWidth: 24 }}>
                          {index + 1}
                        </Typography>
                        <Box sx={{ flex: 1, minWidth: 0 }}>
                          <Typography 
                            variant="body2" 
                            fontWeight={selectedClip?.clip_name === clip.clip_name ? 600 : 400}
                            noWrap
                            sx={{ mb: 0.5 }}
                          >
                            {clip.clip_name}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1 }}>
                            <Chip 
                              label={formatDuration(clip.duration)}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.65rem', height: 18 }}
                            />
                            <Chip 
                              label={`${formatTime(clip.start_time)}-${formatTime(clip.end_time)}`}
                              size="small"
                              variant="outlined"
                              sx={{ fontSize: '0.65rem', height: 18 }}
                            />
                          </Box>
                        </Box>
                        {currentlyPlaying === clip.clip_name && (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <CircularProgress size={16} color="primary" />
                          </Box>
                        )}
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Box>
          </Box>
        </Box>
      )}

      {/* Enhanced Action Buttons */}
      {currentStep === 'clips' && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Button
            onClick={handleTranscribe}
            variant="contained"
            startIcon={<Transcribe />}
          >
            Get Transcriptions
          </Button>
        </Box>
      )}

      {currentStep === 'transcription' && !isTranscribing && (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
          <Button
            onClick={handleSaveToCloud}
            variant="contained"
            startIcon={
              <>
                <CloudUpload />
                <Storage sx={{ ml: 0.5 }} />
              </>
            }
          >
            Save to Cloud & Database
          </Button>
        </Box>
      )}
    </div>
  );
}
