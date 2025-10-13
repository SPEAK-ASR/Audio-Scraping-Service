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
    <Card elevation={2}>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <People sx={{ mr: 1, color: '#1976d2' }} />
          <Typography variant="h6" fontWeight="bold">
            Contributor Statistics
          </Typography>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
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
            backgroundColor: '#f5f5f5',
            borderRadius: 2,
          }}
        >
          <Box>
            <Typography variant="caption" color="text.secondary">
              Total Contributors
            </Typography>
            <Typography variant="h6" fontWeight="bold">
              {sortedData.length}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Total Contributions
            </Typography>
            <Typography variant="h6" fontWeight="bold">
              {totalContributions.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Total Hours
            </Typography>
            <Typography variant="h6" fontWeight="bold">
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
                  borderBottom: index < sortedData.length - 1 ? '1px solid #f0f0f0' : 'none',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1.5 }}>
                  <Avatar
                    sx={{
                      width: 40,
                      height: 40,
                      backgroundColor: isNonAdmin ? '#9e9e9e' : getAdminColor(index),
                      mr: 2,
                    }}
                  >
                    {isNonAdmin ? <People /> : <Person />}
                  </Avatar>
                  
                  <Box sx={{ flex: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                      <Typography variant="body1" fontWeight={500}>
                        {formatAdminName(contributor.admin)}
                      </Typography>
                      <Typography variant="body2" fontWeight="bold" color="primary">
                        {contributor.percentage.toFixed(1)}%
                      </Typography>
                    </Box>
                    
                    <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        {contributor.transcription_count.toLocaleString()} transcriptions
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {contributor.total_duration_hours.toFixed(2)} hours
                      </Typography>
                    </Box>
                    
                    {/* Progress bar */}
                    <Box
                      sx={{
                        width: '100%',
                        height: 8,
                        backgroundColor: '#f5f5f5',
                        borderRadius: 1,
                        overflow: 'hidden',
                      }}
                    >
                      <Box
                        sx={{
                          width: `${barWidth}%`,
                          height: '100%',
                          backgroundColor: isNonAdmin ? '#9e9e9e' : getAdminColor(index),
                          transition: 'width 0.3s ease',
                          borderRadius: 1,
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
            <Typography color="text.secondary">
              No contribution data available
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
