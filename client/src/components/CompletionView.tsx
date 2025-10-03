import { CheckCircle } from 'lucide-react';
import { Button } from '@mui/material';
import type { VideoMetadata } from '../lib/api';
// Completion view for successful processing

interface CompletionViewProps {
  videoId: string;
  videoMetadata: VideoMetadata | null;
  totalClips: number;
  transcriptionCount: number;
  onReset: () => void;
}

export function CompletionView({
  totalClips, 
  transcriptionCount,
  onReset,
  videoMetadata
}: CompletionViewProps) {

  const videoTitle = videoMetadata?.title ?? 'Video title unavailable';
  const videoAuthor = videoMetadata?.uploader ?? 'Unknown creator';

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-card rounded-lg p-8 pt-4 text-center">
        <div className="mb-2">
          <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-4" />
          <h2 className="text-3xl font-bold text-green-500 mb-2">Processing Complete!</h2>
          <p className="text-muted-foreground">
            All audio clips have been processed and saved successfully
          </p>
        </div>

        <div className="bg-secondary rounded-lg p-6 mb-2">

          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-primary mb-1">{totalClips}</div>
              <div className="text-sm text-muted-foreground">Total Clips</div>
            </div>

            <div className="rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-500 mb-1">{transcriptionCount}</div>
              <div className="text-sm text-muted-foreground">Transcribed</div>
            </div>

            <div className="rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-500 mb-1">
                {totalClips > 0 ? Math.round((transcriptionCount / totalClips) * 100) : 0}%
              </div>
              <div className="text-sm text-muted-foreground">Success Rate</div>
            </div>
          </div>
        </div>
          <Button
            onClick={onReset}
            variant="outlined"
            size="medium"
            sx={{ 
              textTransform: 'none',
              mb: 2
            }}
          >
            Process Another Video
          </Button>
        

        <div className="mt-6 text-xs text-muted-foreground">
          <p>Audio files are stored locally and in Google Cloud Storage</p>
          <p>Transcription data has been saved to the database</p>
        </div>
      </div>
    </div>
  );
}
