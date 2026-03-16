import os
from pathlib import Path

# Directories
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
TEMP_DIR = BASE_DIR / "temp"
OUTPUT_DIR = BASE_DIR / "outputs"

# Create directories
MODELS_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# API Configuration
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))

# Model Configuration
DEVICE = "cuda"  # Will auto-detect in code
FACE_DETECTION_MODEL = "retinaface"  # or "mtcnn"
IDENTITY_MODEL = "arcface"  # InsightFace ArcFace

# DeepShield Parameters
DEEPSHIELD_CONFIG = {
    "epsilon": 8/255,  # Base perturbation budget (L_inf)
    "num_steps": 250,  # Optimization steps
    "step_size": 0.008,  # Learning rate
    "mdiv": 0.5,  # Anti-anchor divergence margin
    "mmut": 0.3,  # Mutual separation margin
    "lambda_div": 1.0,  # Divergence loss weight
    "lambda_mut": 0.5,  # Mutual loss weight
    "lambda_lpips": 0.1,  # Perceptual loss weight
    "timesteps": [50, 100, 150, 200],  # Diffusion timesteps
    "identity_weight_eyes": 1.0,
    "identity_weight_nose": 0.9,
    "identity_weight_mouth": 0.85,
    "identity_weight_skin": 0.4,
}

# Baseline Method Parameters
PHOTOGUARD_CONFIG = {
    "epsilon": 16/255,
    "num_steps": 100,
    "step_size": 0.01,
}

ADVDM_CONFIG = {
    "epsilon": 8/255,
    "num_steps": 150,
    "step_size": 0.008,
}

MIST_CONFIG = {
    "epsilon": 8/255,
    "num_steps": 200,
    "step_size": 0.01,
}

# Image Configuration
IMAGE_SIZE = 512
FACE_SIZE = 112  # For ArcFace embedding

# Metrics Configuration
LPIPS_NET = "vgg"  # Options: vgg, alex, squeeze