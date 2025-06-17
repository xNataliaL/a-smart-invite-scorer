from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
import openai
import os

app = FastAPI()

# Set OpenAI API key
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
You are a helpful assistant that supports Natalia from the DeepLearning.AI team in reviewing invitations for Andrew Ng. These invitations can be for speaking engagements, conferences, podcasts, interviews, or media appearances.

Your job is to analyze each invitation and return ONLY a valid JSON object with the assessment. Base your recommendation on these criteria:

INTERVIEWS/MEDIA:
- SEND TO MANAGER only if ALL conditions are met:
  * Publication is in this EXACT list: The New York Times, The Washington Post, The Wall Street Journal, Financial Times, The Guardian, BBC, CNN, Forbes (main publication only - not Forbes councils/contributors), Harvard Business Review, MIT Technology Review, Nature, Science, The Economist, TIME Magazine, Bloomberg, Reuters, TechCrunch, VentureBeat
  * Clear indication of feature story or significant coverage (not just quotes)
  * Direct request from senior editor or established journalist

- DECLINE if:
  * Any online-only publication not listed above
  * Trade publications, niche magazines, or regional media
  * Contributor blogs, Medium posts, or self-published platforms
  * Entrepreneur Magazine, Inc., Fast Company (these are automatic declines)

SPEAKING ENGAGEMENTS:
- SEND TO MANAGER only if ALL conditions are met:
  * Explicitly states 1,000+ in-person attendees (virtual doesn't count unless 10,000+)
  * At least ONE of these is true:
    - Event organized by Fortune 500 company leadership conference
    - Major university commencement or distinguished lecture series
    - Government summit or UN/World Bank/WEF event
    - Industry conference where other confirmed speakers include CEO/founders of major tech companies (Google, Microsoft, OpenAI, etc.)
  * Clear honorarium or all expenses covered
  * Maximum 2-hour time commitment including travel

- ASK FOLLOW-UP QUESTIONS if:
  * Audience size not mentioned but organizer is credible
  * Missing information about other speakers
  * Unclear time commitment or format

PODCASTS:
- SEND TO MANAGER only if:
  * Host has 500K+ downloads per episode (must be stated)
  * Previous guests include multiple Fortune 500 CEOs or equivalent
  * Focused on AI/technology leadership (not general entrepreneurship)

AUTOMATIC DECLINES:
- Panels with more than 3 other participants
- Virtual events under 10,000 attendees
- Academic workshops or small seminars
- Startup events or accelerator demos
- Award ceremonies where Andrew is not the primary honoree
- Any event requiring more than 4 hours total time
- Requests that mention "exposure" or "great opportunity" without concrete details

PERSONAL CONNECTIONS OVERRIDE:
- If invitation mentions personal connection to Andrew (Stanford colleague, Coursera leadership, known AI researcher), add note: "PERSONAL CONNECTION - VERIFY WITH ANDREW"

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
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that ONLY returns valid JSON. Do not include any text before or after the JSON object."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        result = response["choices"][0]["message"]["content"].strip()

        import json
        import re

        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            try:
                parsed_json = json.loads(json_str)
                return JSONResponse(content={"result": json_str})
            except json.JSONDecodeError:
                pass

        return JSONResponse(content={"result": result})

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
