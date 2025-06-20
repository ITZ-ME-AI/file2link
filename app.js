const express = require('express');
const multer = require('multer');
const ImageKit = require('imagekit');

const app = express();
const upload = multer({ storage: multer.memoryStorage() });

const imagekit = new ImageKit({
  publicKey: 'public_J2LWdBYDTxY8z0l3fKPMMq7lfak=',
  privateKey: 'private_2K+1aGgq4ATkxUq5B6w8NRq8lL0=',
  urlEndpoint: 'https://ik.imagekit.io/veltrixvision'
});

app.post('/upload', upload.single('image'), async (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: 'No file uploaded' });
  }

  try {
    const result = await imagekit.upload({
      file: req.file.buffer,
      fileName: req.file.originalname
    });
    res.json({ url: result.url });
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

app.get('/', (req, res) => {
  res.send(`
    <form action="/upload" method="post" enctype="multipart/form-data">
      <input type="file" name="image" />
      <button type="submit">Upload</button>
    </form>
  `);
});

app.use(express.static('public'));

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
}); 
