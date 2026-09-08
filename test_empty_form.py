import requests
import time

print("Submitting empty request to test fallback logic...")
res = requests.post("http://localhost:5000/submit", data={})
job_id = res.json()["job_id"]
print(f"Got job ID: {job_id}")

while True:
    status_res = requests.get(f"http://localhost:5000/status/{job_id}").json()
    status = status_res["status"]
    print(f"Status: {status}")
    if status == "completed":
        html = requests.get(f"http://localhost:5000/results/{job_id}").text
        print("Success! Result HTML length:", len(html))
        break
    elif status == "error":
        print("Error in background job")
        break
    time.sleep(5)
