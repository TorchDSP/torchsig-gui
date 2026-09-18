import type { NextConfig } from "next";
import { PHASE_PRODUCTION_BUILD } from "next/constants";

// Defines the configuration details for static builds from Next.js
// - Uses the build phase instead of an environment variable, so the build command works in every shell, including on Windows
const nextConfig = (phase: string): NextConfig => ({
  // Makes a static single page application on build
  output: "export",

  // Sets the name of the folder containing the static build
  // - Writes production builds into the Python package, so the server can host them
  // - Otherwise, uses the default value of ".next" to hold the dev build
  distDir: phase === PHASE_PRODUCTION_BUILD ? "torchsiggui/webbuild" : ".next",

  // Uses a fixed build ID so rebuilding unchanged source reproduces the committed static build
  generateBuildId: async () => "torchsiggui",

  // Makes Next Image components unoptimized to allow static building
  images: {
    unoptimized: true,
  },
});

export default nextConfig;
