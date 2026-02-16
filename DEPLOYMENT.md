# RL-TTS Deployment Guide

## Quick Start

The RL-TTS service is a text-to-speech API that generates PCM 16-bit audio at 8kHz using Coqui TTS with GPU acceleration.

### Build and Deploy

```bash
# Build the Docker image
docker build -t yeager1977/rl-tts:latest .

# Push to Docker Hub
docker push yeager1977/rl-tts:latest

# Deploy to Kubernetes (rl-edge namespace)
kubectl apply -f k8s/rl-tts.yaml

# Check deployment status
kubectl get pods -n rl-edge -l app=rl-tts
kubectl logs -n rl-edge -l app=rl-tts -f
```

### Test the Service

```bash
# Port forward to local machine
kubectl port-forward -n rl-edge svc/rl-tts 8080:8080

# Run health check
python test_client.py --health

# Generate speech
python test_client.py --text "Hello, this is a test" --language en

# Test with Spanish
python test_client.py --text "Hola, esto es una prueba" --language es
```

## Service Details

- **Endpoint**: `http://rl-tts.rl-edge.svc.cluster.local:8080`
- **Model**: XTTS v2 (multilingual)
- **Audio Format**: PCM 16-bit, 8kHz, mono
- **GPU**: Requires 1 NVIDIA GPU
- **Namespace**: rl-edge

## API Endpoints

### POST /synthesize
Generate speech from text.

**Request:**
```json
{
  "text": "Text to synthesize",
  "language": "en"
}
```

**Response:**
```json
{
  "audio_data": [binary PCM data],
  "sample_rate": 8000,
  "format": "pcm16"
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "gpu_available": true
}
```

## Supported Languages

- en (English)
- es (Spanish)
- fr (French)
- de (German)
- it (Italian)
- pt (Portuguese)
- pl (Polish)
- tr (Turkish)
- ru (Russian)
- nl (Dutch)
- cs (Czech)
- ar (Arabic)
- zh-cn (Chinese)
- ja (Japanese)
- hu (Hungarian)
- ko (Korean)

## GPU Configuration

The service is configured to use GPU ID: `GPU-91f8dded-a053-fcb2-febc-7bc2c0d5684e`

To check your GPU ID:
```bash
nvidia-smi -L
```

Update the deployment YAML with your GPU ID if different.

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod -n rl-edge -l app=rl-tts
kubectl logs -n rl-edge -l app=rl-tts
```

### Model download issues
The first time the service starts, it needs to download the TTS model (~2GB). This can take several minutes.

### GPU not available
Ensure:
- NVIDIA GPU operator is installed on the cluster
- GPU device ID matches your hardware
- PVC `ai-models-pvc` exists and is writable

## Implementation Notes

- The service uses Coqui TTS XTTS v2 model for multilingual support
- Audio is generated at 24kHz and resampled to 8kHz for telephony compatibility
- Simple linear interpolation is used for resampling
- Model cache is persisted to `/app/models` via PVC

## Future Enhancements

- [ ] Add streaming audio support
- [ ] Implement voice cloning
- [ ] Add caching for frequently requested phrases
- [ ] Support custom speaker embeddings
- [ ] Add audio format conversion options (WAV, MP3, etc.)

