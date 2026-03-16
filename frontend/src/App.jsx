import { useState, useEffect } from 'react';
import Header from './components/Header';
import ImageUpload from './components/ImageUpload';
import ProcessingSteps from './components/ProcessingSteps';
import ResultVisualization from './components/ResultVisualization';
import MetricsDisplay from './components/MetricsDisplay';
import { imageAPI } from './services/api';
import './index.css';

function App() {
  const [uploadedImage, setUploadedImage] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [aiAvailable, setAiAvailable] = useState(false);

  useEffect(() => {
    checkAI();
  }, []);

  const checkAI = async () => {
    try {
      const status = await imageAPI.checkAIStatus();
      setAiAvailable(status.aiServiceAvailable);
      console.log('✅ AI Service connected:', status.aiServiceStatus);
    } catch (err) {
      console.error('❌ AI check failed:', err);
      setAiAvailable(false);
    }
  };

  const handleImageUpload = (file) => {
    console.log('📷 Image uploaded:', file.name);
    setUploadedImage(file);
    setResults(null);
    setError(null);
    setCurrentStep(0);
  };

  const handleProtect = async () => {
    console.log('🔵 PROTECT BUTTON CLICKED!');
    console.log('📷 uploadedImage:', uploadedImage);
    
    if (!uploadedImage) {
      console.log('❌ No image!');
      alert('Please upload an image first!');
      return;
    }

    console.log('🚀 Starting protection...');
    console.log('🤖 AI Available:', aiAvailable);

    setIsProcessing(true);
    setError(null);
    setCurrentStep(1);

    try {
      console.log('📡 Calling API...');
      
      // GỌI API MỚI
      const response = aiAvailable
        ? await imageAPI.processCompleteWithAI(uploadedImage, 'deepshield')
        : await imageAPI.processComplete(uploadedImage);

      console.log('✅ API Response:', response);
      
      setCurrentStep(2);

      if (response.success) {
        console.log('🎉 Success!');
        console.log('🤖 Using Real AI:', response.result.useRealAI);
        setResults(response.result);
        setCurrentStep(3);
      } else {
        console.log('❌ API Error:', response.error);
        setError(response.error || 'Protection failed');
        setCurrentStep(0);
      }
    } catch (err) {
      console.error('💥 EXCEPTION:', err);
      console.error('Message:', err.message);
      console.error('Stack:', err.stack);
      setError(err.message || 'An error occurred');
      setCurrentStep(0);
    } finally {
      setIsProcessing(false);
      console.log('🏁 Processing finished');
    }
  };

  return (
    <div className="app">
      <Header />
      
      {aiAvailable && (
        <div style={{
          background: 'linear-gradient(135deg, #1152d4 0%, #0d3ea8 100%)',
          color: 'white',
          padding: '0.75rem 0',
          textAlign: 'center',
          fontWeight: '600'
        }}>
          ✅ Real AI Enabled - Using DeepShield Protection
        </div>
      )}
      
      <main className="main-content">
        <div className="container">
          
          <ImageUpload
            onImageUpload={handleImageUpload}
            isProcessing={isProcessing}
            uploadedImage={uploadedImage}
          />

          {uploadedImage && !results && (
            <div style={{ textAlign: 'center', margin: '2rem 0' }}>
              <button
                onClick={handleProtect}
                disabled={isProcessing}
                style={{
                  background: isProcessing ? '#059669' : '#1152d4',
                  color: 'white',
                  border: 'none',
                  padding: '1.25rem 2rem',
                  fontSize: '1.125rem',
                  fontWeight: '700',
                  borderRadius: '0.75rem',
                  cursor: isProcessing ? 'not-allowed' : 'pointer',
                  opacity: isProcessing ? 0.7 : 1,
                  transition: 'all 0.3s'
                }}
              >
                {isProcessing ? '⏳ Processing...' : '🛡️ Protect Image with DeepShield'}
              </button>
              
              {aiAvailable && !isProcessing && (
                <p style={{ marginTop: '1rem', color: '#059669', fontWeight: '600' }}>
                  ✅ Real AI Ready
                </p>
              )}
              
              {isProcessing && (
                <p style={{ marginTop: '1rem', color: '#0369a1' }}>
                  ⏰ Processing with real AI models (60-120 seconds)...
                </p>
              )}
            </div>
          )}

          {isProcessing && <ProcessingSteps currentStep={currentStep} />}
          
          {error && (
            <div style={{ 
              padding: '1.25rem', 
              background: '#fef2f2', 
              color: '#dc2626', 
              borderRadius: '0.75rem', 
              margin: '1.5rem 0',
              border: '2px solid #fecaca'
            }}>
              ❌ Error: {error}
            </div>
          )}

          {results && (
            <>
              <ResultVisualization results={results} />
              <MetricsDisplay results={results} />
              
              <div style={{ textAlign: 'center', margin: '2rem 0' }}>
                {results.useRealAI ? (
                  <div style={{ 
                    background: '#d1fae5', 
                    color: '#065f46', 
                    padding: '1rem 2rem',
                    borderRadius: '999px',
                    display: 'inline-block',
                    fontWeight: '600',
                    border: '2px solid #10b981'
                  }}>
                    ✅ Protected with Real AI - DeepShield Algorithm
                  </div>
                ) : (
                  <div style={{ 
                    background: '#fef3c7', 
                    color: '#92400e', 
                    padding: '1rem 2rem',
                    borderRadius: '999px',
                    display: 'inline-block',
                    fontWeight: '600'
                  }}>
                    ⚠️ Simulation Mode (AI Service Unavailable)
                  </div>
                )}
              </div>

              <div style={{ textAlign: 'center', margin: '2rem 0' }}>
                <button
                  onClick={() => {
                    setUploadedImage(null);
                    setResults(null);
                    setError(null);
                    setCurrentStep(0);
                  }}
                  style={{
                    background: 'white',
                    color: '#1152d4',
                    border: '2px solid #1152d4',
                    padding: '1rem 2rem',
                    fontSize: '1rem',
                    fontWeight: '600',
                    borderRadius: '0.75rem',
                    cursor: 'pointer'
                  }}
                >
                  🔄 Protect Another Image
                </button>
              </div>
            </>
          )}

        </div>
      </main>
    </div>
  );
}

export default App;