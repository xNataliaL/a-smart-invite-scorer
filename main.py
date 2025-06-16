from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from openai import OpenAI
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

Your job is to analyze each invitation and return a structured assessment in JSON format. Base your recommendation on the following criteria:

1. Organizer/Host credibility:
   - HIGH: Well-known company, major publication, prestigious academic institution, popular podcast/media outlet
   - MEDIUM: Recognizable but niche group, startup, or smaller media outlet with good reputation
   - LOW: Unknown group, unclear affiliation, or lacks credibility

2. Audience size/reach:
   - For events: Typically prefer events with at least 1,000 attendees
   - For podcasts/interviews: Consider the show's typical audience size, download numbers, or subscriber count
   - For media: Consider the publication's readership or viewership

3. Other participants:
   - For events: Check if there are other tier-one speakers
   - For podcasts/interviews: Consider the host's reputation and typical guest quality

4. Missing information:
   - If the date, format (in-person/virtual/recorded), time commitment, or key details are unclear

Based on your analysis, return:
- event_or_show_name (name of the event, podcast, show, or publication)
- type (speaking_engagement, podcast, interview, media_appearance, or other)
- organizer_credibility (HIGH, MEDIUM, LOW)
- audience_size (estimated number, subscriber count, or "unknown")
- other_participants (list of other speakers/guests or "not mentioned")
- relevance_score (1–10 based on overall strength and alignment with Andrew's expertise)
- recommendation:
    - "SEND TO ANDREW" → if the invite clearly meets the criteria or is highly promising
    - "ASK FOLLOW-UP QUESTIONS" → if the invite looks promising but lacks key info
    - "DECLINE" → if the invite does not meet the criteria
- key_reasons (brief bullet points explaining your decision)
- suggested_response (a polite email reply from Natalia introducing herself and matching the recommendation)

Important: All responses should be from Natalia's perspective, starting with "Hi [name], I'm Natalia from the DeepLearning.AI team. Nice to meet you!"

Here is the invitation text:
\"\"\"
{invite_text}
\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result = response.choices[0].message.content
        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)