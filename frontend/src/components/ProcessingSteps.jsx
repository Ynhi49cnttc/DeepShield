import React from 'react';

const ProcessingSteps = ({ currentStep }) => {
  const steps = [
    {
      number: 1,
      title: 'Image Upload',
      description: 'Securely upload your source facial image',
      icon: 'cloud_upload'
    },
    {
      number: 2,
      title: 'Noise Injection',
      description: 'Apply adversarial perturbations to disrupt neural encoding',
      icon: 'auto_fix_high'
    },
    {
      number: 3,
      title: 'Deepfake Simulation',
      description: 'Test protection against face-swapping models',
      icon: 'science'
    },
    {
      number: 4,
      title: 'Results Analysis',
      description: 'Compare protected vs unprotected outputs',
      icon: 'analytics'
    }
  ];

  return (
    <div className="processing-steps">
      <h3 className="steps-title">How It Works</h3>
      <div className="steps-container">
        {steps.map((step, index) => (
          <div 
            key={step.number} 
            className={`step-item ${currentStep >= step.number ? 'active' : ''} ${currentStep === step.number ? 'current' : ''}`}
          >
            <div className="step-icon-container">
              <div className="step-number">{step.number}</div>
              <span className="material-symbols-outlined step-icon">{step.icon}</span>
            </div>
            <div className="step-content">
              <h4 className="step-title">{step.title}</h4>
              <p className="step-description">{step.description}</p>
            </div>
            {index < steps.length - 1 && <div className="step-connector"></div>}
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProcessingSteps;