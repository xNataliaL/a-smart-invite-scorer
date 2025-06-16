import requests

print("⏳ Sending request to invite scorer...")

url = "https://5c5da351-39ac-4335-a91c-448795ba567c-00-1j1p4a8we3qi4.kirk.replit.dev/score_invite"

data = {
    "invite_text": "Hi Andrew, we’d love to invite you to be a keynote speaker at AI World Congress 2025 in New York. The event gathers 5,000+ industry professionals and past speakers include Sam Altman and Fei-Fei Li. Please let us know if you’d be open to joining!"
}

try:
    response = requests.post(url, json=data)
    print("✅ Status code:", response.status_code)
    print("📬 Response content:")
    print(response.text)
except Exception as e:
    print("❌ Error while making request:", e)


