import React, { useState } from 'react';

const ImageUpload = ({ onImageUpload, isProcessing, uploadedImage }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file) => {
    // Validate file type
    if (!file.type.match('image.*')) {
      alert('Please upload an image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      alert('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    
    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewUrl(reader.result);
    };
    reader.readAsDataURL(file);

    // GỌI CALLBACK NGAY KHI UPLOAD
    if (onImageUpload) {
      onImageUpload(file);
    }
  };


  const handleClear = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
  };

  return (
    <div className="upload-section">
      <div className="section-header">
        <span className="step-number">1</span>
        <h3 className="section-title">Upload Source Identity</h3>
      </div>

      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''} ${previewUrl ? 'has-preview' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        {!previewUrl ? (
          <>
            <span className="material-symbols-outlined upload-icon">cloud_upload</span>
            <div className="upload-text">
              <p className="upload-title">Drop your image here</p>
              <p className="upload-subtitle">
                Supports JPG, PNG, GIF, WebP (Max 10MB). Images are processed locally for privacy.
              </p>
            </div>
            <label className="upload-button">
              <span>Select Image</span>
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleChange}
                style={{ display: 'none' }}
                disabled={isProcessing}
              />
            </label>
          </>
        ) : (
          <div className="preview-container">
            <img src={previewUrl} alt="Preview" className="preview-image" />
            <div className="preview-overlay">
              <div className="preview-info">
                <p className="file-name">{selectedFile?.name}</p>
                <p className="file-size">{(selectedFile?.size / 1024).toFixed(2)} KB</p>
              </div>
              <button className="clear-button" onClick={handleClear} disabled={isProcessing}>
                <span className="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>
        )}
      </div>

    </div>
  );
};

export default ImageUpload;