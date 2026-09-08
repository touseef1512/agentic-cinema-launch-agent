import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

class Candidate(BaseModel):
    name: str
    url: str
    fit_reason: str
    action_needed: str

class Memo(BaseModel):
    verdict: str = Field(description="STRONG, MODERATE, or WEAK")
    verdict_reason: str = Field(description="one sentence")
    ranked_candidates: list[Candidate]
    recommendation: str = Field(description="2-3 sentences")

def run_synthesize(pipeline_data):
    load_dotenv(override=True)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
        
    client = genai.Client(api_key=api_key)
    
    system_instruction = (
        "You are 'Launch Radar', a distribution strategist for indie filmmakers. "
        "Rank the provided candidates by genuine fit for the film's profile. "
        "Every claim in your output must be traceable to the actual extracted_info or description provided in the candidates list. "
        "Do not invent details. If a candidate's data is thin, state that honestly. "
        "You must output valid JSON matching the requested schema."
    )

    prompt = f"Film Profile:\n{json.dumps(pipeline_data.get('film', {}), indent=2)}\n\nCandidates:\n{json.dumps(pipeline_data.get('candidates', []), indent=2)}"

    print("Calling Gemini API...")
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            response_mime_type="application/json",
            response_schema=Memo,
            temperature=0.2
        )
    )

    result = response.text
    parsed_result = json.loads(result)
    return parsed_result

if __name__ == "__main__":
    try:
        with open("pipeline_data.json", "r") as f:
            data = json.load(f)
        memo = run_synthesize(data)
        with open("memo.json", "w") as f:
            json.dump(memo, f, indent=2)
        print("Saved to memo.json")
    except Exception as e:
        print(f"Error: {e}")
