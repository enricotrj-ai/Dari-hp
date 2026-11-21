import React from "react";
import { Easing, Img, interpolate, staticFile } from "remotion";
import { feature, mesh } from "topojson-client";
import { geoBounds, geoContains, geoPath, geoTransform } from "d3-geo";
import us from "us-atlas/states-10m.json";
import world from "world-atlas/countries-50m.json";
import timeline from "./timeline.json";

/* World pixel space = equirectangular 4096 x 2048 (matches the Blue Marble texture). */
const WW = 4096, WH = 2048;
const wx = (lon: number) => ((lon + 180) / 360) * WW;
const wy = (lat: number) => ((90 - lat) / 180) * WH;
const proj = geoTransform({
  point(lon: number, lat: number) {
    (this as any).stream.point(wx(lon), wy(lat));
  },
});
const path = geoPath(proj);
const SQUEEZE = 0.8; // ~cos(37deg): undo equirectangular east-west stretch over the US

const states = (feature(us as any, (us as any).objects.states) as any).features as any[];
const LOWER48 = states.filter((f) => !["02", "15", "60", "66", "69", "72", "78"].includes(f.id));
const usPath = LOWER48.map((f) => path(f)).join(" ");
const stateLines = path(mesh(us as any, (us as any).objects.states, (a: any, b: any) => a !== b) as any) || "";
const countryLines = path(mesh(world as any, (world as any).objects.countries) as any) || "";
const byId = (id: string) => path(states.find((f) => f.id === id));
const TEXAS = byId("48") || "";
// States where Tasty Chick'n runs its 84 restaurants (AL, AR, FL, IL, IN, KY, MO, MS, TN, VA)
const OPS = ["01", "05", "12", "17", "18", "21", "29", "28", "47", "51"].map((id) => ({
  id,
  d: byId(id) || "",
  c: path.centroid(states.find((f) => f.id === id)),
}));
const PLANO = [wx(-96.7), wy(33.02)];

const SEG = timeline.segments;
const S = (i: number) => SEG[i].start;

const e = (s: number, a: number, b: number) =>
  interpolate(s, [a, b], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic) });

/* camera keyframes: [time, lon, lat, zoom(screen px per world px)] */
const KEYS: [number, number, number, number][] = [
  [0, -97, 40, 1.45],
  [2.4, -97, 38.5, 1.95],
  [S(2) + 0.4, -86, 34.2, 4.0],
  [S(6) - 0.3, -86.3, 34.0, 4.15],
  [S(6) + 0.6, -96, 37.8, 2.05],
  [S(13), -96, 37.5, 2.1],
  [S(15) - 0.1, -96, 37.5, 2.1],
  [S(15) + 1.1, -99.3, 31.3, 5.0],
  [S(17) - 0.1, -98.5, 31.6, 5.1],
  [S(17) + 0.9, -91.5, 34.5, 3.0],
  [S(19) - 0.2, -91.2, 34.6, 3.05],
  [S(19) + 0.8, -96, 37.5, 2.1],
  [timeline.total, -96, 37.8, 2.2],
];
const camera = (s: number) => {
  let i = KEYS.findIndex((k, j) => j < KEYS.length - 1 && s >= k[0] && s < KEYS[j + 1][0]);
  if (i < 0) i = KEYS.length - 2;
  const [t0, lo0, la0, z0] = KEYS[i];
  const [t1, lo1, la1, z1] = KEYS[i + 1];
  const p = e(s, t0, t1);
  return { lon: lo0 + (lo1 - lo0) * p, lat: la0 + (la1 - la0) * p, z: z0 * Math.pow(z1 / z0, p) };
};

