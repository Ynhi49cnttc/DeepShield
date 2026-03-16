import React from 'react';

const Header = () => {
  return (
    <header className="header">
      <div className="header-content">
        <div className="logo-section">
          <span className="material-symbols-outlined shield-icon">shield_locked</span>
          <h1 className="project-title">DeepShield</h1>
        </div>
        <nav className="nav-links">
          <a href="#demo" className="nav-link active">Demo</a>
          <a href="#research" className="nav-link">Research</a>
          <a href="#methodology" className="nav-link">Methodology</a>
        </nav>
      </div>
      <div className="hero-section">
        <div className="badge">Academic Research Project</div>
        <h2 className="hero-title">
          Proactive Defense Against <span className="highlight">Deepfake</span> Generation
        </h2>
        <p className="hero-description">
          DeepShield protects digital identity by injecting invisible adversarial perturbations 
          into images, making them unusable for generative models while remaining visually 
          unchanged to humans.
        </p>
      </div>
    </header>
  );
};

export default Header;