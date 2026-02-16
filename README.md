# RL-TTS Service

Text-to-Speech service using Coqui TTS with GPU acceleration for the ResilientLink Edge platform.

## Features

- **Multilingual Support**: Supports multiple languages (English, Spanish, French, German, Italian, Portuguese, Polish, Turkish, Russian, Dutch, Czech, Arabic, Chinese, Japanese, Hungarian, Korean)
- **GPU Acceleration**: Leverages NVIDIA GPU for fast inference
- **PCM 16-bit Audio**: Generates PCM 16-bit audio at 8kHz sample rate
- **REST API**: FastAPI-based REST API for easy integration
- **Kubernetes Ready**: Includes deployment manifests for K8s with GPU support

## API Endpoints

### POST /synthesize
Synthesize speech from text.

**Request:**
```json
{
  "text": "Hello, this is a test.",
  "language": "en"
}
```

**Response:**
```json
{
  "audio_data": [bytes],
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

## Local Development

### Prerequisites
- Python 3.10+
- CUDA-capable GPU (optional, will fall back to CPU)

### Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running Locally

```bash
python main.py
```

The service will start on `http://localhost:8080`

### Testing

```bash
# Health check
python test_client.py --health

# Synthesize speech
python test_client.py --text "Hello, this is a test" --language en

# Test with different language
python test_client.py --text "Hola, esto es una prueba" --language es
```

## Kubernetes Deployment

### Prerequisites
- Kubernetes cluster with GPU support
- NVIDIA GPU operator installed
- Docker registry access (yeager1977/rl-tts)
- `ai-models-pvc` PersistentVolumeClaim for model storage

### Deploy

```bash
# Build and push Docker image
docker build -t yeager1977/rl-tts:latest .
docker push yeager1977/rl-tts:latest

# Deploy to Kubernetes
kubectl apply -f k8s/rl-tts.yaml

# Check deployment status
kubectl get pods -n rl-edge -l app=rl-tts
kubectl logs -n rl-edge -l app=rl-tts
```

Or use the deployment script:

```bash
./deploy.sh
```

### Service Access

Within the cluster:
```
http://rl-tts.rl-edge.svc.cluster.local:8080
```

### Testing in Kubernetes

```bash
# Port forward to test locally
kubectl port-forward -n rl-edge svc/rl-tts 8080:8080

# Test with curl
curl -X POST http://localhost:8080/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello from Kubernetes", "language": "en"}' \
  --output test.raw

# Play the audio
ffplay -f s16le -ar 8000 -ac 1 test.raw
```

## Supported Languages

- `en` - English
- `es` - Spanish
- `fr` - French
- `de` - German
- `it` - Italian
- `pt` - Portuguese
- `pl` - Polish
- `tr` - Turkish
- `ru` - Russian
- `nl` - Dutch
- `cs` - Czech
- `ar` - Arabic
- `zh-cn` - Chinese
- `ja` - Japanese
- `hu` - Hungarian
- `ko` - Korean

## Configuration

### Environment Variables

- `TTS_HOME`: Directory for model cache (default: `/app/models`)
- `NVIDIA_VISIBLE_DEVICES`: GPU device ID
- `CUDA_VISIBLE_DEVICES`: CUDA device selection

### GPU Configuration

The service requires 1 GPU. Update the deployment YAML to match your GPU device ID:

```yaml
env:
- name: NVIDIA_VISIBLE_DEVICES
  value: "GPU-<your-gpu-id>"
```

Get your GPU ID:
```bash
nvidia-smi -L
```

## Architecture

- **Framework**: FastAPI
- **TTS Engine**: Coqui TTS (XTTS v2)
- **Audio Format**: PCM 16-bit, 8kHz, mono
- **Resampling**: Linear interpolation from 24kHz to 8kHz
- **GPU Support**: CUDA via PyTorch

## License

MIT License

