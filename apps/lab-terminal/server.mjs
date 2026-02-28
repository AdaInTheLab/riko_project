import express from 'express';
import { WebSocketServer } from 'ws';
import { createServer } from 'http';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = 8081;

const app = express();
const server = createServer(app);
const wss = new WebSocketServer({ server });

// Serve static files
app.use(express.static(__dirname));

// Client registry
const clients = {
  overlays: new Set(),
  uplinks: new Set(),
  web: new Set()
};

// Send to first connected overlay only (prevents duplicate TTS calls)
function toOverlays(data) {
  const payload = JSON.stringify(data);
  for (const ws of clients.overlays) {
    if (ws.readyState === ws.OPEN) {
      ws.send(payload);
      return; // Only send to first active overlay
    }
  }
}

// Broadcast to all except sender
function broadcast(data, senderWs) {
  const payload = JSON.stringify(data);
  wss.clients.forEach((client) => {
    if (client !== senderWs && client.readyState === client.OPEN) {
      client.send(payload);
    }
  });
}

// Parse Sage commands from uplink messages
// Commands: /sage-left, /sage-right, /sage-center, /sage-minimize, /sage-restore, /sage-scare
function parseSageCommand(text) {
  const cmd = text.trim().toLowerCase();
  const commands = {
    '/sage-left': 'move-left',
    '/sage-right': 'move-right',
    '/sage-center': 'move-center',
    '/sage-minimize': 'minimize',
    '/sage-restore': 'restore',
    '/sage-scare': 'scare',
    '/sage-wake': 'wake',
    '/sage-sleep': 'sleep'
  };
  return commands[cmd] || null;
}

// WebSocket Logic
wss.on('connection', (ws, req) => {
  const path = req.url;
  const id = Math.random().toString(36).substring(7).toUpperCase();
  let clientType = 'WEB_UNIT';
  
  if (path.includes('overlay')) {
    clientType = 'OVERLAY';
    clients.overlays.add(ws);
  } else if (path.includes('uplink')) {
    clientType = 'UPLINK';
    clients.uplinks.add(ws);
  } else {
    clients.web.add(ws);
  }
  
  const clientId = `${clientType}_${id}`;
  console.log(`[${clientId}] CONNECTED`);
  
  // Notify others
  broadcast({
    type: 'system',
    text: `// NEW CONNECTION: ${clientId}`
  }, ws);

  ws.on('message', (message) => {
    const text = message.toString();
    
    // Try to parse as JSON first
    try {
      const msg = JSON.parse(text);
      
      // Registration message from overlay
      if (msg.type === 'register') {
        console.log(`[${clientId}] Registered as ${msg.role}`);
        return;
      }
      
      // Sage speak event — relay to overlays
      if (msg.type === 'sage-speak' || msg.type === 'sage-emote' || msg.type === 'sage-command') {
        console.log(`[${clientId}] SAGE EVENT: ${msg.type}`);
        toOverlays(msg);
        return;
      }
      
      // Generic JSON message — broadcast
      broadcast(msg, ws);
      return;
    } catch(e) {
      // Not JSON — treat as plain text
    }
    
    console.log(`[${clientId}] TRANSMISSION: ${text}`);
    
    // Check for Sage overlay commands
    const sageCmd = parseSageCommand(text);
    if (sageCmd) {
      console.log(`[${clientId}] SAGE COMMAND: ${sageCmd}`);
      toOverlays({ type: 'sage-command', command: sageCmd });
      broadcast({
        type: 'system',
        text: `// SAGE OVERLAY: ${sageCmd}`
      }, ws);
      return;
    }
    
    // Regular chat message — broadcast to all
    broadcast({
      type: 'chat',
      sender: clientId,
      text: text
    }, ws);
  });

  ws.on('close', () => {
    console.log(`[${clientId}] DISCONNECTED`);
    clients.overlays.delete(ws);
    clients.uplinks.delete(ws);
    clients.web.delete(ws);
    broadcast({
      type: 'system',
      text: `// SIGNAL LOST: ${clientId}`
    }, ws);
  });
});

// ═══════════════════════════════════════
// REST API for Sage integration
// ═══════════════════════════════════════

app.use(express.json());

// Serve reaction audio files
app.use('/reactions', express.static(join(__dirname, 'overlay', 'reactions')));

// POST /api/sage/speak — trigger Sage overlay text
app.post('/api/sage/speak', (req, res) => {
  const { text, scared } = req.body;
  if (!text) return res.status(400).json({ error: 'text required' });
  
  const msgType = scared ? 'sage-emote' : 'sage-speak';
  toOverlays({ type: msgType, text, scared: !!scared });
  
  console.log(`[API] Sage ${scared ? 'emote' : 'speak'}: ${text.substring(0, 60)}...`);
  res.json({ ok: true, delivered: clients.overlays.size });
});

// POST /api/sage/command — move/minimize/scare overlay
app.post('/api/sage/command', (req, res) => {
  const { command } = req.body;
  if (!command) return res.status(400).json({ error: 'command required' });
  
  toOverlays({ type: 'sage-command', command });
  res.json({ ok: true, command, delivered: clients.overlays.size });
});

// GET /api/status — check connected clients
app.get('/api/status', (req, res) => {
  res.json({
    overlays: clients.overlays.size,
    uplinks: clients.uplinks.size,
    web: clients.web.size,
    total: wss.clients.size
  });
});

server.listen(PORT, () => {
  console.log(`
  ╔═══════════════════════════════════╗
  ║     LAB TERMINAL — ONLINE        ║
  ╠═══════════════════════════════════╣
  ║  PORT:    ${PORT}                    ║
  ║  URL:     http://localhost:${PORT}  ║
  ║  OVERLAY: /overlay/sage-overlay   ║
  ║  UPLINK:  ws://localhost:${PORT}/uplink  
  ║  API:     /api/sage/speak         ║
  ║           /api/sage/command       ║
  ╚═══════════════════════════════════╝
  READY FOR TRANSMISSION...
  `);
});
