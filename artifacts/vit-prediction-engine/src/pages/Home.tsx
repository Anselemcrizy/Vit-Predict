import React, { useState } from 'react';
import { Activity, Layers, Database } from 'lucide-react';
import { HistorySidebar } from '@/components/layout/HistorySidebar';
import { ImageUploader } from '@/components/predictions/ImageUploader';
import { PredictionDetails } from '@/components/predictions/PredictionDetails';
import { useGetPrediction } from '@workspace/api-client-react';

export default function Home() {
  const [activePredictionId, setActivePredictionId] = useState<number | null>(null);

  const { data: activePrediction, isLoading: isLoadingPrediction } = useGetPrediction(
    activePredictionId as number,
    { query: { enabled: !!activePredictionId } }
  );

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col lg:flex-row overflow-hidden relative tech-grid">
      
      {/* Background visual element defined in requirements.yaml */}
      <div className="fixed inset-0 z-0 pointer-events-none opacity-20 mixing-blend-screen">
        <img 
          src={`${import.meta.env.BASE_URL}images/tech-bg.png`} 
          alt="" 
          className="w-full h-full object-cover"
        />
      </div>

      {/* Radial gradient overlay to ensure readability */}
      <div className="fixed inset-0 z-0 pointer-events-none bg-[radial-gradient(circle_at_center,transparent_0%,hsl(var(--background))_80%)]" />

      {/* Sidebar */}
      <div className="relative z-10 h-screen hidden lg:block">
        <HistorySidebar 
          activeId={activePredictionId} 
          onSelect={(id) => setActivePredictionId(id)} 
        />
      </div>

      {/* Main Content */}
      <main className="flex-1 h-screen overflow-y-auto relative z-10 flex flex-col">
        {/* Header */}
        <header className="px-8 py-6 border-b border-border/50 glass-panel sticky top-0 z-20 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/30 flex items-center justify-center glow-box">
              <Layers className="w-5 h-5 text-primary" />
            </div>
            <div>
              <h1 className="font-display text-2xl font-bold tracking-wide">VIT<span className="text-primary">ENGINE</span></h1>
              <p className="text-xs text-muted-foreground font-mono">Vision Transformer Inference v1.0</p>
            </div>
          </div>
          
          <div className="hidden md:flex items-center gap-6 text-sm font-mono text-muted-foreground">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-success animate-pulse" />
              API Connected
            </div>
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4" />
              PgSQL Ready
            </div>
          </div>
        </header>

        <div className="flex-1 p-4 md:p-8 flex flex-col">
          {/* Mobile sidebar trigger/replacement could go here, omitting for brevity to focus on core UI */}
          
          <div className="max-w-6xl w-full mx-auto space-y-12 pb-12">
            
            {/* Top section: Upload */}
            <section>
              <div className="mb-6 text-center">
                <h2 className="text-2xl font-display font-semibold mb-2">New Analysis</h2>
                <p className="text-muted-foreground text-sm max-w-lg mx-auto">
                  Submit an image to the Vision Transformer model to extract classifications, 
                  labels, and confidence scores in real-time.
                </p>
              </div>
              
              <ImageUploader onSuccess={(id) => setActivePredictionId(id)} />
            </section>

            {/* Bottom section: Results */}
            <section className="min-h-[400px]">
              {activePredictionId ? (
                isLoadingPrediction ? (
                  <div className="h-[400px] w-full glass-panel rounded-2xl flex items-center justify-center border-dashed">
                    <div className="flex flex-col items-center text-primary">
                      <Activity className="w-8 h-8 animate-spin" />
                      <span className="mt-4 font-mono text-sm">Retrieving tensor data...</span>
                    </div>
                  </div>
                ) : activePrediction ? (
                  <div className="pt-8 border-t border-border/50">
                    <h2 className="text-2xl font-display font-semibold mb-6 flex items-center gap-2">
                      <Activity className="w-6 h-6 text-secondary" />
                      Inference Results
                    </h2>
                    <PredictionDetails prediction={activePrediction} />
                  </div>
                ) : null
              ) : (
                <div className="h-full min-h-[300px] flex flex-col items-center justify-center text-muted-foreground/50 border-2 border-dashed border-border/50 rounded-2xl mt-8">
                  <Layers className="w-12 h-12 mb-4 opacity-50" />
                  <p className="font-display text-xl">Awaiting Input</p>
                  <p className="text-sm font-mono mt-2">Select a history item or upload a new image</p>
                </div>
              )}
            </section>

          </div>
        </div>
      </main>

      {/* Mobile History View (Simplified below main content on small screens) */}
      <div className="lg:hidden relative z-10 border-t border-border/50 h-[40vh]">
         <HistorySidebar 
          activeId={activePredictionId} 
          onSelect={(id) => {
            setActivePredictionId(id);
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }} 
        />
      </div>
    </div>
  );
}
