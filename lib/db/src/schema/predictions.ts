import { pgTable, text, serial, timestamp, real, integer, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const predictionsTable = pgTable("predictions", {
  id: serial("id").primaryKey(),
  sport: text("sport").notNull(),
  homeTeam: text("home_team").notNull(),
  awayTeam: text("away_team").notNull(),
  league: text("league"),
  matchDate: text("match_date"),
  homeWinProb: real("home_win_prob").notNull(),
  drawProb: real("draw_prob"),
  awayWinProb: real("away_win_prob").notNull(),
  predictedHomeScore: real("predicted_home_score"),
  predictedAwayScore: real("predicted_away_score"),
  bestBet: text("best_bet").notNull(),
  bestBetEv: real("best_bet_ev").notNull(),
  bestBetConfidence: real("best_bet_confidence").notNull(),
  valueRating: text("value_rating").notNull(),
  aiConsensus: text("ai_consensus").notNull(),
  marketPredictions: jsonb("market_predictions").notNull().$type<Array<{
    market: string;
    prediction: string;
    confidence: number;
    ev: number;
    recommendedOdds: number;
  }>>(),
  scoreSimulations: jsonb("score_simulations").notNull().$type<Array<{
    home: number;
    away: number;
    probability: number;
  }>>(),
  processingTimeMs: integer("processing_time_ms"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertPredictionSchema = createInsertSchema(predictionsTable).omit({
  id: true,
  createdAt: true,
});
export type InsertPrediction = z.infer<typeof insertPredictionSchema>;
export type Prediction = typeof predictionsTable.$inferSelect;
