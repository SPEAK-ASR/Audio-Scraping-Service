import { Card, CardContent, Typography, Box, Avatar } from '@mui/material';
import { Person, People } from '@mui/icons-material';
import type { AdminContributionData } from '../../lib/statisticsApi';

interface AdminContributionChartProps {
  data: AdminContributionData[];
}

export function AdminContributionChart({ data }: AdminContributionChartProps) {
  // Sort by contribution count descending
  const sortedData = [...data].sort((a, b) => b.transcription_count - a.transcription_count);

  const getAdminColor = (index: number) => {
    const colors = [
      '#1976d2', '#9c27b0', '#f57c00', '#388e3c', '#d32f2f',
      '#0288d1', '#7b1fa2', '#e64a19', '#00796b', '#c62828',
    ];
    return colors[index % colors.length];
  };

  const formatAdminName = (admin: string) => {
    if (admin === 'non_admin') return 'Non-Admin Contributors';
    return admin
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  // Calculate total for percentage bars
  const totalContributions = sortedData.reduce((sum, d) => sum + d.transcription_count, 0);

  return (
    <Card 
      elevation={2}
      sx={{
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 100%)',
        color: 'white'
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <People sx={{ mr: 1, color: '#64b5f6' }} />
          <Typography variant="h6" fontWeight="bold" color="white">
            Contributor Statistics
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mb: 3, color: '#b0bec5' }}>
          Transcription contributions by admins and contributors
        </Typography>

        {/* Summary stats */}
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
              Total Contributors
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {sortedData.length}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>
              Total Contributions
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {totalContributions.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>
              Total Hours
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {sortedData.reduce((sum, d) => sum + d.total_duration_hours, 0).toFixed(2)}
            </Typography>
          </Box>
        </Box>

        {/* Contributors list */}
        <Box sx={{ mt: 2 }}>
          {sortedData.map((contributor, index) => {
            const barWidth = (contributor.transcription_count / totalContributions) * 100;
            const isNonAdmin = contributor.admin === 'non_admin';
            
            return (
              <Box
                key={contributor.admin}
                sx={{
                  mb: 2.5,
                  pb: 2.5,
                  borderBottom: index < sortedData.length - 1 ? '1px solid rgba(100, 181, 246, 0.1)' : 'none',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                  <Avatar
                    sx={{
                      width: 40,
                      height: 40,
                      backgroundColor: isNonAdmin ? '#78909c' : getAdminColor(index),
                      mr: 2,
                      border: '2px solid rgba(100, 181, 246, 0.2)',
                    }}
                  >
                    {isNonAdmin ? <People /> : <Person />}
                  </Avatar>
                  
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                      <Typography variant="body1" fontWeight={500} color="white">
                        {formatAdminName(contributor.admin)}
                      </Typography>
                      <Typography variant="body2" fontWeight="bold" sx={{ color: '#64b5f6' }}>
                        {contributor.percentage.toFixed(1)}%
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                      <Typography variant="caption" sx={{ color: '#90caf9' }}>
                        {contributor.transcription_count.toLocaleString()} transcriptions
                      </Typography>
                      <Typography variant="caption" sx={{ color: '#90caf9' }}>
                        {contributor.total_duration_hours.toFixed(2)} hours
                      </Typography>
                    </Box>
                    
                    {/* Progress bar */}
                    <Box
                      sx={{
                        width: '100%',
                        height: 10,
                        backgroundColor: 'rgba(255, 255, 255, 0.05)',
                        borderRadius: 1.5,
                        overflow: 'hidden',
                        border: '1px solid rgba(100, 181, 246, 0.1)',
                      }}
                    >
                      <Box
                        sx={{
                          width: `${barWidth}%`,
                          height: '100%',
                          background: `linear-gradient(90deg, ${isNonAdmin ? '#78909c' : getAdminColor(index)}, ${isNonAdmin ? '#78909c' : getAdminColor(index)}dd)`,
                          transition: 'width 0.3s ease',
                          borderRadius: 1.5,
                          boxShadow: `0 2px 8px ${isNonAdmin ? '#78909c' : getAdminColor(index)}40`,
                        }}
                      />
                    </Box>
                  </Box>
                </Box>
              </Box>
            );
          })}
        </Box>

        {sortedData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography sx={{ color: '#78909c' }}>
              No contribution data available
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
