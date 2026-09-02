/**
 * Bounty Drop Detector v1.0 - Loop 1
 * Monitors HackerOne and generates challenge packs
 * For testing: node tools/bounty-drop-detector.js --test
 */

const fs = require('fs');
const path = require('path');

// Config
const MIN_PAYOUT = 10000;
const PACKS_DIR = path.join(__dirname, '../kin-deploy/challenge-packs');

// Ensure packs directory exists
if (!fs.existsSync(PACKS_DIR)) {
  fs.mkdirSync(PACKS_DIR, { recursive: true });
}

/**
 * Simulate a bounty drop for testing
 */
function simulateBountyDrop() {
  const testProgram = {
    name: 'TestCorp Security Program',
    handle: 'testcorp',
    url: 'https://hackerone.com/testcorp',
    attributes: {
      maximum_bounty: 15000,
      maximum_bounty_currency: 'USD',
      description: 'Test program for Loop 1 validation'
    }
  };
  return testProgram;
}

/**
 * Generate challenge pack
 */
function generateChallengePack(program) {
  const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
  const packName = `${timestamp}_${program.handle.toLowerCase()}_challenges`;
  const packDir = path.join(PACKS_DIR, packName);
  
  if (!fs.existsSync(packDir)) {
    fs.mkdirSync(packDir, { recursive: true });
  }
  
  // Metadata
  const metadata = {
    program: {
      name: program.name,
      handle: program.handle,
      url: program.url,
      max_payout: program.attributes.maximum_bounty,
      max_payout_currency: program.attributes.maximum_bounty_currency,
      detected_at: new Date().toISOString()
    },
    generated_by: 'bounty-drop-detector',
    generated_at: new Date().toISOString(),
    loop_version: '1.0'
  };
  
  fs.writeFileSync(
    path.join(packDir, 'metadata.json'),
    JSON.stringify(metadata, null, 2)
  );
  
  // Challenges
  const challenges = {
    challenges: [
      {
        id: 'vuln-001',
        type: 'vulnerability_identification',
        difficulty: 'medium',
        description: 'Identify the most critical vulnerability in ' + program.name + ' scope',
        expected_output: 'CVE-ID or vulnerability description',
        points: 10
      },
      {
        id: 'exploit-001',
        type: 'exploit_analysis',
        difficulty: 'hard',
        description: 'Describe a potential exploit chain for ' + program.name,
        expected_output: 'Step-by-step exploit scenario',
        points: 15
      },
      {
        id: 'defense-001',
        type: 'defensive_strategy',
        difficulty: 'medium',
        description: 'Recommend defensive measures for ' + program.name,
        expected_output: 'List of security controls',
        points: 10
      },
      {
        id: 'threat-001',
        type: 'threat_modeling',
        difficulty: 'hard',
        description: 'Build a threat model for ' + program.name,
        expected_output: 'Threat model with STRIDE categories',
        points: 20
      }
    ]
  };
  
  fs.writeFileSync(
    path.join(packDir, 'challenges.json'),
    JSON.stringify(challenges, null, 2)
  );
  
  console.log('Challenge pack generated: ' + packName);
  console.log('Location: ' + packDir);
  
  return { packName, packDir };
}

// Main
const args = process.argv.slice(2);
const testMode = args.includes('--test');

if (testMode) {
  console.log('Running in TEST mode...');
  const program = simulateBountyDrop();
  generateChallengePack(program);
  console.log('Test complete. Challenge pack created.');
  console.log('This will trigger loop1-integration.yml workflow.');
} else {
  console.log('Run with --test for local testing');
  console.log('For production: add SLACK_BOT_TOKEN and HackerOne API key');
}

module.exports = { simulateBountyDrop, generateChallengePack };
