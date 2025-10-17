import { Typography, Box, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import { LineChart } from '@mui/x-charts/LineChart';
import type { DailyTranscriptionData } from '../../lib/statisticsApi';

interface DailyTranscriptionGraphProps {
  data: DailyTranscriptionData[];
  days: number;
  onDaysChange: (days: 7 | 30) => void;
}

export function DailyTranscriptionGraph({ data, days, onDaysChange }: DailyTranscriptionGraphProps) {
  // Data is already sorted and filtered by the backend to match the requested days
  const displayData = data;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  const totalTranscriptions = displayData.reduce((sum, d) => sum + d.transcription_count, 0);
  const avgPerDay = displayData.length > 0 ? totalTranscriptions / displayData.length : 0;
  const totalHours = displayData.reduce((sum, d) => sum + d.total_duration_hours, 0);

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
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
          <Typography variant="h6" fontWeight="bold" color="white">
            Daily Transcription Activity
          </Typography>
          <TrendingUp sx={{ color: '#64b5f6', fontSize: 22 }} />
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="body2" sx={{ color: '#b0bec5' }}>
            Transcription trends over the last {displayData.length} days
          </Typography>
          <ToggleButtonGroup
            value={days}
            exclusive
            onChange={(_, newValue) => {
              if (newValue !== null) {
                onDaysChange(newValue);
              }
            }}
            size="small"
            sx={{
              '& .MuiToggleButton-root': {
                color: '#90caf9',
                borderColor: 'rgba(100, 181, 246, 0.3)',
                '&.Mui-selected': {
                  backgroundColor: 'rgba(100, 181, 246, 0.25)',
                  color: '#64b5f6',
                  '&:hover': {
                    backgroundColor: 'rgba(100, 181, 246, 0.35)',
                  },
                },
                '&:hover': {
                  backgroundColor: 'rgba(100, 181, 246, 0.15)',
                },
              },
            }}
          >
            <ToggleButton value={7}>7 days</ToggleButton>
            <ToggleButton value={30}>30 days</ToggleButton>
          </ToggleButtonGroup>
        </Box>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
            gap: 1.5,
            mb: 2,
            p: 1.5,
            background: 'linear-gradient(135deg, rgba(100, 181, 246, 0.15) 0%, rgba(63, 81, 181, 0.15) 100%)',
            borderRadius: 2,
            border: '1px solid rgba(100, 181, 246, 0.3)',
          }}
        >
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Total</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{totalTranscriptions.toLocaleString()}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Avg/Day</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{avgPerDay.toFixed(1)}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Total Hours</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{totalHours.toFixed(2)}</Typography>
          </Box>
        </Box>

        <Box sx={{ width: '100%', height: 280 }}>
          <LineChart
            xAxis={[{
              scaleType: 'point',
              data: displayData.map(item => formatDate(item.date)),
              tickLabelStyle: {
                angle: -45,
                textAnchor: 'end',
                fontSize: 10,
                fill: '#90caf9',
              },
            }]}
            yAxis={[{
              tickLabelStyle: {
                fontSize: 11,
                fill: '#90caf9',
              },
            }]}
            series={[{
              data: displayData.map(item => item.transcription_count),
              label: 'Transcriptions',
              color: '#64b5f6',
              area: true,
              showMark: true,
            }]}
            // margin={{ left: 60, right: 30, top: 20, bottom: 70 }}
            grid={{ horizontal: true }}
            sx={{
              '& .MuiChartsAxis-line': { stroke: '#90caf9' },
              '& .MuiChartsAxis-tick': { stroke: '#90caf9' },
              '& .MuiChartsGrid-line': { stroke: 'rgba(100, 181, 246, 0.1)' },
              '& .MuiLineElement-root': { strokeWidth: 2 },
              '& .MuiAreaElement-root': { fillOpacity: 0.3 },
            }}
          />
        </Box>

        {displayData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <Typography sx={{ color: '#78909c' }}>
              No transcription data available
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
