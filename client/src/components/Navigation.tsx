import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { BarChart, Home } from '@mui/icons-material';

interface NavigationProps {
  currentPage: 'home' | 'statistics';
  onNavigate: (page: 'home' | 'statistics') => void;
}

export function Navigation({ currentPage, onNavigate }: NavigationProps) {
  return (
    <AppBar position="static" elevation={1} sx={{ mb: 3 }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1, fontWeight: 'bold' }}>
          Audio Processor
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button
            color="inherit"
            startIcon={<Home />}
            onClick={() => onNavigate('home')}
            sx={{
              fontWeight: currentPage === 'home' ? 'bold' : 'normal',
              backgroundColor: currentPage === 'home' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            }}
          >
            Home
          </Button>
          
          <Button
            color="inherit"
            startIcon={<BarChart />}
            onClick={() => onNavigate('statistics')}
            sx={{
              fontWeight: currentPage === 'statistics' ? 'bold' : 'normal',
              backgroundColor: currentPage === 'statistics' ? 'rgba(255, 255, 255, 0.1)' : 'transparent',
            }}
          >
            Statistics
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
