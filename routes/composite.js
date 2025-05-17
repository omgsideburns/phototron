// composite.js
// puts captures onto a template..

import express from 'express';
import fs from 'fs';
import path from 'path';
import { Jimp } from 'jimp';

const router = express.Router();

router.post('/composite', async (req, res) => {
  const { template, photos } = req.body;
  if (!template || !Array.isArray(photos) || photos.length === 0) {
    return res.status(400).json({ error: 'Missing template or photo list' });
  }

  const templateDir = path.join(path.resolve(), 'templates', template);
  const layoutPath = path.join(templateDir, 'layout.json');
  const bgPath = path.join(templateDir, 'background.png');

  try {
    const layout = JSON.parse(fs.readFileSync(layoutPath, 'utf8'));
    const slots = layout.layouts[photos.length.toString()];
    if (!slots) {
      return res.status(400).json({ error: `No layout for ${photos.length} photo(s)` });
    }

  const background = await Jimp.read(bgPath);
    const images = await Promise.all(
      photos.map(filename => Jimp.read(path.join(path.resolve(), 'captured', filename)))
    );

    slots.forEach((slot, idx) => {
      if (images[idx]) {
        images[idx].resize({ w: slot.width, h: slot.height });
        background.composite(images[idx], slot.x, slot.y);
      }
    });

    const outputFilename = `composited_${Date.now()}.jpg`;
    const outputPath = path.join(path.resolve(), 'captured', outputFilename);
    await background.write(outputPath, { quality: 90 });

    res.json({ path: `/captured/${outputFilename}` });
  } catch (err) {
    console.error('Composite error:', err);
    res.status(500).json({ error: 'Failed to generate composite' });
  }
});

export default router;