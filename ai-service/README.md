# DeepShield AI Service - Setup Guide

## Overview

The AI Service is a Python FastAPI application that implements real deep learning models for facial protection against deepfakes.

## Architecture

```
ai-service/
├── main.py                  # FastAPI application
├── config.py                # Configuration
├── requirements.txt         # Python dependencies
├── models/
│   └── arcface_model.py     # ArcFace identity embedding
├── protection/
│   ├── deepshield.py        # DeepShield implementation
│   └── baselines.py         # PhotoGuard, AdvDM, Mist
├── utils/
│   ├── face_utils.py        # Face detection & alignment
│   └── metrics.py           # PSNR, SSIM, LPIPS, etc.
├── models/                  # Downloaded pretrained models
├── temp/                    # Temporary files
└── outputs/                 # Generated results
```

## Requirements

### System Requirements
- **GPU**: NVIDIA GPU with CUDA support (highly recommended)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB for models and dependencies
- **OS**: Linux (Ubuntu 20.04+), Windows 10/11, macOS

### Software Requirements
- Python 3.8 - 3.11
- CUDA 11.7+ (for GPU support)
- cuDNN 8.x

## Installation

### Step 1: Create Virtual Environment

```bash
cd ai-service

# Create virtual environment
python -m venv venv

# Activate
# Linux/Mac:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

### Step 2: Install PyTorch

**With CUDA (GPU - Recommended):**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**CPU Only:**
```bash
pip install torch torchvision torchaudio
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (API server)
- InsightFace (face detection & recognition)
- LPIPS (perceptual metrics)
- OpenCV (image processing)
- And more...

### Step 4: Download Pretrained Models

InsightFace models will be automatically downloaded on first run.

The models (~500MB) will be cached in:
- Linux: `~/.insightface/`
- Windows: `C:\Users\<username>\.insightface\`

## Running the AI Service

### Development Mode

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The service will run on: **http://localhost:8000**

### Production Mode

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
```

## API Endpoints

### 1. Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "ok",
  "device": "cuda",
  "cuda_available": true
}
```

### 2. Protect Image

```bash
POST /protect
```

Form Data:
- `file`: Image file (JPG, PNG)
- `method`: Protection method (deepshield | photoguard | advdm | mist)

Example using cURL:

```bash
curl -X POST http://localhost:8000/protect \
  -F "file=@face.jpg" \
  -F "method=deepshield"
```

Response:
```json
{
  "success": true,
  "method": "deepshield",
  "output_id": "uuid",
  "files": {
    "original": "path/to/original.png",
    "protected": "path/to/protected.png",
    "perturbation": "path/to/perturbation.png"
  },
  "metrics": {
    "psnr": 38.29,
    "ssim": 0.9867,
    "lpips": 0.0114,
    "identity_similarity": 0.0921,
    "l2_distance": 0.0051,
    "frequency_rate": 20.96
  }
}
```

### 3. Compare All Methods

```bash
POST /compare
```

Form Data:
- `file`: Image file

Example:

```bash
curl -X POST http://localhost:8000/compare \
  -F "file=@face.jpg"
```

Response:
```json
{
  "success": true,
  "output_id": "uuid",
  "comparison_grid": "path/to/comparison.png",
  "methods": {
    "deepshield": {
      "metrics": {...},
      "files": {...}
    },
    "photoguard": {...},
    "advdm": {...},
    "mist": {...}
  }
}
```

## Configuration

Edit `config.py` to customize:

### DeepShield Parameters

```python
DEEPSHIELD_CONFIG = {
    "epsilon": 8/255,          # Perturbation budget
    "num_steps": 250,          # Optimization steps
    "step_size": 0.008,        # Learning rate
    "mdiv": 0.5,              # Anti-anchor divergence margin
    "mmut": 0.3,              # Mutual separation margin
    "lambda_div": 1.0,        # Divergence loss weight
    "lambda_mut": 0.5,        # Mutual loss weight
    "lambda_lpips": 0.1,      # Perceptual loss weight
}
```

### GPU/CPU Selection

```python
DEVICE = "cuda"  # or "cpu"
```

## Testing

### Test with Python

```python
import requests

url = "http://localhost:8000/protect"

with open("test_face.jpg", "rb") as f:
    files = {"file": f}
    data = {"method": "deepshield"}
    response = requests.post(url, files=files, data=data)
    
print(response.json())
```

### Test with cURL

```bash
# Test health
curl http://localhost:8000/health

# Test protection
curl -X POST http://localhost:8000/protect \
  -F "file=@test.jpg" \
  -F "method=deepshield"
```

## Performance

### Processing Time (NVIDIA RTX 3090)

- Face Detection: ~50ms
- DeepShield Protection: ~15-20 seconds
- PhotoGuard: ~8-10 seconds
- AdvDM: ~12-15 seconds
- Mist: ~15-18 seconds

### GPU Memory Usage

- Face Detection: ~500MB
- Protection (single image): ~2-3GB
- Batch processing: ~4-6GB

## Troubleshooting

### CUDA Out of Memory

Reduce batch size or image size in `config.py`:

```python
IMAGE_SIZE = 256  # Reduce from 512
```

### InsightFace Installation Fails

```bash
pip install onnxruntime-gpu  # For GPU
pip install onnxruntime  # For CPU only
```

### Slow Processing

- Ensure CUDA is properly installed
- Check GPU usage: `nvidia-smi`
- Reduce `num_steps` in config for faster processing

### Model Download Fails

Manually download models:

```bash
python -c "from insightface.app import FaceAnalysis; app = FaceAnalysis(name='buffalo_l'); app.prepare(ctx_id=0)"
```

## Production Deployment

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM pytorch/pytorch:2.0.0-cuda11.7-cudnn8-runtime

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t deepshield-ai .
docker run -p 8000:8000 --gpus all deepshield-ai
```

### Using Gunicorn

```bash
pip install gunicorn

gunicorn main:app \
  --workers 2 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

## Metrics Explained

### Visual Quality
- **PSNR**: 35-45 dB is excellent (imperceptible)
- **SSIM**: > 0.95 is very good
- **LPIPS**: < 0.05 is imperceptible

### Protection Effectiveness
- **Identity Similarity**: < 0.2 means strong protection
- **L2 Distance**: Higher means more disruption
- **Frequency Rate**: Higher means noise in imperceptible frequencies

## Next Steps

1. Integrate with Node.js backend
2. Update frontend to call AI service
3. Add batch processing support
4. Implement caching for faster responses

## Support

For issues or questions:
- Check logs: `uvicorn.log`
- GPU status: `nvidia-smi`
- Python errors: Check console output