export const MapBg: React.FC<{ s: number }> = ({ s }) => {
  const { lon, lat, z } = camera(s);
  const usRed = e(s, S(1) + 0.3, S(1) + 0.55) * (1 - e(s, S(14) - 0.1, S(14) + 0.25));
  const usGreen = e(s, S(14) - 0.1, S(14) + 0.25) * (1 - e(s, S(15), S(15) + 0.3));
  const tx = e(s, S(15) + 0.05, S(15) + 0.35);
  const pulse = 0.85 + 0.15 * Math.sin(s * 6);
  const lines = e(s, S(17), S(17) + 1.2);
  // dim the map behind busy pop-up scenes so text stays readable
  const dim = interpolate(
    s,
    [0, 1.2, 2.6, 3.0, S(13) - 0.2, S(13), S(14) - 0.2, S(14), S(16) - 0.1, S(16) + 0.2, S(18), S(18) + 0.3, S(19), S(19) + 0.3],
    [0.05, 0.05, 0.15, 0.5, 0.5, 0.6, 0.6, 0.18, 0.18, 0.3, 0.3, 0.6, 0.6, 0.45],
    { extrapolateLeft: "clamp", extrapolateRight: "clamp" }
  );
  const k = 1 / z; // keep strokes roughly constant on screen
  return (
    <div style={{ position: "absolute", inset: 0, overflow: "hidden", background: "#07131f" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          top: 0,
          width: WW,
          height: WH,
          transformOrigin: "0 0",
          transform: `translate(540px, 960px) scale(${z * SQUEEZE}, ${z}) translate(${-wx(lon)}px, ${-wy(lat)}px)`,
        }}
      >
        <Img src={staticFile("americas.jpg")} style={{ position: "absolute", left: 113, top: 0, width: 1706, height: 1479 }} />
        <svg width={WW} height={WH} style={{ position: "absolute", left: 0, top: 0, overflow: "visible" }}>
          <defs>
            <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation={3 * k * 2} />
            </filter>
          </defs>
          <path d={countryLines} fill="none" stroke="rgba(255,255,255,0.35)" strokeWidth={1.6 * k} />
          {/* whole US: red, then green */}
          <path d={usPath} fill="#ff2020" style={{ mixBlendMode: "color" }} opacity={usRed * 0.95} />
          <path d={usPath} fill="#d01010" opacity={usRed * 0.35 * pulse} />
          <path d={usPath} fill="#22c55e" style={{ mixBlendMode: "color" }} opacity={usGreen * 0.9} />
          <path d={usPath} fill="#16a34a" opacity={usGreen * 0.25} />
          <path d={stateLines} fill="none" stroke="rgba(255,255,255,0.45)" strokeWidth={1.2 * k} />
          <path d={usPath} fill="none" stroke={`rgba(255,${usRed > 0.5 ? 120 : 240},${usRed > 0.5 ? 120 : 240},0.9)`} strokeWidth={2.6 * k} />
          {/* the 10 states where the franchisee's stores are */}
          {OPS.map((o, i) => {
            const on = e(s, S(17) + 0.35 + i * 0.08, S(17) + 0.65 + i * 0.08);
            return (
              <g key={o.id} opacity={on}>
                <path d={o.d} fill="#ff9d1c" style={{ mixBlendMode: "color" }} />
                <path d={o.d} fill="#ff8a00" opacity={0.35} />
                <path d={o.d} fill="none" stroke="#ffd27a" strokeWidth={2.2 * k} />
              </g>
            );
          })}
          {/* Texas */}
          <g opacity={tx}>
            <path d={TEXAS} fill="none" stroke="#ff3b3b" strokeWidth={14 * k} filter="url(#glow)" opacity={pulse} />
            <path d={TEXAS} fill="#ff1a1a" style={{ mixBlendMode: "color" }} />
            <path d={TEXAS} fill="#e01313" opacity={0.4} />
            <path d={TEXAS} fill="none" stroke="#ffd0d0" strokeWidth={3 * k} />
          </g>
          {/* routes from Plano HQ to the stores */}
          {OPS.map((o, i) => {
            const [x2, y2] = o.c;
            const mx = (PLANO[0] + x2) / 2, my = Math.min(PLANO[1], y2) - 18;
            const p = e(s, S(17) + i * 0.08, S(17) + 0.6 + i * 0.08);
            return (
              <path key={o.id} d={`M${PLANO[0]} ${PLANO[1]} Q${mx} ${my} ${x2} ${y2}`} fill="none" stroke="#ffe066" strokeWidth={3.2 * k} strokeLinecap="round" pathLength={1} strokeDasharray="1 1" strokeDashoffset={1 - p} opacity={lines} />
            );
          })}
          {/* Plano pin */}
          <g opacity={e(s, S(16) + 0.9, S(16) + 1.2)}>
            <circle cx={PLANO[0]} cy={PLANO[1]} r={9 * k * (1 + 0.4 * Math.sin(s * 8))} fill="#ffe066" opacity={0.35} />
            <circle cx={PLANO[0]} cy={PLANO[1]} r={4.5 * k} fill="#ffe066" stroke="#1c1a17" strokeWidth={1.6 * k} />
          </g>
        </svg>
      </div>
      <div style={{ position: "absolute", inset: 0, background: `rgba(5,10,18,${dim})` }} />
      <div style={{ position: "absolute", inset: 0, background: "radial-gradient(ellipse at 50% 45%, rgba(0,0,0,0) 45%, rgba(0,0,0,0.55) 100%)" }} />
    </div>
  );
};

export const planoScreen = (s: number) => {
  const { lon, lat, z } = camera(s);
  return [540 + (PLANO[0] - wx(lon)) * z * SQUEEZE, 960 + (PLANO[1] - wy(lat)) * z];
};

/* project any lon/lat to screen pixels for the camera at time s */
export const project = (s: number, lon: number, lat: number) => {
  const c = camera(s);
  return [540 + (wx(lon) - wx(c.lon)) * c.z * SQUEEZE, 960 + (wy(lat) - wy(c.lat)) * c.z];
};

/* 84 store locations spread across the franchisee's 10 states (illustrative positions) */
let seed = 1234567;
const rnd = () => {
  seed = (seed * 1664525 + 1013904223) % 4294967296;
  return seed / 4294967296;
};
const PER_STATE = [13, 12, 13, 12, 13, 13, 13, 12, 13, 14]; // = 128 (84 open + 44 closed)
export const STORES: { lon: number; lat: number; state: string }[] = [];
OPS.forEach((o, i) => {
  const f = states.find((x) => x.id === o.id);
  const [[x0, y0], [x1, y1]] = geoBounds(f);
  let n = 0, guard = 0;
  while (n < PER_STATE[i] && guard++ < 5000) {
    const lon = x0 + (x1 - x0) * rnd(), lat = y0 + (y1 - y0) * rnd();
    if (geoContains(f, [lon, lat])) {
      STORES.push({ lon, lat, state: o.id });
      n++;
    }
  }
});
