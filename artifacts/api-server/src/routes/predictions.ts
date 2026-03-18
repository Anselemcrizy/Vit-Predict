import { Router, type IRouter } from "express";
import { eq, desc } from "drizzle-orm";
import { db, predictionsTable } from "@workspace/db";
import {
  ListPredictionsResponse,
  GetPredictionResponse,
  GetPredictionParams,
  DeletePredictionParams,
  CreatePredictionBody,
} from "@workspace/api-zod";
import { runVitPrediction } from "../lib/vit-inference.js";

const router: IRouter = Router();

router.get("/predictions", async (_req, res): Promise<void> => {
  const predictions = await db
    .select()
    .from(predictionsTable)
    .orderBy(desc(predictionsTable.createdAt));
  res.json(ListPredictionsResponse.parse(predictions));
});

router.post("/predictions", async (req, res): Promise<void> => {
  const parsed = CreatePredictionBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const { imageUrl, imageData } = parsed.data;

  const inference = await runVitPrediction(imageUrl, imageData ?? null);

  const [prediction] = await db
    .insert(predictionsTable)
    .values({
      imageUrl,
      imageData: imageData ?? null,
      topLabel: inference.topLabel,
      topConfidence: inference.topConfidence,
      results: inference.results,
      modelName: inference.modelName,
      processingTimeMs: inference.processingTimeMs,
    })
    .returning();

  res.status(201).json(GetPredictionResponse.parse(prediction));
});

router.get("/predictions/:id", async (req, res): Promise<void> => {
  const params = GetPredictionParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [prediction] = await db
    .select()
    .from(predictionsTable)
    .where(eq(predictionsTable.id, params.data.id));

  if (!prediction) {
    res.status(404).json({ error: "Prediction not found" });
    return;
  }

  res.json(GetPredictionResponse.parse(prediction));
});

router.delete("/predictions/:id", async (req, res): Promise<void> => {
  const params = DeletePredictionParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [prediction] = await db
    .delete(predictionsTable)
    .where(eq(predictionsTable.id, params.data.id))
    .returning();

  if (!prediction) {
    res.status(404).json({ error: "Prediction not found" });
    return;
  }

  res.sendStatus(204);
});

export default router;
