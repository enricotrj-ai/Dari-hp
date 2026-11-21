import React from "react";
import { Composition } from "remotion";
import { Video } from "./Video";
import timeline from "./timeline.json";

export const FPS = 30;

export const Root: React.FC = () => (
  <Composition
    id="KfcTexas"
    component={Video}
    durationInFrames={Math.ceil(timeline.total * FPS)}
    fps={FPS}
    width={1080}
    height={1920}
  />
);
