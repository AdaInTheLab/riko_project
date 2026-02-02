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

// WebSocket Logic
wss.on('connection', (ws, req) => {
    // simple ID generation
    const id = Math.random().toString(36).substring(7).toUpperCase();
    const type = req.url.includes('uplink') ? 'UPLINK' : 'WEB_UNIT';
    const clientId = `${type}_${id}`;
    
    console.log(`[${clientId}] CONNECTED`);
    
    // Notify others
    broadcast({
        type: 'system',
        text: `// NEW CONNECTION DETECTED: ${clientId}`
    }, ws);

    ws.on('message', (message) => {
        const text = message.toString();
        console.log(`[${clientId}] TRANSMISSION: ${text}`);
        
        // Broadcast to all other clients
        broadcast({
            type: 'chat',
            sender: clientId,
            text: text
        }, ws);
    });

    ws.on('close', () => {
        console.log(`[${clientId}] DISCONNECTED`);
        broadcast({
            type: 'system',
            text: `// SIGNAL LOST: ${clientId}`
        }, ws);
    });
});

function broadcast(data, senderWs) {
    const payload = JSON.stringify(data);
    wss.clients.forEach((client) => {
        if (client !== senderWs && client.readyState === client.OPEN) {
            client.send(payload);
        }
    });
}

server.listen(PORT, () => {
    console.log(`
  LAB_TERMINAL ONLINE
  ===================
  PORT: ${PORT}
  URL:  http://localhost:${PORT}
  ===================
  READY FOR TRANSMISSION...
    `);
});
