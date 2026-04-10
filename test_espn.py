import requests

url = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
response = requests.get(url)
print("Status code:", response.status_code)
print("Response:", response.text[:500])
