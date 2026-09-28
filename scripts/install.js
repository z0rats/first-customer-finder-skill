#!/usr/bin/env node

const fs = require("fs");
const os = require("os");
const path = require("path");

function usage() {
  console.log(`
Claude First Customer Finder Skill installer

Usage:
  npx first-customer-finder-skill
  first-customer-finder-skill --skills-dir ~/.claude/skills

Options:
  --skills-dir PATH  Install into a custom Claude Code skills directory
  --help             Show this help
`);
}

function expandHome(value) {
  if (!value) return value;
  if (value === "~") return os.homedir();
  if (value.startsWith("~/")) return path.join(os.homedir(), value.slice(2));
  return value;
}

function parseArgs(argv) {
  const options = {};
  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === "--help" || arg === "-h") {
      options.help = true;
      continue;
    }
    if (arg === "--skills-dir") {
      const value = argv[index + 1];
      if (!value) throw new Error("--skills-dir requires a value");
      options.skillsDir = expandHome(value);
      index += 1;
      continue;
    }
    throw new Error(`Unknown option: ${arg}`);
  }
  return options;
}

function defaultSkillsDir() {
  const claudeHome = process.env.CLAUDE_CONFIG_DIR || path.join(os.homedir(), ".claude");
  return path.join(claudeHome, "skills");
}

function copyDirectory(source, destination) {
  fs.mkdirSync(destination, { recursive: true });
  for (const entry of fs.readdirSync(source, { withFileTypes: true })) {
    if (entry.name === "__pycache__" || entry.name.endsWith(".pyc")) continue;
    const sourcePath = path.join(source, entry.name);
    const destinationPath = path.join(destination, entry.name);
    if (entry.isDirectory()) copyDirectory(sourcePath, destinationPath);
    else if (entry.isFile()) fs.copyFileSync(sourcePath, destinationPath);
  }
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  if (options.help) {
    usage();
    return;
  }

  const source = path.resolve(__dirname, "..", "first-customer-finder");
  const skillsDir = path.resolve(options.skillsDir || defaultSkillsDir());
  const destination = path.join(skillsDir, "first-customer-finder");
  if (!fs.existsSync(source)) throw new Error(`Cannot find bundled skill at ${source}`);

  fs.mkdirSync(skillsDir, { recursive: true });
  let destinationStat;
  try {
    destinationStat = fs.lstatSync(destination);
  } catch (error) {
    if (error.code !== "ENOENT") throw error;
  }
  if (destinationStat && destinationStat.isSymbolicLink()) {
    throw new Error(`${destination} is a symlink (a development checkout?). Update its source instead of overwriting it.`);
  }

  // Copy into a staging directory first so a failed copy never leaves a half-installed skill.
  // The previous install waits in the same directory until the swap succeeds.
  const stagingRoot = fs.mkdtempSync(path.join(skillsDir, ".first-customer-finder-stage-"));
  let keepStaging = false;
  try {
    const staged = path.join(stagingRoot, "new");
    const previous = path.join(stagingRoot, "previous");
    copyDirectory(source, staged);
    if (destinationStat) fs.renameSync(destination, previous);
    try {
      fs.renameSync(staged, destination);
    } catch (error) {
      if (destinationStat && !fs.existsSync(destination)) {
        try {
          fs.renameSync(previous, destination);
        } catch (restoreError) {
          // Never delete the only remaining copy of the old install.
          keepStaging = true;
          throw new Error(`${error.message}. The previous install could not be restored and was kept at ${previous}`);
        }
      }
      throw error;
    }
  } finally {
    if (!keepStaging) fs.rmSync(stagingRoot, { recursive: true, force: true });
  }

  console.log("Installed first-customer-finder skill.");
  console.log(`Location: ${destination}`);
  console.log("");
  console.log("Restart Claude Code, then run:");
  console.log("  Find ten potential first customers for https://example.com.");
}

try {
  main();
} catch (error) {
  console.error(`Error: ${error.message}`);
  process.exit(1);
}
