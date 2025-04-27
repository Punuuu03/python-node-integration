import express from 'express';
import multer from 'multer';
import path from 'path';
import fs from 'fs';
import csv from 'csv-parser';
import cors from 'cors';
import { GoogleGenerativeAI } from '@google/generative-ai';
import { fileURLToPath } from 'url';

// Handle __dirname and __filename in ESM
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());

// --- Configuration ---
const GEMINI_API_KEY = 'AIzaSyC-jFHHfOHCCkF3MiQ52ZNpm4oq3V79xF0';
const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);

// --- File Upload Setup ---
const uploadFolder = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadFolder)) {
  fs.mkdirSync(uploadFolder);
}
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, uploadFolder);
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + '-' + file.originalname);
  }
});
const upload = multer({ storage });

// --- Gemini API Call Functions ---
async function callGeminiForSummary(caseDataText) {
  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-pro-latest' });  // Updated model
  const prompt = `
  Based on the following crime case details, please provide a detailed summary.
  Include key aspects such as the type of crime, location (if available), the main circumstances, and any additional relevant details.
  The summary should be comprehensive and provide a clear understanding of the case in a detailed paragraph.
  
  Case Details:
  ---
  ${caseDataText}
  ---
  Write the Summary directly without adding extra headers.
  `;
  
  try {
    console.log("Calling Gemini API for Summary...");
    await new Promise(r => setTimeout(r, 5000)); // Sleep 5 seconds
    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  } catch (error) {
    console.error('Error generating summary:', error);
    return "Error generating summary.";
  }
}

async function callGeminiForPriority(caseDataText) {
  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-pro-latest' });  // Updated model
  const prompt = `
Analyze the following crime case details carefully.

1. Assign a Priority Level: High, Medium, or Low.
2. Provide a detailed explanation for your choice of priority. Discuss all the relevant aspects from the case, including the type of crime, location, and any other factors that influenced your decision.
3. Format your answer strictly like this:

Priority Level: <High/Medium/Low>
Reasoning: <your detailed explanation, including all aspects that influenced the priority level>

Do not add any extra text.

Case Details:
---
${caseDataText}
---
`;

  try {
    console.log("Calling Gemini API for Priority...");
    await new Promise(r => setTimeout(r, 10000)); // Sleep 10 seconds
    const result = await model.generateContent(prompt);
    const response = await result.response;
    return response.text();
  } catch (error) {
    console.error('Error generating priority:', error);
    return "Error generating priority.";
  }
}

// --- Process Uploaded File ---
async function processUploadedFile(filePath) {
  return new Promise((resolve, reject) => {
    const results = [];
    let index = 0;

    console.log("Processing file:", filePath);
    fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', (row) => {
        console.log("Row data:", row);
        results.push(row);
      })
      .on('end', async () => {
        console.log("File reading complete. Generating output...");
        const output = [];

        for (const row of results) {
          try {
            const allDataText = Object.entries(row)
              .filter(([_, value]) => value && value.trim() !== '')
              .map(([key, value]) => `${key}: ${value}`)
              .join('\n');

            if (!allDataText) continue;

            const summary = await callGeminiForSummary(allDataText);
            const priority = await callGeminiForPriority(allDataText);

            output.push({
              Case_No: ++index,
              Summary: summary,
              Priority: priority
            });
            console.log(`Processed Case ${index}:`, { Summary: summary, Priority: priority });
          } catch (error) {
            console.error('Error processing row:', error);
          }
        }

        console.log("Processing complete. Returning output.");
        resolve(output);
      })
      .on('error', (error) => {
        reject(error);
      });
  });
}

// --- Upload Endpoint ---
app.post('/upload', upload.single('file'), async (req, res) => {
  if (!req.file) {
    console.log("No file uploaded");
    return res.status(400).json({ error: 'No file uploaded' });
  }

  const filePath = req.file.path;
  console.log("File uploaded successfully:", req.file.originalname);

  try {
    const output = await processUploadedFile(filePath);
    console.log("File processed successfully:", output);
    res.json(output);
  } catch (error) {
    console.error('Error processing file:', error);
    res.status(500).json({ error: 'Failed to process the file' });
  }
});

// --- Start the server ---
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
