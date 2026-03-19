/**
 * VIT — Value Intelligence Trust Prediction Engine
 * Orchestrates the Python model service and builds full betting market analysis.
 */

import { fetchLiveOdds, type LiveOdds } from "./odds-fetcher.js";

export type Sport = "football" | "basketball" | "tennis";

export interface MarketPrediction {
  market: string;
  prediction: string;
  confidence: number;
  ev: number;
  recommendedOdds: number;
}

export interface ScoreSimulation {
  home: number;
  away: number;
  probability: number;
}

export interface VitResult {
  homeWinProb: number;
  drawProb: number | null;
  awayWinProb: number;
  predictedHomeScore: number | null;
  predictedAwayScore: number | null;
  bestBet: string;
  bestBetEv: number;
  bestBetConfidence: number;
  valueRating: string;
  aiConsensus: string;
  marketPredictions: MarketPrediction[];
  scoreSimulations: ScoreSimulation[];
  processingTimeMs: number;
}

const PYTHON_SERVICE_URL = "http://localhost:8000";

interface PythonPredictResponse {
  home_win: number;
  draw: number | null;
  away_win: number;
  predicted_home_score: number | null;
  predicted_away_score: number | null;
  score_simulations: Array<{ home: number; away: number; probability: number }>;
  model_meta: Record<string, unknown>;
  processing_time_ms: number;
}

async function callPythonModel(sport: Sport, homeTeam: string, awayTeam: string): Promise<PythonPredictResponse> {
  const res = await fetch(`${PYTHON_SERVICE_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sport, home_team: homeTeam, away_team: awayTeam }),
    signal: AbortSignal.timeout(15000),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Python model service error ${res.status}: ${text}`);
  }

  return res.json() as Promise<PythonPredictResponse>;
}

function round2(v: number) {
  return Math.round(v * 100) / 100;
}

function round4(v: number) {
  return Math.round(v * 10000) / 10000;
}

function getValueRating(ev: number): string {
  if (ev >= 0.20) return "STRONG VALUE";
  if (ev >= 0.10) return "GOOD VALUE";
  if (ev >= 0.03) return "MODERATE";
  if (ev >= -0.05) return "LOW VALUE";
  return "NO VALUE";
}

function impliedOdds(prob: number): number {
  return round2(1 / Math.max(0.01, prob));
}

function computeEv(trueProb: number, marketProb: number): number {
  return round4(trueProb / marketProb - 1);
}

/** EV using real decimal odds: trueProb * decimalOdds - 1 */
function evFromOdds(trueProb: number, decimalOdds: number): number {
  return round4(trueProb * decimalOdds - 1);
}

function buildFootballMarkets(
  homeWin: number, draw: number, awayWin: number,
  homeScore: number, awayScore: number,
  liveOdds: LiveOdds | null = null,
): MarketPrediction[] {
  const total = homeScore + awayScore;
  const over25 = total > 2.45 ? Math.min(0.82, 0.48 + (total - 2.45) * 0.18) : Math.max(0.22, 0.48 - (2.45 - total) * 0.18);
  const btts = Math.min(homeScore, awayScore) > 0.75 ? Math.min(0.78, 0.45 + Math.min(homeScore, awayScore) * 0.2) : Math.max(0.22, 0.42 - (0.75 - Math.min(homeScore, awayScore)) * 0.3);
  const marketOddsVigor = 1.06;

  const isHomeWin = homeWin >= awayWin && homeWin >= draw;
  const isAwayWin = !isHomeWin && awayWin >= draw;
  const resultProb = Math.max(homeWin, awayWin, draw);
  const resultPrediction = isHomeWin ? "Home Win" : isAwayWin ? "Away Win" : "Draw";
  const resultRealOdds = liveOdds
    ? (isHomeWin ? liveOdds.homeOdds : isAwayWin ? liveOdds.awayOdds : (liveOdds.drawOdds ?? impliedOdds(draw)))
    : null;

  const ouLine = liveOdds?.overLine ?? 2.5;
  const ouLabel = `Over/Under ${ouLine}`;
  const ouProb = over25;
  const ouIsOver = ouProb > 0.5;
  const ouBestOdds = liveOdds
    ? (ouIsOver ? liveOdds.overOdds : liveOdds.underOdds)
    : null;

  const markets: MarketPrediction[] = [
    {
      market: "Match Result",
      prediction: resultPrediction,
      confidence: round4(resultProb),
      ev: resultRealOdds
        ? evFromOdds(resultProb, resultRealOdds)
        : computeEv(resultProb, resultProb * marketOddsVigor),
      recommendedOdds: resultRealOdds ?? round2(impliedOdds(resultProb) * 0.97),
    },
    {
      market: ouLabel,
      prediction: ouIsOver ? `Over ${ouLine} Goals` : `Under ${ouLine} Goals`,
      confidence: round4(Math.max(ouProb, 1 - ouProb)),
      ev: ouBestOdds
        ? evFromOdds(Math.max(ouProb, 1 - ouProb), ouBestOdds)
        : computeEv(Math.max(ouProb, 1 - ouProb), Math.max(ouProb, 1 - ouProb) * marketOddsVigor),
      recommendedOdds: ouBestOdds ?? round2(impliedOdds(Math.max(ouProb, 1 - ouProb)) * 0.97),
    },
    {
      market: "BTTS",
      prediction: btts > 0.5 ? "BTTS Yes" : "BTTS No",
      confidence: round4(Math.max(btts, 1 - btts)),
      ev: computeEv(Math.max(btts, 1 - btts), Math.max(btts, 1 - btts) * marketOddsVigor),
      recommendedOdds: round2(impliedOdds(Math.max(btts, 1 - btts)) * 0.97),
    },
    {
      market: "Double Chance",
      prediction: homeWin + draw > 0.5 ? "Home/Draw" : "Away Win",
      confidence: round4(Math.max(homeWin + draw, awayWin)),
      ev: computeEv(Math.max(homeWin + draw, awayWin), Math.max(homeWin + draw, awayWin) * marketOddsVigor),
      recommendedOdds: round2(impliedOdds(Math.max(homeWin + draw, awayWin)) * 0.98),
    },
    {
      market: "First Half Result",
      prediction: homeWin > awayWin ? "Home/Draw HT" : "Away Win HT",
      confidence: round4(homeWin > awayWin ? Math.min(0.72, homeWin + draw * 0.55) : Math.min(0.72, awayWin + draw * 0.45)),
      ev: computeEv(0.52, 0.52 * marketOddsVigor),
      recommendedOdds: round2(1.85),
    },
  ];

  return markets;
}

