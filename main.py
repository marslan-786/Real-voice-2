import os
import sys
import uvicorn
import time
import gc
import torch
import soundfile as sf
from fastapi import FastAPI, Form, Response

# 🔥 HARD PRINTING: STARTUP DIAGNOSTICS
print("\n" + "="*60)
print("🚀 PROJECT C: F5-TTS REALISM ENGINE STARTING...")
print("="*60)

# 1. System Info
print(f"🐍 Python Version: {sys.version.split()[0]}")
print(f"📂 Current Directory: {os.getcwd()}")

# 2. Check GPU/CPU
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"🔧 Hardware Device: {device.upper()}")
if device == "cpu":
    print("⚠️ WARNING: Running on CPU. F5-TTS will be slow (2-5 mins per audio).")
    print("   If possible, use a GPU server for <10s generation.")

# 3. Check Voices
print("-" * 20)
print("🎙️ CHECKING VOICE SAMPLES:")
voice_files = [f for f in os.listdir('.') if f.endswith('.wav')]
if not voice_files:
    print("❌ CRITICAL ERROR: No .wav files found! Upload 'voice_1.wav', etc.")
else:
    for v in voice_files:
        print(f"   ✅ Found: {v}")
print("-" * 20)

# 4. Import F5-TTS (Might take time)
print("⏳ Importing F5-TTS Libraries (This might take a moment)...")
try:
    from f5_tts.api import F5TTS
    print("✅ F5-TTS Library Imported Successfully!")
except Exception as e:
    print(f"❌ ERROR Importing F5-TTS: {e}")
    sys.exit(1)

# 5. Load Model
print("⏳ Loading F5-TTS Model into RAM...")
try:
    # Load the model (HuggingFace se auto download karega)
    f5tts = F5TTS(model_type="F5-TTS", device=device)
    print("✅ Model Loaded & Ready to Speak!")
except Exception as e:
    print(f"❌ Model Load Failed: {e}")
    sys.exit(1)

print("="*60 + "\n")

# 🔥 SERVER SETUP
app = FastAPI()
DEFAULT_VOICE = "voice_1.wav"

@app.get("/")
def home():
    return {
        "status": "alive", 
        "engine": "F5-TTS (Project C)", 
        "device": device,
        "loaded_voices": voice_files
    }

@app.post("/speak")
async def speak(text: str = Form(...), speaker: str = Form(DEFAULT_VOICE)):
    start_time = time.time()
    
    # Check voice existence
    target_voice = speaker if os.path.exists(speaker) else DEFAULT_VOICE
    if not os.path.exists(target_voice):
        # Agar default bhi nahi mila to pehli wav file utha lo
        target_voice = voice_files[0] if voice_files else None
    
    if not target_voice:
        return Response(content="Server has no voice files!", status_code=500)

    print(f"🎙️ [REQUEST] Text: {text[:30]}... | Speaker: {target_voice}")

    output_path = f"out_{os.urandom(4).hex()}.wav"

    try:
        # 🔥 F5-TTS GENERATION
        # This is where the magic happens. 
        # It copies the emotion from 'target_voice' and applies it to 'text'
        wav, sr, _ = f5tts.infer(
            ref_file=target_voice,
            ref_text="", # Blank rakhein taakay wo sirf tone copy kare
            gen_text=text,
            remove_silence=True,
        )

        # Save to file
        sf.write(output_path, wav, sr)
        
        duration = time.time() - start_time
        print(f"✅ Generated in {duration:.2f}s")

        with open(output_path, "rb") as f:
            data = f.read()
        
        # Cleanup
        if os.path.exists(output_path): os.remove(output_path)
        gc.collect() # RAM Safai
        
        return Response(content=data, media_type="audio/wav")

    except Exception as e:
        print(f"❌ Generation Error: {e}")
        return Response(content=str(e), status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))