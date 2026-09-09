import os
from dotenv import load_dotenv
from parallel import Parallel

load_dotenv()
client = Parallel(api_key=os.environ["PARALLEL_API_KEY"])

target_urls = ["https://www.linkedin.com/company/cinewyre", "https://www.linkedin.com/company/boston-film-festival"]
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
