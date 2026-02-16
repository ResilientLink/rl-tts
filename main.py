import os
import io
import wave
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from TTS.api import TTS
import torch
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RL-TTS Service", version="1.0.0")

# Global TTS model
tts_model = None


class TTSRequest(BaseModel):
    text: str
    language: str = "en"


class TTSResponse(BaseModel):
    audio_data: bytes
    sample_rate: int = 8000
    format: str = "pcm16"


def initialize_tts():
    """Initialize the TTS model"""
    global tts_model
    try:
        # Check if GPU is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"Initializing TTS model on {device}")

        # Use a multilingual model that supports various languages
        # Using XTTS v2 for multilingual support
        tts_model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(device)
        logger.info("TTS model initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize TTS model: {e}")
        raise


@app.on_event("startup")
async def startup_event():
    """Initialize TTS model on startup"""
    initialize_tts()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": tts_model is not None,
        "gpu_available": torch.cuda.is_available()
    }


@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text
    Returns PCM 16-bit audio at 8kHz
    """
    if tts_model is None:
        raise HTTPException(status_code=503, detail="TTS model not initialized")

    try:
        logger.info(f"Synthesizing text in language '{request.language}': {request.text[:50]}...")

        # Generate audio using TTS
        # XTTS generates at 24kHz by default
        wav = tts_model.tts(text=request.text, language=request.language)

        # Convert to numpy array
        audio_array = np.array(wav)

        # Resample from 24kHz to 8kHz
        audio_8khz = resample_audio(audio_array, 24000, 8000)

        # Convert to PCM 16-bit
        audio_pcm16 = convert_to_pcm16(audio_8khz)

        logger.info(f"Audio generated: {len(audio_pcm16)} bytes")

        return {
            "audio_data": audio_pcm16,
            "sample_rate": 8000,
            "format": "pcm16"
        }

    except Exception as e:
        logger.error(f"Error synthesizing speech: {e}")
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio to target sample rate using linear interpolation"""
    if orig_sr == target_sr:
        return audio

    duration = len(audio) / orig_sr
    target_length = int(duration * target_sr)

    # Simple linear interpolation for resampling
    indices = np.linspace(0, len(audio) - 1, target_length)
    resampled = np.interp(indices, np.arange(len(audio)), audio)

    return resampled


def convert_to_pcm16(audio: np.ndarray) -> bytes:
    """Convert float audio array to PCM 16-bit bytes"""
    # Normalize to [-1, 1] if needed
    if audio.max() > 1.0 or audio.min() < -1.0:
        audio = audio / np.max(np.abs(audio))

    # Convert to 16-bit integer
    audio_int16 = (audio * 32767).astype(np.int16)

    # Convert to bytes
    return audio_int16.tobytes()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RL-TTS",
        "version": "1.0.0",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
