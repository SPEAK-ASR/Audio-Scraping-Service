import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#4F8EFF', // Blue accent
      light: '#7BA8FF',
      dark: '#2C5BA8',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#FFFFFF',
      light: '#FFFFFF',
      dark: '#E0E0E0',
      contrastText: '#000000',
    },
    background: {
      default: '#141414', // Rich black background (not pitch black)
      paper: '#1F1F1F', // Card background
    },
    surface: {
      main: '#2A2A2A',
    },
    text: {
      primary: '#FAFAFA',
      secondary: '#999999',
    },
    divider: '#333333',
    error: {
      main: '#FF5252',
    },
    warning: {
      main: '#FFA726',
    },
    info: {
      main: '#29B6F6',
    },
    success: {
      main: '#66BB6A',
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '3rem',
      fontWeight: 700,
      background: 'linear-gradient(135deg, #4F8EFF 0%, #FFFFFF 100%)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      backgroundClip: 'text',
    },
    h2: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: '#FAFAFA',
    },
    h3: {
      fontSize: '2rem',
      fontWeight: 600,
      color: '#FAFAFA',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: '#FAFAFA',
    },
    body1: {
      fontSize: '1rem',
      color: '#FAFAFA',
    },
    body2: {
      fontSize: '0.875rem',
      color: '#999999',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          background: `
            linear-gradient(135deg, 
              rgba(79, 142, 255, 0.15) 0%, 
              #0A0A0A 25%, 
              #000000 50%, 
              #0A0A0A 75%, 
              rgba(79, 142, 255, 0.15) 100%
            ),
            linear-gradient(45deg, 
              rgba(79, 142, 255, 0.08) 0%, 
              transparent 30%, 
              transparent 70%, 
              rgba(79, 142, 255, 0.08) 100%
            ),
            radial-gradient(circle at 20% 20%, rgba(79, 142, 255, 0.12) 0%, transparent 40%),
            radial-gradient(circle at 80% 80%, rgba(79, 142, 255, 0.08) 0%, transparent 40%),
            #000000
          `,
          backgroundAttachment: 'fixed',
          minHeight: '100vh',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          background: 'rgba(31, 31, 31, 0.8)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(79, 142, 255, 0.1)',
          borderRadius: 12,
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.2)',
          transition: 'all 0.3s ease',
          '&:hover': {
            background: 'rgba(42, 42, 42, 0.9)',
            borderColor: 'rgba(79, 142, 255, 0.2)',
            transform: 'translateY(-2px)',
            boxShadow: '0 8px 24px rgba(0, 0, 0, 0.3)',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          fontWeight: 500,
          fontSize: '0.875rem',
          padding: '8px 16px',
          boxShadow: 'none',
          transition: 'all 0.3s ease',
          minHeight: 'auto',
        },
        contained: {
          background: 'linear-gradient(135deg, #4F8EFF 0%, rgba(79, 142, 255, 0.8) 100%)',
          boxShadow: '0 2px 8px rgba(79, 142, 255, 0.3)',
          '&:hover': {
            background: 'linear-gradient(135deg, #7BA8FF 0%, #4F8EFF 100%)',
            boxShadow: '0 4px 12px rgba(79, 142, 255, 0.4)',
            transform: 'translateY(-1px)',
          },
        },
        sizeLarge: {
          padding: '10px 20px',
          fontSize: '1rem',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            backgroundColor: 'rgba(42, 42, 42, 0.8)',
            backdropFilter: 'blur(10px)',
            borderRadius: 12,
            '& fieldset': {
              borderColor: '#333333',
              transition: 'all 0.3s ease',
            },
            '&:hover fieldset': {
              borderColor: 'rgba(79, 142, 255, 0.3)',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#4F8EFF',
              boxShadow: '0 0 0 3px rgba(79, 142, 255, 0.2)',
            },
          },
          '& .MuiInputLabel-root': {
            color: '#999999',
            '&.Mui-focused': {
              color: '#4F8EFF',
            },
          },
        },
      },
    },
    MuiIconButton: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          transition: 'all 0.3s ease',
          '&:hover': {
            backgroundColor: 'rgba(79, 142, 255, 0.1)',
            transform: 'scale(1.05)',
          },
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          color: '#4F8EFF',
          '& .MuiSlider-track': {
            background: 'linear-gradient(90deg, #4F8EFF 0%, rgba(79, 142, 255, 0.7) 100%)',
            boxShadow: '0 0 8px rgba(79, 142, 255, 0.3)',
          },
          '& .MuiSlider-thumb': {
            backgroundColor: '#4F8EFF',
            boxShadow: '0 0 6px rgba(79, 142, 255, 0.4)',
            '&:hover': {
              boxShadow: '0 0 12px rgba(79, 142, 255, 0.6)',
            },
          },
          '& .MuiSlider-rail': {
            color: '#333333',
          },
        },
      },
    },
    MuiStepper: {
      styleOverrides: {
        root: {
          backgroundColor: 'transparent',
        },
      },
    },
    MuiStepIcon: {
      styleOverrides: {
        root: {
          '&.Mui-active': {
            color: '#4F8EFF',
            boxShadow: '0 0 12px rgba(79, 142, 255, 0.4)',
          },
          '&.Mui-completed': {
            color: '#4F8EFF',
          },
        },
      },
    },
    MuiStepLabel: {
      styleOverrides: {
        label: {
          color: '#999999',
          '&.Mui-active': {
            color: '#4F8EFF',
            fontWeight: 600,
          },
          '&.Mui-completed': {
            color: '#4F8EFF',
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          backgroundColor: '#333333',
          borderRadius: 8,
          height: 8,
        },
        bar: {
          background: 'linear-gradient(90deg, #4F8EFF 0%, rgba(79, 142, 255, 0.7) 100%)',
          borderRadius: 8,
          boxShadow: '0 0 8px rgba(79, 142, 255, 0.3)',
        },
      },
    },
  },
});

// Extend the theme to include custom types
declare module '@mui/material/styles' {
  interface Palette {
    surface: Palette['primary'];
  }

  interface PaletteOptions {
    surface?: PaletteOptions['primary'];
  }
}