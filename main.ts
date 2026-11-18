// News-image entry, 18 November 2026.
//
// The front page was already drawn during the build: render.py produced
// entry.png, which sits next to this file. This entrypoint only carries
// that finished image into the platform's output directory. It uses the
// Node standard library alone and starts no other program, so it runs in
// a bare container with nothing extra installed.

import { copyFileSync, existsSync, mkdirSync, statSync } from 'node:fs';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const IMAGE_FILE = 'entry.png';

// Directory holding this file, which is also where the rendered image lives.
function repoDir(): string {
  return dirname(fileURLToPath(import.meta.url));
}

// Where the platform wants the deliverable: its environment variable when
// set, otherwise the conventional output location.
function outputDir(): string {
  const fromEnv = process.env.MAKEFUN_OUTPUT_DIR;
  if (fromEnv && fromEnv.trim() !== '') {
    return resolve(fromEnv);
  }
  return '/output';
}

function sourcePath(): string {
  return join(repoDir(), IMAGE_FILE);
}

function targetPath(): string {
  return join(outputDir(), IMAGE_FILE);
}

function makeDir(path: string): void {
  mkdirSync(path, { recursive: true });
}

function copyImage(from: string, to: string): void {
  copyFileSync(from, to);
}

// Confirm the copy really landed and is the same size as the source.
function checkCopy(from: string, to: string): number {
  if (!existsSync(to)) {
    throw new Error(`output image not found after copy: ${to}`);
  }
  const sourceBytes = statSync(from).size;
  const copiedBytes = statSync(to).size;
  if (copiedBytes !== sourceBytes) {
    throw new Error(
      `output image size mismatch: expected ${sourceBytes} bytes, got ${copiedBytes}`,
    );
  }
  return copiedBytes;
}

// Fail fast with a clear message if the rendered image is missing.
function requireSource(path: string): void {
  if (!existsSync(path)) {
    throw new Error(`rendered image not found next to the entrypoint: ${path}`);
  }
}

function main(): void {
  const from = sourcePath();
  const to = targetPath();
  requireSource(from);
  makeDir(dirname(to));
  copyImage(from, to);
  const bytes = checkCopy(from, to);
  console.log(`copied ${IMAGE_FILE} (${bytes} bytes) to ${to}`);
}

main();
