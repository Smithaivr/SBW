import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);

  return (
    <div className="min-h-screen bg-gray-950 text-white flex items-center justify-center">
      <div className="bg-gray-900 p-8 rounded-2xl shadow-xl w-[500px]">

        <h1 className="text-2xl font-semibold mb-2">
          Screenplay Breakdown Studio
        </h1>

        <p className="text-gray-400 mb-6">
          Convert screenplay into structured production-ready Excel
        </p>

        <label className="border-2 border-dashed border-gray-700 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer hover:border-yellow-500 transition">
          <input
            type="file"
            accept=".pdf"
            className="hidden"
            onChange={(e) => setFile(e.target.files[0])}
          />
          <p className="text-gray-400">
            {file ? file.name : "Drag & drop PDF or click to upload"}
          </p>
        </label>

        <button className="mt-6 w-full bg-yellow-500 text-black font-medium py-2 rounded-xl hover:bg-yellow-400 transition">
          Convert Script
        </button>

      </div>
    </div>
  );
}

export default App;