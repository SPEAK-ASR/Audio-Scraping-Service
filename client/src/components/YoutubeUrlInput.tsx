import { useState } from 'react';
import {
  CardContent,
  TextField,
  Button,
  Typography,
  Box,
  Alert,
  CircularProgress,
  InputAdornment,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider
} from '@mui/material';
import { YouTube, Send, Info, Settings } from '@mui/icons-material';
import { audioApi, type ClipData, type VideoMetadata } from '../lib/api';

interface YoutubeUrlInputProps {
  onSubmit: () => void;
  onClipsGenerated: (videoId: string, metadata: VideoMetadata, clips: ClipData[]) => void;
}

export function YoutubeUrlInput({ onSubmit, onClipsGenerated }: YoutubeUrlInputProps) {
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Advanced parameters with default values
  const [vadAggressiveness, setVadAggressiveness] = useState(2);
  const [startPadding, setStartPadding] = useState(1);
  const [endPadding, setEndPadding] = useState(0.5);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) return;

    setIsLoading(true);
    setError(null);
    onSubmit();

    try {
      const response = await audioApi.splitAudio(url, vadAggressiveness, startPadding, endPadding);
      if (response.success) {
        onClipsGenerated(response.video_id, response.video_metadata, response.clips);
      } else {
        setError('Failed to process YouTube video');
        setIsLoading(false);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsLoading(false);
    }
  };

  const isValidYoutubeUrl = (url: string) => {
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
    return youtubeRegex.test(url);
  };

  return (
    <Box 
      sx={{ 
        maxWidth: 600, 
        mx: 'auto',
        bgcolor: 'background.paper',
        borderRadius: 2,
        boxShadow: 3,
      }}
    >
      <CardContent sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 2, mb: 3 }}>
          <YouTube 
            sx={{ 
              fontSize: 32, 
              color: '#FF0000',
            }} 
          />
          <Typography variant="h5" component="h2" fontWeight="600" sx={{ fontSize: '1.25rem' }}>
            Enter YouTube URL
          </Typography>
        </Box>

        {/* Form */}
        <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <TextField
            fullWidth
            label="YouTube Video URL"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={isLoading}
            error={Boolean(url && !isValidYoutubeUrl(url))}
            helperText={url && !isValidYoutubeUrl(url) ? "Please enter a valid YouTube URL" : undefined}
            size="small"
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <YouTube color="primary" fontSize="small" />
                </InputAdornment>
              ),
            }}
          />

          {/* Advanced Options */}
          <Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <Settings fontSize="small" color="primary" />
              <Typography variant="subtitle2" color="text.primary" sx={{ fontSize: '0.875rem', fontWeight: 500 }}>
                Advanced Options
              </Typography>
            </Box>
            
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
              {/* VAD Aggressiveness - Compact */}
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel sx={{ fontSize: '0.875rem' }}>VAD Level</InputLabel>
                <Select
                  value={vadAggressiveness}
                  label="VAD Level"
                  onChange={(e) => setVadAggressiveness(Number(e.target.value))}
                  disabled={isLoading}
                  sx={{ fontSize: '0.875rem' }}
                >
                  <MenuItem value={0} sx={{ fontSize: '0.875rem' }}>0 - Least</MenuItem>
                  <MenuItem value={1} sx={{ fontSize: '0.875rem' }}>1 - Low</MenuItem>
                  <MenuItem value={2} sx={{ fontSize: '0.875rem' }}>2 - Moderate</MenuItem>
                  <MenuItem value={3} sx={{ fontSize: '0.875rem' }}>3 - Most</MenuItem>
                </Select>
              </FormControl>

              {/* Padding Controls - Side by Side */}
              <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                {/* Start Padding */}
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    Start Padding: {startPadding}s
                  </Typography>
                  <Slider
                    value={startPadding}
                    onChange={(_, value) => setStartPadding(value as number)}
                    min={0}
                    max={5}
                    step={0.1}
                    disabled={isLoading}
                    size="small"
                    sx={{ 
                      color: 'primary.main',
                      '& .MuiSlider-thumb': { width: 16, height: 16 },
                      '& .MuiSlider-track': { height: 3 },
                      '& .MuiSlider-rail': { height: 3 }
                    }}
                  />
                </Box>

                {/* End Padding */}
                <Box sx={{ flex: 1, minWidth: 0 }}>
                  <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.75rem' }}>
                    End Padding: {endPadding}s
                  </Typography>
                  <Slider
                    value={endPadding}
                    onChange={(_, value) => setEndPadding(value as number)}
                    min={0}
                    max={5}
                    step={0.1}
                    disabled={isLoading}
                    size="small"
                    sx={{ 
                      color: 'primary.main',
                      '& .MuiSlider-thumb': { width: 16, height: 16 },
                      '& .MuiSlider-track': { height: 3 },
                      '& .MuiSlider-rail': { height: 3 }
                    }}
                  />
                </Box>
              </Box>
            </Box>
          </Box>

          {error && (
            <Alert severity="error" sx={{ fontSize: '0.875rem' }}>
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            variant="contained"
            disabled={!url.trim() || !isValidYoutubeUrl(url) || isLoading}
            startIcon={
              isLoading ? (
                <CircularProgress size={20} color="inherit" />
              ) : (
                <Send />
              )
            }
          >
            {isLoading ? 'Processing Video...' : 'Process Video'}
          </Button>
        </Box>

        {/* Info Section */}
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
            <Info fontSize="small" />
            Video will be split using voice activity detection
          </Typography>
        </Box>
      </CardContent>
    </Box>
  );
}
