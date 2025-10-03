import { useState } from 'react';
import { Typography, Box } from '@mui/material';
import { YoutubeUrlInput } from './components/YoutubeUrlInput';
import { AudioClipsDisplay } from './components/AudioClipsDisplay';
import { TranscriptionView } from './components/TranscriptionView';
import { ProgressIndicator } from './components/ProgressIndicator';
import { CompletionView } from './components/CompletionView';
import { Footer } from './components/Footer';
import { LoadingState } from './components/LoadingState';
import type { ClipData, TranscribedClip, VideoMetadata } from './lib/api';

export type ProcessingStep = 'input' | 'processing' | 'clips' | 'transcription' | 'storage' | 'complete';

function App() {
  const [currentStep, setCurrentStep] = useState<ProcessingStep>('input');
  const [videoId, setVideoId] = useState<string>('');
  const [videoMetadata, setVideoMetadata] = useState<VideoMetadata | null>(null);
  const [clips, setClips] = useState<ClipData[]>([]);
  const [transcriptions, setTranscriptions] = useState<TranscribedClip[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processingError, setProcessingError] = useState<string | null>(null);

  const handleYoutubeSubmit = () => {
    setCurrentStep('processing');
    setIsProcessing(true);
    setProcessingError(null);
  };

  const handleClipsGenerated = (videoId: string, metadata: VideoMetadata, clipsData: ClipData[]) => {
    setVideoId(videoId);
    setVideoMetadata(metadata);
    setClips(clipsData);
    setCurrentStep('clips');
    setIsProcessing(false);
    setProcessingError(null);
  };

  const handleTranscriptionComplete = (transcribedClips: TranscribedClip[]) => {
    setTranscriptions(transcribedClips);
    setCurrentStep('transcription');
  };

  const handleStorageComplete = () => {
    setCurrentStep('complete');
  };

  const handleReset = () => {
    setCurrentStep('input');
    setVideoId('');
    setVideoMetadata(null);
    setClips([]);
    setTranscriptions([]);
    setIsProcessing(false);
    setProcessingError(null);
  };

  const handleProcessingError = (errorMessage: string) => {
    setCurrentStep('input');
    setIsProcessing(false);
    setProcessingError(errorMessage);
  };

  return (
    <Box sx={{ minHeight: '100vh', p: 2 }}>
      <Box sx={{ maxWidth: 1200, mx: 'auto' }}>
        <Box sx={{ textAlign: 'center', mb: 4, mt: 1}}>
          <Typography variant="h3" component="h1" fontWeight="bold" sx={{ mb: 1 }}>
            Audio Processor
          </Typography>
          <Typography 
            variant="body1" 
            color="text.secondary" 
            sx={{ 
              '& .highlight': {
                color: 'primary.main',
                fontWeight: 500,
              }
            }}
          >
            Process YouTube videos into audio clips with{' '}
            <Typography component="span" className="highlight">
              transcription
            </Typography>{' '}
            and{' '}
            <Typography component="span" className="highlight">
              cloud storage
            </Typography>
          </Typography>
        </Box>
        <ProgressIndicator 
          currentStep={currentStep} 
          isProcessing={isProcessing}
        />

        <Box sx={{ mt: 3 }}>
          {currentStep === 'input' && (
            <YoutubeUrlInput 
              onSubmit={handleYoutubeSubmit}
              onClipsGenerated={handleClipsGenerated}
              onError={handleProcessingError}
              initialError={processingError}
            />
          )}

          {currentStep === 'processing' && (
            <LoadingState
              title="Processing YouTube video..."
              description="This may take a few minutes depending on video length"
            />
          )}

          {(currentStep === 'clips' || currentStep === 'transcription' || currentStep === 'storage' || currentStep === 'complete') && (
            <AudioClipsDisplay
              videoId={videoId}
              clips={clips}
              videoMetadata={videoMetadata}
              onTranscriptionComplete={handleTranscriptionComplete}
              onStorageComplete={handleStorageComplete}
              onRevert={handleReset}
              currentStep={currentStep}
            />
          )}

          {currentStep === 'complete' && (
            <CompletionView
              videoId={videoId}
              videoMetadata={videoMetadata}
              totalClips={clips.length}
              transcriptionCount={transcriptions.length}
              onReset={handleReset}
            />
          )}

          {currentStep === 'transcription' && transcriptions.length > 0 && (
            <TranscriptionView
              transcriptions={transcriptions}
              videoMetadata={videoMetadata}
            />
          )}
        </Box>

        <Footer />
      </Box>
    </Box>
  );
}

export default App;
