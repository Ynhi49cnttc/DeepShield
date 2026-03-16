"""
Baseline Protection Methods
Simplified implementations of PhotoGuard, AdvDM, and Mist
"""

import torch
import torch.nn.functional as F
import numpy as np
from tqdm import tqdm

from models.arcface_model import DifferentiableArcFace
from utils.metrics import MetricsCalculator


class PhotoGuard:
    """
    PhotoGuard: Proactive Defense Against Image Manipulation
    Simplified implementation focusing on encoder disruption
    """
    
    def __init__(self, config, device='cuda'):
        self.config = config
        self.device = device
        self.epsilon = config['epsilon']
        self.num_steps = config['num_steps']
        self.step_size = config['step_size']
        
        self.arcface = DifferentiableArcFace(device=device)
        self.metrics_calc = MetricsCalculator(device=device)
    
    def protect(self, image, verbose=True):
        """
        Apply PhotoGuard protection
        
        Args:
            image: numpy array [H, W, 3], range [0, 255]
            verbose: bool
            
        Returns:
            protected_image, metrics, perturbation_vis
        """
        x_orig = self._image_to_tensor(image).to(self.device)
        
        # Extract original embedding
        with torch.no_grad():
            emb_orig = self.arcface.forward(x_orig)
        
        # Initialize perturbation
        delta = torch.zeros_like(x_orig, requires_grad=True)
        optimizer = torch.optim.Adam([delta], lr=self.step_size)
        
        iterator = tqdm(range(self.num_steps), desc="PhotoGuard") if verbose else range(self.num_steps)
        
        for step in iterator:
            optimizer.zero_grad()
            
            # Apply perturbation
            x_adv = x_orig + delta
            x_adv = torch.clamp(x_adv, -1, 1)
            delta.data = torch.clamp(delta.data, -self.epsilon, self.epsilon)
            
            # Extract perturbed embedding
            emb_adv = self.arcface.extract_with_grad(x_adv)
            
            # PhotoGuard loss: maximize distance from original embedding
            loss_identity = F.cosine_similarity(emb_adv, emb_orig, dim=1).mean()
            
            # Perceptual quality constraint
            loss_lpips = self.metrics_calc.compute_lpips(x_orig, x_adv)
            loss_lpips = torch.tensor(loss_lpips, device=self.device, requires_grad=True)
            
            # Total loss
            loss = loss_identity + 0.1 * loss_lpips
            
            loss.backward()
            optimizer.step()
            
            if verbose and step % 10 == 0:
                iterator.set_postfix({'loss': f'{loss.item():.4f}'})
        
        # Generate protected image
        with torch.no_grad():
            x_protected = torch.clamp(x_orig + delta, -1, 1)
            emb_protected = self.arcface.forward(x_protected)
        
        protected_image = self._tensor_to_image(x_protected)
        
        # Compute metrics
        metrics = self.metrics_calc.compute_all_metrics(
            image, protected_image,
            emb_orig.cpu().numpy()[0],
            emb_protected.cpu().numpy()[0]
        )
        
        # Visualize perturbation
        from utils.metrics import visualize_perturbation
        perturbation_vis = visualize_perturbation(image, protected_image)
        
        return protected_image, metrics, perturbation_vis
    
    def _image_to_tensor(self, image):
        image = image.astype(np.float32) / 255.0
        image = image.transpose(2, 0, 1)
        image = torch.from_numpy(image).unsqueeze(0)
        image = image * 2.0 - 1.0
        return image
    
    def _tensor_to_image(self, tensor):
        image = tensor.squeeze(0).cpu().numpy()
        image = (image + 1.0) / 2.0
        image = image.transpose(1, 2, 0)
        image = (image * 255.0).clip(0, 255).astype(np.uint8)
        return image


