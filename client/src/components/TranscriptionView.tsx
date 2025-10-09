import { useState } from 'react';
import { MessageSquare, ChevronDown, ChevronUp, Copy, Check, Trash2, RefreshCw } from 'lucide-react';
import type { TranscribedClip, VideoMetadata } from '../lib/api';
import { audioApi } from '../lib/api';
import { cn } from '../lib/utils';

interface TranscriptionViewProps {
  transcriptions: TranscribedClip[];
  videoMetadata: VideoMetadata | null;
  videoId: string;
  onCleanupComplete?: (deletedFiles: string[]) => void;
  onRevert?: () => void;
}

export function TranscriptionView({ transcriptions, videoMetadata, videoId, onCleanupComplete, onRevert }: TranscriptionViewProps) {
  const [expandedClips, setExpandedClips] = useState<Set<string>>(new Set());
  const [copiedClips, setCopiedClips] = useState<Set<string>>(new Set());
  const [isDeleting, setIsDeleting] = useState(false);
  const [isReverting, setIsReverting] = useState(false);

  const toggleExpanded = (clipName: string) => {
    const newExpanded = new Set(expandedClips);
    if (expandedClips.has(clipName)) {
      newExpanded.delete(clipName);
    } else {
      newExpanded.add(clipName);
    }
    setExpandedClips(newExpanded);
  };

  const copyToClipboard = async (clipName: string, text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedClips(prev => new Set(prev).add(clipName));
      setTimeout(() => {
        setCopiedClips(prev => {
          const newSet = new Set(prev);
          newSet.delete(clipName);
          return newSet;
        });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  const copyAllTranscriptions = async () => {
    const allText = transcriptions
      .map(clip => `${clip.clip_name}:\n${(clip.transcription && clip.transcription.trim() !== '') ? clip.transcription : 'No transcription available'}`)
      .join('\n\n');
    
    try {
      await navigator.clipboard.writeText(`${videoMetadata?.title || 'YouTube Video'} - Transcriptions\n\n${allText}`);
      setCopiedClips(new Set(['all']));
      setTimeout(() => {
        setCopiedClips(prev => {
          const newSet = new Set(prev);
          newSet.delete('all');
          return newSet;
        });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy all text:', err);
    }
  };

  const handleDeleteFailedTranscriptions = async () => {
    const nullCount = transcriptions.filter(clip => !clip.transcription || clip.transcription.trim() === '').length;
    
    if (nullCount === 0) {
      alert('No failed transcriptions to delete!');
      return;
    }

    const confirmDelete = window.confirm(
      `This will permanently delete ${nullCount} audio file${nullCount > 1 ? 's' : ''} with no transcription and remove them from all metadata.\n\nAre you sure you want to continue?`
    );

    if (!confirmDelete) return;

    setIsDeleting(true);
    try {
      const response = await audioApi.cleanNullTranscriptions(videoId);
      if (response.success) {
        alert(`Successfully deleted ${response.total_deleted} audio files with null transcriptions.\n\n${response.remaining_clips} clips remaining.`);
        // Call the callback to update parent component state
        if (onCleanupComplete) {
          onCleanupComplete(response.deleted_files);
        }
      }
    } catch (error) {
      console.error('Failed to delete null transcriptions:', error);
      alert('Failed to delete null transcriptions. Please check the console for details.');
    } finally {
      setIsDeleting(false);
    }
  };

  const handleRevert = async () => {
    const confirmRevert = window.confirm(
      `This will permanently delete all audio files and metadata for this video.\n\nAre you sure you want to start over?`
    );

    if (!confirmRevert) return;

    setIsReverting(true);
    try {
      await audioApi.deleteAudioFiles(videoId);
      if (onRevert) {
        onRevert();
      }
    } catch (error) {
      console.error('Start over failed:', error);
      alert('Failed to delete files. Please check the console for details.');
    } finally {
      setIsReverting(false);
    }
  };

  const truncateText = (text: string | null, maxLength: number = 150) => {
    if (!text || text.trim() === '') return 'No transcription available';
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength) + '...';
  };

  const nullTranscriptionCount = transcriptions.filter(clip => !clip.transcription || clip.transcription.trim() === '').length;

  return (
    <div className="mt-2">
      <div className="bg-card rounded-lg p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-primary" />
            <h3 className="text-xl font-semibold">Transcriptions</h3>
            <span className="bg-primary/10 text-primary px-2 py-1 rounded-full text-sm">
              {transcriptions.length} clips
            </span>
            {nullTranscriptionCount > 0 && (
              <span className="bg-red-100 text-red-800 px-2 py-1 rounded-full text-sm">
                {nullTranscriptionCount} failed
              </span>
            )}
          </div>
          
          <div className="flex gap-2">
            <button
              onClick={handleRevert}
              disabled={isReverting}
              className={cn(
                "flex items-center gap-2 px-3 py-2 text-sm bg-orange-600 hover:bg-orange-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
                isReverting && "cursor-wait"
              )}
              title="Delete all files and start over"
            >
              <RefreshCw className={cn("w-4 h-4", isReverting && "animate-spin")} />
              {isReverting ? 'Starting Over...' : 'Start Over'}
            </button>
            {nullTranscriptionCount > 0 && (
              <button
                onClick={handleDeleteFailedTranscriptions}
                disabled={isDeleting}
                className={cn(
                  "flex items-center gap-2 px-3 py-2 text-sm bg-red-600 hover:bg-red-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed",
                  isDeleting && "cursor-wait"
                )}
                title={`Delete ${nullTranscriptionCount} audio file${nullTranscriptionCount > 1 ? 's' : ''} with no transcription`}
              >
                <Trash2 className="w-4 h-4" />
                {isDeleting ? 'Deleting...' : `Delete Failed (${nullTranscriptionCount})`}
              </button>
            )}
            <button
              onClick={copyAllTranscriptions}
              className={cn(
                "flex items-center gap-2 px-3 py-2 text-sm bg-secondary hover:bg-secondary/80 rounded-md transition-colors",
                copiedClips.has('all') && "bg-green-600 hover:bg-green-600/80"
              )}
            >
              {copiedClips.has('all') ? (
                <>
                  <Check className="w-4 h-4" />
                  Copied!
                </>
              ) : (
                <>
                  <Copy className="w-4 h-4" />
                  Copy All
                </>
              )}
            </button>
          </div>
        </div>

        <div className="space-y-4 max-h-[300px] overflow-y-auto">
          {transcriptions.map((clip) => {
            const isExpanded = expandedClips.has(clip.clip_name);
            const isCopied = copiedClips.has(clip.clip_name);
            const displayText = isExpanded ? ((clip.transcription && clip.transcription.trim() !== '') ? clip.transcription : 'No transcription available') : truncateText(clip.transcription);
            const needsTruncation = (clip.transcription && clip.transcription.trim() !== '' && clip.transcription.length > 150);

            return (
              <div key={clip.clip_name} className="bg-secondary rounded-lg p-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium text-sm truncate">{clip.clip_name}</h4>
                        {(!clip.transcription || clip.transcription.trim() === '') && (
                          <span className="bg-red-100 text-red-800 text-xs px-2 py-1 rounded-full">
                            Failed
                          </span>
                        )}
                      </div>
                      <div className="flex items-center gap-2 flex-shrink-0">
                        <button
                          onClick={() => copyToClipboard(clip.clip_name, (clip.transcription && clip.transcription.trim() !== '') ? clip.transcription : 'No transcription available')}
                          className={cn(
                            "p-1 hover:bg-muted rounded transition-colors",
                            isCopied && "text-green-500"
                          )}
                          title="Copy transcription"
                        >
                          {isCopied ? (
                            <Check className="w-4 h-4" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                        
                        {needsTruncation && (
                          <button
                            onClick={() => toggleExpanded(clip.clip_name)}
                            className="p-1 hover:bg-muted rounded transition-colors"
                            title={isExpanded ? "Show less" : "Show more"}
                          >
                            {isExpanded ? (
                              <ChevronUp className="w-4 h-4" />
                            ) : (
                              <ChevronDown className="w-4 h-4" />
                            )}
                          </button>
                        )}
                      </div>
                    </div>
                    
                    <p className={cn(
                      "text-sm leading-relaxed whitespace-pre-wrap",
                      (clip.transcription && clip.transcription.trim() !== '') ? "text-muted-foreground" : "text-red-500 italic"
                    )}>
                      {displayText}
                    </p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {transcriptions.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <MessageSquare className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>No transcriptions available</p>
          </div>
        )}
      </div>
    </div>
  );
}
