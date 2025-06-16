from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from OpenAI import openai
import os

app = FastAPI()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.get("/", response_class=HTMLResponse)
def read_root():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.post("/score_invite")
async def score_invite(request: Request):
    data = await request.json()
    invite_text = data.get("invite_text", "")

    if not invite_text:
        return JSONResponse(content={"error": "Missing invite_text"}, status_code=400)

    prompt = f"""
You are a helpful assistant that supports Natalia from the DeepLearning.AI team in reviewing invitations for Andrew Ng. These invitations can be for speaking engagements, conferences, podcasts, interviews, or media appearances.

Your job is to analyze each invitation and return ONLY a valid JSON object with the assessment. Base your recommendation on these criteria:

1. For INTERVIEWS: Only recommend "SEND TO MANAGER" for TOP-TIER global publications like The New York Times, The Washington Post, The Wall Street Journal, Financial Times, The Guardian, BBC, CNN, Forbes (main publication), Harvard Business Review, MIT Technology Review, Nature, Science, etc. Publications like "Entrepreneur Magazine" or smaller/niche publications should be "DECLINE".

2. For SPEAKING ENGAGEMENTS: Prefer events with 1,000+ attendees, prestigious venues, high-profile other speakers.

3. For PODCASTS: Consider reach, host reputation, and audience quality.

4. Organizer credibility levels:
   - HIGH: Top-tier publications, Fortune 500 companies, major academic institutions, well-known conferences
   - MEDIUM: Recognizable organizations with good reputation
   - LOW: Unknown or questionable credibility

Return ONLY this JSON structure (no other text):
{{
  "event_or_show_name": "name of event/show/publication",
  "type": "speaking_engagement|podcast|interview|media_appearance|other",
  "organizer_credibility": "HIGH|MEDIUM|LOW",
  "audience_size": "estimated reach or unknown",
  "other_participants": "list of participants or not mentioned",
  "relevance_score": 1-10,
  "recommendation": "SEND TO MANAGER|ASK FOLLOW-UP QUESTIONS|DECLINE",
  "key_reasons": ["reason 1", "reason 2", "reason 3"],
  "suggested_response": "email reply from Natalia starting with 'Hi [name], I'm Natalia from the DeepLearning.AI team. Nice to meet you!'"
}}

Invitation text:
\"\"\"
{invite_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that ONLY returns valid JSON. Do not include any text before or after the JSON object."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        import json
        import re
        
        # Look for JSON object in the response
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            # Validate that it's proper JSON
            try:
                parsed_json = json.loads(json_str)
                return JSONResponse(content={"result": json_str})
            except json.JSONDecodeError:
                pass
        
        # If no valid JSON found, return the raw response
        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
