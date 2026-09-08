import requests
import time

print("Submitting request...")
res = requests.post("http://localhost:5000/submit", data={
    "genre": "psychological thriller",
    "runtime_minutes": 92,
    "budget_tier": "micro-budget (under $500k)",
    "festival_pedigree": "world premiere, no prior festival history"
})
job_id = res.json()["job_id"]
print(f"Got job ID: {job_id}")

while True:
    status_res = requests.get(f"http://localhost:5000/status/{job_id}").json()
    status = status_res["status"]
    print(f"Status: {status}")
    if status == "completed":
        html = requests.get(f"http://localhost:5000/results/{job_id}").text
        print("Success! Result HTML length:", len(html))
        print(html[:200])
        break
    elif status == "error":
        print("Error in background job")
        break
    time.sleep(5)
