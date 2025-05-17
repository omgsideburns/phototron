// take.js

const socket = io();

const promptSection = document.getElementById('prompt');
const statusSection = document.getElementById('status');
const previewSection = document.getElementById('preview');
const statusText = document.getElementById('status-text');
const finalImage = document.getElementById('final-image');
const countdownText = document.getElementById('countdown');
const printBtn = document.getElementById('print-btn');

const cameraWrapper = document.getElementById('camera-wrapper');
const cameraPreview = document.getElementById('camera-preview');
const countdownOverlay = document.getElementById('countdown-overlay');
const whiteFlash = document.getElementById('white-flash');

let countdownTimer = null;

// start the webcam preview
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => {
    cameraPreview.srcObject = stream;
  })
  .catch(err => {
    console.error('Camera error:', err);
    statusText.textContent = "Couldn’t start camera.";
  });

function showStatus(message) {
  promptSection.style.display = 'none';
  statusSection.style.display = 'block';
  statusText.textContent = message;
}

function showPreview(imagePath) {
  statusSection.style.display = 'none';
  cameraWrapper.style.display = 'none';
  previewSection.style.display = 'block';
  finalImage.src = imagePath;

  let seconds = 10;
  countdownText.textContent = `Returning to start in ${seconds}...`;
  countdownTimer = setInterval(() => {
    seconds--;
    countdownText.textContent = `Returning to start in ${seconds}...`;
    if (seconds <= 0) {
      clearInterval(countdownTimer);
      location.href = '/';
    }
  }, 1000);
}

function startCountdownAndCapture() {
  let countdown = 3;
  countdownOverlay.textContent = countdown;
  cameraWrapper.style.display = 'block';

  console.log("GPIO: flash ON");

  const interval = setInterval(() => {
    countdown--;
    if (countdown > 0) {
      countdownOverlay.textContent = countdown;
    } else {
      clearInterval(interval);
      countdownOverlay.textContent = '';
      whiteFlash.style.display = 'block';

      setTimeout(() => {
        whiteFlash.style.display = 'none';
        console.log("📸 Capturing browser photo...");

        const canvas = document.createElement('canvas');
        canvas.width = cameraPreview.videoWidth;
        canvas.height = cameraPreview.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(cameraPreview, 0, 0);

        const jpegData = canvas.toDataURL('image/jpeg', 0.95);

        fetch('/upload-browser-photo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ imageData: jpegData, template: 'classic' })
        })
          .then(res => res.json())
          .then(result => {
            if (result.path) {
              showPreview(result.path);
            } else {
              statusText.textContent = "Compositing failed.";
            }
          })
          .catch(err => {
            console.error("Composite error:", err);
            statusText.textContent = "Compositing failed.";
          });
      }, 150);
    }
  }, 1000);
}

document.querySelector('[data-count="1"]').addEventListener('click', () => {
  showStatus('Get ready...');
  startCountdownAndCapture();
});

socket.on('photo-taken', (data) => {
  fetch('/composite', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      template: 'classic',
      photos: [data.filename]
    })
  })
    .then(res => res.json())
    .then(result => {
      if (result.path) {
        showPreview(result.path);
      } else {
        statusText.textContent = "Compositing failed.";
      }
    })
    .catch(err => {
      console.error("Composite error:", err);
      statusText.textContent = "Compositing failed.";
    });
});

printBtn.addEventListener('click', () => {
  const filename = finalImage.src.split('/').pop();
  socket.emit('print-photo', filename);
});