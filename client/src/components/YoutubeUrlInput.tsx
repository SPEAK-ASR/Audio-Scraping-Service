import { useState, useEffect } from 'react';
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
  onClipsGenerated: (videoId: string, domain: string, metadata: VideoMetadata, clips: ClipData[]) => void;
  onError: (errorMessage: string) => void;
  initialError?: string | null;
}

export function YoutubeUrlInput({ onSubmit, onClipsGenerated, onError, initialError }: YoutubeUrlInputProps) {
  const [url, setUrl] = useState('');
  const [domain, setDomain] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(initialError || null);

  // Update error when initialError changes
  useEffect(() => {
    setError(initialError || null);
  }, [initialError]);
  
  // Advanced parameters with default values
  const [vadAggressiveness, setVadAggressiveness] = useState(2);
  const [startPadding, setStartPadding] = useState(1);
  const [endPadding, setEndPadding] = useState(0.5);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim() || !domain) return;

    setIsLoading(true);
    setError(null);
    onSubmit();

    try {
      const response = await audioApi.splitAudio(url, domain, vadAggressiveness, startPadding, endPadding);
      if (response.success) {
        onClipsGenerated(response.video_id, response.domain, response.video_metadata, response.clips);
      } else {
        setError('Failed to process YouTube video');
        setIsLoading(false);
      }
    } catch (err) {
      let errorMessage = 'An error occurred';
      
      if (err && typeof err === 'object' && 'response' in err) {
        const axiosError = err as any;
        if (axiosError.response?.status === 409) {
          // Handle video already exists error
          const errorData = axiosError.response?.data;
          if (errorData && typeof errorData === 'object' && errorData.detail) {
            if (typeof errorData.detail === 'object' && errorData.detail.error === 'VIDEO_ALREADY_EXISTS') {
              errorMessage = `Video "${errorData.detail.video_title}" has already been processed. ${errorData.detail.suggestion}`;
            } else if (typeof errorData.detail === 'string') {
              errorMessage = errorData.detail;
            }
          } else {
            errorMessage = 'This video has already been processed';
          }
        } else if (axiosError.response?.status === 500) {
          // Handle database connection errors
          const errorData = axiosError.response?.data;
          if (errorData && typeof errorData === 'object' && errorData.detail) {
            if (typeof errorData.detail === 'string' && errorData.detail.includes('Database connection error')) {
              errorMessage = 'Database connection error. Please check if the database server is running and try again.';
            } else {
              errorMessage = 'Server error occurred. Please try again later.';
            }
          } else {
            errorMessage = 'Server error occurred. Please try again later.';
          }
        } else if (axiosError.response?.data?.detail) {
          errorMessage = typeof axiosError.response.data.detail === 'string' 
            ? axiosError.response.data.detail 
            : 'Processing failed';
        } else if (axiosError.message) {
          errorMessage = axiosError.message;
        }
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      setIsLoading(false);
      onError(errorMessage); // Reset to input step in parent component
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
            onChange={(e) => {
              setUrl(e.target.value);
              if (error) setError(null); // Clear error when user starts typing
            }}
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

          {/* Domain Selection */}
          <FormControl size="small" fullWidth required error={!domain && error !== null}>
            <InputLabel>Video Category *</InputLabel>
            <Select
              value={domain}
              label="Video Category *"
              onChange={(e) => {
                setDomain(e.target.value);
                if (error) setError(null);
              }}
              disabled={isLoading}
            >
              <MenuItem value="education">Education</MenuItem>
              <MenuItem value="health">Health</MenuItem>
              <MenuItem value="politics_and_government">Politics and Government</MenuItem>
              <MenuItem value="news_and_current_affairs">News and Current Affairs</MenuItem>
              <MenuItem value="science">Science</MenuItem>
              <MenuItem value="technology_and_computing">Technology and Computing</MenuItem>
              <MenuItem value="business_and_finance">Business and Finance</MenuItem>
              <MenuItem value="entertainment">Entertainment</MenuItem>
              <MenuItem value="food_and_drink">Food and Drink</MenuItem>
              <MenuItem value="law_and_justice">Law and Justice</MenuItem>
              <MenuItem value="environment_and_sustainability">Environment and Sustainability</MenuItem>
              <MenuItem value="religion">Religion</MenuItem>
              <MenuItem value="media_marketing">Media Marketing</MenuItem>
              <MenuItem value="history_and_cultural">History and Cultural</MenuItem>
              <MenuItem value="work_and_careers">Work and Careers</MenuItem>
              <MenuItem value="others">Others</MenuItem>
            </Select>
          </FormControl>

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
            <Alert 
              severity={error.includes('already been processed') ? 'warning' : 'error'} 
              sx={{ 
                fontSize: '0.875rem',
                '& .MuiAlert-message': {
                  fontSize: '0.875rem'
                }
              }}
            >
              {error}
            </Alert>
          )}

          <Button
            type="submit"
            variant="contained"
            disabled={!url.trim() || !domain || !isValidYoutubeUrl(url) || isLoading}
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