function buildBasketballMarkets(
  homeWin: number, awayWin: number,
  homeScore: number, awayScore: number,
  liveOdds: LiveOdds | null = null,
): MarketPrediction[] {
  const total = homeScore + awayScore;
  const overUnderLine = liveOdds?.overLine ?? Math.round(total / 5) * 5;
  const spread = Math.abs(homeScore - awayScore);
  const favoredHome = homeScore > awayScore;
  const marketOddsVigor = 1.05;

  const mlProb = Math.max(homeWin, awayWin);
  const mlOdds = liveOdds ? (homeWin > 0.5 ? liveOdds.homeOdds : liveOdds.awayOdds) : null;
  const ouBestOdds = liveOdds ? liveOdds.overOdds : null;

  return [
    {
      market: "Moneyline",
      prediction: homeWin > 0.5 ? "Home Win" : "Away Win",
      confidence: round4(mlProb),
      ev: mlOdds
        ? evFromOdds(mlProb, mlOdds)
        : computeEv(mlProb, mlProb * marketOddsVigor),
      recommendedOdds: mlOdds ?? round2(impliedOdds(mlProb) * 0.97),
    },
    {
      market: `Total Points O/U ${overUnderLine}`,
      prediction: total > overUnderLine ? `Over ${overUnderLine}` : `Under ${overUnderLine}`,
      confidence: round4(0.52),
      ev: ouBestOdds
        ? evFromOdds(0.52, ouBestOdds)
        : computeEv(0.52, 0.52 * marketOddsVigor),
      recommendedOdds: ouBestOdds ?? round2(1.91),
    },
    {
      market: "Point Spread",
      prediction: favoredHome ? `Home -${Math.round(spread / 2)}` : `Away -${Math.round(spread / 2)}`,
      confidence: round4(Math.max(homeWin, awayWin) * 0.88),
      ev: computeEv(0.52, 0.52 * marketOddsVigor),
      recommendedOdds: round2(1.91),
    },
    {
      market: "First Quarter",
      prediction: homeWin > 0.5 ? "Home Q1" : "Away Q1",
      confidence: round4(0.50 + Math.abs(homeWin - 0.5) * 0.5),
      ev: computeEv(0.51, 0.51 * marketOddsVigor),
      recommendedOdds: round2(1.85),
    },
  ];
}

function buildTennisMarkets(
  homeWin: number, awayWin: number,
  liveOdds: LiveOdds | null = null,
): MarketPrediction[] {
  const marketOddsVigor = 1.05;
  const topSets = homeWin > 0.55 ? "2-0" : homeWin > 0.45 ? "2-1" : awayWin > 0.55 ? "0-2" : "1-2";
  const winnerProb = Math.max(homeWin, awayWin);
  const winnerOdds = liveOdds ? (homeWin > 0.5 ? liveOdds.homeOdds : liveOdds.awayOdds) : null;

  return [
    {
      market: "Match Winner",
      prediction: homeWin > 0.5 ? "Player 1 Win" : "Player 2 Win",
      confidence: round4(winnerProb),
      ev: winnerOdds
        ? evFromOdds(winnerProb, winnerOdds)
        : computeEv(winnerProb, winnerProb * marketOddsVigor),
      recommendedOdds: winnerOdds ?? round2(impliedOdds(winnerProb) * 0.97),
    },
    {
      market: "Total Sets",
      prediction: Math.max(homeWin, awayWin) > 0.68 ? "Under 2.5 Sets" : "Over 2.5 Sets",
      confidence: round4(Math.max(homeWin, awayWin) > 0.68 ? 0.62 : 0.54),
      ev: computeEv(0.54, 0.54 * marketOddsVigor),
      recommendedOdds: round2(1.85),
    },
    {
      market: "Set 1 Winner",
      prediction: homeWin > 0.5 ? "Player 1" : "Player 2",
      confidence: round4(0.50 + Math.abs(homeWin - 0.5) * 0.7),
      ev: computeEv(0.50 + Math.abs(homeWin - 0.5) * 0.7, (0.50 + Math.abs(homeWin - 0.5) * 0.7) * marketOddsVigor),
      recommendedOdds: round2(impliedOdds(0.50 + Math.abs(homeWin - 0.5) * 0.7) * 0.97),
    },
    {
      market: "Correct Score (Sets)",
      prediction: topSets,
      confidence: round4(Math.max(homeWin, awayWin) * 0.55),
      ev: computeEv(Math.max(homeWin, awayWin) * 0.55, Math.max(homeWin, awayWin) * 0.55 * marketOddsVigor),
      recommendedOdds: round2(impliedOdds(Math.max(homeWin, awayWin) * 0.55) * 0.97),
    },
  ];
}

