import os
import json
from dotenv import load_dotenv
from parallel import Parallel

load_dotenv()
client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])

print("Searching for CineWyre Film Festival and Boston Film Festival...")

res = client.search(search_queries=["CineWyre Film Festival official site", "Boston Film Festival official site"])
urls = [r.url for r in res.results[:5]]
# Filter down roughly by names
boston_urls = [u for u in urls if 'boston' in u.lower()]
cinewyre_urls = [u for u in urls if 'cinewyre' in u.lower()]

# Wait, search might not return them perfectly separated if we used a combined query.
# Let's search separately.
res1 = client.search(search_queries=["CineWyre Film Festival"])
url1 = res1.results[0].url if res1.results else "https://filmfreeway.com/CineWyre"

res2 = client.search(search_queries=["Boston Film Festival"])
url2 = res2.results[0].url if res2.results else "https://bostonfilmfestival.org/"

target_urls = [url1, url2]

print("Extracting from:", target_urls)

extract_result = client.extract(
    urls=target_urls,
    objective=(
        "Extract this organization's film submission deadlines, eligibility "
        "requirements, submission fees, and acquisition or programming "
        "criteria for independent films."
    ),
)

for r in extract_result.results:
    print(f"\n=== RAW EXTRACT FOR {r.url} ===")
    excerpts = r.excerpts if r.excerpts else []
    print("\n".join(excerpts))
    print("=" * 40)
