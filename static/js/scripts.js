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