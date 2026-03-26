# -------------------------------
# Load Test Script for Export API
# -------------------------------

$backend = "https://export-api-374229827468.us-central1.run.app"
$headers = @{ "x-api-key" = "demo123" }

$jobs = @()
$job_count = 20

Write-Host "🚀 Starting $job_count export jobs..."

# 1️⃣ Fire multiple export requests in parallel
for ($i = 1; $i -le $job_count; $i++) {
    $jobs += Start-Job -ScriptBlock {
        param($backend, $headers)

        $response = Invoke-RestMethod -Uri "$backend/api/export" -Method POST -Headers $headers
        return $response.job_id
    } -ArgumentList $backend, $headers
}

# Wait for all jobs to finish firing
$job_ids = $jobs | ForEach-Object { Receive-Job -Wait $_ }

Write-Host "✅ All jobs created. Job IDs:"
$job_ids | ForEach-Object { Write-Host $_ }

# 2️⃣ Poll each job for completion
foreach ($job_id in $job_ids) {
    $status = ""
    Write-Host "⏳ Polling job $job_id..."
    while ($status -ne "completed") {
        try {
            $response = Invoke-RestMethod -Uri "$backend/api/jobs/$job_id/status" -Method GET -Headers $headers
            $status = $response.status
        } catch {
            Write-Warning "Failed to fetch status for job $job_id. Retrying..."
            Start-Sleep -Seconds 2
            continue
        }

        Write-Host "Job $job_id status: $status"
        Start-Sleep -Seconds 2
    }
    Write-Host "✅ Job $job_id completed!"
}

Write-Host "🎉 All jobs completed!"