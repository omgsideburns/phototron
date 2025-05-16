const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const Webcam = require('node-webcam');
const Jimp = require('jimp');
const fs = require('fs');
const path = require('path');
const { exec } = require('child_process'); // using exec for printing

const PORT = 3000;

// Configure webcam
const cam = Webcam.create({
    width: 1280,
    height: 720,
    delay: 0,
    saveShots: true,
    output: "jpeg",
    device: false,
    callbackReturn: "location",
    verbose: true // 👈 enables debug logging
});

app.use(express.static(path.join(__dirname, 'public')));
app.set('view engine', 'ejs');

// ROUTES
app.get('/', (req, res) => {
    res.render('index');
});

// SOCKETS
io.on('connection', (socket) => {
    console.log('User connected');

    socket.on('take-photo', async () => {
        console.log('📸 take-photo event received');
        const timestamp = Date.now();
        const filename = `photo_${timestamp}.jpg`;
        const filepath = path.join(__dirname, 'captured', filename);

        cam.capture(filepath, async (err, data) => {
            if (err) {
                console.error('Capture error:', err);
                socket.emit('photo-error');
                return;
            }

            console.log('✅ Photo captured:', filename);
            socket.emit('photo-taken', { path: `/captured/${filename}`, filename });
        });
    });

    // Handle print request
    socket.on('print-photo', (filename) => {
        const photoPath = path.join(__dirname, 'captured', filename);

        if (!fs.existsSync(photoPath)) {
            socket.emit('print-error', 'File not found');
            return;
        }

        exec(`lp "${photoPath}"`, (error, stdout, stderr) => {
            if (error) {
                console.error(`Print error: ${error.message}`);
                socket.emit('print-error', error.message);
                return;
            }
            console.log(`🖨️ Printed: ${stdout.trim()}`);
            socket.emit('print-success', stdout.trim());
        });
    });
});

// Serve captured photos
app.use('/captured', express.static(path.join(__dirname, 'captured')));

http.listen(PORT, () => {
    console.log(`PhotoBooth running at http://localhost:${PORT}`);
});