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
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Transcription Status
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
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
          }}
        >
          <Box
            sx={{
              width: `${transcribedPercentage}%`,
              backgroundColor: '#388e3c',
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
              backgroundColor: '#e0e0e0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'width 0.3s ease',
            }}
          >
            {nonTranscribedPercentage > 15 && (
              <Typography variant="body2" color="text.secondary" fontWeight="bold">
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
              backgroundColor: '#e8f5e9',
              border: '1px solid #c8e6c9',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <CheckCircle sx={{ color: '#388e3c', mr: 1 }} />
              <Typography variant="body2" fontWeight="bold" color="#388e3c">
                Transcribed
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 0.5 }}>
              {data.transcribed_count.toLocaleString()}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {data.transcribed_duration_hours.toFixed(2)} hours
            </Typography>
          </Box>

          {/* Non-transcribed */}
          <Box
            sx={{
              p: 2,
              borderRadius: 2,
              backgroundColor: '#f5f5f5',
              border: '1px solid #e0e0e0',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
              <RadioButtonUnchecked sx={{ color: '#757575', mr: 1 }} />
              <Typography variant="body2" fontWeight="bold" color="text.secondary">
                Not Transcribed
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 0.5 }}>
              {data.non_transcribed_count.toLocaleString()}
            </Typography>
            <Typography variant="caption" color="text.secondary">
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
            backgroundColor: '#f5f5f5',
            textAlign: 'center',
          }}
        >
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Total Audio Clips
          </Typography>
          <Typography variant="h4" fontWeight="bold">
            {data.total_count.toLocaleString()}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
}
