import express from 'express';
import fs from 'fs';
import path from 'path';
import { Jimp } from 'jimp';

const router = express.Router();

router.post('/upload-browser-photo', async (req, res) => {
  try {
    const { imageData, template } = req.body;
    if (!imageData || typeof imageData !== 'string') {
      return res.status(400).json({ error: 'Missing or invalid imageData' });
    }

    // Strip base64 prefix and decode (support any image MIME type)
    const base64Data = imageData.replace(/^data:image\/\w+;base64,/, '');
    const buffer = Buffer.from(base64Data, 'base64');

    console.log('📦 Buffer size:', buffer.length);

    // Save raw photo to captured folder
    const filename = `photo_${Date.now()}.jpg`;
    const photoPath = path.join(process.cwd(), 'captured', filename);

    const image = await Jimp.read(buffer);

    if (typeof image.write !== 'function') {
      console.warn('⚠️ Jimp image did not load correctly:', image);
      return res.status(500).json({ error: 'Jimp failed to load image' });
    }

    console.log('✅ Image read:', image.constructor.name);
    await image.write(photoPath);

    // Call composite route internally
    const compositeRes = await fetch('http://localhost:3000/composite', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        template: template || 'classic',
        photos: [filename]
      })
    });

    const compositeText = await compositeRes.text();
    console.log("🧩 Composite response:", compositeText);

    let compositeData;
    try {
      compositeData = JSON.parse(compositeText);
      res.json(compositeData);
    } catch (e) {
      console.error("❌ Composite JSON parse failed:", e);
      res.status(500).json({ error: 'Invalid composite response' });
    }
  } catch (err) {
    console.error('Upload error:', err);
    res.status(500).json({ error: 'Failed to process uploaded image' });
  }
});

export default router;
