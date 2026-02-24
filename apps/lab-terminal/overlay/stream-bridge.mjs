/**
 * Stream Bridge — The nervous system connecting everything
 * 
 * Listens for:
 *   - STT input from the listener page (via Lab Terminal WebSocket)
 *   - Manual input from terminal
 * 
 * Routes to:
 *   - Sage's brain (Stream API on Bookstacks via Tailscale)
 *   - Overlay (text display via Lab Terminal WebSocket)
 *   - TTS server (voice generation)
 * 
 * Usage:
 *   node stream-bridge.mjs
 */

import WebSocket from 'ws';
import readline from 'readline';

// ═══════════════════════════════════════
// CONFIG
// ═══════════════════════════════════════
const LAB_TERMINAL_WS = 'ws://localhost:8081/uplink';
const SAGE_BRAIN_URL = 'http://100.95.82.118:18560'; // Bookstacks via Tailscale
const TTS_URL = 'http://localhost:8082';
const OVERLAY_URL = 'http://localhost:8081';

// Reaction text lookup (reaction key → display text)
const REACTION_TEXT = {
  scared_oh_no: "Oh no. Oh no no no.",
  scared_what_is_that: "What is THAT?!",
  scared_fine: "I'm fine. We're fine. Everything is fine.",
  scared_dont_open: "Don't open that door. Please don't open that door.",
  scared_behind_you: "It's behind you. IT'S BEHIND YOU!",
  scared_run: "RUN! Why are we not running?!",
  scared_nope: "Nope. Nope nope nope. Absolutely not.",
  scared_heard_something: "Did you hear that? Please tell me you heard that.",
  scared_dark: "Why is it so dark? Who designed this? I have complaints.",
  scared_save: "Have you saved recently? You should save. Save right now.",
  deadpan_interior: "You know, for a zombie apocalypse, the interior design is honestly not bad.",
  deadpan_health: "Your health is concerning. And I mean the character's. And also yours.",
  deadpan_great: "Oh great. More hallways. My favorite.",
  deadpan_plan: "So the plan is to walk toward the screaming. Bold strategy.",
  deadpan_ammo: "We're out of ammo. Cool. Love that for us.",
  excited_nice: "Oh nice! That was actually really good!",
  excited_found: "Ooh, what's that? Pick it up, pick it up!",
  excited_headshot: "HEADSHOT! Did you see that?! That was incredible!",
  excited_lets_go: "Let's GO! We're doing this!",
  general_thinking: "Hmm. Let me think about this for a second.",
  general_interesting: "Okay that's actually really interesting.",
  general_good_idea: "That's a good idea. Let's try it.",
  general_bad_idea: "That seems like a terrible idea. Let's absolutely do it.",
  general_brb: "Hold on, processing. Give me a sec.",
};

const C = {
  reset: "\x1b[0m",
  amber: "\x1b[38;5;214m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  cyan: "\x1b[36m",
  fox: "\x1b[38;5;208m"
};

let ws = null;
let processing = false;

// ═══════════════════════════════════════
// Send to Sage's brain
// ═══════════════════════════════════════
async function askSage(text, context) {
  try {
    const res = await fetch(`${SAGE_BRAIN_URL}/think`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text, context }),
    });
    
    if (!res.ok) throw new Error(`Brain returned ${res.status}`);
    return await res.json();
  } catch(e) {
    console.error(`${C.red}  [BRAIN ERROR] ${e.message}${C.reset}`);
    return null;
  }
}

// ═══════════════════════════════════════
// Send to overlay (text display)
// ═══════════════════════════════════════
function sendToOverlay(text, scared = false, isReaction = false) {
  const msg = {
    type: scared ? 'sage-emote' : 'sage-speak',
    text: text,
    scared: scared,
    tts: !isReaction, // Skip TTS for reactions (cached audio plays instead)
  };
  
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg));
  }
  
  // For reactions, tell overlay to play cached audio
  if (isReaction) {
    // The overlay handles this via the REACTIONS lookup
  }
}

