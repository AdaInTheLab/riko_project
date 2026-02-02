import WebSocket from 'ws';
import readline from 'readline';

const SERVER_URL = 'ws://localhost:8081/uplink';
const ws = new WebSocket(SERVER_URL);

// UI Configuration
const COLORS = {
    reset: "\x1b[0m",
    amber: "\x1b[38;5;214m",
    dim: "\x1b[2m",
    red: "\x1b[31m",
    green: "\x1b[32m"
};

const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    prompt: ''
});

console.clear();
console.log(`${COLORS.amber}=== UPLINK TERMINAL ESTABLISHED ===${COLORS.reset}\n`);

ws.on('open', () => {
    console.log(`${COLORS.green}>> SIGNAL LOCKED: ${SERVER_URL}${COLORS.reset}`);
    process.stdout.write(`${COLORS.amber}> ${COLORS.reset}`);
});

ws.on('message', (data) => {
    // Clear current line to avoid messing up the prompt
    readline.clearLine(process.stdout, 0);
    readline.cursorTo(process.stdout, 0);

    try {
        const msg = JSON.parse(data);
        
        if (msg.type === 'system') {
            console.log(`${COLORS.dim}${msg.text}${COLORS.reset}`);
        } else if (msg.type === 'chat') {
            // Format: [SENDER] Message
            console.log(`${COLORS.dim}[${msg.sender}]${COLORS.reset} ${COLORS.amber}${msg.text}${COLORS.reset}`);
        }
    } catch (e) {
        console.log(`${COLORS.dim}RAW: ${data}${COLORS.reset}`);
    }

    // Restore prompt
    process.stdout.write(`${COLORS.amber}> ${COLORS.reset}`);
});

ws.on('close', () => {
    console.log(`\n${COLORS.red}>> CONNECTION TERMINATED${COLORS.reset}`);
    process.exit(0);
});

ws.on('error', (err) => {
    console.error(`\n${COLORS.red}>> ERROR: ${err.message}${COLORS.reset}`);
    process.exit(1);
});

// Handle User Input
rl.on('line', (line) => {
    const text = line.trim();
    if (text && ws.readyState === WebSocket.OPEN) {
        // Move cursor up one line to overwrite the input with a "sent" log if desired,
        // or just let it stay. Let's keep it simple.
        ws.send(text);
    }
    process.stdout.write(`${COLORS.amber}> ${COLORS.reset}`);
});
