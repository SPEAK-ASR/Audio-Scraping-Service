import { Card, CardContent, Typography, Box } from '@mui/material';
import { CheckCircle, RadioButtonUnchecked } from '@mui/icons-material';
import type { TranscriptionStatusData } from '../../lib/statisticsApi';

interface TranscriptionStatusChartProps {
  data: TranscriptionStatusData;
}

export function TranscriptionStatusChart({ data }: TranscriptionStatusChartProps) {
  const transcribedPercentage = data.transcription_rate;
  const nonTranscribedPercentage = 100 - transcribedPercentage;

  return (
    <Card 
      elevation={2}
      sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        color: 'white'
      }}
    >
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="bold" color="white">
          Transcription Status
        </Typography>
        <Typography variant="body2" sx={{ mb: 3, color: '#b0bec5' }}>
          Transcribed vs non-transcribed audio clips
        </Typography>

        {/* Progress bar */}
        <Box
          sx={{
            width: '100%',
            height: 40,
            borderRadius: 2,
            overflow: 'hidden',
            display: 'flex',
            mb: 3,
            border: '1px solid rgba(100, 181, 246, 0.2)',
          }}
        >
          <Box
            sx={{
              width: `${transcribedPercentage}%`,
              backgroundColor: '#66bb6a',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'width 0.3s ease',
            }}
          >
            {transcribedPercentage > 15 && (
              <Typography variant="body2" color="white" fontWeight="bold">
                {transcribedPercentage.toFixed(1)}%
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              width: `${nonTranscribedPercentage}%`,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'width 0.3s ease',
            }}
          >
            {nonTranscribedPercentage > 15 && (
              <Typography variant="body2" sx={{ color: '#b0bec5' }} fontWeight="bold">
                {nonTranscribedPercentage.toFixed(1)}%
              </Typography>
            )}
          </Box>
        </Box>

        {/* Statistics cards */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
          {/* Transcribed */}
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(102, 187, 106, 0.2) 0%, rgba(76, 175, 80, 0.2) 100%)',
              border: '1px solid rgba(102, 187, 106, 0.4)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircle sx={{ color: '#81c784', mr: 1 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#a5d6a7' }}>
                Transcribed
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 0.5 }} color="white">
              {data.transcribed_count.toLocaleString()}
            </Typography>
            <Typography variant="caption" sx={{ color: '#a5d6a7' }}>
              {data.transcribed_duration_hours.toFixed(2)} hours
            </Typography>
          </Box>

          {/* Non-transcribed */}
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <RadioButtonUnchecked sx={{ color: '#90a4ae', mr: 1 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#b0bec5' }}>
                Not Transcribed
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 0.5 }} color="white">
              {data.non_transcribed_count.toLocaleString()}
            </Typography>
            <Typography variant="caption" sx={{ color: '#b0bec5' }}>
              {data.non_transcribed_duration_hours.toFixed(2)} hours
            </Typography>
          </Box>
        </Box>

        {/* Total */}
        <Box
          sx={{
            mt: 2,
            p: 2,
            borderRadius: 2,
            background: 'linear-gradient(135deg, rgba(100, 181, 246, 0.15) 0%, rgba(63, 81, 181, 0.15) 100%)',
            border: '1px solid rgba(100, 181, 246, 0.3)',
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" sx={{ color: '#90caf9' }} gutterBottom>
            Total Audio Clips
          </Typography>
          <Typography variant="h4" fontWeight="bold" color="white">
            {data.total_count.toLocaleString()}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
