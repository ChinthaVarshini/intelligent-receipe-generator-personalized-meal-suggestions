import React, { useRef, useState, useCallback } from 'react';
import Webcam from 'react-webcam';
import './CameraModal.css';

const CameraModal = ({ isOpen, onClose, onCapture }) => {
  const webcamRef = useRef(null);
  const [facingMode, setFacingMode] = useState('environment'); // Default to back camera on mobile
  const [isCapturing, setIsCapturing] = useState(false);

  const capture = useCallback(() => {
    if (webcamRef.current) {
      setIsCapturing(true);
      const imageSrc = webcamRef.current.getScreenshot();
      if (imageSrc) {
        // Convert base64 to blob
        fetch(imageSrc)
          .then(res => res.blob())
          .then(blob => {
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
            onCapture(file);
            setIsCapturing(false);
            onClose();
          })
          .catch(err => {
            console.error('Error converting image:', err);
            setIsCapturing(false);
          });
      } else {
        setIsCapturing(false);
      }
    }
  }, [webcamRef, onCapture, onClose]);

  const toggleCamera = () => {
    setFacingMode(facingMode === 'user' ? 'environment' : 'user');
  };

  if (!isOpen) return null;

  const videoConstraints = {
    width: 1280,
    height: 720,
    facingMode: facingMode
  };

  return (
    <div className="camera-modal-overlay" onClick={onClose}>
      <div className="camera-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="camera-modal-header">
          <h3>📸 Take Photo</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="camera-container">
          <Webcam
            audio={false}
            ref={webcamRef}
            screenshotFormat="image/jpeg"
            videoConstraints={videoConstraints}
            className="camera-feed"
          />

          <div className="camera-controls">
            <button
              className="camera-btn toggle-camera"
              onClick={toggleCamera}
              title="Switch Camera"
            >
              🔄
            </button>

            <button
              className="camera-btn capture-btn"
              onClick={capture}
              disabled={isCapturing}
            >
              {isCapturing ? '⏳' : '📸'}
            </button>
          </div>
        </div>

        <div className="camera-instructions">
          <p>Position ingredients clearly in frame and tap the camera button</p>
        </div>
      </div>
    </div>
  );
};

export default CameraModal;
