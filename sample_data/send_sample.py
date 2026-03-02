import requests, json, time
PAYLOAD = json.load(open("sample_email_1.json"))

def send():
    r = requests.post("http://localhost:8000/ingest/email", json=PAYLOAD)
    print("status:", r.status_code, r.text)

if __name__ == "__main__":
    send()
