import os
import time
from dotenv import load_dotenv
from parallel import Parallel

load_dotenv()

client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])

# Step 1: Ingest — more specific, targets organizations not individuals
ingest_result = client.beta.findall.ingest(
    objective=(
        "Official film festivals and independent film distribution companies "
        "(organizations, not individual people) that are currently accepting "
        "submissions or acquiring independent films, with an official website "
        "listing submission guidelines or acquisition criteria."
    )
)
print("INGEST RESULT:")
print(ingest_result)

# Step 2: Create run with base generator for better quality
run = client.beta.findall.create(
    objective=ingest_result.objective,
    entity_type=ingest_result.entity_type,
    match_conditions=ingest_result.match_conditions,
    generator="base",
    match_limit=8,
)
findall_id = run.findall_id
print(f"\nRUN CREATED: {findall_id}")

# Step 3: Poll until done
print("\nPolling...")
while True:
    status = client.beta.findall.retrieve(findall_id)
    print(f"  status={status.status.status}  candidates_matched={status.status.metrics.matched_candidates_count}")
    if not status.status.is_active:
        break
    time.sleep(5)

# Step 4: Fetch final results
result = client.beta.findall.result(findall_id)
print("\nFINAL RESULT:")
for c in result.candidates:
    print(f"\n- {c.name} ({c.match_status}) — {c.url}")
    print(f"  {c.description[:150] if c.description else ''}")
