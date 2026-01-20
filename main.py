import os
import sys
import uvicorn
import time
import gc
import torch
import soundfile as sf
from fastapi import FastAPI, Form, Response

# 🔥 HARD PRINTING
print("\n" + "="*60)
print("🚀 PROJECT C: F5-TTS STABLE ENGINE STARTING...")
print(f"🔧 Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
print("="*60 + "\n")

# Load F5-TTS
try:
    from f5_tts.api import F5TTS
    # ✅ Fixed: No arguments needed for updated library, enables auto-detection
    f5tts = F5TTS() 
    print("✅ Model Loaded Successfully!")
except Exception as e:
    print(f"❌ Critical Error: {e}")
    sys.exit(1)

app = FastAPI()
DEFAULT_VOICE = "voice_1.wav"

# 👇👇👇 YAHAN APNI TEXT LIKHNA (Speed 2x Hojaye gi) 👇👇👇
# Agar apko pata hai Fatima ne kya bola tha, to yahan likh den.
# Agar nahi pata, to isay Khali chor den (""), wo khud detect karega (magar slow hoga).
KNOWN_TEXTS = {
    "voice_ft.wav": "meri block list me na koi 1200 number thy phir meny WhatsApp ko permanently delete kiya tha phir dobara bnaya tha mujy kuch ho raha tha inko daikh kr",  # Example: "Main theek hun, tum sunao?"
    "voice_kami.wav": "" 
}

@app.post("/speak")
async def speak(text: str = Form(...), speaker: str = Form(DEFAULT_VOICE)):
    start_time = time.time()
    
    target_voice = speaker if os.path.exists(speaker) else DEFAULT_VOICE
    if not os.path.exists(target_voice):
        target_voice = list(KNOWN_TEXTS.keys())[0] if KNOWN_TEXTS else "voice_1.wav"

    print(f"🎙️ [REQUEST] Text: {text[:30]}... | Speaker: {target_voice}")

    # ✅ Check if we have pre-defined text to skip transcription
    ref_text_value = KNOWN_TEXTS.get(target_voice, "")
    
    if ref_text_value:
        print(f"⚡ Using Known Text (Skipping Whisper): {ref_text_value}")
    else:
        print("🐢 Listening to audio to extract emotion (Whisper)...")

    output_path = f"out_{os.urandom(4).hex()}.wav"

    try:
        # 🔥 GENERATION
        wav, sr, _ = f5tts.infer(
            ref_file=target_voice,
            ref_text=ref_text_value, # Agar text hoga to speed tez, nahi to slow
            gen_text=text,
            remove_silence=True,
        )

        sf.write(output_path, wav, sr)
        
        duration = time.time() - start_time
        print(f"✅ Generated in {duration:.2f}s")

        with open(output_path, "rb") as f:
            data = f.read()
        
        if os.path.exists(output_path): os.remove(output_path)
        gc.collect() 
        
        return Response(content=data, media_type="audio/wav")

    except Exception as e:
        print(f"❌ Generation Error: {e}")
        return Response(content=str(e), status_code=500)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))