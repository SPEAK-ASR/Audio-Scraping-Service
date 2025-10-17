import { Fab, Tooltip, Zoom } from '@mui/material';
import { BarChart, Home } from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

export function StatisticsFloatingButton() {
  const navigate = useNavigate();
  const location = useLocation();
  const isOnStatisticsPage = location.pathname === '/statistics';
  
  const handleClick = () => {
    if (isOnStatisticsPage) {
      navigate('/');
    } else {
      navigate('/statistics');
    }
  };
  
  return (
    <Zoom in={true}>
      <Tooltip 
        title={isOnStatisticsPage ? "Back to Home" : "View Statistics"} 
        placement="left"
        arrow
      >
        <Fab
          color="primary"
          aria-label={isOnStatisticsPage ? "back to home" : "view statistics"}
          onClick={handleClick}
          sx={{
            position: 'fixed',
            bottom: 32,
            right: 32,
            background: 'linear-gradient(135deg, #4F8EFF 0%, rgba(79, 142, 255, 0.9) 100%)',
            boxShadow: '0 4px 20px rgba(79, 142, 255, 0.4)',
            transition: 'all 0.3s ease',
            zIndex: 1000,
            '&:hover': {
              background: 'linear-gradient(135deg, #7BA8FF 0%, #4F8EFF 100%)',
              boxShadow: '0 6px 28px rgba(79, 142, 255, 0.6)',
              transform: 'scale(1.1) translateY(-2px)',
            },
            '&:active': {
              transform: 'scale(0.95)',
            },
          }}
        >
          {isOnStatisticsPage ? <Home /> : <BarChart />}
        </Fab>
      </Tooltip>
    </Zoom>
  );
}
