function LiveCamera() {
  const token = localStorage.getItem("token");

  return (
    <>
      <div className="page-header">
        <span className="page-title">กล้องเรียลไทม์</span>
      </div>

      <div className="camera-box">
        <img
          src={`http://localhost:8000/video_feed?token=${token}`}
          alt="ภาพกล้องแบบเรียลไทม์"
        />
      </div>
    </>
  );
}

export default LiveCamera;
