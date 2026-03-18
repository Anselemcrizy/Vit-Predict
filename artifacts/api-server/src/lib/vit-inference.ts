/**
 * VIT (Vision Transformer) Prediction Engine
 *
 * This module provides image classification using the Hugging Face Inference API
 * with the google/vit-base-patch16-224 model, with a fallback to simulated results.
 */

const VIT_MODEL = "google/vit-base-patch16-224";

export interface PredictionResult {
  label: string;
  confidence: number;
}

export interface InferenceResult {
  topLabel: string;
  topConfidence: number;
  results: PredictionResult[];
  modelName: string;
  processingTimeMs: number;
}

async function fetchFromHuggingFace(imageData: string | null, imageUrl: string): Promise<PredictionResult[]> {
  const HF_TOKEN = process.env.HUGGINGFACE_API_KEY || process.env.HF_TOKEN;
  const apiUrl = `https://api-inference.huggingface.co/models/${VIT_MODEL}`;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };

  if (HF_TOKEN) {
    headers["Authorization"] = `Bearer ${HF_TOKEN}`;
  }

  let body: string;

  if (imageData) {
    const base64Data = imageData.replace(/^data:image\/[a-z]+;base64,/, "");
    const binaryStr = atob(base64Data);
    const bytes = new Uint8Array(binaryStr.length);
    for (let i = 0; i < binaryStr.length; i++) {
      bytes[i] = binaryStr.charCodeAt(i);
    }

    const response = await fetch(apiUrl, {
      method: "POST",
      headers: { ...headers, "Content-Type": "application/octet-stream" },
      body: bytes,
    });

    if (!response.ok) {
      throw new Error(`HuggingFace API error: ${response.status} ${response.statusText}`);
    }

    return (await response.json()) as PredictionResult[];
  } else {
    const response = await fetch(apiUrl, {
      method: "POST",
      headers,
      body: JSON.stringify({ inputs: imageUrl }),
    });

    if (!response.ok) {
      throw new Error(`HuggingFace API error: ${response.status} ${response.statusText}`);
    }

    return (await response.json()) as PredictionResult[];
  }
}

function normalizeResults(raw: PredictionResult[]): PredictionResult[] {
  return raw
    .map((r) => ({
      label: r.label || "Unknown",
      confidence: typeof r.score === "number" ? (r as unknown as { score: number }).score : r.confidence,
    }))
    .sort((a, b) => b.confidence - a.confidence)
    .slice(0, 10);
}

function generateSimulatedResults(seed: string): PredictionResult[] {
  const commonLabels = [
    "Egyptian cat", "tabby cat", "tiger cat", "Persian cat", "Siamese cat",
    "Labrador retriever", "golden retriever", "German shepherd", "poodle", "beagle",
    "African elephant", "Indian elephant", "tusker",
    "sports car", "convertible", "racer", "beach wagon",
    "banana", "granny smith", "pineapple", "strawberry", "orange",
    "acoustic guitar", "electric guitar", "violin", "drumkit",
    "mountain bike", "bicycle", "scooter", "go-kart",
    "desktop computer", "laptop", "mobile phone", "television",
    "pizza", "burger", "hotdog", "waffle", "pretzel",
    "daisy", "sunflower", "rose", "tulip", "orchid",
  ];

  let hash = 0;
  for (let i = 0; i < seed.length; i++) {
    hash = (hash << 5) - hash + seed.charCodeAt(i);
    hash |= 0;
  }

  const startIdx = Math.abs(hash) % commonLabels.length;
  const results: PredictionResult[] = [];
  let remainingConfidence = 1.0;

  for (let i = 0; i < 5; i++) {
    const label = commonLabels[(startIdx + i * 7) % commonLabels.length];
    const maxShare = remainingConfidence * (i === 0 ? 0.85 : 0.7);
    const minShare = remainingConfidence * (i === 4 ? 1 : 0.05);
    const confidence = Math.min(maxShare, Math.max(minShare, remainingConfidence * (0.3 + Math.random() * 0.5)));
    results.push({ label, confidence: Math.round(confidence * 10000) / 10000 });
    remainingConfidence -= confidence;
    if (remainingConfidence <= 0.01) break;
  }

  return results.sort((a, b) => b.confidence - a.confidence);
}

export async function runVitPrediction(imageUrl: string, imageData: string | null): Promise<InferenceResult> {
  const startTime = Date.now();

  let results: PredictionResult[];
  let usedModel = VIT_MODEL;

  try {
    const rawResults = await fetchFromHuggingFace(imageData, imageUrl);
    results = normalizeResults(rawResults);
  } catch (err) {
    console.warn("HuggingFace API unavailable, using simulated results:", err instanceof Error ? err.message : err);
    await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 700));
    results = generateSimulatedResults(imageUrl + (imageData?.slice(0, 50) ?? ""));
    usedModel = `${VIT_MODEL} (simulated)`;
  }

  const processingTimeMs = Date.now() - startTime;

  return {
    topLabel: results[0]?.label ?? "Unknown",
    topConfidence: results[0]?.confidence ?? 0,
    results,
    modelName: usedModel,
    processingTimeMs,
  };
}
