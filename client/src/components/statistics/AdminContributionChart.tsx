import { Typography, Box } from '@mui/material';
import { People } from '@mui/icons-material';
import { BarChart } from '@mui/x-charts/BarChart';
import type { AdminContributionData } from '../../lib/statisticsApi';

interface AdminContributionChartProps {
  data: AdminContributionData[];
}

export function AdminContributionChart({ data }: AdminContributionChartProps) {
  const sortedData = [...data].sort((a, b) => b.transcription_count - a.transcription_count);

  const formatAdminName = (admin: string) => {
    if (admin === 'non_admin') return 'Non-Admin Contributors';
    return admin
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const totalContributions = sortedData.reduce((sum, d) => sum + d.transcription_count, 0);

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
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
          <People sx={{ mr: 1, color: '#64b5f6', fontSize: 22 }} />
          <Typography variant="h6" fontWeight="bold" color="white">
            Contributor Statistics
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mb: 2, color: '#b0bec5' }}>
          Transcription contributions by admins and contributors
        </Typography>

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
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Total Contributors</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{sortedData.length}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Total Contributions</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{totalContributions.toLocaleString()}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Total Hours</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{sortedData.reduce((sum, d) => sum + d.total_duration_hours, 0).toFixed(2)}</Typography>
          </Box>
        </Box>

        <Box sx={{ width: '100%', height: 300 }}>
          <BarChart
            layout="horizontal"
            yAxis={[{
              scaleType: 'band',
              data: sortedData.map(item => formatAdminName(item.admin)),
              tickLabelStyle: {
                fontSize: 11,
                fill: '#90caf9',
              },
            }]}
            xAxis={[{
              tickLabelStyle: {
                fontSize: 11,
                fill: '#90caf9',
              },
              label: 'Transcriptions',
            }]}
            series={[{
              data: sortedData.map(item => item.transcription_count),
              label: 'Contributions',
              color: '#64b5f6',
            }]}
            // margin={{ left: 150, right: 30, top: 20, bottom: 50 }}
            grid={{ vertical: true }}
            sx={{
              '& .MuiChartsAxis-line': { stroke: '#90caf9' },
              '& .MuiChartsAxis-tick': { stroke: '#90caf9' },
              '& .MuiChartsGrid-line': { stroke: 'rgba(100, 181, 246, 0.1)' },
              '& .MuiBarElement-root': { rx: 2 },
            }}
          />
        </Box>

        {sortedData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography sx={{ color: '#78909c' }}>
              No contribution data available
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
