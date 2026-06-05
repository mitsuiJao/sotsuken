import requests
import os

api_key = os.environ.get("NEWSAPI_KEY")

url = "https://newsapi.org/v2/everything?q=株&language=jp"

payload = {}
headers = {
  'Authorization': api_key
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)

out_path = os.path.join(os.path.dirname(__file__), "news_response.json")
with open(out_path, "w", encoding="utf-8") as f:
  f.write(response.text)
