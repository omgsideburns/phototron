import express from 'express';
import { createServer } from 'http';
import { Server as SocketIO } from 'socket.io';
import Webcam from 'node-webcam';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import compositeRoute from './routes/composite.js';
import { config } from './config.js';

const app = express();

app.use(express.json({ limit: '5mb' }));
app.use((req, res, next) => {
    if (req.is('application/json')) {
        next();
    } else {
        let data = '';
        req.on('data', chunk => {
            data += chunk;
        });
        req.on('end', () => {
            if (!data) return next(); // skip empty bodies
            try {
                req.body = JSON.parse(data);
                next();
            } catch (err) {
                console.warn('❌ Failed to parse JSON body:', data);
                next();
            }
        });
    }
});

// testing browser snaps instead of imagesnap
import uploadBrowserPhoto from './routes/upload-browser-photo.js';
app.use(uploadBrowserPhoto);
// end browser test

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.json({ limit: '5mb' }));

const http = createServer(app);
const io = new SocketIO(http);

const { app: appConfig, camera: camConfig, paths } = config;

app.use(compositeRoute);

// Webcam setup using config
const cam = Webcam.create({
    width: parseInt(camConfig.resolution.split('x')[0]),
    height: parseInt(camConfig.resolution.split('x')[1]),
    delay: camConfig.delay || 0,
    saveShots: true,
    output: camConfig.outputFormat || 'jpeg',
    device: camConfig.device || false,
    callbackReturn: "location",
    verbose: !!appConfig.debug
});

// Static assets
app.use(express.static(path.join(__dirname, paths.public)));
app.use('/captured', express.static(path.join(__dirname, paths.captured)));

// Routes
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, paths.public, 'index.html'));
});

// Sockets
io.on('connection', (socket) => {
    console.log('User connected');

    socket.on('take-photo', () => {
        console.log('📸 take-photo event received');
        const timestamp = Date.now();
        const filename = `photo_${timestamp}.jpg`;
        const filepath = path.join(__dirname, paths.captured, filename);

        cam.capture(filepath, (err, data) => {
            if (err) {
                console.error('❌ Capture error:', err);
                socket.emit('photo-error');
                return;
            }

            console.log('✅ Photo captured:', filename);
            socket.emit('photo-taken', { path: `/captured/${filename}`, filename });
        });
    });

    socket.on('print-photo', (filename) => {
        const photoPath = path.join(__dirname, paths.captured, filename);

        if (!fs.existsSync(photoPath)) {
            socket.emit('print-error', 'File not found');
            return;
        }

        exec(`lp "${photoPath}"`, (error, stdout, stderr) => {
            if (error) {
                console.error(`🖨️ Print error: ${error.message}`);
                socket.emit('print-error', error.message);
                return;
            }
            console.log(`🖨️ Printed: ${stdout.trim()}`);
            socket.emit('print-success', stdout.trim());
        });
    });
});

// Start server
http.listen(appConfig.port, () => {
    console.log(`🚀 Phototron running at http://localhost:${appConfig.port}`);
});