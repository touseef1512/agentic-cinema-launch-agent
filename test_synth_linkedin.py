import json
import subprocess

cinewyre_extract = """* linkedin company id: -60267450
* company id: 193503178
* Slug: cinewyre
* Name: CineWyre Film Festival
* description
- CineWyre Film Festival is a bold new celebration of cinema on the Fylde Coast, founded by Ed Greenberg (Lytham International Film Festival, Firestorm, CineWyre). Launching in 2025, CineWyre champions diverse voices and global storytelling through four vibrant strands: Family Friendly, Documentary, LGBTQ+, and Horror/Thriller. Rooted in Fleetwood, the festival is part of a wider vision to unite regional film culture under the Lancashire Film Network, supporting filmmakers, audiences, and creative communities across the North West.
* Website: https://cwfilmfest.com/
* employee count: 2
* founded year: 2025
* follower count: 18
* linkedin url: https://www.linkedin.com/company/cinewyre
* Type: Non Profit
* Size: 2
* company headline: Yearly film festival celebrating the diversity, fun and impact of storytelling.
* slug status: A"""

boston_extract = """* linkedin company id: 2279617
* company id: 81922079
* Slug: boston-film-festival
* Name: Boston Film Festival
* description
- Since 1984, the Boston Film Festival presents independent voices alongside studio premieres, entertaining, enlightening and educating audiences. This nonprofit festival supports emerging filmmakers, features panels and red carpet events, and highlights social impact and environmental work through screenings and yearly awards.
* Website: http://www.bostonfilmfestival.org
* employee count: 37
* founded year: 1984
* follower count: 2030
* linkedin url: https://www.linkedin.com/company/boston-film-festival
* country iso: US
* country name: United States
* Locality: Boston
* Type: Non Profit
* Size: 2
* company headline
- Boston's premier film festival, showcasing independent voices, studio premieres, and emerging talent since 1984.
* slug status: A"""

pipeline_data = {
    "film": {
        "genre": "psychological thriller",
        "runtime_minutes": 92,
        "budget_tier": "micro-budget (under $500k)",
        "festival_pedigree": "world premiere, no prior festival history"
    },
    "candidates": [
        {
            "name": "CineWyre Film Festival",
            "url": "https://www.linkedin.com/company/cinewyre",
            "description": "A film festival.",
            "extracted_info": cinewyre_extract
        },
        {
            "name": "Boston Film Festival",
            "url": "https://www.linkedin.com/company/boston-film-festival",
            "description": "A film festival.",
            "extracted_info": boston_extract
        }
    ]
}

with open("pipeline_data.json", "w") as f:
    json.dump(pipeline_data, f, indent=2)

subprocess.run(["venv/bin/python", "synthesize.py"])

with open("memo.json", "r") as f:
    memo = json.load(f)

for c in memo.get("ranked_candidates", []):
    print(f"{c['name']} -> URL: {c['url']}")

