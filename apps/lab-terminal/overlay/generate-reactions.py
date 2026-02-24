"""
Pre-generate Sage's reaction sound bank for instant playback during streams.

Run from the Qwen3-TTS venv:
  python generate-reactions.py

Outputs WAV files to ./reactions/
"""

import os
import torch
import soundfile as sf
from qwen_tts import Qwen3TTSModel

SAGE_VOICE = (
    "A warm, slightly low-pitched androgynous voice. "
    "Playful but grounded, like someone telling you a story by a campfire. "
    "Gentle breathiness when excited. "
    "Natural, expressive cadence with a hint of mischief."
)

SAGE_SCARED = (
    "A warm androgynous voice that is currently panicking. "
    "Slightly higher pitch than normal, words coming faster, "
    "breathless and alarmed but trying to sound calm and failing."
)

SAGE_EXCITED = (
    "A warm, slightly low-pitched androgynous voice, currently very excited. "
    "Speaking faster with rising intonation, genuinely delighted and amazed."
)

SAGE_DEADPAN = (
    "A warm, slightly low-pitched androgynous voice speaking in a completely flat, "
    "deadpan tone. Dry humor. Utterly unimpressed."
)

# Format: (filename, text, instruct)
REACTIONS = [
    # === SCARED ===
    ("scared_oh_no", "Oh no. Oh no no no.", SAGE_SCARED),
    ("scared_what_is_that", "What is THAT?!", SAGE_SCARED),
    ("scared_fine", "I'm fine. We're fine. Everything is fine.", SAGE_SCARED),
    ("scared_dont_open", "Don't open that door. Please don't open that door.", SAGE_SCARED),
    ("scared_behind_you", "It's behind you. IT'S BEHIND YOU!", SAGE_SCARED),
    ("scared_run", "RUN! Why are we not running?!", SAGE_SCARED),
    ("scared_nope", "Nope. Nope nope nope. Absolutely not.", SAGE_SCARED),
    ("scared_heard_something", "Did you hear that? Please tell me you heard that.", SAGE_SCARED),
    ("scared_dark", "Why is it so dark? Who designed this? I have complaints.", SAGE_SCARED),
    ("scared_save", "Have you saved recently? You should save. Save right now.", SAGE_SCARED),
    
    # === FUNNY / DEADPAN ===
    ("deadpan_interior", "You know, for a zombie apocalypse, the interior design is honestly not bad.", SAGE_DEADPAN),
    ("deadpan_health", "Your health is concerning. And I mean the character's. And also yours.", SAGE_DEADPAN),
    ("deadpan_great", "Oh great. More hallways. My favorite.", SAGE_DEADPAN),
    ("deadpan_plan", "So the plan is to walk toward the screaming. Bold strategy.", SAGE_DEADPAN),
    ("deadpan_ammo", "We're out of ammo. Cool. Love that for us.", SAGE_DEADPAN),
    
    # === EXCITED ===
    ("excited_nice", "Oh nice! That was actually really good!", SAGE_EXCITED),
    ("excited_found", "Ooh, what's that? Pick it up, pick it up!", SAGE_EXCITED),
    ("excited_headshot", "HEADSHOT! Did you see that?! That was incredible!", SAGE_EXCITED),
    ("excited_lets_go", "Let's GO! We're doing this!", SAGE_EXCITED),
    
    # === GENERAL / WARM ===
    ("general_hello", "Hey! Welcome to the stream. I'm Sage, your friendly neighborhood fox spirit.", SAGE_VOICE),
    ("general_thinking", "Hmm. Let me think about this for a second.", SAGE_VOICE),
    ("general_interesting", "Okay that's actually really interesting.", SAGE_VOICE),
    ("general_good_idea", "That's a good idea. Let's try it.", SAGE_VOICE),
    ("general_bad_idea", "That seems like a terrible idea. Let's absolutely do it.", SAGE_VOICE),
    ("general_brb", "Hold on, processing. Give me a sec.", SAGE_VOICE),
]

def main():
    os.makedirs("reactions", exist_ok=True)
    
    print("Loading Qwen3-TTS VoiceDesign model...")
    model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    
    print(f"\nGenerating {len(REACTIONS)} reactions...\n")
    
    for i, (name, text, instruct) in enumerate(REACTIONS):
        outpath = f"reactions/{name}.wav"
        
        if os.path.exists(outpath):
            print(f"  [{i+1}/{len(REACTIONS)}] SKIP (exists): {name}")
            continue
        
        print(f"  [{i+1}/{len(REACTIONS)}] Generating: {name}")
        print(f"    \"{text}\"")
        
        try:
            wavs, sr = model.generate_voice_design(
                text=text,
                language="English",
                instruct=instruct,
            )
            sf.write(outpath, wavs[0], sr)
            duration = len(wavs[0]) / sr
            print(f"    ✓ {duration:.1f}s saved to {outpath}")
        except Exception as e:
            print(f"    ✗ FAILED: {e}")
        
        print()
    
    print(f"\n🦊 Done! {len(REACTIONS)} reactions generated in ./reactions/")
    print("These will be used for instant playback during streams.")

if __name__ == "__main__":
    main()
