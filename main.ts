// news-image-20261118 entry (Node 22, standard library only): its image is
// the entry.png beside this file, and the program copies it to
// /output/entry.png. The gate takes a whole PNG or JPEG of at most 1 MiB
// and 1024 by 1024 pixels, and the judge sees exactly the bytes copied.
// The image itself was composed by render.py (PIL labels + original
// flat-editorial vignettes in assets/) and sums up the world news of
// Wednesday 18 November 2026; see SOURCES.md for the verified headlines.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

// The copy is byte-for-byte identical on every run: the image is a fixed
// file in the repository, so the grader's two runs write the same bytes.
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
