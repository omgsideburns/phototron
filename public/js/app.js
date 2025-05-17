const socket = io();
const video = document.getElementById('preview');
const output = document.getElementById('output');

// Try to start camera preview
navigator.mediaDevices.getUserMedia({ video: true })
  .then(stream => video.srcObject = stream)
  .catch(err => console.error('Camera error:', err));

// When capture button is clicked, ask server to take a photo
document.getElementById('capture').addEventListener('click', () => {
  socket.emit('take-photo');
});

// When photo is taken, show preview
socket.on('photo-taken', data => {
  output.innerHTML = `<img src="${data.path}" width="300">`;
});