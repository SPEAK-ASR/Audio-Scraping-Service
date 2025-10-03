import { cn } from '../lib/utils';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function LoadingSpinner({ size = 'md', className }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-16 w-16'
  };

  return (
    <div className={cn('animate-spin rounded-full border-b-2 border-primary', sizeClasses[size], className)} />
  );
}

interface LoadingStateProps {
  title: string;
  description?: string;
  progress?: number;
}

export function LoadingState({ title, description, progress }: LoadingStateProps) {
  return (
    <div className="text-center py-12">
      <LoadingSpinner size="lg" className="mx-auto mb-6" />
      <h3 className="text-xl font-semibold mb-2">{title}</h3>
      {description && (
        <p className="text-muted-foreground mb-4">{description}</p>
      )}
      {progress !== undefined && (
        <div className="max-w-xs mx-auto">
          <div className="w-full bg-muted rounded-full h-2 mb-2">
            <div 
              className="bg-primary h-2 rounded-full transition-all duration-300"
              style={{ width: `${Math.min(100, Math.max(0, progress))}%` }}
            />
          </div>
          <p className="text-sm text-muted-foreground">{Math.round(progress)}% complete</p>
        </div>
      )}
    </div>
  );
}