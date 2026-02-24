#!/usr/bin/env node
/**
 * Sage Bridge — Connects OpenClaw agent output to the stream overlay
 * 
 * Usage:
 *   node sage-bridge.mjs
 * 
 * This connects to the Lab Terminal server and provides a way
 * to pipe Sage's responses to the overlay. Can be used:
 * 
 * 1. Manually: type messages to display on overlay
 * 2. Via API: POST to localhost:8081/api/sage/speak
 * 3. Via OpenClaw: hook into agent responses
 * 
 * Commands (type in terminal):
 *   /left /right /center   — move overlay position
 *   /minimize /restore     — shrink/restore overlay
 *   /scare                 — trigger scare mode 💀
 *   /wake /sleep           — force active/idle state
 *   Anything else          — display as Sage's speech
 */

import WebSocket from 'ws';
import readline from 'readline';

const SERVER_URL = 'ws://localhost:8081/uplink';

const C = {
  reset: "\x1b[0m",
  amber: "\x1b[38;5;214m",
  dim: "\x1b[2m",
  red: "\x1b[31m",
  green: "\x1b[32m",
  fox: "\x1b[38;5;208m"
};

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: ''
});

let ws;

function connect() {
  ws = new WebSocket(SERVER_URL);

  ws.on('open', () => {
    console.clear();
    console.log(`${C.fox}  🦊 SAGE BRIDGE — ONLINE${C.reset}`);
    console.log(`${C.dim}  Connected to Lab Terminal${C.reset}`);
    console.log(`${C.dim}  Type to speak. Commands: /left /right /center /scare /minimize /restore${C.reset}\n`);
    process.stdout.write(`${C.fox}sage > ${C.reset}`);
  });

  ws.on('message', (data) => {
    // We mostly ignore incoming — overlay handles display
  });

  ws.on('close', () => {
    console.log(`\n${C.red}  Connection lost. Reconnecting...${C.reset}`);
    setTimeout(connect, 3000);
  });

  ws.on('error', () => {});
}

rl.on('line', (line) => {
  const text = line.trim();
  if (!text || !ws || ws.readyState !== WebSocket.OPEN) {
    process.stdout.write(`${C.fox}sage > ${C.reset}`);
    return;
  }

  // Check for overlay commands
  const cmdMap = {
    '/left': 'move-left',
    '/right': 'move-right', 
    '/center': 'move-center',
    '/minimize': 'minimize',
    '/restore': 'restore',
    '/scare': 'scare',
    '/wake': 'wake',
    '/sleep': 'sleep'
  };

  const cmd = cmdMap[text.toLowerCase()];
  if (cmd) {
    ws.send(JSON.stringify({ type: 'sage-command', command: cmd }));
    console.log(`${C.dim}  ↪ overlay: ${cmd}${C.reset}`);
  } else {
    // Send as speech
    const scared = text.includes('💀') || text.includes('WHAT') || text.toUpperCase() === text;
    ws.send(JSON.stringify({ type: 'sage-speak', text, scared }));
    console.log(`${C.dim}  ↪ speaking: ${text.substring(0, 60)}${text.length > 60 ? '...' : ''}${C.reset}`);
  }

  process.stdout.write(`${C.fox}sage > ${C.reset}`);
});

connect();
