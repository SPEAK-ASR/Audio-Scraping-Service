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
  MenuItem
} from '@mui/material';
import { Refresh } from '@mui/icons-material';
import { statisticsApi, type StatisticsResponse } from '../lib/statisticsApi';
import { SummaryCards } from '../components/statistics/SummaryCards';
import { CategoryDurationChart } from '../components/statistics/CategoryDurationChart';
import { TranscriptionStatusChart } from '../components/statistics/TranscriptionStatusChart';
import { DailyTranscriptionGraph } from '../components/statistics/DailyTranscriptionGraph';
import { AdminContributionChart } from '../components/statistics/AdminContributionChart';
import { AudioDistributionGraph } from '../components/statistics/AudioDistributionGraph';
import { TranscriptionMetadataChart } from '../components/statistics/TranscriptionMetadataChart';

export function StatisticsPage() {
  const [statistics, setStatistics] = useState<StatisticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [days, setDays] = useState(30);
  const [dailyDays, setDailyDays] = useState<7 | 30>(30);

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

  const fetchDailyStatistics = async (selectedDays: 7 | 30) => {
    try {
      const data = await statisticsApi.getDailyTranscriptions(selectedDays);
      setStatistics(prev => prev ? { ...prev, daily_transcriptions: data.data } : null);
    } catch (err) {
      console.error('Error fetching daily statistics:', err);
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

  const handleDailyDaysChange = (newDays: 7 | 30) => {
    setDailyDays(newDays);
    fetchDailyStatistics(newDays);
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
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 2, pt: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="h4" fontWeight="bold">
            Database Statistics
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 1.5, alignItems: 'center' }}>
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
        
        <Typography variant="body2" color="text.secondary">
          Comprehensive overview of your audio transcription database
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Box sx={{ mb: 2 }}>
        <SummaryCards summary={statistics.summary} />
      </Box>

      {/* Main Charts Grid */}
      <Box sx={{ display: 'grid', gap: 2, mb: 2 }}>
        {/* Transcription Quality Metrics - Full Width */}
        <TranscriptionMetadataChart data={statistics.transcription_metadata} />

        {/* Row 1: Two columns */}
        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 1fr' }, gap: 2 }}>
          {/* Left Column */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TranscriptionStatusChart data={statistics.transcription_status} />
            <CategoryDurationChart data={statistics.category_durations} />
            <AdminContributionChart data={statistics.admin_contributions} />
          </Box>
          {/* Right Column */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <AudioDistributionGraph data={statistics.audio_distribution} />
            <DailyTranscriptionGraph 
              data={statistics.daily_transcriptions} 
              days={dailyDays}
              onDaysChange={handleDailyDaysChange}
            />
            {/* <TranscriptionMetadataChart data={statistics.transcription_metadata} /> */}
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
