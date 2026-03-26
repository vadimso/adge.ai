import { useState } from "react";

export default function App() {
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [url, setUrl] = useState(null);

  const startExport = async () => {
    const res = await fetch("https://export-api-374229827468.us-central1.run.app/api/export", {
      method: "POST",
      headers: { "x-api-key": "demo123" },
    });
    const data = await res.json();
    setJobId(data.job_id);
    pollStatus(data.job_id);
  };

  const pollStatus = async (jobId) => {
    const interval = setInterval(async () => {
      const res = await fetch(`https://export-api-374229827468.us-central1.run.app/api/jobs/${jobId}/status`, {
        headers: { "x-api-key": "demo123" },
      });
      const data = await res.json();
      setStatus(data.status);
      if (data.status === "done") {
        setUrl(data.file_url);
        clearInterval(interval);
      }
    }, 2000);
  };

  return (
    <div>
      <h1>Export Demo</h1>
      <button onClick={startExport}>Start Export</button>
      {jobId && <p>Job ID: {jobId}</p>}
      {status && <p>Status: {status}</p>}
      {url && <p><a href={url} target="_blank">Download File</a></p>}
    </div>
  );
}