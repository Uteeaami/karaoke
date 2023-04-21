import React, { useState, useRef, useEffect } from 'react';

function VideoPlayer({videosrc, videoname}) {
  const videoRef = useRef(null);
  const [showVideo, setShowVideo] = useState(false);

  useEffect(() => {
    if (showVideo && videoRef.current) {
      videoRef.current.requestFullscreen().then(() => {
        videoRef.current.play();
      });
      document.addEventListener("fullscreenchange", handleFullScreenChange);
    }
    return () => {
      document.removeEventListener("fullscreenchange", handleFullScreenChange);
    };
  }, [showVideo]);

  const handlePlayClick = () => {
    setShowVideo(true);
  };
  
  const handleFullScreenChange = () => {
    if (!document.fullscreenElement) {
      setShowVideo(false);
      videoRef.current.pause();
    }
  };

  return (
    <div className='video-container mt-5'>
      {showVideo && (
        <video ref={videoRef} controls>
          <source src={videosrc} type="video/webm" />
        </video>
      )}
      {!showVideo && (
        <button className="btn btn-info btn-lg custombtn" onClick={handlePlayClick}>{videoname}</button>
      )}
    </div>
  );
}

export default VideoPlayer;
