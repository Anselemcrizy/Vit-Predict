import { pgTable, text, serial, timestamp, real, integer, jsonb } from "drizzle-orm/pg-core";
import { createInsertSchema } from "drizzle-zod";
import { z } from "zod/v4";

export const predictionsTable = pgTable("predictions", {
  id: serial("id").primaryKey(),
  imageUrl: text("image_url").notNull(),
  imageData: text("image_data"),
  topLabel: text("top_label").notNull(),
  topConfidence: real("top_confidence").notNull(),
  results: jsonb("results").notNull().$type<Array<{ label: string; confidence: number }>>(),
  modelName: text("model_name").notNull().default("google/vit-base-patch16-224"),
  processingTimeMs: integer("processing_time_ms"),
  createdAt: timestamp("created_at", { withTimezone: true }).notNull().defaultNow(),
});

export const insertPredictionSchema = createInsertSchema(predictionsTable).omit({
  id: true,
  createdAt: true,
});
export type InsertPrediction = z.infer<typeof insertPredictionSchema>;
export type Prediction = typeof predictionsTable.$inferSelect;
