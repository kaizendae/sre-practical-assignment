import requests
import time
import random

endpoints = [
    "http://api.test/",
    "http://api.test/healthz",
    "http://api.test/readyz",
    "http://auth.test/",
    "http://auth.test/healthz",
    "http://auth.test/readyz",
    "http://images.test/upload",
    "http://images.test/healthz",
    "http://images.test/readyz"

]

print("Starting traffic generation...")

try:
    while True:
        url = random.choice(endpoints)
        try:
            response = requests.get(url, timeout=5, allow_redirects=False)
            print(f"Requested {url} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error requesting {url}: {e}")
        time.sleep(random.uniform(0.001, 1.0)) # Random delay between 0.1 and 1.0 seconds
except KeyboardInterrupt:
    print("\nTraffic generation stopped.")
