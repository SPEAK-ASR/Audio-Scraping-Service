import { Box, Card, CardContent, Typography } from '@mui/material';
import {
  VideoLibrary,
  AudioFile,
  AccessTime,
  CheckCircle,
} from '@mui/icons-material';
import type { TotalDataSummary } from '../../lib/statisticsApi';

interface SummaryCardsProps {
  summary: TotalDataSummary;
}

export function SummaryCards({ summary }: SummaryCardsProps) {
  const formatHours = (hours: number) => {
    return `${hours.toFixed(2)} hrs`;
  };

  const formatSeconds = (seconds: number) => {
    return `${seconds.toFixed(1)} sec`;
  };

  const cards = [
    {
      title: 'Total Videos',
      value: summary.total_videos.toLocaleString(),
      icon: <VideoLibrary sx={{ fontSize: 40 }} />,
      color: '#1976d2',
      bgColor: '#e3f2fd',
    },
    {
      title: 'Total Audio Clips',
      value: summary.total_audio_clips.toLocaleString(),
      icon: <AudioFile sx={{ fontSize: 40 }} />,
      color: '#9c27b0',
      bgColor: '#f3e5f5',
    },
    {
      title: 'Total Duration',
      value: formatHours(summary.total_duration_hours),
      subtitle: `Avg: ${formatSeconds(summary.average_clip_duration_seconds)} per clip`,
      icon: <AccessTime sx={{ fontSize: 40 }} />,
      color: '#f57c00',
      bgColor: '#fff3e0',
    },
    {
      title: 'Transcribed Duration',
      value: formatHours(summary.transcribed_duration_hours),
      subtitle: `${summary.total_transcriptions.toLocaleString()} transcriptions`,
      icon: <CheckCircle sx={{ fontSize: 40 }} />,
      color: '#388e3c',
      bgColor: '#e8f5e9',
    },
  ];

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 3 }}>
      {cards.map((card, index) => (
        <Card
          key={index}
          elevation={2}
          sx={{
            height: '100%',
            transition: 'transform 0.2s, box-shadow 0.2s',
            '&:hover': {
              transform: 'translateY(-4px)',
              boxShadow: 4,
            },
          }}
        >
          <CardContent>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 2,
              }}
            >
              <Typography variant="body2" color="text.secondary" fontWeight={500}>
                {card.title}
              </Typography>
              <Box
                sx={{
                  backgroundColor: card.bgColor,
                  color: card.color,
                  borderRadius: 2,
                  p: 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                {card.icon}
              </Box>
            </Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 0.5 }}>
              {card.value}
            </Typography>
            {card.subtitle && (
              <Typography variant="caption" color="text.secondary">
                {card.subtitle}
              </Typography>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
}
