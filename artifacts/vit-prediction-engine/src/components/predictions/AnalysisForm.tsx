import { useState } from "react";
import { useCreatePrediction, getListPredictionsQueryKey } from "@workspace/api-client-react";
import { usePredictionUI } from "@/hooks/use-prediction-ui";
import { useQueryClient } from "@tanstack/react-query";
import { Card, CardContent, CardHeader, CardTitle, Button, Input, cn } from "@/components/ui";
import { motion } from "framer-motion";
import { Cpu, Target, Zap, ActivitySquare } from "lucide-react";

export function AnalysisForm() {
  const [sport, setSport] = useState<"football" | "basketball" | "tennis">("football");
  const [homeTeam, setHomeTeam] = useState("");
  const [awayTeam, setAwayTeam] = useState("");
  const [league, setLeague] = useState("");
  
  const createMutation = useCreatePrediction();
  const queryClient = useQueryClient();
  const { setActivePredictionId } = usePredictionUI();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!homeTeam || !awayTeam) return;

    createMutation.mutate(
      {
        data: {
          sport,
          homeTeam,
          awayTeam,
          league: league || null,
        }
      },
      {
        onSuccess: (data) => {
          queryClient.invalidateQueries({ queryKey: getListPredictionsQueryKey() });
          setActivePredictionId(data.id);
        }
      }
    );
  };

  if (createMutation.isPending) {
    return (
      <div className="w-full max-w-2xl mx-auto mt-20 flex flex-col items-center justify-center space-y-8">
        <div className="relative">
          <div className="absolute inset-0 bg-primary/20 blur-3xl rounded-full w-40 h-40 animate-pulse-slow" />
          <motion.div 
            animate={{ rotate: 360 }} 
            transition={{ repeat: Infinity, duration: 8, ease: "linear" }}
            className="w-32 h-32 border-2 border-dashed border-primary/50 rounded-full flex items-center justify-center relative z-10"
          >
            <Cpu className="w-12 h-12 text-primary animate-pulse" />
          </motion.div>
        </div>
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-display font-bold glow-text uppercase tracking-widest text-primary">Running VIT Models</h2>
          <p className="text-muted-foreground font-mono text-sm">Aggregating market data • Running simulations • Calculating EV</p>
        </div>
        
        <div className="w-full max-w-md h-1 bg-white/5 rounded-full overflow-hidden">
          <motion.div 
            className="h-full bg-primary"
            initial={{ width: "0%" }}
            animate={{ width: "100%" }}
            transition={{ duration: 2.5, ease: "easeInOut" }}
          />
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-3xl mx-auto mt-12"
    >
      <div className="text-center mb-10">
        <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-4 tracking-tight">
          Value Intelligence <span className="text-primary glow-text">Trust</span>
        </h1>
        <p className="text-muted-foreground text-lg max-w-2xl mx-auto">
          Advanced predictive modeling for sports betting. Identify true expected value using neural networks and market consensus.
        </p>
      </div>

      <Card className="glass-panel overflow-hidden border-t-primary/30">
        <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-primary/50 to-transparent" />
        <CardHeader className="border-b border-white/5 bg-white/5 pb-8">
          <CardTitle className="flex items-center gap-2 text-2xl">
            <Target className="w-6 h-6 text-primary" />
            Initialize Analysis
          </CardTitle>
        </CardHeader>
        <CardContent className="pt-8">
          <form onSubmit={handleSubmit} className="space-y-8">
            
            {/* Sport Selection */}
            <div className="space-y-3">
              <label className="text-xs font-display uppercase tracking-widest text-muted-foreground">Select Domain</label>
              <div className="grid grid-cols-3 gap-4">
                {[
                  { id: "football", label: "Football", icon: "⚽", color: "var(--football)" },
                  { id: "basketball", label: "Basketball", icon: "🏀", color: "var(--basketball)" },
                  { id: "tennis", label: "Tennis", icon: "🎾", color: "var(--tennis)" }
                ].map((s) => (
                  <button
                    key={s.id}
                    type="button"
                    onClick={() => setSport(s.id as any)}
                    className={cn(
                      "relative p-4 rounded-xl border flex flex-col items-center gap-2 transition-all duration-300",
                      sport === s.id 
                        ? "bg-white/10 border-white/30 shadow-lg" 
                        : "bg-black/20 border-white/5 hover:border-white/15 hover:bg-white/5"
                    )}
                  >
                    {sport === s.id && (
                      <motion.div layoutId="sport-highlight" className="absolute inset-0 rounded-xl ring-2 ring-primary ring-offset-2 ring-offset-background" />
                    )}
                    <span className="text-2xl">{s.icon}</span>
                    <span className="font-display font-semibold tracking-wide">{s.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Teams Input */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative">
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-8 h-8 rounded-full bg-background border border-white/10 flex items-center justify-center z-10 font-display font-bold text-xs text-muted-foreground">
                VS
              </div>
              <div className="space-y-3">
                <label className="text-xs font-display uppercase tracking-widest text-muted-foreground">Home / Player 1</label>
                <Input 
                  placeholder="e.g. Real Madrid" 
                  value={homeTeam}
                  onChange={(e) => setHomeTeam(e.target.value)}
                  required
                  className="h-14 text-lg bg-black/40 border-white/10 focus-visible:ring-primary/50"
                />
              </div>
              <div className="space-y-3">
                <label className="text-xs font-display uppercase tracking-widest text-muted-foreground">Away / Player 2</label>
                <Input 
                  placeholder="e.g. Barcelona" 
                  value={awayTeam}
                  onChange={(e) => setAwayTeam(e.target.value)}
                  required
                  className="h-14 text-lg bg-black/40 border-white/10 focus-visible:ring-primary/50"
                />
              </div>
            </div>

            {/* Optional Metadata */}
            <div className="space-y-3">
              <label className="text-xs font-display uppercase tracking-widest text-muted-foreground">League / Tournament (Optional)</label>
              <Input 
                placeholder="e.g. Champions League" 
                value={league}
                onChange={(e) => setLeague(e.target.value)}
                className="bg-black/40 border-white/10"
              />
            </div>

            <Button 
              type="submit" 
              size="lg" 
              className="w-full h-14 text-lg font-display tracking-wider mt-4"
              disabled={!homeTeam || !awayTeam || createMutation.isPending}
            >
              <Zap className="w-5 h-5 mr-2" />
              RUN PREDICTION ENGINE
            </Button>

          </form>
        </CardContent>
      </Card>

      <div className="mt-8 grid grid-cols-3 gap-4 text-center">
        <div className="p-4 rounded-lg bg-white/5 border border-white/5">
          <ActivitySquare className="w-6 h-6 text-primary mx-auto mb-2" />
          <div className="text-sm font-semibold text-white">Live Odds</div>
          <div className="text-xs text-muted-foreground">Real-time sync</div>
        </div>
        <div className="p-4 rounded-lg bg-white/5 border border-white/5">
          <Cpu className="w-6 h-6 text-primary mx-auto mb-2" />
          <div className="text-sm font-semibold text-white">Neural Net</div>
          <div className="text-xs text-muted-foreground">10k+ simulations</div>
        </div>
        <div className="p-4 rounded-lg bg-white/5 border border-white/5">
          <Target className="w-6 h-6 text-primary mx-auto mb-2" />
          <div className="text-sm font-semibold text-white">True EV</div>
          <div className="text-xs text-muted-foreground">Edge detection</div>
        </div>
      </div>
    </motion.div>
  );
}
