import { useGetPrediction } from "@workspace/api-client-react";
import { Card, Badge, cn } from "@/components/ui";
import { motion } from "framer-motion";
import { format } from "date-fns";
import { ShieldAlert, TrendingUp, BarChart3, BrainCircuit, Calendar, Activity } from "lucide-react";

export function PredictionDetails({ id }: { id: number }) {
  const { data: prediction, isLoading, error } = useGetPrediction(id);

  if (isLoading) return <div className="p-12 text-center text-muted-foreground animate-pulse">Loading intelligence data...</div>;
  if (error || !prediction) return <div className="p-12 text-center text-destructive">Failed to load prediction data.</div>;

  const formatEv = (ev: number) => {
    const sign = ev > 0 ? "+" : "";
    return `${sign}${ev.toFixed(2)}%`;
  };

  const isPositiveEv = prediction.bestBetEv > 0;

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="w-full max-w-5xl mx-auto pb-20 space-y-6"
    >
      {/* Header / Match Info */}
      <Card className="glass-panel overflow-hidden border-t-primary/30 relative">
        <div className="absolute top-0 right-0 p-8 opacity-5 pointer-events-none">
           <Activity className="w-64 h-64" />
        </div>
        
        <div className="p-8 flex flex-col md:flex-row justify-between items-center gap-6 relative z-10">
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start gap-3 mb-2">
              <Badge variant="outline" className="bg-white/5 border-white/10 uppercase tracking-widest text-[10px]">
                {prediction.sport}
              </Badge>
              {prediction.league && (
                <span className="text-sm text-muted-foreground font-display">{prediction.league}</span>
              )}
              {prediction.matchDate && (
                <span className="text-sm text-muted-foreground flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> {prediction.matchDate}
                </span>
              )}
            </div>
            <h2 className="text-3xl md:text-5xl font-display font-bold text-white tracking-tight">
              {prediction.homeTeam} <span className="text-primary/50 font-sans text-2xl mx-2">vs</span> {prediction.awayTeam}
            </h2>
            <div className="mt-2 text-xs font-mono text-muted-foreground opacity-50 flex gap-4">
              <span>ID: {prediction.id}</span>
              <span>TIME: {prediction.processingTimeMs}ms</span>
            </div>
          </div>
          
          {/* Hero Metric: Best Bet */}
          <div className="flex-shrink-0 bg-black/40 border border-white/10 rounded-2xl p-6 text-center min-w-[240px] shadow-inner shadow-black/50">
            <div className="text-xs font-display uppercase tracking-widest text-muted-foreground mb-2 flex items-center justify-center gap-2">
              <TrendingUp className="w-4 h-4 text-primary" /> Primary Edge
            </div>
            <div className="text-2xl font-bold text-white mb-1">{prediction.bestBet}</div>
            <div className="flex items-center justify-center gap-3">
              <Badge className={cn("text-lg font-mono px-3 py-1", isPositiveEv ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-rose-500/20 text-rose-400 border border-rose-500/30")}>
                EV: {formatEv(prediction.bestBetEv)}
              </Badge>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column: Probs & AI */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Win Probabilities */}
          <Card className="p-6 bg-card/60 backdrop-blur-md border-white/5">
            <h3 className="text-sm font-display uppercase tracking-widest text-muted-foreground mb-6 flex items-center gap-2">
              <BarChart3 className="w-4 h-4" /> True Probabilities
            </h3>
            
            <div className="space-y-4">
              <div className="flex justify-between text-sm font-semibold">
                <span className="text-white w-1/3 text-left">{prediction.homeTeam}</span>
                {prediction.drawProb !== null && <span className="text-muted-foreground w-1/3 text-center">Draw</span>}
                <span className="text-white w-1/3 text-right">{prediction.awayTeam}</span>
              </div>
              
              <div className="h-6 flex rounded-full overflow-hidden bg-white/5 border border-white/10">
                <div 
                  className="h-full bg-blue-500 transition-all duration-1000 ease-out"
                  style={{ width: `${prediction.homeWinProb * 100}%` }}
                />
                {prediction.drawProb !== null && (
                  <div 
                    className="h-full bg-slate-500 transition-all duration-1000 ease-out border-l border-r border-black/20"
                    style={{ width: `${prediction.drawProb * 100}%` }}
                  />
                )}
                <div 
                  className="h-full bg-purple-500 transition-all duration-1000 ease-out"
                  style={{ width: `${prediction.awayWinProb * 100}%` }}
                />
              </div>
              
              <div className="flex justify-between text-xl font-display font-bold">
                <span className="text-blue-400 w-1/3 text-left">{(prediction.homeWinProb * 100).toFixed(1)}%</span>
                {prediction.drawProb !== null && <span className="text-slate-400 w-1/3 text-center">{(prediction.drawProb * 100).toFixed(1)}%</span>}
                <span className="text-purple-400 w-1/3 text-right">{(prediction.awayWinProb * 100).toFixed(1)}%</span>
              </div>
            </div>
          </Card>

          {/* AI Consensus Narrative */}
          <Card className="p-6 bg-primary/5 border-primary/20 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-1 h-full bg-primary" />
            <h3 className="text-sm font-display uppercase tracking-widest text-primary mb-4 flex items-center gap-2">
              <BrainCircuit className="w-4 h-4" /> Neural Consensus
            </h3>
            <p className="text-white/80 leading-relaxed font-sans text-sm md:text-base">
              {prediction.aiConsensus}
            </p>
          </Card>

        </div>

        {/* Right Column: Score Sims & Value Rating */}
        <div className="space-y-6">
          
          <Card className="p-6 bg-card/60 backdrop-blur-md border-white/5 flex flex-col items-center justify-center text-center">
             <h3 className="text-sm font-display uppercase tracking-widest text-muted-foreground mb-4">Value Rating</h3>
             <div className={cn(
               "text-3xl font-display font-bold uppercase tracking-wider mb-2",
               prediction.valueRating.includes("STRONG") ? "text-emerald-400 glow-text" :
               prediction.valueRating.includes("GOOD") ? "text-teal-400" :
               prediction.valueRating.includes("LOW") ? "text-rose-400" : "text-blue-400"
             )}>
               {prediction.valueRating}
             </div>
             <p className="text-xs text-muted-foreground max-w-[200px]">Confidence rating based on market deviance and model certainty.</p>
          </Card>

          {prediction.scoreSimulations?.length > 0 && (
            <Card className="p-6 bg-card/60 backdrop-blur-md border-white/5 flex-1">
              <h3 className="text-sm font-display uppercase tracking-widest text-muted-foreground mb-4">Top Score Simulations</h3>
              <div className="grid grid-cols-2 gap-3">
                {prediction.scoreSimulations.map((sim, i) => (
                  <div key={i} className="bg-black/30 border border-white/5 rounded-lg p-3 flex flex-col items-center">
                    <div className="text-xl font-display font-bold text-white tracking-widest">
                      {sim.home} - {sim.away}
                    </div>
                    <div className="text-xs font-mono text-primary mt-1">
                      {(sim.probability * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

        </div>
      </div>

      {/* Market Predictions Table */}
      <Card className="bg-card/60 backdrop-blur-md border-white/5 overflow-hidden">
        <div className="p-6 border-b border-white/5 flex items-center gap-2">
          <ShieldAlert className="w-5 h-5 text-muted-foreground" />
          <h3 className="text-lg font-display uppercase tracking-widest text-white">Full Market Analysis</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="bg-black/20 text-xs uppercase tracking-wider text-muted-foreground font-display">
              <tr>
                <th className="px-6 py-4 font-semibold">Market</th>
                <th className="px-6 py-4 font-semibold">Prediction</th>
                <th className="px-6 py-4 font-semibold">Model Confidence</th>
                <th className="px-6 py-4 font-semibold">Rec. Odds</th>
                <th className="px-6 py-4 font-semibold text-right">Edge (EV)</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {prediction.marketPredictions.map((market, idx) => (
                <tr key={idx} className="hover:bg-white/5 transition-colors">
                  <td className="px-6 py-4 font-medium text-white/90">{market.market}</td>
                  <td className="px-6 py-4 text-white">{market.prediction}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 h-1.5 bg-white/10 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary" 
                          style={{ width: `${market.confidence * 100}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs text-muted-foreground">{(market.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-mono text-muted-foreground">{market.recommendedOdds.toFixed(2)}</td>
                  <td className="px-6 py-4 text-right font-mono font-bold">
                    <span className={market.ev > 0 ? "text-emerald-400" : market.ev < 0 ? "text-rose-400" : "text-slate-400"}>
                      {formatEv(market.ev)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

    </motion.div>
  );
}
