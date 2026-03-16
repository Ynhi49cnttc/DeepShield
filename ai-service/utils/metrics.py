"""
Metrics Computation
PSNR, SSIM, LPIPS, Identity Similarity
"""

import torch
import torch.nn.functional as F
import numpy as np
from skimage.metrics import peak_signal_noise_ratio, structural_similarity
import lpips


class MetricsCalculator:
    """Calculate various image quality and protection metrics"""
    
    def __init__(self, device='cuda'):
        self.device = device
        
        # Initialize LPIPS model
        self.lpips_model = lpips.LPIPS(net='vgg').to(device)
        self.lpips_model.eval()
        
    def compute_psnr(self, img1, img2):
        """
        Compute Peak Signal-to-Noise Ratio
        
        Args:
            img1, img2: numpy arrays [H, W, 3], range [0, 255]
            
        Returns:
            psnr: float (higher is better, typically 20-40 dB)
        """
        return peak_signal_noise_ratio(img1, img2, data_range=255)
    
    def compute_ssim(self, img1, img2):
        """
        Compute Structural Similarity Index
        
        Args:
            img1, img2: numpy arrays [H, W, 3], range [0, 255]
            
        Returns:
            ssim: float in [0, 1] (higher is better)
        """
        return structural_similarity(
            img1, img2, 
            multichannel=True,
            channel_axis=2,
            data_range=255
        )
    
    def compute_lpips(self, img1, img2):
        """
        Compute Learned Perceptual Image Patch Similarity
        
        Args:
            img1, img2: numpy arrays [H, W, 3], range [0, 255]
                       or torch tensors [B, 3, H, W], range [-1, 1]
            
        Returns:
            lpips_score: float (lower is better, typically 0-1)
        """
        # Convert numpy to tensor if needed
        if isinstance(img1, np.ndarray):
            img1 = self._numpy_to_tensor(img1)
            img2 = self._numpy_to_tensor(img2)
        
        # Ensure batch dimension
        if img1.dim() == 3:
            img1 = img1.unsqueeze(0)
            img2 = img2.unsqueeze(0)
        
        # Move to device
        img1 = img1.to(self.device)
        img2 = img2.to(self.device)
        
        # Compute LPIPS
        with torch.no_grad():
            lpips_score = self.lpips_model(img1, img2)
        
        return float(lpips_score.mean().cpu())
    
    def compute_all_metrics(self, original, protected, original_embedding, protected_embedding):
        """
        Compute all metrics for protection evaluation
        
        Args:
            original: numpy array [H, W, 3], range [0, 255]
            protected: numpy array [H, W, 3], range [0, 255]
            original_embedding: numpy array [512]
            protected_embedding: numpy array [512]
            
        Returns:
            metrics: dict with all computed metrics
        """
        # Visual quality metrics
        psnr = self.compute_psnr(original, protected)
        ssim = self.compute_ssim(original, protected)
        lpips_score = self.compute_lpips(original, protected)
        
        # Identity preservation
        identity_similarity = float(np.dot(original_embedding, protected_embedding))
        
        # L2 distance (normalized)
        l2_distance = float(np.linalg.norm(original - protected) / np.sqrt(original.size))
        
        # Frequency analysis
        freq_rate = self._compute_frequency_rate(original, protected)
        
        return {
            'psnr': round(psnr, 2),
            'ssim': round(ssim, 4),
            'lpips': round(lpips_score, 4),
            'identity_similarity': round(identity_similarity, 4),
            'l2_distance': round(l2_distance, 6),
            'frequency_rate': round(freq_rate, 2)
        }
    
    def _numpy_to_tensor(self, img):
        """Convert numpy image to tensor for LPIPS"""
        # img: [H, W, 3], range [0, 255]
        img = img.astype(np.float32) / 255.0
        img = img.transpose(2, 0, 1)  # [3, H, W]
        img = torch.from_numpy(img)
        img = img * 2.0 - 1.0  # Normalize to [-1, 1]
        return img
    
    def _compute_frequency_rate(self, img1, img2):
        """
        Compute the ratio of perturbation energy in low-frequency bands
        
        Returns:
            freq_rate: float (percentage of energy in low frequencies)
        """
        # Compute perturbation
        perturbation = img2.astype(np.float32) - img1.astype(np.float32)
        
        # DCT transform
        from scipy.fftpack import dctn
        
        # Average across channels
        perturbation_gray = perturbation.mean(axis=2)
        
        # 2D DCT
        dct_coeffs = dctn(perturbation_gray, norm='ortho')
        
        # Compute energy in different frequency bands
        h, w = dct_coeffs.shape
        
        # Low frequency: top-left quarter
        low_freq_energy = np.sum(np.abs(dct_coeffs[:h//4, :w//4]))
        total_energy = np.sum(np.abs(dct_coeffs))
        
        if total_energy == 0:
            return 0.0
        
        freq_rate = (low_freq_energy / total_energy) * 100
        return freq_rate


class ProtectionMetrics:
    """Compute protection effectiveness metrics"""
    
    @staticmethod
    def compute_protection_success_rate(identity_similarity, threshold=0.3):
        """
        Compute protection success based on identity similarity reduction
        
        Args:
            identity_similarity: float, similarity between original and protected
            threshold: float, threshold for successful protection
            
        Returns:
            success_rate: float (0-100%)
        """
        if identity_similarity < threshold:
            # Calculate how much below threshold
            success_rate = (1 - identity_similarity / threshold) * 100
        else:
            success_rate = 0.0
        
        return min(100.0, success_rate)
    
    @staticmethod
    def compute_attack_success_rate(deepfake_similarity, original_similarity, threshold=0.8):
        """
        Compute attack success rate (how well deepfake matches target)
        
        Args:
            deepfake_similarity: similarity between deepfake and target
            original_similarity: baseline similarity
            threshold: success threshold
            
        Returns:
            attack_success: float (0-100%)
        """
        relative_similarity = deepfake_similarity / max(original_similarity, 0.01)
        
        if relative_similarity > threshold:
            attack_success = min(100.0, relative_similarity * 100)
        else:
            attack_success = 0.0
        
        return attack_success


def visualize_perturbation(original, protected, amplification=10):
    """
    Visualize the adversarial perturbation
    
    Args:
        original: numpy array [H, W, 3]
        protected: numpy array [H, W, 3]
        amplification: int, amplify perturbation for visibility
        
    Returns:
        perturbation_vis: numpy array [H, W, 3], visualized perturbation
    """
    # Compute perturbation
    perturbation = protected.astype(np.float32) - original.astype(np.float32)
    
    # Amplify for visualization
    perturbation_vis = perturbation * amplification
    
    # Shift to [0, 255] range
    perturbation_vis = perturbation_vis + 127.5
    perturbation_vis = np.clip(perturbation_vis, 0, 255).astype(np.uint8)
    
    return perturbation_vis


def create_comparison_grid(images, labels, grid_size=None):
    """
    Create a comparison grid of images
    
    Args:
        images: list of numpy arrays [H, W, 3]
        labels: list of strings for each image
        grid_size: tuple (rows, cols), auto-computed if None
        
    Returns:
        grid: numpy array with comparison grid
    """
    import cv2
    
    n_images = len(images)
    
    if grid_size is None:
        # Auto-compute grid size
        cols = min(4, n_images)
        rows = (n_images + cols - 1) // cols
        grid_size = (rows, cols)
    
    rows, cols = grid_size
    h, w = images[0].shape[:2]
    
    # Create grid
    grid = np.ones((h * rows, w * cols, 3), dtype=np.uint8) * 255
    
    for idx, (img, label) in enumerate(zip(images, labels)):
        row = idx // cols
        col = idx % cols
        
        # Add label to image
        img_labeled = img.copy()
        cv2.putText(img_labeled, label, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)
        
        # Place in grid
        grid[row*h:(row+1)*h, col*w:(col+1)*w] = img_labeled
    
    return grid