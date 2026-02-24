"""
Sage TTS Server — Wraps Qwen3-TTS VoiceDesign in a FastAPI endpoint.

Endpoints:
  POST /speak  {"text": "...", "instruct": "..."}  → returns WAV audio
  POST /speak/stream  {"text": "..."}  → returns streaming audio (future)
  GET  /health  → status check

Run:
  python tts-server.py

Requires: qwen-tts, fastapi, uvicorn (all installed with qwen-tts)
"""

import io
import torch
import soundfile as sf
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn
import time

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Sage TTS Server")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════
# Model loading (once at startup)
# ═══════════════════════════════════════
model = None
SAGE_VOICE_INSTRUCT = (
    "A warm, slightly low-pitched androgynous voice. "
    "Playful but grounded, like someone telling you a story by a campfire. "
    "Gentle breathiness when excited. "
    "Natural, expressive cadence with a hint of mischief."
)

def load_model():
    global model
    print("Loading Qwen3-TTS VoiceDesign model...")
    from qwen_tts import Qwen3TTSModel
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    print("Model loaded! Sage has a voice. 🦊")

# ═══════════════════════════════════════
# API models
# ═══════════════════════════════════════
class SpeakRequest(BaseModel):
    text: str
    instruct: Optional[str] = None  # Override voice style (defaults to Sage)
    language: Optional[str] = "English"
    scared: Optional[bool] = False  # Adjust voice for scare moments

class SpeakResponse(BaseModel):
    ok: bool
    duration_ms: float
    text: str

# ═══════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════
@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": model is not None, "voice": "sage"}

@app.post("/speak")
async def speak(req: SpeakRequest):
    if model is None:
        return JSONResponse(status_code=503, content={"error": "Model not loaded yet"})
    
    # Use scared instruct if flagged
    instruct = req.instruct or SAGE_VOICE_INSTRUCT
    if req.scared and not req.instruct:
        instruct = (
            "A warm androgynous voice that is currently panicking. "
            "Slightly higher pitch than normal, words coming faster, "
            "breathless and alarmed but trying to sound calm and failing. "
            "Like someone who just saw something terrifying and is pretending they didn't."
        )
    
    start = time.time()
    
    wavs, sr = model.generate_voice_design(
        text=req.text,
        language=req.language,
        instruct=instruct,
    )
    
    elapsed = (time.time() - start) * 1000
    
    # Convert to WAV in memory
    buf = io.BytesIO()
    sf.write(buf, wavs[0], sr, format="WAV")
    buf.seek(0)
    
    print(f"[SAGE TTS] {elapsed:.0f}ms | {req.text[:60]}{'...' if len(req.text) > 60 else ''}")
    
    return StreamingResponse(
        buf,
        media_type="audio/wav",
        headers={
            "X-Duration-Ms": str(round(elapsed)),
            "X-Scared": str(req.scared).lower(),
        }
    )

@app.post("/speak/json")
async def speak_json(req: SpeakRequest):
    """Same as /speak but saves to file and returns metadata (for overlay integration)."""
    if model is None:
        return JSONResponse(status_code=503, content={"error": "Model not loaded yet"})
    
    instruct = req.instruct or SAGE_VOICE_INSTRUCT
    if req.scared and not req.instruct:
        instruct = (
            "A warm androgynous voice that is currently panicking. "
            "Slightly higher pitch than normal, words coming faster, "
            "breathless and alarmed but trying to sound calm and failing."
        )
    
    start = time.time()
    
    wavs, sr = model.generate_voice_design(
        text=req.text,
        language=req.language,
        instruct=instruct,
    )
    
    elapsed = (time.time() - start) * 1000
    
    # Save to file for audio playback
    outpath = "sage_latest.wav"
    sf.write(outpath, wavs[0], sr)
    
    # Calculate duration
    duration_s = len(wavs[0]) / sr
    
    return {
        "ok": True,
        "duration_ms": round(elapsed),
        "audio_duration_s": round(duration_s, 2),
        "file": outpath,
        "text": req.text,
        "scared": req.scared,
    }

# ═══════════════════════════════════════
# Startup
# ═══════════════════════════════════════
@app.on_event("startup")
async def startup():
    load_model()

if __name__ == "__main__":
    print("Starting Sage TTS Server on port 8082...")
    uvicorn.run(app, host="0.0.0.0", port=8082)
