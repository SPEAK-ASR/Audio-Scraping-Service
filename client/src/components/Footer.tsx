import { Heart } from 'lucide-react';

export function Footer() {
  return (
    <footer className="mt-16 border-t border-border bg-card/50">
      <div className="container mx-auto px-4 py-8">
        <div className="text-center">          
          <p className="text-xs text-muted-foreground flex items-center justify-center gap-1">
            Made with <Heart className="w-3 h-3 text-red-500" /> for S.P.E.A.K.
          </p>
        </div>
      </div>
    </footer>
  );
}