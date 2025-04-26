import express from 'express';
import multer from 'multer';
import path from 'path';
import { exec } from 'child_process';
import cors from 'cors';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const app = express();

// To replace __dirname in ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// Enable CORS for frontend
app.use(cors());

// Set up storage engine for multer
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, path.join(__dirname, 'uploads'));  // Save files in backend/uploads/
  },
  filename: (req, file, cb) => {
    cb(null, 'uploaded.csv');  // Save uploaded file always as 'uploaded.csv'
  }
});

const upload = multer({ storage });

// POST route to upload CSV and call Python script
app.post('/upload', upload.single('file'), (req, res) => {
  console.log('File uploaded:', req.file);

  // Call your Python script after upload
  exec('python app.py', { cwd: __dirname }, (error, stdout, stderr) => {
    if (error) {
      console.error(`Python error: ${error.message}`);
      return res.status(500).json({ error: 'Error running Python script' });
    }
    if (stderr) {
      console.error(`Python stderr: ${stderr}`);
    }
    console.log(`Python output: ${stdout}`);
    res.json({ message: 'File uploaded and processed successfully', output: stdout });
  });
});

// Start server
const PORT = 5000;
app.listen(PORT, () => {
  console.log(`Server started on http://localhost:${PORT}`);
});
