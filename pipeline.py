import os
import time
import json
from dotenv import load_dotenv
from parallel import Parallel

load_dotenv()

client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])

# ---- INPUT: film details (edit these for real runs) ----
FILM = {
    "genre": "psychological thriller",
    "runtime_minutes": 92,
    "budget_tier": "micro-budget (under $500k)",
    "festival_pedigree": "world premiere, no prior festival history",
}

# ---- STEP 1: Find All — discover active festivals/distributors ----
print("=== FIND ALL ===")
objective = (
    f"Official film festivals and independent film distribution companies "
    f"(organizations, not individual people) currently accepting submissions "
    f"or acquiring {FILM['genre']} independent films around {FILM['runtime_minutes']} "
    f"minutes runtime, suited to a {FILM['budget_tier']} project. Must have an "
    f"official website with submission guidelines or acquisition criteria."
)

ingest_result = client.beta.findall.ingest(objective=objective)

run = client.beta.findall.create(
    objective=ingest_result.objective,
    entity_type=ingest_result.entity_type,
    match_conditions=ingest_result.match_conditions,
    generator="base",
    match_limit=10,
)
findall_id = run.findall_id
print(f"Run: {findall_id}")

while True:
    status = client.beta.findall.retrieve(findall_id)
    print(f"  status={status.status.status}")
    if not status.status.is_active:
        break
    time.sleep(5)

findall_result = client.beta.findall.result(findall_id)

# Keep only real "matched"/"generated" candidates with a usable URL, dedupe, cap at 8
candidates = []
seen = set()
for c in findall_result.candidates:
    if c.match_status in ("matched", "generated") and c.url and c.url not in seen:
        candidates.append(c)
        seen.add(c.url)
    if len(candidates) >= 8:
        break

print(f"\nKept {len(candidates)} candidates:")
for c in candidates:
    print(f"  - {c.name}: {c.url}")

# ---- STEP 2: Extract — pull real submission info off each site ----
print("\n=== EXTRACT ===")
urls = [c.url for c in candidates]

extract_result = client.extract(
    urls=urls,
    objective=(
        "Extract this organization's film submission deadlines, eligibility "
        "requirements, submission fees, and acquisition or programming "
        "criteria for independent films."
    ),
)

# Build a lookup of url -> extracted excerpt text
extracted_by_url = {}
for r in extract_result.results:
    extracted_by_url[r.url] = " ".join(r.excerpts) if r.excerpts else ""

# ---- Save combined raw data for the Gemini step ----
combined = []
for c in candidates:
    combined.append({
        "name": c.name,
        "url": c.url,
        "description": c.description,
        "extracted_info": extracted_by_url.get(c.url, "(no extract data)"),
    })

with open("pipeline_data.json", "w") as f:
    json.dump({"film": FILM, "candidates": combined}, f, indent=2)

print(f"\nSaved {len(combined)} candidates with extract data to pipeline_data.json")
print("Next: feed pipeline_data.json into Gemini for ranking + memo generation.")
