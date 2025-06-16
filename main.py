from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import openai
import os

app = FastAPI()

# Load your OpenAI API key from the environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

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
You are a helpful assistant that supports an assistant to Andrew Ng in reviewing speaking and interview invitations.

Your job is to analyze each invitation and return a structured assessment in JSON format. Base your recommendation on the following real-world criteria:

1. Organizer credibility:
   - HIGH: Well-known company, major publication, prestigious academic institution.
   - MEDIUM: Recognizable but niche group or startup.
   - LOW: Unknown group, unclear affiliation, or lacks credibility.

2. Audience size:
   - Typically only forward invites for events with at least 1,000 attendees.

3. Speaker lineup:
   - If the event has no other tier-one speakers, it’s less likely to be accepted.

4. Missing information:
   - If the date, location, format (in-person/virtual), or time commitment are unclear, that reduces clarity.

Based on your analysis, return:
- event_name
- organizer_credibility (HIGH, MEDIUM, LOW)
- audience_size (estimated number or "unknown")
- other_speakers (list or "not mentioned")
- relevance_score (1–10 based on overall strength)
- recommendation:
    - "SEND TO BOSS" → if the invite clearly meets the criteria or is highly promising
    - "ASK FOLLOW-UP QUESTIONS" → if the invite looks promising but lacks key info (e.g. date, time, location)
    - "DECLINE" → if the invite does not meet the criteria
- key_reasons (brief bullet points explaining your decision)
- suggested_response (a short, polite email reply that matches the recommendation)

Here is the invitation text:
\"\"\"
{invite_text}
\"\"\"
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result = response["choices"][0]["message"]["content"]
        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

