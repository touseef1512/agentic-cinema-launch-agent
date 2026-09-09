import os
import time
import json
from dotenv import load_dotenv
from parallel import Parallel

def run_pipeline(film_data):
    load_dotenv()
    client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])
    FILM = film_data

    # ---- STEP 1: Search — gather broad seeds ----
    print("=== SEARCH ===")
    search_query = f"festivals and distributors currently accepting submissions for {FILM['genre']} films in 2026"
    print(f"Querying: {search_query}")
    search_res = client.search(search_queries=[search_query])

    search_context = []
    for i, r in enumerate(search_res.results[:3]):
        snippet = " ".join(r.excerpts) if getattr(r, "excerpts", None) else getattr(r, "summary", "")
        print(f"Result {i+1}: {r.url}\n  Snippet: {snippet[:150]}...")
        search_context.append(f"URL: {r.url}\nContext: {snippet}")

    seed_context = "\n\n".join(search_context)

    # ---- STEP 2: Find All — discover active festivals/distributors ----
    print("\n=== FIND ALL ===")
    objective = (
        f"Film festivals, distribution companies, or streaming platforms currently "
        f"accepting submissions or acquiring independent {FILM['genre']} feature films. "
        f"Include any platforms that accept indie films, even without specific budget requirements. "
        f"Must have an official website.\n\n"
        f"Additional Context / Potential Leads:\n{seed_context}"
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

    # ---- STEP 3: Extract — pull real submission info off each site ----
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

    pipeline_data = {"film": FILM, "candidates": combined}
    return pipeline_data

if __name__ == "__main__":
    FILM = {
        "genre": "coming-of-age indie dramedy",
        "runtime_minutes": 105,
        "budget_tier": "low-budget ($50K–$500K)",
        "festival_pedigree": "no prior festival history",
    }
    data = run_pipeline(FILM)
    with open("pipeline_data.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"\nSaved {len(data['candidates'])} candidates to pipeline_data.json")
