import os
import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from google import genai
from google.genai import types

load_dotenv()


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

def main():
    # 1. Load pipeline_data.json
    try:
        with open("pipeline_data.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("Error: pipeline_data.json not found.")
        return

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY environment variable not set.")
        return
    client = genai.Client(api_key=api_key)
    
    # 3. System prompt instructing it to act as "Launch Radar"
    # 4. Instruct it not to hallucinate, every claim must be traceable
    system_instruction = (
        "You are 'Launch Radar', a distribution strategist for indie filmmakers. "
        "Rank the provided candidates by genuine fit for the film's profile. "
        "Every claim in your output must be traceable to the actual extracted_info or description provided in the candidates list. "
        "Do not invent details. If a candidate's data is thin, state that honestly. "
        "You must output valid JSON matching the requested schema."
    )

    prompt = f"Film Profile:\n{json.dumps(data.get('film', {}), indent=2)}\n\nCandidates:\n{json.dumps(data.get('candidates', []), indent=2)}"

    print("Calling Gemini API...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=Memo,
                temperature=0.2
            )
        )
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return

    result = response.text
    
    # Check if the result is valid JSON
    try:
        parsed_result = json.loads(result)
        print("Successfully generated valid JSON output.")
    except json.JSONDecodeError as e:
        print(f"Error: API returned invalid JSON. Result was:\n{result}\nError: {e}")
        return

    # 6. Save the result to memo.json
    with open("memo.json", "w") as f:
        json.dump(parsed_result, f, indent=2)
        
    print("Saved to memo.json")

if __name__ == "__main__":
    main()
