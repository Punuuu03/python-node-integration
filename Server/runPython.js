import { spawn } from "child_process";

export function runPythonScript() {
  return new Promise((resolve, reject) => {
    const pythonProcess = spawn("python", ["crime_script.py"]);

    let output = "";
    let error = "";

    pythonProcess.stdout.on("data", (data) => {
      output += data.toString();
    });

    pythonProcess.stderr.on("data", (data) => {
      error += data.toString();
    });

    pythonProcess.on("close", (code) => {
      if (code === 0) {
        resolve(output);
      } else {
        reject(error);
      }
    });
  });
}
