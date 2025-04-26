import React, { useState } from "react";
import axios from "axios";

const UploadPage = () => {
  const [file, setFile] = useState(null);
  const [uploadResult, setUploadResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      setLoading(true);
      const response = await axios.post("http://localhost:5000/upload", formData);
      console.log("Upload success:", response.data);
      setUploadResult(response.data); // Save the full response { message, output }
    } catch (error) {
      console.error("Upload error:", error);
      alert("Failed to process file");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto bg-white p-8 rounded shadow-lg">
      <h1 className="text-3xl font-bold text-center mb-6 text-blue-700">Crime Case Summarizer</h1>

      <div className="flex flex-col items-center space-y-4">
        <input
          type="file"
          accept=".csv"
          onChange={handleFileChange}
          className="border rounded p-2 w-full"
        />
        <button
          onClick={handleUpload}
          className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded transition duration-200"
        >
          {loading ? "Processing..." : "Upload and Summarize"}
        </button>
      </div>

      {uploadResult && (
        <div className="mt-8 bg-gray-50 p-6 rounded-lg shadow-inner">
          <h2 className="text-2xl font-bold text-green-600 mb-4">{uploadResult.message}</h2>
          <pre className="bg-white p-4 rounded text-gray-800 overflow-x-auto whitespace-pre-wrap">
            {uploadResult.output}
          </pre>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
