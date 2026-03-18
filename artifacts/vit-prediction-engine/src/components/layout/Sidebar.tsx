import { useListPredictions, useDeletePrediction, getListPredictionsQueryKey } from "@workspace/api-client-react";
import { usePredictionUI } from "@/hooks/use-prediction-ui";
import { format } from "date-fns";
import { Activity, Plus, Trash2, Trophy, Loader2 } from "lucide-react";
import { Button, cn } from "@/components/ui";
import { useQueryClient } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";

export function Sidebar() {
  const { data: predictions, isLoading } = useListPredictions();
  const { activePredictionId, setActivePredictionId, setFormOpen } = usePredictionUI();
  const deleteMutation = useDeletePrediction();
  const queryClient = useQueryClient();

  const handleDelete = (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    deleteMutation.mutate(
      { id },
      {
        onSuccess: () => {
          queryClient.invalidateQueries({ queryKey: getListPredictionsQueryKey() });
          if (activePredictionId === id) {
            setFormOpen(true);
          }
        },
      }
    );
  };

  const getSportIcon = (sport: string) => {
    switch (sport.toLowerCase()) {
      case "football": return "⚽";
      case "basketball": return "🏀";
      case "tennis": return "🎾";
      default: return "🎯";
    }
  };

  const getValueColor = (rating: string) => {
    if (rating.includes("STRONG")) return "text-emerald-400";
    if (rating.includes("GOOD")) return "text-teal-400";
    if (rating.includes("LOW") || rating.includes("NO")) return "text-rose-400";
    return "text-blue-400";
  };

  return (
    <aside className="w-80 flex-shrink-0 border-r border-white/5 bg-card/30 backdrop-blur-xl h-screen sticky top-0 flex flex-col z-20">
      <div className="p-6 border-b border-white/5">
        <div className="flex items-center gap-3 text-primary mb-6">
          <div className="p-2 bg-primary/10 rounded-lg border border-primary/20 glow-box">
            <Activity className="w-6 h-6" />
          </div>
          <div>
            <h1 className="text-xl font-display font-bold text-white tracking-widest glow-text">VIT ENGINE</h1>
            <p className="text-[10px] text-muted-foreground uppercase tracking-widest font-sans">Value Intelligence Trust</p>
          </div>
        </div>

        <Button 
          className="w-full justify-start gap-2 bg-white/5 hover:bg-white/10 border border-white/10 text-white shadow-none" 
          onClick={() => setFormOpen(true)}
        >
          <Plus className="w-4 h-4" />
          New Analysis
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-2">
        <div className="text-xs font-display text-muted-foreground uppercase tracking-widest mb-4 px-2">Recent Predictions</div>
        
        {isLoading && (
          <div className="flex justify-center p-8">
            <Loader2 className="w-6 h-6 animate-spin text-primary/50" />
          </div>
        )}

        {!isLoading && predictions?.length === 0 && (
          <div className="text-center p-6 text-sm text-muted-foreground border border-dashed border-white/10 rounded-lg mx-2">
            No historical data. Run an analysis to build your edge.
          </div>
        )}

        <AnimatePresence>
          {predictions?.map((pred) => (
            <motion.div
              key={pred.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              onClick={() => setActivePredictionId(pred.id)}
              className={cn(
                "group relative p-4 rounded-xl cursor-pointer transition-all duration-300 border",
                activePredictionId === pred.id 
                  ? "bg-primary/10 border-primary/30 shadow-[0_0_20px_rgba(0,255,255,0.1)]" 
                  : "bg-white/5 border-white/5 hover:bg-white/10 hover:border-white/10"
              )}
            >
              <div className="flex justify-between items-start mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-lg" title={pred.sport}>{getSportIcon(pred.sport)}</span>
                  <span className={cn("text-[10px] font-bold uppercase tracking-wider", getValueColor(pred.valueRating))}>
                    {pred.valueRating}
                  </span>
                </div>
                <button 
                  onClick={(e) => handleDelete(e, pred.id)}
                  className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive transition-opacity"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              
              <div className="font-display font-semibold text-sm leading-tight mb-1 line-clamp-2">
                {pred.homeTeam} <span className="text-muted-foreground text-xs font-sans mx-1">vs</span> {pred.awayTeam}
              </div>
              
              <div className="flex justify-between items-end mt-3">
                <div className="flex items-center gap-1.5 text-xs font-medium text-white/80">
                  <Trophy className="w-3 h-3 text-primary" />
                  <span className="truncate max-w-[120px]">{pred.bestBet}</span>
                </div>
                <div className="text-[10px] text-muted-foreground">
                  {format(new Date(pred.createdAt), "MMM d, HH:mm")}
                </div>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </aside>
  );
}
