import {
  Stepper,
  Step,
  StepLabel,
  Box,
  CircularProgress,
  styled
} from '@mui/material';
import {
  Input as InputIcon,
  VideoLibrary as ProcessingIcon,
  AudioFile as ClipsIcon,
  Transcribe as TranscriptionIcon,
  CloudUpload as StorageIcon,
  CheckCircle as CompleteIcon
} from '@mui/icons-material';
import type { ProcessingStep } from '../App';

interface ProgressIndicatorProps {
  currentStep: ProcessingStep;
  isProcessing: boolean;
}

const steps = [
  { key: 'input', label: 'Input URL', icon: InputIcon },
  { key: 'processing', label: 'Processing', icon: ProcessingIcon },
  { key: 'clips', label: 'Audio Clips', icon: ClipsIcon },
  { key: 'transcription', label: 'Transcription', icon: TranscriptionIcon },
  { key: 'storage', label: 'Cloud Storage', icon: StorageIcon },
  { key: 'complete', label: 'Complete', icon: CompleteIcon },
];

const CustomStepIcon = styled(Box, {
  shouldForwardProp: (prop) => prop !== 'active' && prop !== 'completed',
})<{ active?: boolean; completed?: boolean }>(({ theme, active, completed }) => ({
  width: 40,
  height: 40,
  border: `2px solid ${completed || active ? theme.palette.primary.main : theme.palette.divider}`,
  borderRadius: '50%',
  backgroundColor: completed ? theme.palette.primary.main : 'transparent',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  transition: 'all 0.3s ease',
  boxShadow: active || completed ? `0 0 12px ${theme.palette.primary.main}40` : 'none',
  transform: active ? 'scale(1.05)' : 'scale(1)',
  color: completed ? theme.palette.primary.contrastText : 
         active ? theme.palette.primary.main : theme.palette.text.secondary,
}));

const CustomStepLabel = styled(StepLabel)(({ theme }) => ({
  '& .MuiStepLabel-label': {
    marginTop: theme.spacing(1),
    fontSize: '0.75rem',
    fontWeight: 500,
    transition: 'all 0.3s ease',
    
    '&.Mui-active': {
      color: theme.palette.primary.main,
      fontWeight: 600,
    },
    
    '&.Mui-completed': {
      color: theme.palette.primary.main,
      opacity: 0.9,
    },
  },
}));



export function ProgressIndicator({ currentStep, isProcessing }: ProgressIndicatorProps) {
  const getCurrentStepIndex = () => {
    return steps.findIndex(step => step.key === currentStep);
  };

  const currentStepIndex = getCurrentStepIndex();

  return (
    <Box sx={{ my: 5, overflow: 'visible' }}>
      <Stepper 
        activeStep={currentStepIndex} 
        alternativeLabel
        sx={{
          '& .MuiStepConnector-root': {
            top: 20,
            '& .MuiStepConnector-line': {
              height: 2,
              border: 0,
              backgroundColor: 'divider',
              borderRadius: 1,
            },
          },
          '& .MuiStepConnector-active .MuiStepConnector-line': {
            background: 'linear-gradient(90deg, #4F8EFF 0%, rgba(79, 142, 255, 0.7) 100%)',
            boxShadow: '0 0 6px rgba(79, 142, 255, 0.3)',
          },
          '& .MuiStepConnector-completed .MuiStepConnector-line': {
            background: 'linear-gradient(90deg, #4F8EFF 0%, rgba(79, 142, 255, 0.7) 100%)',
            boxShadow: '0 0 6px rgba(79, 142, 255, 0.3)',
          },
        }}
      >
          {steps.map((step, index) => {
            const isCompleted = index < currentStepIndex;
            const isCurrent = index === currentStepIndex;
            const isProcessingStep = isCurrent && isProcessing;
            const IconComponent = step.icon;

            return (
              <Step key={step.key} completed={isCompleted}>
                <CustomStepLabel
                  StepIconComponent={() => (
                    <Box sx={{ position: 'relative', display: 'inline-flex' }}>
                      <CustomStepIcon
                        active={isCurrent}
                        completed={isCompleted}
                      >
                        {isProcessingStep ? (
                          <CircularProgress 
                            size={20} 
                            sx={{ 
                              color: 'primary.main',
                              animation: 'pulse 2s ease-in-out infinite',
                            }} 
                          />
                        ) : (
                          <IconComponent 
                            sx={{ 
                              fontSize: 20,
                            }} 
                          />
                        )}
                      </CustomStepIcon>
                    </Box>
                  )}
                >
                  {step.label}
                </CustomStepLabel>
              </Step>
            );
          })}
        </Stepper>
    </Box>
  );
}