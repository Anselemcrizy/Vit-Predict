/**
 * The Odds API integration — fetches real bookmaker odds for EV calculation.
 * Returns null gracefully if the match is not found or the API is unavailable.
 */

import type { Sport } from "./vit-engine.js";

export interface LiveOdds {
  homeOdds: number;
  drawOdds: number | null;
  awayOdds: number;
  overLine: number | null;
  overOdds: number | null;
  underOdds: number | null;
}

const ODDS_API_KEY = process.env.ODDS_API_KEY;
const ODDS_BASE = "https://api.the-odds-api.com/v4";

const SPORT_KEYS: Record<Sport, string[]> = {
  football: [
    "soccer_epl",
    "soccer_la_liga",
    "soccer_germany_bundesliga",
    "soccer_italy_serie_a",
    "soccer_france_ligue_one",
    "soccer_uefa_champs_league",
    "soccer_uefa_europa_league",
    "soccer_usa_mls",
    "soccer_efl_champ",
  ],
  basketball: ["basketball_nba", "basketball_euroleague"],
  tennis: ["tennis_atp", "tennis_wta"],
};

function r2(v: number) {
  return Math.round(v * 100) / 100;
}

function nameMatch(apiName: string, userInput: string): boolean {
  const a = apiName.toLowerCase().trim();
  const b = userInput.toLowerCase().trim();
  return a === b || a.includes(b) || b.includes(a);
}

function avgPrice(outcomes: any[], name: string): number | null {
  const prices = outcomes
    .filter((o: any) => nameMatch(String(o.name), name))
    .map((o: any) => Number(o.price))
    .filter((p) => p > 1);
  if (!prices.length) return null;
  return prices.reduce((a, b) => a + b, 0) / prices.length;
}

export async function fetchLiveOdds(
  sport: Sport,
  homeTeam: string,
  awayTeam: string,
): Promise<LiveOdds | null> {
  if (!ODDS_API_KEY) return null;

  const sportKeys = SPORT_KEYS[sport] ?? [];

  for (const sportKey of sportKeys) {
    try {
      const url =
        `${ODDS_BASE}/sports/${sportKey}/odds` +
        `?apiKey=${ODDS_API_KEY}&regions=uk,eu&markets=h2h,totals&oddsFormat=decimal`;

      const res = await fetch(url, { signal: AbortSignal.timeout(6000) });
      if (!res.ok) continue;

      const games: any[] = await res.json();
      if (!Array.isArray(games)) continue;

      const game = games.find(
        (g: any) =>
          (nameMatch(g.home_team, homeTeam) && nameMatch(g.away_team, awayTeam)) ||
          (nameMatch(g.home_team, awayTeam) && nameMatch(g.away_team, homeTeam)),
      );

      if (!game) continue;

      const allH2H: any[] = [];
      const allTotals: any[] = [];

      for (const bm of game.bookmakers ?? []) {
        for (const mkt of bm.markets ?? []) {
          if (mkt.key === "h2h") allH2H.push(...(mkt.outcomes ?? []));
          if (mkt.key === "totals") allTotals.push(...(mkt.outcomes ?? []));
        }
      }

      const homeOdds = avgPrice(allH2H, game.home_team);
      const awayOdds = avgPrice(allH2H, game.away_team);
      const drawOdds = sport === "football" ? avgPrice(allH2H, "Draw") : null;

      const overOuts = allTotals.filter((o: any) => o.name === "Over");
      const underOuts = allTotals.filter((o: any) => o.name === "Under");

      const overLine: number | null = overOuts[0]?.point ?? null;
      const overOdds =
        overOuts.length
          ? overOuts.reduce((a: number, b: any) => a + Number(b.price), 0) / overOuts.length
          : null;
      const underOdds =
        underOuts.length
          ? underOuts.reduce((a: number, b: any) => a + Number(b.price), 0) / underOuts.length
          : null;

      if (homeOdds && awayOdds) {
        return {
          homeOdds: r2(homeOdds),
          drawOdds: drawOdds ? r2(drawOdds) : null,
          awayOdds: r2(awayOdds),
          overLine: overLine ?? null,
          overOdds: overOdds ? r2(overOdds) : null,
          underOdds: underOdds ? r2(underOdds) : null,
        };
      }
    } catch {
      continue;
    }
  }

  return null;
}
