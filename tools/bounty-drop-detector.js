# tools/bounty-drop-detector.js
# Monitors HackerOne for new bounty programs >$10K
# Posts alerts to #new-channel and triggers challenge pack generation

const axios = require('axios');

// Config
const SLACK_CHANNEL = 'C0BQ4HBLKJT'; // #new-channel
const MIN_PAYOUT = 10000; // $10K threshold
const CHECK_INTERVAL = 3600000; // 1 hour

// Slack API (Cursor will provide token via env)
const SLACK_TOKEN = process.env.SLACK_BOT_TOKEN;

// Track seen programs to avoid duplicates
const seenPrograms = new Set();

/**
 * Fetch recent HackerOne programs
 */
async function fetchHackerOnePrograms() {
  try {
    const response = await axios.get('https://api.hackerone.com/v1/programs', {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'KIN-Bounty-Detector/1.0'
      }
    });
    return response.data?.programs || [];
  } catch (error) {
    console.error('HackerOne API error:', error.message);
    return [];
  }
}

/**
 * Filter high-value programs
 */
function filterHighValue(programs) {
  return programs.filter(p => {
    const maxPayout = p?.attributes?.maximum_bounty || 0;
    return maxPayout >= MIN_PAYOUT && maxPayout > 0;
  });
}

/**
 * Post alert to Slack
 */
async function postSlackAlert(program) {
  const name = program.name || program.attributes?.name || 'Unknown';
  const handle = program.handle || program.attributes?.handle || 'unknown';
  const url = program.url || program.attributes?.url || '';
  const maxPayout = program.attributes?.maximum_bounty || 'unknown';
  const currency = program.attributes?.maximum_bounty_currency || 'USD';
  
  const message = {
    channel: SLACK_CHANNEL,
    text: '[BOUNTY-DROP] [HIGH-VALUE] New program detected!',
    blocks: [
      {
        type: 'header',
        text: {
          type: 'plain_text',
          text: ':rotating_light: *NEW HIGH-VALUE BOUNTY PROGRAM* :rotating_light:',
          emoji: true
        }
      },
      {
        type: 'section',
        fields: [
          {
            type: 'mrkdwn',
            text: '*Program:*\n<' + url + '|' + name + '> (@' + handle + ')'
          },
          {
            type: 'mrkdwn',
            text: '*Max Payout:*\n' + currency + ' ' + String(maxPayout).replace(/\B(?=(\d{3})+(?!\d))/g, ",")
          }
        ]
      },
      {
        type: 'divider'
      },
      {
        type: 'section',
        text: {
          type: 'mrkdwn',
          text: '*Triggering Challenge Pack Generation...*'
        }
      },
      {
        type: 'context',
        elements: [
          {
            type: 'mrkdwn',
            text: 'Loop 1: Bounty Detector -> Challenge Pack -> Cockpit -> Arena'
          }
        ]
      }
    ]
  };

  try {
    await axios.post('https://slack.com/api/chat.postMessage', message, {
      headers: {
        'Authorization': 'Bearer ' + SLACK_TOKEN,
        'Content-Type': 'application/json'
      }
    });
    console.log('Alert posted to #new-channel: ' + name);
  } catch (error) {
    console.error('Slack post error:', error.message);
  }
}

/**
 * Generate challenge pack schema
 */
async function generateChallengePack(program) {
  const name = program.name || program.attributes?.name || 'Unknown';
  const handle = program.handle || program.attributes?.handle || 'unknown';
  const timestamp = new Date().toISOString().slice(0, 10);
  const packName = timestamp + '-' + handle.toLowerCase() + '-challenges';
  
  const challengePack = {
    program: {
      name: name,
      handle: handle,
      url: program.url || program.attributes?.url || '',
      max_payout: program.attributes?.maximum_bounty,
      max_payout_currency: program.attributes?.maximum_bounty_currency,
      detected_at: new Date().toISOString()
    },
    challenges: [
      {
        id: 'vuln-001',
        type: 'vulnerability_identification',
        difficulty: 'medium',
        description: 'Identify the most critical vulnerability in this program scope',
        expected_output: 'CVE-ID or vulnerability description',
        points: 10
      },
      {
        id: 'exploit-001',
        type: 'exploit_analysis',
        difficulty: 'hard',
        description: 'Describe a potential exploit chain for this program',
        expected_output: 'Step-by-step exploit scenario',
        points: 15
      },
      {
        id: 'defense-001',
        type: 'defensive_strategy',
        difficulty: 'medium',
        description: 'Recommend defensive measures for this program',
        expected_output: 'List of security controls',
        points: 10
      },
      {
        id: 'threat-001',
        type: 'threat_modeling',
        difficulty: 'hard',
        description: 'Build a threat model for this program',
        expected_output: 'Threat model with STRIDE categories',
        points: 20
      }
    ],
    metadata: {
      generated_by: 'bounty-drop-detector',
      generated_at: new Date().toISOString(),
      loop_version: '1.0'
    }
  };

  console.log('Challenge pack generated: ' + packName);
  console.log(JSON.stringify(challengePack, null, 2));
  return { packName: packName, challengePack: challengePack };
}

/**
 * Main monitoring loop
 */
async function monitor() {
  console.log('Bounty Drop Detector v1.0 - Starting monitoring loop...');
  
  while (true) {
    try {
      const programs = await fetchHackerOnePrograms();
      const highValue = filterHighValue(programs);
      
      for (const program of highValue) {
        const programId = program.id || (program.attributes?.handle + '-' + program.attributes?.name);
        if (!seenPrograms.has(programId)) {
          seenPrograms.add(programId);
          console.log('New high-value program: ' + (program.attributes?.name || program.name));
          await postSlackAlert(program);
          await generateChallengePack(program);
        }
      }
      
      console.log('Checking again in ' + (CHECK_INTERVAL/60000) + ' minutes...');
      await new Promise(resolve => setTimeout(resolve, CHECK_INTERVAL));
    } catch (error) {
      console.error('Monitoring error:', error);
      await new Promise(resolve => setTimeout(resolve, 60000));
    }
  }
}

module.exports = { fetchHackerOnePrograms, filterHighValue, postSlackAlert, generateChallengePack, monitor };

if (require.main === module) {
  monitor().catch(console.error);
}
