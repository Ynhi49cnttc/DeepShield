import React from 'react';

const ResultVisualization = ({ results }) => {
  if (!results) return null;

  const { original, protected: protectedImg, deepfakeFromOriginal, deepfakeFromProtected } = results;

  return (
    <div className="results-section">
      <div className="section-header">
        <span className="step-number">3</span>
        <h3 className="section-title">Experimental Results</h3>
      </div>

      <div className="results-grid">
        {/* Original Image */}
        <div className="result-card">
          <div className="result-image-container">
            <img 
              src={original.url} 
              alt="Original" 
              className="result-image"
            />
            <div className="result-badge badge-neutral">Original</div>
          </div>
          <p className="result-label">Reference Image</p>
        </div>

        {/* Protected Image */}
        <div className="result-card featured">
          <div className="result-image-container protected">
            <img 
              src={protectedImg.url} 
              alt="Protected" 
              className="result-image"
            />
            <div className="result-badge badge-primary">DeepShield Protected</div>
            <div className="protection-overlay"></div>
          </div>
          <p className="result-label primary">Defended Image</p>
        </div>

        {/* Deepfake from Original */}
        <div className="result-card">
          <div className="result-image-container vulnerable">
            <img 
              src={deepfakeFromOriginal.url} 
              alt="Deepfake Original" 
              className="result-image"
            />
            <div className="result-badge badge-danger">Deepfake (Unprotected)</div>
            <span className="material-symbols-outlined status-icon danger">cancel</span>
          </div>
          <p className="result-label danger">Vulnerable Synthesis</p>
          <div className="metric-mini">
            Identity Match: {(parseFloat(deepfakeFromOriginal.metrics.identitySimilarity) * 100).toFixed(1)}%
          </div>
        </div>

        {/* Deepfake from Protected */}
        <div className="result-card">
          <div className="result-image-container success">
            <img 
              src={deepfakeFromProtected.url} 
              alt="Deepfake Protected" 
              className="result-image disrupted"
            />
            <div className="result-badge badge-success">Deepfake (Protected)</div>
            <div className="failed-overlay">
              <span className="failed-text">FAILED</span>
            </div>
            <span className="material-symbols-outlined status-icon success">check_circle</span>
          </div>
          <p className="result-label success">Disrupted Synthesis</p>
          <div className="metric-mini">
            Identity Match: {(parseFloat(deepfakeFromProtected.metrics.identitySimilarity) * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Visual Comparison */}
      <div className="comparison-section">
        <div className="comparison-card">
          <h4 className="comparison-title">Visual Quality Comparison</h4>
          <div className="slider-container">
            <div className="comparison-slider">
              <img src={original.url} alt="Original" className="comparison-img base" />
              <div className="comparison-overlay">
                <img src={protectedImg.url} alt="Protected" className="comparison-img overlay" />
              </div>
              <div className="slider-handle">
                <span className="material-symbols-outlined">unfold_more</span>
              </div>
            </div>
            <div className="slider-labels">
              <span className="label-left">Original</span>
              <span className="label-right">Protected</span>
            </div>
          </div>
          <p className="comparison-note">
            Perturbations are optimized to be invisible to the human eye while being fatal to AI synthesis.
          </p>
        </div>
      </div>
    </div>
  );
};

export default ResultVisualization;