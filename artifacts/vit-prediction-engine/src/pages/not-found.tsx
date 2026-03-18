import { Card, CardContent } from "@/components/ui";
import { AlertCircle } from "lucide-react";
import { Link } from "wouter";

export default function NotFound() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background tech-grid p-4">
      <Card className="w-full max-w-md border-white/10 bg-black/50 backdrop-blur-xl">
        <CardContent className="pt-10 pb-10 flex flex-col items-center text-center">
          <AlertCircle className="h-16 w-16 text-destructive mb-6" />
          <h1 className="text-3xl font-bold text-white font-display uppercase tracking-widest mb-2">404 Error</h1>
          <p className="text-muted-foreground mb-8">
            The prediction or page you are looking for has been purged from the system.
          </p>
          <Link 
            href="/" 
            className="px-6 py-3 rounded-md bg-primary text-primary-foreground font-semibold hover:bg-primary/90 transition-colors"
          >
            Return to Dashboard
          </Link>
        </CardContent>
      </Card>
    </div>
  );
}
