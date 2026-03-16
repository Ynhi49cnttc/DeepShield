"""
DeepShield Protection Implementation
Based on the research paper methodology
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm
import cv2

from models.arcface_model import DifferentiableArcFace, create_random_identity_embedding
from utils.metrics import MetricsCalculator


class DeepShield:
    """
    DeepShield: Proactive Defense Against Deepfake Generation
    
    Implements:
    1. Trajectory-Based Surrogate Attack
    2. Dual Dynamic Anti-Anchors
    3. Semantic-Aware Spatial Guidance
    4. Perceptual Quality Constraint (LPIPS)
    """
    
    def __init__(self, config, device='cuda'):
        """
        Initialize DeepShield
        
        Args:
            config: dict with DeepShield parameters
            device: torch device
        """
        self.config = config
        self.device = device
        
        # Models
        self.arcface = DifferentiableArcFace(device=device)
        self.metrics_calc = MetricsCalculator(device=device)
        
        # Parameters
        self.epsilon = config['epsilon']
        self.num_steps = config['num_steps']
        self.step_size = config['step_size']
        self.mdiv = config['mdiv']
        self.mmut = config['mmut']
        self.lambda_div = config['lambda_div']
        self.lambda_mut = config['lambda_mut']
        self.lambda_lpips = config['lambda_lpips']
        
    def protect(self, image, face_mask=None, verbose=True):
        """
        Apply DeepShield protection to image
        
        Args:
            image: numpy array [H, W, 3], range [0, 255]
            face_mask: dict with semantic masks (optional)
            verbose: bool, show progress bar
            
        Returns:
            protected_image: numpy array [H, W, 3]
            metrics: dict with protection metrics
            perturbation_vis: numpy array [H, W, 3], visualized perturbation
        """
        # Convert to tensor
        x_orig = self._image_to_tensor(image).to(self.device)
        
        # Extract original identity embedding
        with torch.no_grad():
            emb_orig = self.arcface.forward(x_orig)
        
        # Initialize dual anti-anchors
        anchors = create_random_identity_embedding(self.device, num_embeddings=2)
        anchors = nn.Parameter(anchors)
        
        # Initialize perturbation
        delta = torch.zeros_like(x_orig, requires_grad=True)
        
        # Create spatial guidance mask
        if face_mask is not None:
            spatial_mask = self._create_spatial_mask(face_mask, x_orig.shape[-2:])
        else:
            spatial_mask = torch.ones(1, 1, x_orig.shape[2], x_orig.shape[3]).to(self.device)
        
        # Optimizer
        optimizer = torch.optim.Adam([delta, anchors], lr=self.step_size)
        
        # Optimization loop
        iterator = tqdm(range(self.num_steps), desc="DeepShield Protection") if verbose else range(self.num_steps)
        
        for step in iterator:
            optimizer.zero_grad()
            
            # Apply perturbation with spatial guidance
            x_adv = x_orig + delta * spatial_mask
            x_adv = torch.clamp(x_adv, -1, 1)
            
            # Enforce epsilon constraint
            delta.data = torch.clamp(delta.data, -self.epsilon, self.epsilon)
            
            # Extract embedding from perturbed image
            emb_adv = self.arcface.extract_with_grad(x_adv)
            
            # Loss components
            
            # 1. Trajectory-based identity disruption loss
            loss_traj = self._trajectory_loss(emb_adv, emb_orig, anchors)
            
            # 2. Anti-anchor divergence loss
            loss_div = self._anchor_divergence_loss(anchors, emb_orig)
            
            # 3. Mutual separation loss
            loss_mut = self._mutual_separation_loss(anchors)
            
            # 4. Perceptual quality constraint (LPIPS)
            loss_lpips = self.metrics_calc.compute_lpips(x_orig, x_adv)
            loss_lpips = torch.tensor(loss_lpips, device=self.device, requires_grad=True)
            
            # Total loss
            loss = loss_traj + \
                   self.lambda_div * loss_div + \
                   self.lambda_mut * loss_mut + \
                   self.lambda_lpips * loss_lpips
            
            # Backward and optimize
            loss.backward()
            optimizer.step()
            
            # Update progress bar
            if verbose and step % 10 == 0:
                iterator.set_postfix({
                    'loss': f'{loss.item():.4f}',
                    'traj': f'{loss_traj.item():.4f}',
                    'lpips': f'{loss_lpips.item():.4f}'
                })
        
        # Generate protected image
        with torch.no_grad():
            x_protected = x_orig + delta * spatial_mask
            x_protected = torch.clamp(x_protected, -1, 1)
            
            # Extract final embedding
            emb_protected = self.arcface.forward(x_protected)
        
        # Convert back to numpy
        protected_image = self._tensor_to_image(x_protected)
        
        # Compute metrics
        metrics = self._compute_protection_metrics(
            image, protected_image,
            emb_orig.cpu().numpy()[0],
            emb_protected.cpu().numpy()[0]
        )
        
        # Visualize perturbation
        perturbation_vis = self._visualize_perturbation(image, protected_image)
        
        return protected_image, metrics, perturbation_vis
    
    def _trajectory_loss(self, emb_adv, emb_orig, anchors):
        """
        Trajectory-based identity disruption loss
        Pushes adversarial embedding away from original and toward anti-anchors
        """
        # Push away from original identity
        sim_orig = F.cosine_similarity(emb_adv, emb_orig, dim=1).mean()
        
        # Pull toward anti-anchors
        sim_anchor1 = F.cosine_similarity(emb_adv, anchors[0:1], dim=1).mean()
        sim_anchor2 = F.cosine_similarity(emb_adv, anchors[1:2], dim=1).mean()
        
        # Loss: maximize similarity with original (minimize negative similarity)
        # and minimize similarity with anchors (maximize negative similarity)
        loss = sim_orig - 0.5 * (sim_anchor1 + sim_anchor2)
        
        return loss
    
    def _anchor_divergence_loss(self, anchors, emb_orig):
        """
        Anti-anchor divergence loss
        Ensures anchors diverge from original identity
        """
        sim1 = F.cosine_similarity(anchors[0:1], emb_orig, dim=1)
        sim2 = F.cosine_similarity(anchors[1:2], emb_orig, dim=1)
        
        # ReLU to only penalize when similarity > margin
        loss1 = F.relu(sim1 + self.mdiv)
        loss2 = F.relu(sim2 + self.mdiv)
        
        return loss1.mean() + loss2.mean()
    
    def _mutual_separation_loss(self, anchors):
        """
        Mutual separation loss
        Ensures the two anti-anchors are different from each other
        """
        sim = F.cosine_similarity(anchors[0:1], anchors[1:2], dim=1)
        
        # Penalize when similarity > negative margin
        loss = F.relu(sim - self.mmut)
        
        return loss.mean()
    
    def _create_spatial_mask(self, face_mask, target_size):
        """
        Create semantic-aware spatial guidance mask
        
        Args:
            face_mask: dict with region masks
            target_size: tuple (H, W)
            
        Returns:
            mask: torch tensor [1, 1, H, W]
        """
        h, w = target_size
        
        # Combine masks with different weights
        weights = self.config
        
        mask = np.zeros((h, w), dtype=np.float32)
        
        for region in ['eyes', 'nose', 'mouth', 'skin']:
            if region in face_mask:
                region_mask = cv2.resize(face_mask[region], (w, h))
                weight_key = f'identity_weight_{region}'
                weight = weights.get(weight_key, 0.5)
                mask += region_mask * weight
        
        # Normalize to [0.5, 1.0] range (minimum baseline perturbation)
        mask = mask / (mask.max() + 1e-8)
        mask = 0.5 + mask * 0.5
        
        # Convert to tensor
        mask = torch.from_numpy(mask).unsqueeze(0).unsqueeze(0).to(self.device)
        
        return mask
    
    def _compute_protection_metrics(self, original, protected, emb_orig, emb_protected):
        """Compute comprehensive protection metrics"""
        return self.metrics_calc.compute_all_metrics(
            original, protected, emb_orig, emb_protected
        )
    
    def _visualize_perturbation(self, original, protected, amplification=10):
        """Visualize adversarial perturbation"""
        from utils.metrics import visualize_perturbation
        return visualize_perturbation(original, protected, amplification)
    
    def _image_to_tensor(self, image):
        """Convert numpy image to torch tensor"""
        # image: [H, W, 3], range [0, 255]
        image = image.astype(np.float32) / 255.0
        image = image.transpose(2, 0, 1)  # [3, H, W]
        image = torch.from_numpy(image).unsqueeze(0)  # [1, 3, H, W]
        image = image * 2.0 - 1.0  # Normalize to [-1, 1]
        return image
    
    def _tensor_to_image(self, tensor):
        """Convert torch tensor to numpy image"""
        # tensor: [1, 3, H, W], range [-1, 1]
        image = tensor.squeeze(0).cpu().numpy()
        image = (image + 1.0) / 2.0  # Denormalize to [0, 1]
        image = image.transpose(1, 2, 0)  # [H, W, 3]
        image = (image * 255.0).clip(0, 255).astype(np.uint8)
        return image


class SimplifiedDiffusionSurrogate(nn.Module):
    """
    Simplified diffusion model surrogate for trajectory-based attack
    In production, this would be a real UNet diffusion model
    """
    
    def __init__(self, timesteps=[50, 100, 150, 200]):
        super().__init__()
        self.timesteps = timesteps
        
    def forward(self, x, t):
        """
        Simplified forward diffusion
        In production, this would be a real denoising step
        """
        # Add noise proportional to timestep
        noise_level = t / 1000.0
        noise = torch.randn_like(x) * noise_level
        return x + noise
    
    def denoise(self, x_t, t):
        """
        Simplified denoising
        In production, this would be a UNet prediction
        """
        # Simple denoising: just return input with reduced noise
        return x_t * 0.9