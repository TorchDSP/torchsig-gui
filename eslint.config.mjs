import { defineConfig, globalIgnores } from "eslint/config";
import nextVitals from "eslint-config-next/core-web-vitals";
import nextTs from "eslint-config-next/typescript";

// Defines the lint rules for the interface source code
const eslintConfig = defineConfig([
  ...nextVitals,
  ...nextTs,

  // Skips generated and third-party files
  globalIgnores([
    ".next/**",
    "node_modules/**",
    ".venv/**",
    "torchsiggui/**",
    "next-env.d.ts",
  ]),
]);

export default eslintConfig;
