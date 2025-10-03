import { AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '../lib/utils';

interface ErrorBoundaryProps {
  error: Error | null;
  onRetry: () => void;
}

export function ErrorBoundary({ error, onRetry }: ErrorBoundaryProps) {
  if (!error) return null;

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-destructive/10 border border-destructive rounded-lg p-8 text-center">
        <AlertCircle className="w-16 h-16 text-destructive mx-auto mb-4" />
        <h2 className="text-2xl font-bold text-destructive mb-2">Something went wrong</h2>
        <p className="text-muted-foreground mb-6">
          {error.message || 'An unexpected error occurred while processing your request.'}
        </p>
        
        <div className="bg-secondary rounded-lg p-4 mb-6 text-left">
          <h3 className="font-semibold mb-2">Error Details:</h3>
          <pre className="text-sm text-muted-foreground overflow-auto">
            {error.stack || error.toString()}
          </pre>
        </div>

        <div className="space-y-4">
          <button
            onClick={onRetry}
            className={cn(
              "flex items-center justify-center gap-2 w-full bg-primary text-primary-foreground",
              "py-3 px-6 rounded-lg font-medium hover:bg-primary/90",
              "focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2",
              "transition-colors"
            )}
          >
            <RefreshCw className="w-5 h-5" />
            Try Again
          </button>

          <p className="text-xs text-muted-foreground">
            If the problem persists, please check your internet connection and try again.
          </p>
        </div>
      </div>
    </div>
  );
}