import { Card, CardContent, Typography, Box } from '@mui/material';
import { GraphicEq } from '@mui/icons-material';

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
  // Sort by range order
  const sortedData = [...data];
  
  const maxCount = Math.max(...sortedData.map(d => d.count), 1);

  const getRangeColor = (index: number, isHover: boolean = false) => {
    // Gradient from light blue to deep blue
    const hue = 210;
    const saturation = 70 + (index / sortedData.length) * 30;
    const lightness = isHover ? 60 - (index / sortedData.length) * 20 : 65 - (index / sortedData.length) * 25;
    return `hsl(${hue}, ${saturation}%, ${lightness}%)`;
  };

  // Calculate total for summary
  const totalClips = sortedData.reduce((sum, d) => sum + d.count, 0);
  const totalHours = sortedData.reduce((sum, d) => sum + d.total_duration_hours, 0);

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
          <GraphicEq sx={{ mr: 1, color: '#64b5f6' }} />
          <Typography variant="h6" fontWeight="bold" color="white">
            Audio Duration Distribution
          </Typography>
        </Box>
        <Typography variant="body2" sx={{ mb: 3, color: '#b0bec5' }}>
          Distribution of audio clips across 0.5-second intervals (4.0s - 10.0s range)
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
              Total Clips
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {totalClips.toLocaleString()}
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>
              Total Duration
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {totalHours.toFixed(2)} hrs
            </Typography>
          </Box>
          <Box>
            <Typography variant="caption" sx={{ color: '#90caf9' }}>
              Avg Duration
            </Typography>
            <Typography variant="h6" fontWeight="bold" color="white">
              {totalClips > 0 ? ((totalHours * 3600) / totalClips).toFixed(2) : '0'} sec
            </Typography>
          </Box>
        </Box>

        {/* Histogram */}
        <Box sx={{ mb: 2 }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'flex-end',
              justifyContent: 'space-between',
              height: 280,
              gap: 0.5,
              px: 1,
            }}
          >
            {sortedData.map((item, index) => {
              const height = (item.count / maxCount) * 100;
              
              return (
                <Box
                  key={item.range}
                  sx={{
                    flex: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    position: 'relative',
                    '&:hover .bar': {
                      transform: 'translateY(-3px)',
                      filter: 'brightness(1.2)',
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
                      bottom: '105%',
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
                    <Box fontWeight="bold" color="#90caf9" mb={0.5}>{item.range}</Box>
                    <Box>{item.count.toLocaleString()} clips</Box>
                    <Box>{item.percentage.toFixed(1)}% of total</Box>
                    <Box>{(item.total_duration_hours * 60).toFixed(2)} minutes</Box>
                  </Box>

                  {/* Bar */}
                  <Box
                    className="bar"
                    sx={{
                      width: '100%',
                      height: `${height}%`,
                      minHeight: item.count > 0 ? '8px' : '2px',
                      backgroundColor: item.count > 0 ? getRangeColor(index) : 'rgba(100, 181, 246, 0.1)',
                      border: item.count > 0 ? '1px solid rgba(100, 181, 246, 0.4)' : 'none',
                      borderRadius: '6px 6px 0 0',
                      transition: 'all 0.3s ease',
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: 'center',
                      justifyContent: 'flex-start',
                      pt: 0.5,
                      cursor: item.count > 0 ? 'pointer' : 'default',
                      boxShadow: item.count > 0 ? '0 2px 8px rgba(100, 181, 246, 0.3)' : 'none',
                    }}
                  >
                    {height > 12 && item.count > 0 && (
                      <Typography
                        variant="caption"
                        fontWeight="bold"
                        sx={{
                          color: 'white',
                          fontSize: '0.7rem',
                          textShadow: '0 1px 3px rgba(0,0,0,0.5)',
                        }}
                      >
                        {item.count}
                      </Typography>
                    )}
                  </Box>
                </Box>
              );
            })}
          </Box>

          {/* X-axis labels */}
          <Box
            sx={{
              display: 'flex',
              justifyContent: 'space-between',
              mt: 2,
              gap: 0.5,
              px: 1,
            }}
          >
            {sortedData.map((item) => (
              <Box key={item.range} sx={{ flex: 1, textAlign: 'center' }}>
                <Typography
                  variant="caption"
                  sx={{
                    color: '#90caf9',
                    fontSize: '0.68rem',
                    display: 'block',
                    transform: 'rotate(-45deg)',
                    transformOrigin: 'center',
                    whiteSpace: 'nowrap',
                    fontWeight: 500,
                  }}
                >
                  {item.range}
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>

        {/* Legend */}
        <Box
          sx={{
            mt: 3,
            p: 2,
            background: 'linear-gradient(135deg, rgba(100, 181, 246, 0.08) 0%, rgba(63, 81, 181, 0.08) 100%)',
            borderRadius: 2,
            border: '1px solid rgba(100, 181, 246, 0.2)',
          }}
        >
          <Typography variant="caption" sx={{ color: '#90caf9' }} fontWeight="bold" gutterBottom display="block" mb={1.5}>
            Duration Ranges (seconds)
          </Typography>
          <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: 1.5 }}>
            {sortedData.map((item, index) => (
              <Box
                key={item.range}
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  p: 0.8,
                  backgroundColor: item.count > 0 ? 'rgba(100, 181, 246, 0.1)' : 'transparent',
                  borderRadius: 1,
                  border: item.count > 0 ? '1px solid rgba(100, 181, 246, 0.2)' : '1px solid transparent',
                  transition: 'all 0.2s',
                  '&:hover': item.count > 0 ? {
                    backgroundColor: 'rgba(100, 181, 246, 0.2)',
                    borderColor: 'rgba(100, 181, 246, 0.4)',
                  } : {},
                }}
              >
                <Box
                  sx={{
                    width: 14,
                    height: 14,
                    backgroundColor: item.count > 0 ? getRangeColor(index) : 'rgba(100, 181, 246, 0.2)',
                    border: '1px solid rgba(100, 181, 246, 0.4)',
                    borderRadius: 1.5,
                    flexShrink: 0,
                  }}
                />
                <Typography 
                  variant="caption" 
                  fontSize="0.7rem"
                  sx={{ 
                    color: item.count > 0 ? '#e3f2fd' : '#78909c',
                    fontWeight: item.count > 0 ? 500 : 400,
                  }}
                >
                  {item.range}: <strong>{item.count}</strong> ({item.percentage.toFixed(1)}%)
                </Typography>
              </Box>
            ))}
          </Box>
        </Box>

        {sortedData.length === 0 && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography sx={{ color: '#78909c' }}>
              No audio distribution data available
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}
