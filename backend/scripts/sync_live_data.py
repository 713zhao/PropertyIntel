import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()


def sync():
    print("=" * 60)
    print("  Property Intelligence - Live Data Sync")
    print("=" * 60)

    url = "http://localhost:8002/api/macro-live?refresh=true"
    print(f"Requesting fresh data from: {url}")

    try:
        response = requests.get(url, timeout=60)
        if response.status_code == 200:
            data = response.json()
            print("\n[OK] Sync Successful!")
            print(f"Last Sync: {data.get('last_retrieve_date')}")
            print(f"Next Planned: {data.get('next_retrieve_date')}")

            # Print a quick summary of what was fetched
            payload = data.get("data", {})
            print("\nData Summary:")
            print(f" - PPI Points: {len(payload.get('ppi', []))}")
            print(f" - HDB Points: {len(payload.get('hdb', []))}")
            print(f" - GDP Points: {len(payload.get('gdp', []))}")
        else:
            print(f"\n[ERROR] Sync Failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"\n[ERROR] Error connecting to backend: {e}")
        print("Ensure the backend server is running (python backend/main.py)")


if __name__ == "__main__":
    sync()
