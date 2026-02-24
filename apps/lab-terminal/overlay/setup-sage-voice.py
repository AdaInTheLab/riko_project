"""
Setup Sage's Voice — One-time voice design + clone prompt creation

This script:
1. Uses VoiceDesign (1.7B) to generate a reference clip of Sage's voice
2. Creates a reusable voice_clone_prompt from that reference
3. Saves the prompt so the TTS server can use the faster Base model

Run once, then the TTS server uses the cached prompt for fast generation.

Usage:
  python setup-sage-voice.py
"""

import torch
import soundfile as sf
import pickle
import os
from qwen_tts import Qwen3TTSModel

SAGE_VOICE_INSTRUCT = (
    "A warm, slightly low-pitched androgynous voice. "
    "Playful but grounded, like someone telling you a story by a campfire. "
    "Gentle breathiness when excited. "
    "Natural, expressive cadence with a hint of mischief."
)

REFERENCE_TEXT = (
    "Oh no, oh no no no. What is that in the hallway? "
    "I'm fine. We're fine. Everything is fine. "
    "Okay that's actually really interesting. Let me think about this."
)

OUTPUT_DIR = "voice_cache"

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Step 1: Design the voice
    print("Step 1: Designing Sage's voice with VoiceDesign model...")
    design_model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign",
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    
    ref_wavs, sr = design_model.generate_voice_design(
        text=REFERENCE_TEXT,
        language="English",
        instruct=SAGE_VOICE_INSTRUCT,
    )
    
    ref_path = os.path.join(OUTPUT_DIR, "sage_reference.wav")
    sf.write(ref_path, ref_wavs[0], sr)
    print(f"  ✓ Reference clip saved: {ref_path} ({len(ref_wavs[0])/sr:.1f}s)")
    
    # Free VoiceDesign model memory
    del design_model
    torch.cuda.empty_cache()
    
    # Step 2: Build clone prompt using Base model
    print("\nStep 2: Building reusable clone prompt with Base model...")
    clone_model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    
    voice_clone_prompt = clone_model.create_voice_clone_prompt(
        ref_audio=(ref_wavs[0], sr),
        ref_text=REFERENCE_TEXT,
    )
    
    # Save the prompt for reuse
    prompt_path = os.path.join(OUTPUT_DIR, "sage_clone_prompt.pkl")
    with open(prompt_path, "wb") as f:
        pickle.dump(voice_clone_prompt, f)
    print(f"  ✓ Clone prompt saved: {prompt_path}")
    
    # Step 3: Test it
    print("\nStep 3: Testing clone generation speed...")
    import time
    
    test_text = "Two idiots, one fog town. This is the content the people need."
    
    start = time.time()
    wavs, sr = clone_model.generate_voice_clone(
        text=test_text,
        language="English",
        voice_clone_prompt=voice_clone_prompt,
    )
    elapsed = (time.time() - start) * 1000
    duration = len(wavs[0]) / sr
    
    test_path = os.path.join(OUTPUT_DIR, "sage_clone_test.wav")
    sf.write(test_path, wavs[0], sr)
    
    print(f"  ✓ Test clip: {test_path} ({duration:.1f}s audio)")
    print(f"  ✓ Generation time: {elapsed:.0f}ms")
    print(f"  ✓ Speedup vs VoiceDesign: ~{8000/max(elapsed,1):.1f}x faster")
    
    # Also test with 0.6B for comparison
    del clone_model
    torch.cuda.empty_cache()
    
    print("\nStep 4: Testing 0.6B Base model speed...")
    small_model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-0.6B-Base",
        device_map="cuda:0",
        dtype=torch.bfloat16,
    )
    
    # Rebuild prompt for 0.6B
    voice_clone_prompt_small = small_model.create_voice_clone_prompt(
        ref_audio=(ref_wavs[0], sr),
        ref_text=REFERENCE_TEXT,
    )
    
    prompt_path_small = os.path.join(OUTPUT_DIR, "sage_clone_prompt_0.6B.pkl")
    with open(prompt_path_small, "wb") as f:
        pickle.dump(voice_clone_prompt_small, f)
    
    start = time.time()
    wavs_small, sr = small_model.generate_voice_clone(
        text=test_text,
        language="English",
        voice_clone_prompt=voice_clone_prompt_small,
    )
    elapsed_small = (time.time() - start) * 1000
    duration_small = len(wavs_small[0]) / sr
    
    test_path_small = os.path.join(OUTPUT_DIR, "sage_clone_test_0.6B.wav")
    sf.write(test_path_small, wavs_small[0], sr)
    
    print(f"  ✓ 0.6B Test clip: {test_path_small} ({duration_small:.1f}s audio)")
    print(f"  ✓ 0.6B Generation time: {elapsed_small:.0f}ms")
    
    print(f"""
  🦊 SAGE VOICE SETUP COMPLETE
  ════════════════════════════
  Reference clip:     {ref_path}
  1.7B Clone prompt:  {prompt_path}
  0.6B Clone prompt:  {prompt_path_small}
  
  1.7B speed: {elapsed:.0f}ms for {duration:.1f}s audio
  0.6B speed: {elapsed_small:.0f}ms for {duration_small:.1f}s audio
  
  Pick the fastest one that sounds good!
  Listen to both test clips and decide.
  ════════════════════════════
    """)

if __name__ == "__main__":
    main()
