import React from 'react';
import { format } from 'date-fns';
import { Cpu, Clock, Calendar, CheckCircle2, AlertTriangle, Layers } from 'lucide-react';
import { Progress } from '@/components/ui/progress';
import { Prediction } from '@workspace/api-client-react';
import { motion } from 'framer-motion';

interface PredictionDetailsProps {
  prediction: Prediction;
}

export function PredictionDetails({ prediction }: PredictionDetailsProps) {
  // Safe parsing in case results is empty or malformed
  const results = Array.isArray(prediction.results) ? prediction.results : [];
  
  // High confidence threshold for styling
  const isHighConfidence = prediction.topConfidence > 0.8;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="w-full max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-2 gap-8"
    >
      {/* Left Column: Image */}
      <div className="space-y-4">
        <div className="glass-panel rounded-2xl p-2 relative overflow-hidden group">
          <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 z-0" />
          <div className="relative z-10 rounded-xl overflow-hidden bg-black/50 aspect-square flex items-center justify-center border border-white/5">
            <img 
              src={prediction.imageData || prediction.imageUrl} 
              alt="Analyzed subject" 
              className="w-full h-full object-contain"
              crossOrigin="anonymous"
            />
            {/* Technical scanning line overlay */}
            <div className="absolute top-0 left-0 w-full h-[2px] bg-primary/50 shadow-[0_0_10px_rgba(0,255,255,0.8)] animate-[scan_3s_ease-in-out_infinite]" />
          </div>
        </div>

        <div className="flex flex-wrap gap-2">
          <div className="glass-panel px-3 py-2 rounded-lg flex items-center gap-2 text-xs text-muted-foreground flex-1 min-w-[120px]">
            <Layers className="w-3 h-3 text-primary" />
            <span className="truncate" title={prediction.modelName}>{prediction.modelName}</span>
          </div>
          {prediction.processingTimeMs && (
            <div className="glass-panel px-3 py-2 rounded-lg flex items-center gap-2 text-xs text-muted-foreground shrink-0">
              <Clock className="w-3 h-3 text-secondary" />
              <span>{prediction.processingTimeMs}ms</span>
            </div>
          )}
          <div className="glass-panel px-3 py-2 rounded-lg flex items-center gap-2 text-xs text-muted-foreground shrink-0">
            <Calendar className="w-3 h-3 text-muted-foreground" />
            <span>{format(new Date(prediction.createdAt), 'MMM d, HH:mm')}</span>
          </div>
        </div>
      </div>

      {/* Right Column: Results */}
      <div className="flex flex-col h-full">
        <div className="glass-panel rounded-2xl p-6 flex-1 flex flex-col">
          
          <div className="mb-8">
            <h2 className="text-sm font-semibold uppercase tracking-widest text-muted-foreground mb-2 flex items-center gap-2">
              <Cpu className="w-4 h-4" />
              Primary Classification
            </h2>
            
            <div className="flex items-end gap-4 flex-wrap">
              <h1 className="text-4xl lg:text-5xl font-display font-bold text-foreground leading-none capitalize">
                {prediction.topLabel.split(',')[0]}
              </h1>
              <div className={`px-3 py-1 rounded-full border text-sm font-bold flex items-center gap-1.5 mb-1 ${
                isHighConfidence 
                  ? 'bg-success/10 border-success/30 text-success' 
                  : 'bg-secondary/10 border-secondary/30 text-secondary'
              }`}>
                {isHighConfidence ? <CheckCircle2 className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
                {(prediction.topConfidence * 100).toFixed(1)}% Match
              </div>
            </div>
          </div>

          <div className="space-y-5 flex-1">
            <h3 className="text-sm font-semibold text-foreground border-b border-border/50 pb-2">Full Confidence Distribution</h3>
            
            <div className="space-y-4">
              {results.slice(0, 5).map((result, idx) => (
                <motion.div 
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 + 0.3, duration: 0.4 }}
                >
                  <div className="flex justify-between items-end mb-1 text-sm">
                    <span className="font-medium capitalize text-foreground truncate mr-4">
                      {result.label.split(',')[0]}
                    </span>
                    <span className="font-mono text-muted-foreground shrink-0">
                      {(result.confidence * 100).toFixed(2)}%
                    </span>
                  </div>
                  <Progress 
                    value={result.confidence * 100} 
                    className="h-1.5"
                    indicatorClassName={
                      idx === 0 ? "bg-primary shadow-[0_0_10px_rgba(0,255,255,0.5)]" : 
                      idx === 1 ? "bg-secondary shadow-[0_0_8px_rgba(150,50,255,0.4)]" : 
                      "bg-muted-foreground/40"
                    }
                  />
                </motion.div>
              ))}
            </div>
          </div>
          
        </div>
      </div>
    </motion.div>
  );
}
