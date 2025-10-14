import { Typography, Box } from '@mui/material';
import { BarChart } from '@mui/x-charts/BarChart';
import type { CategoryDurationData } from '../../lib/statisticsApi';

interface CategoryDurationChartProps {
  data: CategoryDurationData[];
}

export function CategoryDurationChart({ data }: CategoryDurationChartProps) {
  const sortedData = [...data].sort((a, b) => b.total_duration_hours - a.total_duration_hours);
  
  const formatCategoryName = (category: string) => {
    return category
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

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
          Duration by Category
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, color: '#b0bec5' }}>
          Total audio duration collected per category
        </Typography>

        <Box sx={{ width: '100%', height: 350 }}>
          <BarChart
            layout="horizontal"
            yAxis={[{
              scaleType: 'band',
              data: sortedData.map(item => formatCategoryName(item.category)),
              width: 120,
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
              label: 'Hours',
            }]}
            series={[{
              data: sortedData.map(item => item.total_duration_hours),
              label: 'Duration (hrs)',
              color: '#64b5f6',
            }]}
            // margin={{ left: 120, right: 30, top: 20, bottom: 50 }}
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
              No category data available
            </Typography>
          </Box>
        )}
      </Box>
    </Box>
  );
}
