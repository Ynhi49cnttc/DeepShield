const express = require('express');
const router = express.Router();
const upload = require('../middleware/upload.middleware');
const imageController = require('../controllers/image.controller');

/**
 * @route   POST /api/images/upload
 * @desc    Upload a facial image
 * @access  Public
 */
router.post('/upload', upload.single('image'), imageController.upload);

/**
 * ==================== NEW AI ENDPOINTS ====================
 * These endpoints use the Python AI service for real model inference
 */

/**
 * @route   POST /api/images/protect-ai
 * @desc    Apply DeepShield protection using real AI service
 * @access  Public
 */
router.post('/protect-ai', imageController.protectWithAI);

/**
 * @route   POST /api/images/compare-ai
 * @desc    Compare all protection methods using AI
 * @access  Public
 */
router.post('/compare-ai', imageController.compareMethodsWithAI);

/**
 * @route   POST /api/images/process-complete-ai
 * @desc    Complete workflow with real AI
 * @access  Public
 */
router.post('/process-complete-ai', upload.single('image'), imageController.processCompleteWithAI);

/**
 * @route   GET /api/images/ai-status
 * @desc    Check if AI service is available
 * @access  Public
 */
router.get('/ai-status', imageController.checkAIService);

/**
 * ==================== OLD ENDPOINTS (Simulation) ====================
 * Kept for backward compatibility and as fallback
 */

/**
 * @route   POST /api/images/protect
 * @desc    Apply protection (simulation)
 * @access  Public
 */
router.post('/protect', imageController.protect);

/**
 * @route   POST /api/images/simulate-deepfake
 * @desc    Simulate deepfake generation
 * @access  Public
 */
router.post('/simulate-deepfake', imageController.simulateDeepfake);

/**
 * @route   POST /api/images/process-complete
 * @desc    Complete workflow (simulation)
 * @access  Public
 */
router.post('/process-complete', upload.single('image'), imageController.processComplete);

module.exports = router;