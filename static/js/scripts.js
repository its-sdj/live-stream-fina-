// Example: Fetch recorded videos dynamically
document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/recorded_videos')
        .then(response => response.json())
        .then(data => {
            const videoList = document.getElementById('video-list');
            data.forEach(video => {
                const videoItem = document.createElement('div');
                videoItem.innerHTML = `<video controls><source src="${video.url}" type="video/mp4"></video>`;
                videoList.appendChild(videoItem);
            });
        });
});
// Replace the captureAndSend function with this:

function captureAndSend() {
    const canvas = document.createElement('canvas');
    canvas.width = preview.videoWidth;
    canvas.height = preview.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(preview, 0, 0, canvas.width, canvas.height);
    
    canvas.toBlob(blob => {
        const reader = new FileReader();
        reader.onload = () => {
            socket.emit('stream_frame', reader.result);
        };
        reader.readAsDataURL(blob);
    }, 'image/jpeg', 0.8);
    
    if (stream_status.live) {
        setTimeout(captureAndSend, 100); // ~10 FPS
    }
}

// Update start button handler:
startBtn.addEventListener('click', async () => {
    try {
        mediaStream = await navigator.mediaDevices.getDisplayMedia({
            video: { displaySurface: 'browser' },
            audio: false
        });
        preview.srcObject = mediaStream;
        
        // Start stream on server
        const response = await fetch('/start_stream');
        if (response.ok) {
            statusElement.textContent = 'LIVE';
            startBtn.disabled = true;
            stopBtn.disabled = false;
            captureAndSend();
        }
    } catch (err) {
        console.error("Error:", err);
    }
});