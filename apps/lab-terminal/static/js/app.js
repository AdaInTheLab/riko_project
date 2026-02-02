const uptimeClock = document.getElementById('uptime-clock');
let startTime = Date.now();

function updateUptime() {
    const diff = Math.floor((Date.now() - startTime) / 1000);
    const h = String(Math.floor(diff / 3600)).padStart(2, '0');
    const m = String(Math.floor((diff % 3600) / 60)).padStart(2, '0');
    const s = String(diff % 60).padStart(2, '0');
    uptimeClock.textContent = `${h}:${m}:${s}`;
}
setInterval(updateUptime, 1000);

const chatForm = document.getElementById('chat-form');
const messageInput = document.getElementById('message-input');
const messagesContainer = document.getElementById('messages');
const chatContainer = document.getElementById('chat-container');
const sendBtn = document.getElementById('send-btn');
const imgBtn = document.getElementById('img-btn');
const personaSelect = document.getElementById('persona-select');
const voiceToggle = document.getElementById('voice-toggle');
const voiceKnob = document.getElementById('voice-knob');
const clawhubToggle = document.getElementById('clawhub-toggle');
const clawhubSidebar = document.getElementById('clawhub-sidebar');
const clawhubClose = document.getElementById('clawhub-close');
const clawhubSearch = document.getElementById('clawhub-search');
const clawhubResults = document.getElementById('clawhub-results');

const vaultToggle = document.getElementById('vault-toggle');
const vaultSidebar = document.getElementById('vault-sidebar');
const vaultClose = document.getElementById('vault-close');
const vaultGrid = document.getElementById('vault-grid');

const forgeToggle = document.getElementById('forge-toggle');
const forgeSidebar = document.getElementById('forge-sidebar');
const forgeClose = document.getElementById('forge-close');
const heatBtn = document.getElementById('heat-btn');
const quenchBtn = document.getElementById('quench-btn');
const forgeDesc = document.getElementById('forge-desc');
const lobsterMode = document.getElementById('lobster-mode');
const forgeStatus = document.getElementById('forge-status');
const forgeOutput = document.getElementById('forge-output');
const forgeCode = document.getElementById('forge-code');
const forgeStep = document.getElementById('forge-step');
const forgeProgress = document.getElementById('forge-progress');

let voiceEnabled = false;
let forgedManifest = '';

// ... (Voice Toggle)

// Sidebar Toggles
clawhubToggle.addEventListener('click', () => {
    clawhubSidebar.classList.toggle('w-0');
    clawhubSidebar.classList.toggle('w-80');
    forgeSidebar.classList.add('w-0');
    forgeSidebar.classList.remove('w-96');
    vaultSidebar.classList.add('w-0');
    vaultSidebar.classList.remove('w-80');
    if (!clawhubSidebar.classList.contains('w-0')) searchClawHub('');
});
clawhubClose.addEventListener('click', () => {
    clawhubSidebar.classList.add('w-0');
    clawhubSidebar.classList.remove('w-80');
});

forgeToggle.addEventListener('click', () => {
    forgeSidebar.classList.toggle('w-0');
    forgeSidebar.classList.toggle('w-96');
    clawhubSidebar.classList.add('w-0');
    clawhubSidebar.classList.remove('w-80');
    vaultSidebar.classList.add('w-0');
    vaultSidebar.classList.remove('w-80');
});
forgeClose.addEventListener('click', () => {
    forgeSidebar.classList.add('w-0');
    forgeSidebar.classList.remove('w-96');
});

vaultToggle.addEventListener('click', () => {
    vaultSidebar.classList.toggle('w-0');
    vaultSidebar.classList.toggle('w-80');
    clawhubSidebar.classList.add('w-0');
    clawhubSidebar.classList.remove('w-80');
    forgeSidebar.classList.add('w-0');
    forgeSidebar.classList.remove('w-96');
    if (!vaultSidebar.classList.contains('w-0')) loadVault();
});
vaultClose.addEventListener('click', () => {
    vaultSidebar.classList.add('w-0');
    vaultSidebar.classList.remove('w-80');
});

// Load Vault
async function loadVault() {
    try {
        const res = await fetch('/vault');
        const data = await res.json();
        vaultGrid.innerHTML = '';
        data.images.forEach(src => {
            const img = document.createElement('img');
            img.src = src;
            img.className = "w-full border border-blue-400/30 glow-border hover:border-blue-400 transition-all cursor-pointer";
            img.onclick = () => addMessage(src, 'bot', true);
            vaultGrid.appendChild(img);
        });
    } catch (e) { console.error("Vault Error", e); }
}

