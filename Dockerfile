FROM python:3.10-slim

# ✅ 1. HARD PRINTING ENVIRONMENT
ENV PYTHONUNBUFFERED=1
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4

# ✅ 2. SYSTEM DEPENDENCIES (FFmpeg & Git are crucial)
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    ffmpeg \
    libsndfile1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ✅ 3. INSTALL PYTHON LIBRARIES
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ✅ 4. PRE-DOWNLOAD F5-TTS MODEL (To avoid timeout on first run)
# ہم ماڈل کو بلڈ ٹائم پر ہی ڈاؤن لوڈ کر رہے ہیں تاکہ رن ٹائم پر انتظار نہ کرنا پڑے
RUN python3 -c "from f5_tts.model import DiT; print('✅ F5-TTS Library Installed Successfully')"

# ✅ 5. COPY FILES
COPY *.wav . 
COPY main.py .

# ✅ 6. START COMMAND
CMD ["python", "main.py"]