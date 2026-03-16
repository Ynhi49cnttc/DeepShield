"""
FastAPI AI Service for DeepShield
Main API endpoints for image protection
"""

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
import torch
import numpy as np
from PIL import Image
import io
import os
from pathlib import Path
import uuid

# Import protection methods
from protection.deepshield import DeepShield
from protection.baselines import PhotoGuard, AdvDM, Mist
from utils.face_utils import FaceDetector, load_image, save_image
from models.arcface_model import ArcFaceEmbedding
from utils.metrics import create_comparison_grid
import config

# Initialize FastAPI
app = FastAPI(title="DeepShield AI Service", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Device
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"🚀 AI Service running on: {DEVICE}")

# Initialize models (lazy loading)
face_detector = None
arcface_model = None
protection_methods = {}


def get_face_detector():
    global face_detector
    if face_detector is None:
        face_detector = FaceDetector(device=DEVICE)
    return face_detector


def get_arcface():
    global arcface_model
    if arcface_model is None:
        arcface_model = ArcFaceEmbedding(device=DEVICE)
    return arcface_model


def get_protection_method(method_name):
    global protection_methods
    if method_name not in protection_methods:
        if method_name == 'deepshield':
            protection_methods[method_name] = DeepShield(config.DEEPSHIELD_CONFIG, DEVICE)
        elif method_name == 'photoguard':
            protection_methods[method_name] = PhotoGuard(config.PHOTOGUARD_CONFIG, DEVICE)
        elif method_name == 'advdm':
            protection_methods[method_name] = AdvDM(config.ADVDM_CONFIG, DEVICE)
        elif method_name == 'mist':
            protection_methods[method_name] = Mist(config.MIST_CONFIG, DEVICE)
        else:
            raise ValueError(f"Unknown method: {method_name}")
    return protection_methods[method_name]


@app.get("/")
async def root():
    return {
        "service": "DeepShield AI Service",
        "version": "1.0.0",
        "status": "running",
        "device": DEVICE
    }


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "device": DEVICE,
        "cuda_available": torch.cuda.is_available()
    }


@app.post("/protect")
async def protect_image(
    file: UploadFile = File(...),
    method: str = Form("deepshield")
):
    """
    Protect a single image with specified method
    """
    try:
        print(f"📥 Received file: {file.filename}, method: {method}")
        
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        image_np = np.array(image)
        
        print(f"📷 Image shape: {image_np.shape}")
        
        # Detect and align face
        print("🔍 Detecting face...")
        detector = get_face_detector()
        result = detector.detect_and_align(
            image_np, 
            target_size=config.IMAGE_SIZE
        )
        
        # CHECK IF FACE DETECTED
        if result is None or result[0] is None:
            print("❌ No face detected!")
            raise HTTPException(
                status_code=400, 
                detail="No face detected in the image. Please upload a clear frontal face photo with good lighting."
            )
        
        aligned_face, bbox, landmarks = result
        print(f"✅ Face detected! Aligned face shape: {aligned_face.shape}")

        # Get face parsing masks (pass landmarks to avoid re-detection)
        print("🎭 Parsing face regions...")
        face_masks = detector.get_face_parsing_mask(aligned_face, landmarks=landmarks) 
        
        # Extract original embedding
        print("🧬 Extracting embeddings...")
        arcface = get_arcface()
        original_embedding = arcface.extract_embedding(aligned_face)
        
        # Apply protection
        print(f"🛡️ Applying {method} protection...")
        protector = get_protection_method(method)
        
        if method == 'deepshield':
            protected, metrics, perturbation = protector.protect(
                aligned_face, 
                face_mask=face_masks,
                verbose=True
            )
        else:
            protected, metrics, perturbation = protector.protect(
                aligned_face,
                verbose=True
            )
        
        print(f"✅ Protection complete! Metrics: {metrics}")
        
        # Save results
        output_id = str(uuid.uuid4())
        output_dir = config.OUTPUT_DIR / output_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        original_path = output_dir / "original.png"
        protected_path = output_dir / "protected.png"
        perturbation_path = output_dir / "perturbation.png"
        
        save_image(aligned_face, original_path)
        save_image(protected, protected_path)
        save_image(perturbation, perturbation_path)
        
        print(f"💾 Results saved to: {output_dir}")
        
        return {
            "success": True,
            "method": method,
            "output_id": output_id,
            "files": {
                "original": f"/output/{output_id}/original.png",
                "protected": f"/output/{output_id}/protected.png",
                "perturbation": f"/output/{output_id}/perturbation.png"
            },
            "metrics": metrics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compare")
async def compare_methods(file: UploadFile = File(...)):
    """
    Compare all protection methods on a single image
    
    Returns:
        Results from all methods with comparison grid
    """
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        image_np = np.array(image)
        
        # Detect and align face
        detector = get_face_detector()
        aligned_face, bbox, landmarks = detector.detect_and_align(
            image_np,
            target_size=config.IMAGE_SIZE
        )
        
        # Get face parsing
        face_masks = detector.get_face_parsing_mask(aligned_face)
        
        # Extract original embedding
        arcface = get_arcface()
        original_embedding = arcface.extract_embedding(aligned_face)
        
        # Test all methods
        methods = ['deepshield', 'photoguard', 'advdm', 'mist']
        results = {}
        images_for_grid = [aligned_face]
        labels_for_grid = ['Original']
        
        for method_name in methods:
            protector = get_protection_method(method_name)
            
            if method_name == 'deepshield':
                protected, metrics, perturbation = protector.protect(
                    aligned_face,
                    face_mask=face_masks,
                    verbose=False
                )
            else:
                protected, metrics, perturbation = protector.protect(
                    aligned_face,
                    verbose=False
                )
            
            results[method_name] = {
                "metrics": metrics,
                "protected_image": protected,
                "perturbation": perturbation
            }
            
            images_for_grid.append(protected)
            labels_for_grid.append(method_name.upper())
        
        # Create comparison grid
        comparison_grid = create_comparison_grid(images_for_grid, labels_for_grid)
        
        # Save results
        output_id = str(uuid.uuid4())
        output_dir = config.OUTPUT_DIR / output_id
        output_dir.mkdir(exist_ok=True)
        
        # Save comparison grid
        grid_path = output_dir / "comparison.png"
        save_image(comparison_grid, grid_path)
        
        # Save individual results
        for method_name, result in results.items():
            method_dir = output_dir / method_name
            method_dir.mkdir(exist_ok=True)
            
            save_image(result["protected_image"], method_dir / "protected.png")
            save_image(result["perturbation"], method_dir / "perturbation.png")
        
        # Format response
        response = {
            "success": True,
            "output_id": output_id,
            "comparison_grid": str(grid_path),
            "methods": {}
        }
        
        for method_name, result in results.items():
            response["methods"][method_name] = {
                "metrics": result["metrics"],
                "files": {
                    "protected": str(output_dir / method_name / "protected.png"),
                    "perturbation": str(output_dir / method_name / "perturbation.png")
                }
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/output/{output_id}/{filename}")
async def get_output_file(output_id: str, filename: str):
    """Serve output files"""
    file_path = config.OUTPUT_DIR / output_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=True
    )