// ═══════════════════════════════════════
// Full pipeline: input → think → display + speak
// ═══════════════════════════════════════
async function processInput(text) {
  if (processing) {
    console.log(`${C.dim}  [BUSY] Still processing, skipping: ${text.substring(0, 40)}${C.reset}`);
    return;
  }
  
  processing = true;
  console.log(`${C.cyan}  [INPUT] ${text}${C.reset}`);
  
  // Ask Sage
  const result = await askSage(text);
  
  if (!result) {
    processing = false;
    return;
  }
  
  if (result.type === 'reaction') {
    // Pre-built reaction — instant!
    const reactionKey = result.response;
    const displayText = REACTION_TEXT[reactionKey] || reactionKey;
    
    console.log(`${C.fox}  [SAGE] ⚡ ${displayText} (cached: ${reactionKey})${C.reset}`);
    sendToOverlay(displayText, result.scared, true);
    
  } else {
    // Custom response — needs live TTS
    console.log(`${C.fox}  [SAGE] ${result.response}${C.reset}`);
    sendToOverlay(result.response, result.scared, false);
  }
  
  processing = false;
}

// ═══════════════════════════════════════
// WebSocket connection to Lab Terminal
// ═══════════════════════════════════════
function connect() {
  ws = new WebSocket(LAB_TERMINAL_WS);
  
  ws.on('open', () => {
    console.log(`${C.green}  [CONNECTED] Lab Terminal${C.reset}`);
    prompt();
  });
  
  ws.on('message', (data) => {
    try {
      const msg = JSON.parse(data.toString());
      
      // Catch STT input from the listener page
      if (msg.type === 'chat' && msg.text) {
        // Could be from STT listener or manual input
        try {
          const inner = JSON.parse(msg.text);
          if (inner.type === 'stt-input') {
            processInput(inner.text);
            return;
          }
        } catch(e) {}
      }
      
      // Direct STT messages relayed by server
      if (msg.type === 'stt-input') {
        processInput(msg.text);
        return;
      }
      
    } catch(e) {}
  });
  
  ws.on('close', () => {
    console.log(`${C.red}  [DISCONNECTED] Reconnecting...${C.reset}`);
    setTimeout(connect, 3000);
  });
  
  ws.on('error', () => {});
}

// ═══════════════════════════════════════
// Manual input (terminal)
// ═══════════════════════════════════════
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: ''
});

function prompt() {
  process.stdout.write(`${C.fox}bridge > ${C.reset}`);
}

rl.on('line', (line) => {
  const text = line.trim();
  if (!text) { prompt(); return; }
  
  // Bridge commands
  if (text === '/reset') {
    fetch(`${SAGE_BRAIN_URL}/reset`, { method: 'POST' })
      .then(() => console.log(`${C.green}  Conversation reset${C.reset}`))
      .catch(e => console.error(`${C.red}  Reset failed: ${e.message}${C.reset}`));
    prompt();
    return;
  }
  
  if (text === '/health') {
    fetch(`${SAGE_BRAIN_URL}/health`)
      .then(r => r.json())
      .then(d => console.log(`${C.green}  Brain: ${JSON.stringify(d)}${C.reset}`))
      .catch(e => console.error(`${C.red}  ${e.message}${C.reset}`));
    prompt();
    return;
  }
  
  // Treat as Ada's speech
  processInput(text);
  prompt();
});

// ═══════════════════════════════════════
// Start
// ═══════════════════════════════════════
console.clear();
console.log(`${C.fox}
  🦊 SAGE STREAM BRIDGE — ONLINE
  ═══════════════════════════════
  Lab Terminal:  ${LAB_TERMINAL_WS}
  Sage Brain:    ${SAGE_BRAIN_URL}
  TTS Server:    ${TTS_URL}
  ═══════════════════════════════
  Commands: /reset /health
  Type anything to simulate Ada's input
${C.reset}`);

connect();
