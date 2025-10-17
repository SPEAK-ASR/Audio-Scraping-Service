import { Typography, Box } from '@mui/material';
import { GraphicEq } from '@mui/icons-material';
import { BarChart } from '@mui/x-charts/BarChart';

interface AudioDurationDistribution {
  range: string;
  count: number;
  total_duration_hours: number;
  percentage: number;
}

interface AudioDistributionGraphProps {
  data: AudioDurationDistribution[];
}

export function AudioDistributionGraph({ data }: AudioDistributionGraphProps) {
  const sortedData = [...data];
  
  const totalClips = sortedData.reduce((sum, d) => sum + d.count, 0);
  const totalHours = sortedData.reduce((sum, d) => sum + d.total_duration_hours, 0);

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
          <GraphicEq sx={{ mr: 1, color: '#64b5f6', fontSize: 22 }} />
          <Typography variant="h6" fontWeight="bold" color="white">
            Audio Duration Distribution
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mb: 2, color: '#b0bec5' }}>
          Distribution of audio clips across duration intervals (0s - 11.5s+)
        </Typography>

        <Box
          sx={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: 1.5,
            mb: 2,
            p: 1.5,
            background: 'linear-gradient(135deg, rgba(100, 181, 246, 0.15) 0%, rgba(63, 81, 181, 0.15) 100%)',
            borderRadius: 2,
            border: '1px solid rgba(100, 181, 246, 0.3)',
          }}
        >
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Total Clips</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{totalClips.toLocaleString()}</Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Total Duration</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{totalHours.toFixed(2)} hrs</Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>Avg Duration</Typography>
            <Typography variant="h6" fontWeight="bold" color="white">{totalClips > 0 ? ((totalHours * 3600) / totalClips).toFixed(2) : '0'} sec</Typography>
          </Box>
        </Box>

        <Box sx={{ width: '100%', height: 300 }}>
          <BarChart
            xAxis={[{ 
              scaleType: 'band', 
              data: sortedData.map(item => item.range),
              height: 50,
              tickLabelStyle: {
                angle: -45,
                textAnchor: 'end',
                fontSize: 11,
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
              data: sortedData.map(item => item.count),
              label: 'Clips',
              color: '#64b5f6',
            }]}
            // margin={{ left: 60, right: 30, top: 20, bottom: 70 }}
            grid={{ horizontal: true }}
            sx={{
              '& .MuiChartsAxis-line': { stroke: '#90caf9' },
              '& .MuiChartsAxis-tick': { stroke: '#90caf9' },
              '& .MuiChartsGrid-line': { stroke: 'rgba(100, 181, 246, 0.1)' },
              '& .MuiBarElement-root': { rx: 4 },
            }}
          />
        </Box>

        {sortedData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography sx={{ color: '#78909c' }}>
              No audio distribution data available
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
