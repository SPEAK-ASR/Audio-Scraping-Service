import { Card, CardContent, Typography, Box } from '@mui/material';
import type { CategoryDurationData } from '../../lib/statisticsApi';

interface CategoryDurationChartProps {
  data: CategoryDurationData[];
}

export function CategoryDurationChart({ data }: CategoryDurationChartProps) {
  // Sort by duration descending
  const sortedData = [...data].sort((a, b) => b.total_duration_hours - a.total_duration_hours);
  
  // Find max duration for scaling
  const maxDuration = Math.max(...sortedData.map(d => d.total_duration_hours));

  const getCategoryColor = (index: number) => {
    const colors = [
      '#1976d2', '#9c27b0', '#f57c00', '#388e3c', '#d32f2f',
      '#0288d1', '#7b1fa2', '#e64a19', '#00796b', '#c62828',
      '#0097a7', '#5e35b1', '#ef6c00', '#00897b', '#ad1457'
    ];
    return colors[index % colors.length];
  };

  const formatCategoryName = (category: string) => {
    return category
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <Card elevation={2}>
      <CardContent>
        <Typography variant="h6" gutterBottom fontWeight="bold">
          Duration by Category
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Total audio duration collected per category
        </Typography>

        <Box sx={{ mt: 2 }}>
          {sortedData.map((item, index) => {
            const percentage = (item.total_duration_hours / maxDuration) * 100;
            
            return (
              <Box key={item.category} sx={{ mb: 3 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2" fontWeight={500}>
                    {formatCategoryName(item.category)}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'baseline', gap: 2 }}>
                    <Typography variant="body2" color="text.secondary" fontSize="0.75rem">
                      {item.clip_count} clips · {item.video_count} videos
                    </Typography>
                    <Typography variant="body2" fontWeight="bold">
                      {item.total_duration_hours.toFixed(2)} hrs
                    </Typography>
                  </Box>
                </Box>
                
                <Box
                  sx={{
                    width: '100%',
                    height: 10,
                    backgroundColor: '#f5f5f5',
                    borderRadius: 1,
                    overflow: 'hidden',
                    position: 'relative',
                  }}
                >
                  <Box
                    sx={{
                      width: `${percentage}%`,
                      height: '100%',
                      backgroundColor: getCategoryColor(index),
                      transition: 'width 0.3s ease',
                      borderRadius: 1,
                    }}
                  />
                </Box>
              </Box>
            );
          })}
        </Box>

        {sortedData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography color="text.secondary">
              No category data available
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
