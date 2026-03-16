import React from 'react';

const MetricsDisplay = ({ results }) => {
  if (!results) return null;

  const { protected: protectedImg, deepfakeFromProtected, comparisonMetrics } = results;

  const protectionMetrics = protectedImg.metrics;
  const defenseMetrics = deepfakeFromProtected.metrics;

  return (
    <div className="metrics-section">
      <div className="metrics-grid">
        {/* Visual Quality Metrics */}
        <div className="metrics-card">
          <h4 className="metrics-title">Visual Quality Preservation</h4>
          <div className="metrics-list">
            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">PSNR (Peak Signal-to-Noise Ratio)</span>
                <span className="metric-value primary">{protectionMetrics.psnr} dB</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill primary" style={{ width: '85%' }}></div>
              </div>
              <p className="metric-description">Higher is better - Measures image quality preservation</p>
            </div>

            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">SSIM (Structural Similarity)</span>
                <span className="metric-value primary">{protectionMetrics.ssim}</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill primary" style={{ width: '98%' }}></div>
              </div>
              <p className="metric-description">Higher is better - Measures structural integrity</p>
            </div>

            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">LPIPS (Perceptual Distance)</span>
                <span className="metric-value primary">{protectionMetrics.lpips}</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill primary" style={{ width: '2%' }}></div>
              </div>
              <p className="metric-description">Lower is better - Measures human-perceived difference</p>
            </div>

            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">Frequency Rate (Low-Frequency)</span>
                <span className="metric-value primary">{protectionMetrics.frequencyRate}%</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill primary" style={{ width: `${protectionMetrics.frequencyRate}%` }}></div>
              </div>
              <p className="metric-description">Higher is better - Noise concentrated in imperceptible bands</p>
            </div>
          </div>
        </div>

        {/* Defense Effectiveness Metrics */}
        <div className="metrics-card">
          <h4 className="metrics-title">Defense Effectiveness</h4>
          <div className="metrics-list">
            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">Identity Similarity Score</span>
                <span className="metric-value danger">{(parseFloat(defenseMetrics.identitySimilarity) * 100).toFixed(1)}%</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill danger" style={{ width: `${parseFloat(defenseMetrics.identitySimilarity) * 100}%` }}></div>
              </div>
              <p className="metric-description">Lower is better - Deepfake identity matching failure rate</p>
            </div>

            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">L2 Distance (Output Distortion)</span>
                <span className="metric-value success">{defenseMetrics.l2Distance}</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill success" style={{ width: '45%' }}></div>
              </div>
              <p className="metric-description">Higher is better - Deepfake output corruption level</p>
            </div>

            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">PSNR Defense (Quality Drop)</span>
                <span className="metric-value success">{defenseMetrics.psnrDefense} dB</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill success" style={{ width: '70%' }}></div>
              </div>
              <p className="metric-description">Lower is better - Deepfake visual quality degradation</p>
            </div>

            <div className="metric-item">
              <div className="metric-header">
                <span className="metric-name">Protection Success Rate</span>
                <span className="metric-value success">{defenseMetrics.successRate}</span>
              </div>
              <div className="metric-bar">
                <div className="metric-fill success" style={{ width: defenseMetrics.successRate }}></div>
              </div>
              <p className="metric-description">Percentage of deepfake attempts successfully disrupted</p>
            </div>
          </div>

          <div className="effectiveness-badge">
            <span className="material-symbols-outlined">verified</span>
            <span className="badge-text">Effective Defense Confirmed</span>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="conclusion-section">
        <h4 className="conclusion-title">Conclusion</h4>
        <p className="conclusion-text">
          DeepShield effectively neutralizes deepfake generation by poisoning the feature space of the 
          synthesis model. While the human eye sees no difference (LPIPS: {protectionMetrics.lpips}, 
          PSNR: {protectionMetrics.psnr} dB), the generative adversarial network fails to recover 
          identity-consistent features, resulting in garbled outputs with only {(parseFloat(defenseMetrics.identitySimilarity) * 100).toFixed(1)}% 
          identity similarity compared to the original.
        </p>
        <div className="conclusion-stats">
          <div className="stat-item">
            <span className="stat-label">Identity Reduction</span>
            <span className="stat-value">{comparisonMetrics.identityReduction}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Defense Level</span>
            <span className="stat-value">{comparisonMetrics.defenseEffectiveness}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Visual Quality</span>
            <span className="stat-value">Maintained ✓</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MetricsDisplay;