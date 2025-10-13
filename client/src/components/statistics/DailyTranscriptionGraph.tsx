import { Card, CardContent, Typography, Box } from '@mui/material';
import { TrendingUp } from '@mui/icons-material';
import type { DailyTranscriptionData } from '../../lib/statisticsApi';

interface DailyTranscriptionGraphProps {
  data: DailyTranscriptionData[];
}

export function DailyTranscriptionGraph({ data }: DailyTranscriptionGraphProps) {
  // Sort by date ascending
  const sortedData = [...data].sort((a, b) => 
    new Date(a.date).getTime() - new Date(b.date).getTime()
  );

  // Get last 30 days for display
  const displayData = sortedData.slice(-30);

  const maxCount = Math.max(...displayData.map(d => d.transcription_count), 1);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Calculate statistics
  const totalTranscriptions = displayData.reduce((sum, d) => sum + d.transcription_count, 0);
  const avgPerDay = displayData.length > 0 ? totalTranscriptions / displayData.length : 0;
  const totalHours = displayData.reduce((sum, d) => sum + d.total_duration_hours, 0);

  return (
    <Card 
      elevation={2}
      sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        color: 'white'
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" fontWeight="bold" color="white">
            Daily Transcription Activity
          </Typography>
          <TrendingUp sx={{ color: '#64b5f6' }} />
        </Box>
        <Typography variant="body2" sx={{ mb: 3, color: '#b0bec5' }}>
          Transcription trends over the last {displayData.length} days
        </Typography>

        {/* Stats summary */}
        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: 2,
            mb: 3,
            p: 2,
            background: 'linear-gradient(135deg, rgba(100, 181, 246, 0.15) 0%, rgba(63, 81, 181, 0.15) 100%)',
            borderRadius: 2,
            border: '1px solid rgba(100, 181, 246, 0.3)',
          }}
        >
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>
              Total
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {totalTranscriptions.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>
              Avg/Day
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {avgPerDay.toFixed(1)}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>
              Total Hours
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {totalHours.toFixed(2)}
            </Typography>
          </Box>
        </Box>

        {/* Bar chart */}
        <Box sx={{ position: 'relative', height: 250, display: 'flex', alignItems: 'flex-end', gap: 0.5 }}>
          {displayData.map((item) => {
            const height = (item.transcription_count / maxCount) * 100;
            const isWeekend = new Date(item.date).getDay() === 0 || new Date(item.date).getDay() === 6;
            
            return (
              <Box
                key={item.date}
                sx={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  position: 'relative',
                  '&:hover .bar': {
                    opacity: 0.8,
                  },
                  '&:hover .tooltip': {
                    opacity: 1,
                    visibility: 'visible',
                  },
                }}
              >
                {/* Tooltip */}
                <Box
                  className="tooltip"
                  sx={{
                    position: 'absolute',
                    bottom: '110%',
                    left: '50%',
                    transform: 'translateX(-50%)',
                    backgroundColor: 'rgba(0, 0, 0, 0.95)',
                    color: 'white',
                    padding: '10px 14px',
                    borderRadius: 2,
                    fontSize: '0.75rem',
                    whiteSpace: 'nowrap',
                    opacity: 0,
                    visibility: 'hidden',
                    transition: 'all 0.3s',
                    zIndex: 10,
                    pointerEvents: 'none',
                    border: '1px solid rgba(100, 181, 246, 0.5)',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
                  }}
                >
                  <Box color="#90caf9" fontWeight="bold">{formatDate(item.date)}</Box>
                  <Box>{item.transcription_count} transcriptions</Box>
                  <Box>{item.total_duration_hours.toFixed(2)} hours</Box>
                </Box>

                {/* Bar */}
                <Box
                  className="bar"
                  sx={{
                    width: '100%',
                    height: `${height}%`,
                    backgroundColor: isWeekend ? '#ce93d8' : '#64b5f6',
                    borderRadius: '4px 4px 0 0',
                    transition: 'all 0.3s',
                    minHeight: item.transcription_count > 0 ? '3px' : '0px',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    boxShadow: '0 2px 8px rgba(100, 181, 246, 0.3)',
                    '&:hover': {
                      filter: 'brightness(1.2)',
                      transform: 'translateY(-2px)',
                    },
                  }}
                />
              </Box>
            );
          })}
        </Box>

        {/* X-axis labels (show every 5 days) */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 }}>
          {displayData.map((item, index) => {
            const showLabel = index % 5 === 0 || index === displayData.length - 1;
            return (
              <Box key={item.date} sx={{ flex: 1, textAlign: 'center' }}>
                {showLabel && (
                  <Typography variant="caption" sx={{ color: '#90caf9' }} fontSize="0.65rem">
                    {formatDate(item.date)}
                  </Typography>
                )}
              </Box>
            );
          })}
        </Box>

        {displayData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <Typography sx={{ color: '#78909c' }}>
              No transcription data available
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
