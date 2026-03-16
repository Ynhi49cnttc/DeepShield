/**
 * Image Controller - Updated with AI Service Integration
 * Forwards requests to Python AI service for real model inference
 */

const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');
const path = require('path');

// AI Service URL
const AI_SERVICE_URL = process.env.AI_SERVICE_URL || 'http://localhost:8000';

// Import old simulation service as fallback
const deepshieldService = require('../services/deepshield.service');

class ImageController {
  
  /**
   * Upload and store image
   */
  async upload(req, res, next) {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      res.json({
        success: true,
        message: 'Image uploaded successfully',
        file: {
          filename: req.file.filename,
          originalName: req.file.originalname,
          size: req.file.size,
          url: `/uploads/${req.file.filename}`
        }
      });
    } catch (error) {
      next(error);
    }
  }

  /**
   * NEW: Protect image with AI service
   * Calls Python AI service for real model inference
   */
  async protectWithAI(req, res, next) {
    try {
      const { filename, method } = req.body;
      
      if (!filename) {
        return res.status(400).json({ error: 'Filename is required' });
      }

      const inputPath = path.join(__dirname, '../../uploads', filename);
      
      // Check if file exists
      if (!fs.existsSync(inputPath)) {
        return res.status(404).json({ error: 'File not found' });
      }

      // Create form data for AI service
      const formData = new FormData();
      formData.append('file', fs.createReadStream(inputPath));
      formData.append('method', method || 'deepshield');

      console.log(`Calling AI service at ${AI_SERVICE_URL}/protect with method: ${method || 'deepshield'}`);

      // Call AI service
      const aiResponse = await axios.post(
        `${AI_SERVICE_URL}/protect`,
        formData,
        {
          headers: formData.getHeaders(),
          timeout: 600000
        }
      );

      res.json({
        success: true,
        message: 'Image protected with AI',
        result: aiResponse.data,
        useRealAI: true
      });

    } catch (error) {
      // Fallback to simulation if AI service unavailable
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        console.warn('⚠️  AI service unavailable, falling back to simulation mode...');
        return this.protect(req, res, next);
      }
      
      console.error('AI service error:', error.message);
      next(error);
    }
  }

  /**
   * NEW: Compare all protection methods using AI
   */
  async compareMethodsWithAI(req, res, next) {
    try {
      const { filename } = req.body;
      
      if (!filename) {
        return res.status(400).json({ error: 'Filename is required' });
      }

      const inputPath = path.join(__dirname, '../../uploads', filename);
      
      if (!fs.existsSync(inputPath)) {
        return res.status(404).json({ error: 'File not found' });
      }

      // Create form data
      const formData = new FormData();
      formData.append('file', fs.createReadStream(inputPath));

      console.log(`Calling AI service compare endpoint...`);

      // Call AI service compare endpoint
      const aiResponse = await axios.post(
        `${AI_SERVICE_URL}/compare`,
        formData,
        {
          headers: formData.getHeaders(),
          timeout: 180000 // 3 minutes for comparing all methods
        }
      );

      res.json({
        success: true,
        message: 'All methods compared with AI',
        result: aiResponse.data,
        useRealAI: true
      });

    } catch (error) {
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        return res.status(503).json({ 
          error: 'AI service unavailable. Please ensure Python AI service is running on port 8000.',
          details: error.message,
          hint: 'Run: cd ai-service && python main.py'
        });
      }
      
      console.error('AI service compare error:', error.message);
      next(error);
    }
  }

  /**
   * NEW: Complete workflow with AI
   * Enhanced version that uses real AI service
   */
  async processCompleteWithAI(req, res, next) {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const inputPath = path.join(__dirname, '../../uploads', req.file.filename);

      // Create form data
      const formData = new FormData();
      formData.append('file', fs.createReadStream(inputPath));
      formData.append('method', 'deepshield');

      console.log(`Processing complete workflow with AI...`);

      // Call AI service
      const aiResponse = await axios.post(
        `${AI_SERVICE_URL}/protect`,
        formData,
        {
          headers: formData.getHeaders(),
          timeout: 120000
        }
      );

      // Format response to match frontend expectations
      const result = {
        original: {
          url: `/uploads/${req.file.filename}`,
          filename: req.file.filename
        },
        protected: {
          url: aiResponse.data.files.protected,
          filename: path.basename(aiResponse.data.files.protected),
          metrics: aiResponse.data.metrics
        },
        perturbation: {
          url: aiResponse.data.files.perturbation,
          filename: path.basename(aiResponse.data.files.perturbation)
        },
        // AI-specific data
        useRealAI: true,
        outputId: aiResponse.data.output_id,
        method: aiResponse.data.method,
        comparisonMetrics: {
          identityReduction: `${((1 - aiResponse.data.metrics.identity_similarity) * 100).toFixed(1)}%`,
          defenseEffectiveness: aiResponse.data.metrics.identity_similarity < 0.3 ? 'High' : 'Medium',
          visualQualityMaintained: aiResponse.data.metrics.psnr > 30
        }
      };

      res.json({
        success: true,
        message: 'Complete workflow processed with real AI',
        result
      });

    } catch (error) {
      // Fallback to simulation
      if (error.code === 'ECONNREFUSED' || error.code === 'ETIMEDOUT') {
        console.warn('⚠️  AI service unavailable, falling back to simulation mode...');
        return this.processComplete(req, res, next);
      }
      
      console.error('AI service complete workflow error:', error.message);
      next(error);
    }
  }

  /**
   * NEW: Check AI service health
   */
  async checkAIService(req, res, next) {
    try {
      const response = await axios.get(`${AI_SERVICE_URL}/health`, {
        timeout: 5000
      });

      res.json({
        aiServiceAvailable: true,
        aiServiceStatus: response.data,
        aiServiceUrl: AI_SERVICE_URL
      });

    } catch (error) {
      res.json({
        aiServiceAvailable: false,
        aiServiceUrl: AI_SERVICE_URL,
        error: error.message,
        fallbackMode: 'simulation'
      });
    }
  }

  /**
   * OLD METHODS (Simulation) - Kept as fallback
   */
  
  async protect(req, res, next) {
    try {
      const { filename } = req.body;
      
      if (!filename) {
        return res.status(400).json({ error: 'Filename is required' });
      }

      const inputPath = path.join(__dirname, '../../uploads', filename);
      const result = await deepshieldService.protectImage(inputPath);

      res.json({
        success: true,
        message: 'Image protected successfully (simulation)',
        result,
        useRealAI: false
      });
    } catch (error) {
      next(error);
    }
  }

  async simulateDeepfake(req, res, next) {
    try {
      const { filename, isProtected } = req.body;
      
      if (!filename) {
        return res.status(400).json({ error: 'Filename is required' });
      }

      const inputPath = path.join(__dirname, '../../uploads', filename);
      const result = await deepshieldService.simulateDeepfake(inputPath, isProtected || false);

      res.json({
        success: true,
        message: 'Deepfake simulation completed',
        result
      });
    } catch (error) {
      next(error);
    }
  }

  async processComplete(req, res, next) {
    try {
      if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
      }

      const inputPath = path.join(__dirname, '../../uploads', req.file.filename);
      const result = await deepshieldService.processComplete(inputPath);

      res.json({
        success: true,
        message: 'Complete workflow processed (simulation)',
        result,
        useRealAI: false
      });
    } catch (error) {
      next(error);
    }
  }
}

module.exports = new ImageController();