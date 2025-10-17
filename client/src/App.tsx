import { useState } from 'react';
import { Routes, Route } from 'react-router-dom';
import { Typography, Box } from '@mui/material';
import { StatisticsFloatingButton } from './components/StatisticsFloatingButton';
import { YoutubeUrlInput } from './components/YoutubeUrlInput';
import { AudioClipsDisplay } from './components/AudioClipsDisplay';
import { TranscriptionView } from './components/TranscriptionView';
import { ProgressIndicator } from './components/ProgressIndicator';
import { CompletionView } from './components/CompletionView';
import { Footer } from './components/Footer';
import { LoadingState } from './components/LoadingState';
import { StatisticsPage } from './pages/StatisticsPage';
import type { ClipData, TranscribedClip, VideoMetadata } from './lib/api';

export type ProcessingStep = 'input' | 'processing' | 'clips' | 'transcription' | 'storage' | 'complete';

function HomePage() {
  const [currentStep, setCurrentStep] = useState<ProcessingStep>('input');
  const [videoId, setVideoId] = useState<string>('');
  const [domain, setDomain] = useState<string>('');
  const [videoMetadata, setVideoMetadata] = useState<VideoMetadata | null>(null);
  const [clips, setClips] = useState<ClipData[]>([]);
  const [transcriptions, setTranscriptions] = useState<TranscribedClip[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [isSavingToCloud, setIsSavingToCloud] = useState(false);
  const [processingError, setProcessingError] = useState<string | null>(null);

  const handleYoutubeSubmit = () => {
    setCurrentStep('processing');
    setIsProcessing(true);
    setProcessingError(null);
  };

  const handleClipsGenerated = (videoId: string, domain: string, metadata: VideoMetadata, clipsData: ClipData[]) => {
    setVideoId(videoId);
    setDomain(domain);
    setVideoMetadata(metadata);
    setClips(clipsData);
    setCurrentStep('clips');
    setIsProcessing(false);
    setProcessingError(null);
  };

  const handleTranscriptionComplete = (transcribedClips: TranscribedClip[]) => {
    setTranscriptions(transcribedClips);
    setIsTranscribing(false);
    if (transcribedClips.length === 0) {
      // If no transcriptions, stay on clips stage
      setCurrentStep('clips');
    }
  };

  const handleTranscriptionStart = () => {
    setCurrentStep('transcription');
    setIsTranscribing(true);
    setTranscriptions([]);
  };

  const handleCleanupComplete = (deletedFiles: string[]) => {
    // Remove deleted clips from both transcriptions and clips state
    setTranscriptions(prev => prev.filter(t => !deletedFiles.includes(t.clip_name)));
    setClips(prev => prev.filter(c => !deletedFiles.includes(c.clip_name)));
  };

  const handleStorageStart = () => {
    setCurrentStep('storage');
    setIsSavingToCloud(true);
  };

  const handleStorageComplete = () => {
    setIsSavingToCloud(false);
    setCurrentStep('complete');
  };

  const handleReset = () => {
    setCurrentStep('input');
    setVideoId('');
    setDomain('');
    setVideoMetadata(null);
    setClips([]);
    setTranscriptions([]);
    setIsProcessing(false);
    setIsTranscribing(false);
    setIsSavingToCloud(false);
    setProcessingError(null);
  };

  const handleProcessingError = (errorMessage: string) => {
    setCurrentStep('input');
    setIsProcessing(false);
    setProcessingError(errorMessage);
  };

  return (
    <Box sx={{ minHeight: '100vh' }}>
      <StatisticsFloatingButton />
      <Box sx={{ p: 2 }}>
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
                onTranscriptionStart={handleTranscriptionStart}
                onStorageStart={handleStorageStart}
                onStorageComplete={handleStorageComplete}
                onRevert={handleReset}
                currentStep={currentStep}
                isTranscribing={isTranscribing}
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

            {currentStep === 'transcription' && isTranscribing && (
              <LoadingState
                title="Transcribing audio clips..."
                description="This may take a few minutes depending on the number of clips"
              />
            )}

            {currentStep === 'transcription' && !isTranscribing && transcriptions.length > 0 && (
              <TranscriptionView
                transcriptions={transcriptions}
                videoMetadata={videoMetadata}
                videoId={videoId}
                onCleanupComplete={handleCleanupComplete}
                onRevert={handleReset}
              />
            )}

            {currentStep === 'storage' && isSavingToCloud && (
              <LoadingState
                title="Saving to cloud storage..."
                description="Uploading audio clips and updating database"
              />
            )}
          </Box>

          <Footer />
        </Box>
      </Box>
    </Box>
  );
}

function StatisticsPageWrapper() {
  return (
    <Box sx={{ minHeight: '100vh' }}>
      <StatisticsFloatingButton />
      <StatisticsPage />
      <Footer />
    </Box>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/statistics" element={<StatisticsPageWrapper />} />
    </Routes>
  );
}

export default App;
