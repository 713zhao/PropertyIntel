import urllib.request
import csv
import sqlite3
import os
import io
import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_hdb():
    db_path = os.getenv("DATABASE_URL", "backend/data/property_data.db")
    dataset_id = "d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
    api_url = f"https://api-open.data.gov.sg/v1/public/api/datasets/{dataset_id}/initiate-download"

    print(f"Initiating HDB Transactions download...")
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(api_url, headers=headers)
    data = res.json()
    csv_url = data.get("data", {}).get("url")

    if not csv_url:
        print("No URL found")
        return

    print(f"Streaming row by row from {csv_url}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create table if not exists
    # Schema based on data.gov.sg HDB transactions
    cursor.execute("DROP TABLE IF EXISTS hdb_transactions")
    cursor.execute("""
        CREATE TABLE hdb_transactions (
            month TEXT, town TEXT, flat_type TEXT, block TEXT, street_name TEXT,
            storey_range TEXT, floor_area_sqm REAL, flat_model TEXT,
            lease_commence_date INTEGER, remaining_lease TEXT, resale_price REAL
        )
    """)

    req = urllib.request.Request(csv_url, headers=headers)
    with urllib.request.urlopen(req) as response:
        # Read the stream
        datas = io.TextIOWrapper(response, encoding="utf-8")
        reader = csv.reader(datas)
        header = next(reader)  # skip header

        batch = []
        count = 0
        for row in reader:
            if not row:
                continue
            batch.append(row)
            if len(batch) >= 1000:
                cursor.executemany(
                    "INSERT INTO hdb_transactions VALUES (?,?,?,?,?,?,?,?,?,?,?)", batch
                )
                conn.commit()
                count += len(batch)
                print(f"Saved {count} records...")
                batch = []

            if count >= 100000:  # Limit for now
                break

        if batch:
            cursor.executemany(
                "INSERT INTO hdb_transactions VALUES (?,?,?,?,?,?,?,?,?,?,?)", batch
            )
            conn.commit()
            count += len(batch)

    conn.close()
    print(f"Successfully populated {count} HDB transactions!")


if __name__ == "__main__":
    fetch_hdb()