class AdvDM:
    """
    AdvDM: Adversarial Examples for Diffusion Models
    Simplified implementation targeting latent representations
    """
    
    def __init__(self, config, device='cuda'):
        self.config = config
        self.device = device
        self.epsilon = config['epsilon']
        self.num_steps = config['num_steps']
        self.step_size = config['step_size']
        
        self.arcface = DifferentiableArcFace(device=device)
        self.metrics_calc = MetricsCalculator(device=device)
    
    def protect(self, image, verbose=True):
        """Apply AdvDM protection"""
        x_orig = self._image_to_tensor(image).to(self.device)
        
        with torch.no_grad():
            emb_orig = self.arcface.forward(x_orig)
        
        delta = torch.zeros_like(x_orig, requires_grad=True)
        optimizer = torch.optim.Adam([delta], lr=self.step_size)
        
        iterator = tqdm(range(self.num_steps), desc="AdvDM") if verbose else range(self.num_steps)
        
        for step in iterator:
            optimizer.zero_grad()
            
            x_adv = torch.clamp(x_orig + delta, -1, 1)
            delta.data = torch.clamp(delta.data, -self.epsilon, self.epsilon)
            
            emb_adv = self.arcface.extract_with_grad(x_adv)
            
            # AdvDM focuses on style and texture disruption
            # Simplified: combine identity loss with high-frequency noise
            loss_identity = F.cosine_similarity(emb_adv, emb_orig, dim=1).mean()
            
            # Add texture loss (simplified as variation)
            loss_texture = torch.mean(torch.abs(x_adv[:, :, 1:, :] - x_adv[:, :, :-1, :])) + \
                          torch.mean(torch.abs(x_adv[:, :, :, 1:] - x_adv[:, :, :, :-1]))
            
            loss_lpips = self.metrics_calc.compute_lpips(x_orig, x_adv)
            loss_lpips = torch.tensor(loss_lpips, device=self.device, requires_grad=True)
            
            loss = loss_identity + 0.2 * loss_texture + 0.1 * loss_lpips
            
            loss.backward()
            optimizer.step()
            
            if verbose and step % 10 == 0:
                iterator.set_postfix({'loss': f'{loss.item():.4f}'})
        
        with torch.no_grad():
            x_protected = torch.clamp(x_orig + delta, -1, 1)
            emb_protected = self.arcface.forward(x_protected)
        
        protected_image = self._tensor_to_image(x_protected)
        
        metrics = self.metrics_calc.compute_all_metrics(
            image, protected_image,
            emb_orig.cpu().numpy()[0],
            emb_protected.cpu().numpy()[0]
        )
        
        from utils.metrics import visualize_perturbation
        perturbation_vis = visualize_perturbation(image, protected_image)
        
        return protected_image, metrics, perturbation_vis
    
    def _image_to_tensor(self, image):
        image = image.astype(np.float32) / 255.0
        image = image.transpose(2, 0, 1)
        image = torch.from_numpy(image).unsqueeze(0)
        image = image * 2.0 - 1.0
        return image
    
    def _tensor_to_image(self, tensor):
        image = tensor.squeeze(0).cpu().numpy()
        image = (image + 1.0) / 2.0
        image = image.transpose(1, 2, 0)
        image = (image * 255.0).clip(0, 255).astype(np.uint8)
        return image


class Mist:
    """
    Mist: Fused Loss for Transferable Adversarial Examples
    Combines semantic and textural objectives
    """
    
    def __init__(self, config, device='cuda'):
        self.config = config
        self.device = device
        self.epsilon = config['epsilon']
        self.num_steps = config['num_steps']
        self.step_size = config['step_size']
        
        self.arcface = DifferentiableArcFace(device=device)
        self.metrics_calc = MetricsCalculator(device=device)
    
    def protect(self, image, verbose=True):
        """Apply Mist protection"""
        x_orig = self._image_to_tensor(image).to(self.device)
        
        with torch.no_grad():
            emb_orig = self.arcface.forward(x_orig)
        
        delta = torch.zeros_like(x_orig, requires_grad=True)
        optimizer = torch.optim.Adam([delta], lr=self.step_size)
        
        iterator = tqdm(range(self.num_steps), desc="Mist") if verbose else range(self.num_steps)
        
        for step in iterator:
            optimizer.zero_grad()
            
            x_adv = torch.clamp(x_orig + delta, -1, 1)
            delta.data = torch.clamp(delta.data, -self.epsilon, self.epsilon)
            
            emb_adv = self.arcface.extract_with_grad(x_adv)
            
            # Mist fused loss: semantic (identity) + textural
            loss_semantic = F.cosine_similarity(emb_adv, emb_orig, dim=1).mean()
            
            # Textural loss: maximize difference in gradient patterns
            grad_x = x_adv[:, :, 1:, :] - x_adv[:, :, :-1, :]
            grad_y = x_adv[:, :, :, 1:] - x_adv[:, :, :, :-1]
            
            grad_orig_x = x_orig[:, :, 1:, :] - x_orig[:, :, :-1, :]
            grad_orig_y = x_orig[:, :, :, 1:] - x_orig[:, :, :, :-1]
            
            loss_textural = -torch.mean(torch.abs(grad_x - grad_orig_x)) - \
                           torch.mean(torch.abs(grad_y - grad_orig_y))
            
            loss_lpips = self.metrics_calc.compute_lpips(x_orig, x_adv)
            loss_lpips = torch.tensor(loss_lpips, device=self.device, requires_grad=True)
            
            # Fused loss with balanced weights
            loss = 0.5 * loss_semantic + 0.3 * loss_textural + 0.1 * loss_lpips
            
            loss.backward()
            optimizer.step()
            
            if verbose and step % 10 == 0:
                iterator.set_postfix({'loss': f'{loss.item():.4f}'})
        
        with torch.no_grad():
            x_protected = torch.clamp(x_orig + delta, -1, 1)
            emb_protected = self.arcface.forward(x_protected)
        
        protected_image = self._tensor_to_image(x_protected)
        
        metrics = self.metrics_calc.compute_all_metrics(
            image, protected_image,
            emb_orig.cpu().numpy()[0],
            emb_protected.cpu().numpy()[0]
        )
        
        from utils.metrics import visualize_perturbation
        perturbation_vis = visualize_perturbation(image, protected_image)
        
        return protected_image, metrics, perturbation_vis
    
    def _image_to_tensor(self, image):
        image = image.astype(np.float32) / 255.0
        image = image.transpose(2, 0, 1)
        image = torch.from_numpy(image).unsqueeze(0)
        image = image * 2.0 - 1.0
        return image
    
    def _tensor_to_image(self, tensor):
        image = tensor.squeeze(0).cpu().numpy()
        image = (image + 1.0) / 2.0
        image = image.transpose(1, 2, 0)
        image = (image * 255.0).clip(0, 255).astype(np.uint8)
        return image