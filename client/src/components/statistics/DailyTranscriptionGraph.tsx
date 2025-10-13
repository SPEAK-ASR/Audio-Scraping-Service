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
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
          <Typography variant="h6" fontWeight="bold">
            Daily Transcription Activity
          </Typography>
          <TrendingUp sx={{ color: '#1976d2' }} />
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
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
            backgroundColor: '#f5f5f5',
            borderRadius: 2,
          }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              Total
            </Typography>
            <Typography variant="h6" fontWeight="bold">
              {totalTranscriptions.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Avg/Day
            </Typography>
            <Typography variant="h6" fontWeight="bold">
              {avgPerDay.toFixed(1)}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Total Hours
            </Typography>
            <Typography variant="h6" fontWeight="bold">
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
                    backgroundColor: 'rgba(0, 0, 0, 0.87)',
                    color: 'white',
                    padding: '8px 12px',
                    borderRadius: 1,
                    fontSize: '0.75rem',
                    whiteSpace: 'nowrap',
                    opacity: 0,
                    visibility: 'hidden',
                    transition: 'opacity 0.2s',
                    zIndex: 10,
                    pointerEvents: 'none',
                  }}
                >
                  <Box>{formatDate(item.date)}</Box>
                  <Box fontWeight="bold">{item.transcription_count} transcriptions</Box>
                  <Box>{item.total_duration_hours.toFixed(2)} hours</Box>
                </Box>

                {/* Bar */}
                <Box
                  className="bar"
                  sx={{
                    width: '100%',
                    height: `${height}%`,
                    backgroundColor: isWeekend ? '#9c27b0' : '#1976d2',
                    borderRadius: '4px 4px 0 0',
                    transition: 'opacity 0.2s',
                    minHeight: item.transcription_count > 0 ? '2px' : '0px',
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
                  <Typography variant="caption" color="text.secondary" fontSize="0.65rem">
                    {formatDate(item.date)}
                  </Typography>
                )}
              </Box>
            );
          })}
        </Box>

        {displayData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 6 }}>
            <Typography color="text.secondary">
              No transcription data available
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
