import type { NextConfig } from "next";

// Defines the configuration details for static builds from Next.js
const nextConfig: NextConfig = {
  // Makes a static single page application on build
  output: "export",

  // Sets the name of the folder containing the static build
  // - Uses a custom folder name set in package.json if the build command is run
  // - Otherwise, uses the devault value of ".next" to hold the dev build
  distDir: process.env.NEXT_STATIC_BUILD ?? ".next",

  // Makes Next Image components unoptimized to allow static building
  images: {
    unoptimized: true,
  },
};

export default nextConfig;