import { Box, Typography } from '@mui/material';
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
      color: '#64b5f6',
      bgColor: 'rgba(100, 181, 246, 0.15)',
      borderColor: 'rgba(100, 181, 246, 0.3)',
    },
    {
      title: 'Total Audio Clips',
      value: summary.total_audio_clips.toLocaleString(),
      icon: <AudioFile sx={{ fontSize: 40 }} />,
      color: '#ba68c8',
      bgColor: 'rgba(186, 104, 200, 0.15)',
      borderColor: 'rgba(186, 104, 200, 0.3)',
    },
    {
      title: 'Total Duration',
      value: formatHours(summary.total_duration_hours),
      subtitle: `Avg: ${formatSeconds(summary.average_clip_duration_seconds)} per clip`,
      icon: <AccessTime sx={{ fontSize: 40 }} />,
      color: '#ffb74d',
      bgColor: 'rgba(255, 183, 77, 0.15)',
      borderColor: 'rgba(255, 183, 77, 0.3)',
    },
    {
      title: 'Transcribed Duration',
      value: formatHours(summary.transcribed_duration_hours),
      subtitle: `${summary.total_transcriptions.toLocaleString()} transcriptions`,
      icon: <CheckCircle sx={{ fontSize: 40 }} />,
      color: '#81c784',
      bgColor: 'rgba(129, 199, 132, 0.15)',
      borderColor: 'rgba(129, 199, 132, 0.3)',
    },
  ];

  return (
    <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 2 }}>
      {cards.map((card, index) => (
        <Box
          key={index}
          sx={{
            height: '100%',
            background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
            color: 'white',
            border: `1px solid ${card.borderColor}`,
            borderRadius: 1,
            boxShadow: 2,
            cursor: 'pointer',
            transition: 'all 0.3s ease-in-out',
            '&:hover': {
              transform: 'translateY(-2px)',
              boxShadow: `0 8px 24px ${card.color}40, 0 0 20px ${card.color}30`,
              border: `1px solid ${card.color}`,
            },
          }}
        >
          <Box sx={{ p: 2 }}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                mb: 1,
              }}
            >
              <Typography variant="body2" sx={{ color: '#b0bec5' }} fontWeight={500}>
                {card.title}
              </Typography>
              <Box
                sx={{
                  background: `linear-gradient(135deg, ${card.bgColor}, ${card.bgColor})`,
                  color: card.color,
                  borderRadius: 2,
                  p: 0.75,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: `1px solid ${card.borderColor}`,
                }}
              >
                {card.icon}
              </Box>
            </Box>
            <Typography variant="h4" fontWeight="bold" sx={{ mb: 0.25 }} color="white">
              {card.value}
            </Typography>
            {card.subtitle && (
              <Typography variant="caption" sx={{ color: '#90caf9' }}>
                {card.subtitle}
              </Typography>
            )}
          </Box>
        </Box>
      ))}
    </Box>
  );
}
