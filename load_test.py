import asyncio
import aiohttp
import time
import statistics

# ==========================
# CONFIGURATION
# ==========================
BACKEND_URL = "https://YOUR_BACKEND_CLOUD_RUN_URL"
API_KEY = "demo123"

TOTAL_REQUESTS = 100          # total jobs to create
CONCURRENT_REQUESTS = 20      # parallel requests
POLL_RESULTS = True           # set False to test submission only
POLL_INTERVAL = 2             # seconds between polling
POLL_TIMEOUT = 120            # max seconds per job

# ==========================
# METRICS STORAGE
# ==========================
request_times = []
errors = 0
completed_jobs = 0

# ==========================
# REQUEST FUNCTIONS
# ==========================
async def create_job(session, request_id):
    global errors
    start = time.time()

    try:
        async with session.post(
            f"{BACKEND_URL}/api/export",
            headers={"x-api-key": API_KEY}
        ) as resp:
            if resp.status != 200:
                errors += 1
                print(f"[{request_id}] ERROR: status {resp.status}")
                return None

            data = await resp.json()
            job_id = data.get("job_id")

            elapsed = time.time() - start
            request_times.append(elapsed)

            print(f"[{request_id}] Created job {job_id} in {elapsed:.2f}s")
            return job_id

    except Exception as e:
        errors += 1
        print(f"[{request_id}] Exception: {e}")
        return None


async def poll_job(session, job_id):
    global completed_jobs

    start = time.time()

    while True:
        if time.time() - start > POLL_TIMEOUT:
            print(f"[{job_id}] TIMEOUT")
            return False

        try:
            async with session.get(
                f"{BACKEND_URL}/api/jobs/{job_id}/status",
                headers={"x-api-key": API_KEY}
            ) as resp:
                if resp.status != 200:
                    await asyncio.sleep(POLL_INTERVAL)
                    continue

                data = await resp.json()
                status = data.get("status")

                if status == "done":
                    completed_jobs += 1
                    print(f"[{job_id}] DONE")
                    return True

        except Exception:
            pass

        await asyncio.sleep(POLL_INTERVAL)


# ==========================
# MAIN LOAD TEST LOGIC
# ==========================
async def worker(sem, session, request_id):
    async with sem:
        job_id = await create_job(session, request_id)

        if job_id and POLL_RESULTS:
            await poll_job(session, job_id)


async def run_test():
    sem = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(worker(sem, session, i))
            for i in range(TOTAL_REQUESTS)
        ]

        start_time = time.time()
        await asyncio.gather(*tasks)
        total_time = time.time() - start_time

    # ==========================
    # RESULTS
    # ==========================
    print("\n======================")
    print("LOAD TEST RESULTS")
    print("======================")
    print(f"Total Requests: {TOTAL_REQUESTS}")
    print(f"Errors: {errors}")
    print(f"Completed Jobs: {completed_jobs}")
    print(f"Total Time: {total_time:.2f}s")

    if request_times:
        print(f"Avg Response Time: {statistics.mean(request_times):.2f}s")
        print(f"P50: {statistics.median(request_times):.2f}s")
        print(f"P95: {statistics.quantiles(request_times, n=100)[94]:.2f}s")
        print(f"Max: {max(request_times):.2f}s")


# ==========================
# ENTRY POINT
# ==========================
if __name__ == "__main__":
    asyncio.run(run_test())