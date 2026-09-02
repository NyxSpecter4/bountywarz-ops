/**
 * Cockpit v2.2 - Multi-Sport Challenge Runner
 * Part of Loop 1: Bounty Drop Detector -> Challenge Pack -> Cockpit -> Arena
 */

const fs = require("fs");
const path = require("path");

// Use absolute path from GITHUB_WORKSPACE
const REPO_ROOT = process.env.GITHUB_WORKSPACE || process.cwd();
const PACKS_DIR = path.join(REPO_ROOT, "kin-deploy/challenge-packs");
const ARENA_DIR = path.join(REPO_ROOT, "arena");

function loadSports() {
  if (!fs.existsSync(PACKS_DIR)) {
    console.log("No challenge packs directory: " + PACKS_DIR);
    return [];
  }

  const packs = fs.readdirSync(PACKS_DIR);
  const loadedSports = [];

  packs.forEach(packName => {
    const packPath = path.join(PACKS_DIR, packName);
    const metadataPath = path.join(packPath, "metadata.json");
    if (fs.existsSync(metadataPath)) {
      try {
        const metadata = JSON.parse(fs.readFileSync(metadataPath, "utf8"));
        const sportNumber = loadedSports.length + 1;
        const sport = {
          id: sportNumber,
          name: packName,
          program: metadata.program || {},
          challenges: [],
          createdAt: metadata.generated_at || new Date().toISOString()
        };
        loadedSports.push(sport);
        console.log("Loaded Sport #" + sportNumber + ": " + packName);
      } catch (error) {
        console.error("Error loading pack " + packName + ":", error.message);
      }
    }
  });

  return loadedSports;
}

async function runAllSports() {
  const allSports = loadSports();
  if (allSports.length === 0) {
    console.log("No sports loaded from " + PACKS_DIR);
    return [];
  }

  console.log("COCKPIT v2.2: Running " + allSports.length + " sports");
  const allResults = [];

  for (const sport of allSports) {
    console.log("Running Sport #" + sport.id + ": " + sport.name);
    for (const challenge of sport.challenges) {
      allResults.push({
        challenge_id: challenge.id,
        sport_id: sport.id,
        response: "Response to: " + challenge.description,
        score: Math.floor(Math.random() * 100),
        status: "completed"
      });
    }
  }

  console.log("COCKPIT v2.2 COMPLETE: " + allResults.length + " results");
  return allResults;
}

// CLI
const args = process.argv.slice(2);
const sportArg = args.find(a => a.startsWith("--sport="));
if (sportArg) {
  const sportNumber = parseInt(sportArg.split("=")[1]);
  const allSports = loadSports();
  const sport = allSports.find(s => s.id === sportNumber);
  if (sport) {
    console.log("Running Sport #" + sportNumber);
  } else {
    console.error("Sport #" + sportNumber + " not found");
    process.exit(1);
  }
} else {
  runAllSports();
}
