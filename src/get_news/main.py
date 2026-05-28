import requests
from dotenv import load_dotenv
import os

load_dotenv()

url = "https://newsapi.org/v2/everything?q=株&language=jp"

payload = {}
headers = {
  'Authorization': os.getenv('NEWSAPI_KEY', '')
}

response = requests.request("GET", url, headers=headers, data=payload)

print(response.text)
