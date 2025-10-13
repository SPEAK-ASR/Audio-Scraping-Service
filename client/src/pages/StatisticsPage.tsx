import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
} from '@mui/material';
import { Refresh, ArrowBack } from '@mui/icons-material';
import { statisticsApi, type StatisticsResponse } from '../lib/statisticsApi';
import { SummaryCards } from '../components/statistics/SummaryCards';
import { CategoryDurationChart } from '../components/statistics/CategoryDurationChart';
import { TranscriptionStatusChart } from '../components/statistics/TranscriptionStatusChart';
import { DailyTranscriptionGraph } from '../components/statistics/DailyTranscriptionGraph';
import { AdminContributionChart } from '../components/statistics/AdminContributionChart';
import { AudioDistributionGraph } from '../components/statistics/AudioDistributionGraph';

interface StatisticsPageProps {
  onBack?: () => void;
}

export function StatisticsPage({ onBack }: StatisticsPageProps) {
  const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);

  const fetchStatistics = async (selectedDays: number) => {
    setLoading(true);
    setError(null);
    try {
      const data = await statisticsApi.getAllStatistics(selectedDays);
      setStatistics(data);
    } catch (err) {
      console.error('Error fetching statistics:', err);
      setError(err instanceof Error ? err.message : 'Failed to load statistics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatistics(days);
  }, [days]);

  const handleRefresh = () => {
    fetchStatistics(days);
  };

  const handleDaysChange = (newDays: number) => {
    setDays(newDays);
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '60vh',
          gap: 2,
        }}
      >
        <CircularProgress size={60} />
        <Typography variant="h6" color="text.secondary">
          Loading statistics...
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
        <Button variant="contained" onClick={handleRefresh} startIcon={<Refresh />}>
          Retry
        </Button>
      </Box>
    );
  }

  if (!statistics) {
    return (
      <Box sx={{ maxWidth: 600, mx: 'auto', mt: 4 }}>
        <Alert severity="warning">No statistics data available</Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {onBack && (
              <Button
                variant="outlined"
                startIcon={<ArrowBack />}
                onClick={onBack}
                sx={{ minWidth: 'auto' }}
              >
                Back
              </Button>
            )}
            <Typography variant="h4" fontWeight="bold">
              Database Statistics
            </Typography>
          </Box>
          
          <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
            <FormControl size="small" sx={{ minWidth: 150 }}>
              <InputLabel>Time Period</InputLabel>
              <Select
                value={days}
                label="Time Period"
                onChange={(e) => handleDaysChange(Number(e.target.value))}
              >
                <MenuItem value={7}>Last 7 days</MenuItem>
                <MenuItem value={14}>Last 14 days</MenuItem>
                <MenuItem value={30}>Last 30 days</MenuItem>
                <MenuItem value={60}>Last 60 days</MenuItem>
                <MenuItem value={90}>Last 90 days</MenuItem>
                <MenuItem value={180}>Last 6 months</MenuItem>
                <MenuItem value={365}>Last year</MenuItem>
              </Select>
            </FormControl>
            
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRefresh}
            >
              Refresh
            </Button>
          </Box>
        </Box>
        
        <Typography variant="body1" color="text.secondary">
          Comprehensive overview of your audio transcription database
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ mb: 4 }}>
        <SummaryCards summary={statistics.summary} />
      </Box>

      {/* Main Charts Grid */}
      <Box sx={{ display: 'grid', gap: 3, mb: 3 }}>
        {/* Row 1: Two columns */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 3 }}>
          <TranscriptionStatusChart data={statistics.transcription_status} />
          <CategoryDurationChart data={statistics.category_durations} />
        </Box>

        {/* Row 2: Audio Distribution */}
        <AudioDistributionGraph data={statistics.audio_distribution} />

        {/* Row 3: Full width */}
        <DailyTranscriptionGraph data={statistics.daily_transcriptions} />

        {/* Row 4: Full width */}
        <AdminContributionChart data={statistics.admin_contributions} />
      </Box>

      {/* Footer info */}
      <Paper
        elevation={0}
        sx={{
          p: 2,
          mt: 4,
          backgroundColor: '#f5f5f5',
          textAlign: 'center',
        }}
      >
        <Typography variant="body2" color="text.secondary">
          Last updated: {new Date().toLocaleString()}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          All durations are calculated from audio clip padded durations
        </Typography>
      </Paper>
    </Box>
  );
}