function generateConsensus(
  sport: Sport, homeTeam: string, awayTeam: string,
  homeWin: number, awayWin: number, draw: number | null,
  bestBet: string, ev: number, valueRating: string,
  meta: Record<string, unknown>,
): string {
  const homeP = Math.round(homeWin * 100);
  const awayP = Math.round(awayWin * 100);
  const evStr = ev >= 0 ? `+${(ev * 100).toFixed(1)}%` : `${(ev * 100).toFixed(1)}%`;

  const modelName = (meta.model as string) ?? "statistical model";
  const xgHint = sport === "football" && meta.home_xg != null
    ? ` (xG: ${meta.home_xg} vs ${meta.away_xg})`
    : "";

  const sportContext: Record<Sport, string> = {
    football: `xG-based Poisson simulation${xgHint}`,
    basketball: `pace-adjusted offensive/defensive efficiency ratings`,
    tennis: `serve & return win probability modeling`,
  };

  if (valueRating === "STRONG VALUE" || valueRating === "GOOD VALUE") {
    return `Our ${modelName} assigns ${homeTeam} a ${homeP}% win probability against ${awayTeam} at ${awayP}%, derived from ${sportContext[sport]}. The ${bestBet} market shows a clear mispricing with an EV of ${evStr} — the model estimates this outcome is being undervalued by bookmakers. AI consensus: strong alignment across simulations, this is a confident edge.`;
  }
  return `${modelName} simulations give ${homeTeam} ${homeP}% vs ${awayTeam} ${awayP}% using ${sportContext[sport]}. The best available line is ${bestBet} with an EV of ${evStr}. The market is fairly priced here — size this bet cautiously and consider line shopping before committing.`;
}

export async function runVitAnalysis(
  sport: Sport,
  homeTeam: string,
  awayTeam: string,
): Promise<VitResult> {
  const startTime = Date.now();

  // Run Python model and odds fetch in parallel
  const [python, liveOdds] = await Promise.all([
    callPythonModel(sport, homeTeam, awayTeam),
    fetchLiveOdds(sport, homeTeam, awayTeam).catch(() => null),
  ]);

  const homeWinProb = round4(python.home_win);
  const awayWinProb = round4(python.away_win);
  const drawProb = python.draw != null ? round4(python.draw) : null;
  const predictedHomeScore = python.predicted_home_score;
  const predictedAwayScore = python.predicted_away_score;
  const scoreSimulations = python.score_simulations.map((s) => ({
    home: s.home,
    away: s.away,
    probability: round4(s.probability),
  }));

  let marketPredictions: MarketPrediction[];
  if (sport === "football") {
    marketPredictions = buildFootballMarkets(
      homeWinProb, drawProb ?? 0, awayWinProb,
      predictedHomeScore ?? 1.2, predictedAwayScore ?? 1.0,
      liveOdds,
    );
  } else if (sport === "basketball") {
    marketPredictions = buildBasketballMarkets(
      homeWinProb, awayWinProb,
      predictedHomeScore ?? 110, predictedAwayScore ?? 107,
      liveOdds,
    );
  } else {
    marketPredictions = buildTennisMarkets(homeWinProb, awayWinProb, liveOdds);
  }

  const bestMarket = [...marketPredictions].sort((a, b) => b.ev - a.ev)[0];
  const bestBet = bestMarket.prediction;
  const bestBetEv = round4(bestMarket.ev);
  const bestBetConfidence = round4(bestMarket.confidence);
  const valueRating = getValueRating(bestBetEv);

  const aiConsensus = generateConsensus(
    sport, homeTeam, awayTeam,
    homeWinProb, awayWinProb, drawProb,
    bestBet, bestBetEv, valueRating,
    python.model_meta,
  );

  return {
    homeWinProb,
    drawProb,
    awayWinProb,
    predictedHomeScore,
    predictedAwayScore,
    bestBet,
    bestBetEv,
    bestBetConfidence,
    valueRating,
    aiConsensus,
    marketPredictions,
    scoreSimulations,
    processingTimeMs: Date.now() - startTime,
  };
}
