"""
Face detection and alignment utilities
"""

import numpy as np
import cv2
from insightface.app import FaceAnalysis
from PIL import Image


def load_image(path):
    """Load image from path"""
    img = Image.open(path).convert('RGB')
    return np.array(img)


def save_image(image, path):
    """Save image to path"""
    if isinstance(image, np.ndarray):
        # Convert to uint8 if needed
        if image.dtype != np.uint8:
            if image.max() <= 1.0:
                image = (image * 255).astype(np.uint8)
            else:
                image = np.clip(image, 0, 255).astype(np.uint8)
        
        # Ensure RGB
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        
        img = Image.fromarray(image)
    else:
        img = image
    
    img.save(path)


class FaceDetector:
    """Face detection and alignment using InsightFace"""
    
    def __init__(self, device='cpu'):
        self.device = device
        
        # Initialize InsightFace
        providers = ['CUDAExecutionProvider', 'CPUExecutionProvider'] if device == 'cuda' else ['CPUExecutionProvider']
        self.app = FaceAnalysis(name='buffalo_l', providers=providers)
        self.app.prepare(ctx_id=0 if device == 'cuda' else -1, det_size=(640, 640))
    
    def detect_and_align(self, image, target_size=512):
        """
        Detect and align face
        
        Returns:
            aligned_face: Aligned face image
            bbox: Bounding box
            landmarks: 106 facial landmarks
        """
        # Detect faces
        faces = self.app.get(image)
        
        if len(faces) == 0:
            print("⚠️ No face detected")
            return None, None, None
        
        # Get largest face
        face = sorted(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))[-1]
        
        # Get landmarks
        landmarks = face.landmark_2d_106 if hasattr(face, 'landmark_2d_106') else face.kps
        bbox = face.bbox
        
        # Align and crop face
        aligned_face = self._align_face(image, landmarks, target_size)
        
        return aligned_face, bbox, landmarks
    
    def _align_face(self, image, landmarks, target_size=512):
        """Align face using landmarks"""
        
        # Use 5 key points if available, otherwise use landmarks
        if landmarks.shape[0] == 106:
            # Extract 5 key points from 106 landmarks
            # Left eye, right eye, nose, left mouth, right mouth
            key_points = np.array([
                landmarks[38],  # Left eye
                landmarks[88],  # Right eye  
                landmarks[86],  # Nose tip
                landmarks[52],  # Left mouth corner
                landmarks[61]   # Right mouth corner
            ])
        else:
            key_points = landmarks[:5]  # Assume first 5 are key points
        
        # Target positions for aligned face
        target_landmarks = np.array([
            [38.2946, 51.6963],
            [73.5318, 51.5014],
            [56.0252, 71.7366],
            [41.5493, 92.3655],
            [70.7299, 92.2041]
        ]) * (target_size / 112.0)
        
        # Estimate transformation
        tform = cv2.estimateAffinePartial2D(key_points, target_landmarks)[0]
        
        # Warp image
        aligned = cv2.warpAffine(
            image, 
            tform, 
            (target_size, target_size),
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(0, 0, 0)
        )
        
        return aligned
    
    def get_face_parsing_mask(self, image, landmarks=None):
        """
        Get semantic face parsing mask using simple geometry
        
        Returns:
            dict with keys: 'eyes', 'nose', 'mouth', 'skin'
        """
        h, w = image.shape[:2]
        
        # Use simple geometric masks (không cần landmarks phức tạp)
        masks = {}
        
        center_x, center_y = w // 2, h // 2
        
        # Eyes region (upper third, symmetrical)
        eye_mask = np.zeros((h, w), dtype=np.float32)
        # Left eye
        cv2.ellipse(
            eye_mask, 
            (int(center_x - w * 0.2), int(center_y - h * 0.15)), 
            (int(w * 0.1), int(h * 0.08)), 
            0, 0, 360, 1.0, -1
        )
        # Right eye
        cv2.ellipse(
            eye_mask, 
            (int(center_x + w * 0.2), int(center_y - h * 0.15)), 
            (int(w * 0.1), int(h * 0.08)), 
            0, 0, 360, 1.0, -1
        )
        masks['eyes'] = eye_mask
        
        # Nose region (center)
        nose_mask = np.zeros((h, w), dtype=np.float32)
        cv2.ellipse(
            nose_mask, 
            (center_x, center_y), 
            (int(w * 0.08), int(h * 0.12)), 
            0, 0, 360, 1.0, -1
        )
        masks['nose'] = nose_mask
        
        # Mouth region (lower third)
        mouth_mask = np.zeros((h, w), dtype=np.float32)
        cv2.ellipse(
            mouth_mask, 
            (center_x, int(center_y + h * 0.2)), 
            (int(w * 0.15), int(h * 0.08)), 
            0, 0, 360, 1.0, -1
        )
        masks['mouth'] = mouth_mask
        
        # Skin region (entire face minus features)
        skin_mask = np.ones((h, w), dtype=np.float32)
        
        # Create face ellipse
        cv2.ellipse(
            skin_mask, 
            (center_x, center_y), 
            (int(w * 0.35), int(h * 0.45)), 
            0, 0, 360, 1.0, -1
        )
        
        # Subtract features
        skin_mask = skin_mask - eye_mask - nose_mask - mouth_mask
        skin_mask = np.clip(skin_mask, 0, 1)
        masks['skin'] = skin_mask
        
        return masks


class FaceNormalizer:
    """Normalize face images for ArcFace"""
    
    @staticmethod
    def normalize_for_arcface(image):
        """
        Normalize image for ArcFace model
        
        Args:
            image: numpy array (H, W, 3) in range [0, 255]
            
        Returns:
            Normalized tensor
        """
        # Convert to float32
        if image.dtype == np.uint8:
            image = image.astype(np.float32)
        
        # Normalize to [-1, 1]
        image = (image - 127.5) / 127.5
        
        # Transpose to (C, H, W)
        image = np.transpose(image, (2, 0, 1))
        
        return image
    
    @staticmethod
    def denormalize(image):
        """
        Denormalize from [-1, 1] back to [0, 255]
        
        Args:
            image: numpy array in range [-1, 1]
            
        Returns:
            Image in range [0, 255] uint8
        """
        # Denormalize from [-1, 1] to [0, 255]
        image = (image * 127.5 + 127.5).clip(0, 255).astype(np.uint8)
        
        return image