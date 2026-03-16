import React from 'react';

const MethodSelector = ({ onMethodChange, selectedMethod, disabled }) => {
  const methods = [
    {
      id: 'deepshield',
      name: 'DeepShield',
      description: 'Our method - Dual anti-anchors with trajectory-based attack',
      color: '#1152d4',
      recommended: true
    },
    {
      id: 'photoguard',
      name: 'PhotoGuard',
      description: 'Baseline - Direct encoder disruption',
      color: '#059669'
    },
    {
      id: 'advdm',
      name: 'AdvDM',
      description: 'Baseline - Diffusion model latent attack',
      color: '#dc2626'
    },
    {
      id: 'mist',
      name: 'Mist',
      description: 'Baseline - Fused semantic & textural loss',
      color: '#7c3aed'
    }
  ];

  return (
    <div className="method-selector">
      <div className="section-header">
        <span className="step-number">2</span>
        <h3 className="section-title">Select Protection Method</h3>
      </div>

      <div className="methods-grid">
        {methods.map((method) => (
          <div
            key={method.id}
            className={`method-card ${selectedMethod === method.id ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
            onClick={() => !disabled && onMethodChange(method.id)}
            style={{ 
              borderColor: selectedMethod === method.id ? method.color : 'transparent',
              cursor: disabled ? 'not-allowed' : 'pointer'
            }}
          >
            {method.recommended && (
              <div className="recommended-badge">Recommended</div>
            )}
            
            <div className="method-header">
              <div 
                className="method-icon" 
                style={{ 
                  backgroundColor: `${method.color}20`, 
                  color: method.color 
                }}
              >
                <span className="material-symbols-outlined">shield</span>
              </div>
              <h4 className="method-name">{method.name}</h4>
            </div>

            <p className="method-description">{method.description}</p>

            {selectedMethod === method.id && (
              <div className="selected-indicator">
                <span className="material-symbols-outlined">check_circle</span>
                <span>Selected</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default MethodSelector;