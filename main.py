import csv
import os
import datetime
import requests

API = "https://www.data.gouv.fr/api/1"
API_KEY = os.getenv("API_KEY")
DATASET = "6491d5d41882972a92567d36"
RESOURCE = "3c718b51-b629-43f4-aac3-93df951d1281"
HEADERS = {"X-API-KEY": API_KEY}


def api_url(path):
    return "".join([API, path])


url = "https://data.metropole-dijon.fr/api/records/1.0/search/?dataset=dispo-parking&q=&sort=nom_parking&facet=nom_parking"

response = requests.get(url)
response.raise_for_status()
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat()
data = []
for record in response.json()["records"]:
    fields = record["fields"]
    data.append([now, fields["nom_parking"], round(fields["taux_doccupation"])])

with requests.get(
    f"https://www.data.gouv.fr/fr/datasets/r/{RESOURCE}", stream=True
) as r:
    r.raise_for_status()
    with open("data.csv", "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

with open("data.csv", "a") as f:
    csv.writer(f).writerows(data)

requests.post(
    api_url(f"/datasets/{DATASET}/resources/{RESOURCE}/upload/"),
    files={"file": open("data.csv", "rb")},
    headers=HEADERS,
).raise_for_status()
