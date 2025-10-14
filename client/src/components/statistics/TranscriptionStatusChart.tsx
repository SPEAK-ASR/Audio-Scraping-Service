import { Typography, Box } from '@mui/material';
import { CheckCircle, RadioButtonUnchecked } from '@mui/icons-material';
import { Gauge, gaugeClasses } from '@mui/x-charts/Gauge';
import type { TranscriptionStatusData } from '../../lib/statisticsApi';

interface TranscriptionStatusChartProps {
  data: TranscriptionStatusData;
}

export function TranscriptionStatusChart({ data }: TranscriptionStatusChartProps) {
  const transcribedPercentage = data.transcription_rate;

  return (
    <Box
      sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        color: 'white',
        borderRadius: 1,
        boxShadow: 2,
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom fontWeight="bold" color="white" sx={{ mb: 0.5 }}>
          Transcription Status
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, color: '#b0bec5' }}>
          Transcribed vs non-transcribed audio clips
        </Typography>

        {/* Gauge Chart */}
        <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
          <Gauge
            width={280}
            height={200}
            value={transcribedPercentage}
            startAngle={-110}
            endAngle={110}
            sx={{
              [`& .${gaugeClasses.valueText}`]: {
                fontSize: 32,
                fontWeight: 'bold',
                fill: '#fff',
              },
              [`& .${gaugeClasses.valueArc}`]: {
                fill: '#66bb6a',
              },
              [`& .${gaugeClasses.referenceArc}`]: {
                fill: 'rgba(255, 255, 255, 0.1)',
              },
            }}
            text={({ value }) => `${value?.toFixed(1) ?? '0'}%`}
          />
        </Box>

        {/* Statistics cards */}
        <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 2 }}>
          {/* Transcribed */}
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(102, 187, 106, 0.2) 0%, rgba(76, 175, 80, 0.2) 100%)',
              border: '1px solid rgba(102, 187, 106, 0.4)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <CheckCircle sx={{ color: '#81c784', mr: 1, fontSize: 20 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#a5d6a7' }}>
                Transcribed
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 0.25 }} color="white">
              {data.transcribed_count.toLocaleString()}
            </Typography>
            <Typography variant="caption" sx={{ color: '#a5d6a7' }}>
              {data.transcribed_duration_hours.toFixed(2)} hours
            </Typography>
          </Box>

          {/* Non-transcribed */}
          <Box
            sx={{
              p: 1.5,
              borderRadius: 2,
              background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
              <RadioButtonUnchecked sx={{ color: '#90a4ae', mr: 1, fontSize: 20 }} />
              <Typography variant="body2" fontWeight="bold" sx={{ color: '#b0bec5' }}>
                Not Transcribed
              </Typography>
            </Box>
            <Typography variant="h5" fontWeight="bold" sx={{ mb: 0.25 }} color="white">
              {data.non_transcribed_count.toLocaleString()}
            </Typography>
            <Typography variant="caption" sx={{ color: '#b0bec5' }}>
              {data.non_transcribed_duration_hours.toFixed(2)} hours
            </Typography>
          </Box>
        </Box>
      </Box>
    </Box>
  );
}