// Load History
async function loadHistory() {
    try {
        const res = await fetch('/history');
        const history = await res.json();
        messagesContainer.innerHTML = ''; // Clear initial greeting if history exists
        
        if (history.length === 0) {
             const div = document.createElement('div');
             div.className = "text-center py-4 opacity-50 text-xs tracking-widest border-b border-dashed border-gray-800 mb-6";
             div.textContent = "// TERMINAL READY. SELECT MODULE.";
             messagesContainer.appendChild(div);
             return;
        }

        history.forEach(msg => {
            // Map DB fields to addMessage parameters
            const isImage = msg.msg_type === 'image';
            const type = msg.sender_type === 'user' ? 'user' : (msg.sender_type === 'system' ? 'system' : 'bot');
            
            // Custom addMessage logic to support explicit sender name from DB
            addMessageFromHistory(msg.content, type, msg.sender_name, isImage, msg.created_at);
        });
        
        scrollToBottom();
    } catch (e) { console.error("History Load Error", e); }
}

function addMessageFromHistory(content, type, senderName, isImage, timestamp) {
    const div = document.createElement('div');
    
    if (type === 'system') {
        div.className = "text-center py-2 opacity-50 text-xs text-amber-400/70 tracking-widest border-t border-b border-amber-400/10 my-4";
        div.textContent = content;
        messagesContainer.appendChild(div);
        return;
    }

    div.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'} message-anim`;
    
    const bubble = document.createElement('div');
    bubble.className = `max-w-[70%] p-4 border ${
        type === 'user' 
            ? 'border-amber-400 bg-amber-400/10 text-amber-50 shadow-[0_0_15px_rgba(255,191,0,0.1)]' 
            : 'border-gray-700 bg-gray-900 text-gray-300'
    }`;
    
    const meta = document.createElement('div');
    meta.className = "text-[10px] tracking-widest opacity-50 mb-1 flex justify-between gap-4";
    
    // Parse timestamp if needed, or just use string
    const time = new Date(timestamp).toLocaleTimeString();
    meta.innerHTML = `<span>${senderName}</span><span>${time}</span>`;

    const body = document.createElement('div');
    body.className = "text-sm leading-relaxed whitespace-pre-wrap font-mono";
    
    if (isImage) {
        const img = document.createElement('img');
        img.src = content;
        img.className = "mt-2 border border-amber-400/30 glow-border max-w-full";
        body.appendChild(img);
    } else {
        body.textContent = content;
    }

    bubble.appendChild(meta);
    bubble.appendChild(body);
    div.appendChild(bubble);
    messagesContainer.appendChild(div);
}

loadHistory();

// ... (ClawHub Search)

// Forge Logic
heatBtn.addEventListener('click', async () => {
    const desc = forgeDesc.value.trim();
    if (!desc) return;

    heatBtn.disabled = true;
    forgeStatus.classList.remove('hidden');
    forgeOutput.classList.add('hidden');
    
    // ... (Steps Interval)
    const steps = ["IGNITING...", "HEATING CORE...", "SHAPING LOGIC...", "TEMPERING..."];
    let p = 0;
    const interval = setInterval(() => {
        forgeStep.textContent = steps[Math.floor(p/25)] || "FINALIZING...";
        forgeProgress.style.width = `${p}%`;
        p += 2;
        if (p > 100) clearInterval(interval);
    }, 50);

    try {
        const res = await fetch('/forge-skill', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ 
                description: desc,
                lobster_mode: lobsterMode.checked
            })
        });
        // ... (Rest of logic)
        const data = await res.json();
        
        clearInterval(interval);
        forgeProgress.style.width = '100%';
        
        if (data.manifest) {
            forgedManifest = data.manifest;
            forgeCode.textContent = data.manifest;
            forgeStatus.classList.add('hidden');
            forgeOutput.classList.remove('hidden');
        } else {
            addMessage(`// FORGE ERROR: ${data.error}`, 'system');
        }
    } catch (e) {
        addMessage("// FORGE CONNECTION FAILED", 'system');
    } finally {
        heatBtn.disabled = false;
    }
});

quenchBtn.addEventListener('click', async () => {
    const nameMatch = forgedManifest.match(/# (.*)/);
    const name = nameMatch ? nameMatch[1] : 'forged-skill';
    
    try {
        const res = await fetch('/quench-skill', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ name, manifest: forgedManifest })
        });
        const data = await res.json();
        if (data.status === 'SUCCESS') {
            addMessage(`// SKILL QUENCHED: ${data.slug.toUpperCase()} SAVED TO DISK`, 'system');
            forgeSidebar.classList.add('w-0');
            forgeSidebar.classList.remove('w-96');
        }
    } catch (e) { alert("Quench Failed"); }
});

