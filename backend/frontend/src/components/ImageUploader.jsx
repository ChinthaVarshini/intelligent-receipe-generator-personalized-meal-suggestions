import React, { useRef, useState } from 'react';

const ImageUploader = ({ onUpload, loading }) => {
  const fileInputRef = useRef(null);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [cameraOpen, setCameraOpen] = useState(false);

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      onUpload(file);
    }
  };

  const handleDrop = (event) => {
    event.preventDefault();
    const file = event.dataTransfer.files[0];
    if (file) {
      onUpload(file);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const handleCameraClick = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      videoRef.current.srcObject = stream;
      videoRef.current.style.display = 'block';
      canvasRef.current.style.display = 'none';
      setCameraOpen(true);
    } catch (error) {
      console.error('Error accessing camera:', error);
      alert('Camera access denied or not available.');
    }
  };

  const handleCapture = () => {
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    canvas.toBlob((blob) => {
      const file = new File([blob], 'captured-image.png', { type: 'image/png' });
      onUpload(file);
      // Stop the camera stream
      const stream = video.srcObject;
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
      video.style.display = 'none';
      canvas.style.display = 'none';
      setCameraOpen(false);
    });
  };

  return (
    <div className="image-uploader">
      <div
        className="upload-area"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current.click()}
      >
        <p>Drag and drop an image here, or click to select a file</p>
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept="image/*"
          style={{ display: 'none' }}
        />
      </div>
      <button className="camera-button" onClick={handleCameraClick}>
        📷 Open Camera
      </button>
      <video ref={videoRef} style={{ display: 'none', width: '100%', maxWidth: '400px' }} autoPlay></video>
      <canvas ref={canvasRef} style={{ display: 'none' }}></canvas>
      {cameraOpen && (
        <button className="capture-button" onClick={handleCapture}>
          📸 Capture
        </button>
      )}
      {loading && <p>Processing image...</p>}
    </div>
  );
};

export default ImageUploader;
