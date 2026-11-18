// Front-page entrypoint for the 18 November 2026 news image.
//
// The drawing itself lives in render.py (PIL). This file only works out
// where the single output PNG belongs and hands the job to the painter.
// Output goes to the platform directory when the platform provides one,
// otherwise to the conventional /output location.
import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const repoRoot = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
const outFile = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });

const painter = spawnSync("python3", [join(repoRoot, "render.py"), outFile], {
  cwd: repoRoot,
  stdio: "inherit",
  env: process.env,
});

if (painter.error) {
  console.error("could not start render.py:", painter.error.message);
  process.exit(1);
}
if (painter.status !== 0) {
  console.error(`render.py exited with status ${painter.status}`);
  process.exit(painter.status ?? 1);
}
if (!existsSync(outFile)) {
  console.error("render.py finished but no entry.png appeared");
  process.exit(1);
}
console.log(`front page written to ${outFile}`);