// Load Personas
async function loadPersonas() {
    try {
        const res = await fetch('/personas');
        const personas = await res.json();
        
        personaSelect.innerHTML = '';
        Object.entries(personas).forEach(([key, data]) => {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = `MODULE: ${data.name.toUpperCase()}`;
            if (key === 'coda') option.selected = true;
            personaSelect.appendChild(option);
        });
    } catch (e) {
        console.error("Failed to load personas", e);
        personaSelect.innerHTML = '<option>ERROR: OFFLINE</option>';
    }
}

personaSelect.addEventListener('change', () => {
     const name = personaSelect.options[personaSelect.selectedIndex].text;
     addMessage(`// SYSTEM RELOAD: ${name} ACTIVE`, 'system');
});

loadPersonas();

function addMessage(content, type, isImage = false) {
    const div = document.createElement('div');
    
    if (type === 'system') {
        div.className = "text-center py-2 opacity-50 text-xs text-amber-400/70 tracking-widest message-anim border-t border-b border-amber-400/10 my-4";
        div.textContent = content;
        messagesContainer.appendChild(div);
        scrollToBottom();
        return;
    }

    div.className = `flex ${type === 'user' ? 'justify-end' : 'justify-start'} message-anim`;
    
    const bubble = document.createElement('div');
    bubble.className = `max-w-[70%] p-4 border ${
        type === 'user' 
            ? 'border-amber-400 bg-amber-400/10 text-amber-50 shadow-[0_0_15px_rgba(255,191,0,0.1)]' 
            : 'border-gray-700 bg-gray-900 text-gray-300'
    }`;
    
    const meta = document.createElement('div');
    meta.className = "text-[10px] tracking-widest opacity-50 mb-1 flex justify-between gap-4";
    
    let sender = 'UNKNOWN';
    if (type === 'user') sender = 'OPERATOR';
    else if (type === 'bot') {
         const selectedOpt = personaSelect.options[personaSelect.selectedIndex];
         sender = selectedOpt ? selectedOpt.text.replace('MODULE: ', '') : 'CORE';
    }

    meta.innerHTML = `<span>${sender}</span><span>${new Date().toLocaleTimeString()}</span>`;

    const body = document.createElement('div');
    body.className = "text-sm leading-relaxed whitespace-pre-wrap font-mono";
    
    if (isImage) {
        const img = document.createElement('img');
        img.src = content;
        img.className = "mt-2 border border-amber-400/30 glow-border max-w-full";
        body.appendChild(img);
    } else {
        body.textContent = content;
    }

    bubble.appendChild(meta);
    bubble.appendChild(body);
    div.appendChild(bubble);
    
    messagesContainer.appendChild(div);
    scrollToBottom();
}

function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function handleTTS(text) {
    if (!voiceEnabled) return;
    try {
        const res = await fetch('/tts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        if (data.audio_url) {
            const audio = new Audio(data.audio_url);
            audio.play();
        }
    } catch (e) { console.error("TTS Error", e); }
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const message = messageInput.value.trim();
    if (!message) return;

    addMessage(message, 'user');
    messageInput.value = '';
    messageInput.disabled = true;
    sendBtn.disabled = true;

    const selectedPersona = personaSelect.value;

    try {
        const response = await fetch('/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, persona: selectedPersona })
        });
        const data = await response.json();
        if (response.ok) {
            addMessage(data.response, 'bot');
            handleTTS(data.response);
        } else {
            addMessage(`// ERROR: ${data.error}`, 'bot');
        }
    } catch (error) {
        addMessage(`// CONNECTION FAILURE: ${error.message}`, 'bot');
    } finally {
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
});

imgBtn.addEventListener('click', async () => {
    const prompt = messageInput.value.trim();
    if (!prompt) {
        addMessage("// ERROR: ENTER PROMPT FOR IMAGE SYNTHESIS", "system");
        return;
    }

    addMessage(`INITIATING IMAGE SYNTHESIS: ${prompt}`, 'user');
    messageInput.value = '';
    messageInput.disabled = true;
    sendBtn.disabled = true;

    try {
        const response = await fetch('/generate-image', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });
        const data = await response.json();
        if (response.ok) {
            addMessage(data.image_url, 'bot', true);
        } else {
            addMessage(`// ERROR: ${data.error}`, 'bot');
        }
    } catch (error) {
        addMessage(`// CONNECTION FAILURE: ${error.message}`, 'bot');
    } finally {
        messageInput.disabled = false;
        sendBtn.disabled = false;
        messageInput.focus();
    }
});
