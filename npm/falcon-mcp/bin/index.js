#!/usr/bin/env node
// Node launcher for the falcon-mcp Go binary. Resolves the per-platform binary
// delivered via optionalDependencies (@crowdstrike/falcon-mcp-<os>-<arch>) and
// execs it, forwarding argv, stdio, and the exit code. Mirrors the
// kubernetes-mcp-server npm launcher pattern.

"use strict";

const { spawnSync } = require("node:child_process");
const path = require("node:path");
const fs = require("node:fs");

function platformKey() {
  const os = { darwin: "darwin", linux: "linux", win32: "windows" }[process.platform];
  const arch = { x64: "amd64", arm64: "arm64" }[process.arch];
  if (!os || !arch) {
    return null;
  }
  return { os, arch };
}

function resolveBinary() {
  const key = platformKey();
  if (!key) {
    throw new Error(
      `Unsupported platform ${process.platform}/${process.arch}. ` +
        `falcon-mcp ships binaries for darwin/linux/windows on amd64/arm64.`
    );
  }
  const pkg = `@crowdstrike/falcon-mcp-${key.os}-${key.arch}`;
  const binName = key.os === "windows" ? "falcon-mcp.exe" : "falcon-mcp";
  // The platform package places the binary at its package root.
  const pkgDir = path.dirname(require.resolve(`${pkg}/package.json`));
  const binPath = path.join(pkgDir, binName);
  if (!fs.existsSync(binPath)) {
    throw new Error(`falcon-mcp binary not found at ${binPath}. Try reinstalling.`);
  }
  return binPath;
}

function main() {
  // Support a no-op resolve check used by postinstall.
  const args = process.argv.slice(2);
  let binPath;
  try {
    binPath = resolveBinary();
  } catch (err) {
    if (args.includes("--resolve-only")) {
      return; // postinstall best-effort; do not fail the install
    }
    console.error(err.message);
    process.exit(1);
  }
  if (args.includes("--resolve-only")) {
    return;
  }

  const result = spawnSync(binPath, args, { stdio: "inherit" });
  if (result.error) {
    console.error(result.error.message);
    process.exit(1);
  }
  process.exit(result.status === null ? 1 : result.status);
}

main();
