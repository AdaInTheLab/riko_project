"""
Sage TTS Server — Uses cached voice clone prompt for fast generation.

Endpoints:
  POST /speak  {"text": "...", "scared": false}  → returns WAV audio
  POST /speak/json  {"text": "..."}  → saves to file, returns metadata
  GET  /health  → status check

Run:
  python tts-server.py

Requires: qwen-tts, fastapi, uvicorn, soundfile
"""

import io
import os
import torch
import pickle
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
voice_clone_prompt = None

VOICE_CACHE_DIR = "voice_cache"
CLONE_PROMPT_PATH = os.path.join(VOICE_CACHE_DIR, "sage_clone_prompt.pkl")

def load_model():
    global model, voice_clone_prompt
    
    # Load cached clone prompt
    if not os.path.exists(CLONE_PROMPT_PATH):
        print("ERROR: No cached voice clone prompt found!")
        print("Run setup-sage-voice.py first to generate it.")
        return
    
    print("Loading cached voice clone prompt...")
    with open(CLONE_PROMPT_PATH, "rb") as f:
        voice_clone_prompt = pickle.load(f)
    print("  ✓ Clone prompt loaded")
    
    # Load the 1.7B Base model (NOT VoiceDesign — faster with cached prompt)
    print("Loading Qwen3-TTS 1.7B Base model...")
    from qwen_tts import Qwen3TTSModel
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    
    # Warmup generation
    print("Warming up...")
    start = time.time()
    wavs, sr = model.generate_voice_clone(
        text="Hello world, Sage is online.",
        language="English",
        voice_clone_prompt=voice_clone_prompt,
    )
    elapsed = (time.time() - start) * 1000
    print(f"  ✓ Warmup: {elapsed:.0f}ms")
    print("Sage has a voice. 🦊")

# ═══════════════════════════════════════
# API models
# ═══════════════════════════════════════
class SpeakRequest(BaseModel):
    text: str
    language: Optional[str] = "English"
    scared: Optional[bool] = False

# ═══════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "model_loaded": model is not None,
        "voice": "sage-clone",
        "mode": "cached_prompt",
    }

@app.post("/speak")
async def speak(req: SpeakRequest):
    if model is None or voice_clone_prompt is None:
        return JSONResponse(status_code=503, content={"error": "Model not loaded yet"})
    
    start = time.time()
    
    wavs, sr = model.generate_voice_clone(
        text=req.text,
        language=req.language,
        voice_clone_prompt=voice_clone_prompt,
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
    """Same as /speak but saves to file and returns metadata."""
    if model is None or voice_clone_prompt is None:
        return JSONResponse(status_code=503, content={"error": "Model not loaded yet"})
    
    start = time.time()
    
    wavs, sr = model.generate_voice_clone(
        text=req.text,
        language=req.language,
        voice_clone_prompt=voice_clone_prompt,
    )
    
    elapsed = (time.time() - start) * 1000
    
    outpath = "sage_latest.wav"
    sf.write(outpath, wavs[0], sr)
    
    duration_s = len(wavs[0]) / sr
    
    print(f"[SAGE TTS] {elapsed:.0f}ms | {duration_s:.1f}s audio | {req.text[:60]}")
    
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
