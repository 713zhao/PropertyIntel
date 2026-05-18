import requests
import sqlite3
import os
import json
from dotenv import load_dotenv

load_dotenv()


class URAFetcher:
    BASE_URL = "https://www.ura.gov.sg/maps/api"

    def __init__(self, db_path=None):
        if db_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.db_path = os.path.join(base_dir, "data", "property_data.db")
        else:
            self.db_path = db_path

        self.access_key = os.getenv("URA_ACCESS_KEY")
        self.conn = sqlite3.connect(self.db_path)

    def get_token(self):
        if not self.access_key:
            print("URA_ACCESS_KEY not found in environment variables.")
            return None

        print(f"Requesting URA token with AccessKey: {self.access_key[:5]}...")
        url = f"{self.BASE_URL}/access_token?access_key={self.access_key}"
        headers = {"AccessKey": self.access_key, "User-Agent": "Mozilla/5.0"}
        try:
            response = requests.get(url, headers=headers, timeout=30)
            print(f"Token response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("Status") == "Success":
                    return data.get("Result")
                else:
                    print(f"URA API Error: {data.get('Message')}")

            print(f"Failed to get URA token: {response.text}")
        except Exception as e:
            print(f"Error getting URA token: {e}")
        return None

    def fetch_private_transactions(self, token, batch=1):
        print(f"Requesting URA transactions batch {batch}...")
        url = f"{self.BASE_URL}/property/transaction?batch={batch}"
        headers = {
            "AccessKey": self.access_key,
            "Token": token,
            "User-Agent": "Mozilla/5.0",
        }
        try:
            response = requests.get(url, headers=headers, timeout=60)
            print(f"Transactions response status: {response.status_code}")
            if response.status_code == 200:
                return response.json().get("Result", [])
            else:
                print(
                    f"Failed to fetch URA transactions (Batch {batch}): {response.text}"
                )
        except Exception as e:
            print(f"Error fetching transactions: {e}")
        return []

    def save_transactions(self, transactions):
        if not transactions:
            return

        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ura_transactions (
                project TEXT,
                marketSegment TEXT,
                street TEXT,
                x TEXT,
                y TEXT,
                transaction_date TEXT,
                area TEXT,
                floorRange TEXT,
                noOfUnits TEXT,
                price TEXT,
                propertyType TEXT,
                district TEXT,
                typeOfArea TEXT,
                tenure TEXT,
                typeOfSale TEXT,
                unitPrice TEXT
            )
        """)

        # Flattens the nested 'transaction' list inside each project result
        flat_data = []
        for project in transactions:
            project_name = project.get("project")
            market_segment = project.get("marketSegment")
            street = project.get("street")
            x = project.get("x")
            y = project.get("y")

            for tx in project.get("transaction", []):
                flat_data.append(
                    (
                        project_name,
                        market_segment,
                        street,
                        x,
                        y,
                        tx.get("contractDate"),
                        tx.get("area"),
                        tx.get("floorRange"),
                        tx.get("noOfUnits"),
                        tx.get("price"),
                        tx.get("propertyType"),
                        tx.get("district"),
                        tx.get("typeOfArea"),
                        tx.get("tenure"),
                        tx.get("typeOfSale"),
                        tx.get("unitPrice"),
                    )
                )

        cursor.executemany(
            """
            INSERT INTO ura_transactions VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
            flat_data,
        )
        self.conn.commit()
        print(f"Saved {len(flat_data)} transactions to ura_transactions table.")

    def run(self):
        token = self.get_token()
        if token:
            print("Successfully got URA token.")
            # We can loop through batches if needed
            for i in range(1, 2):  # Just fetch 1 batch for testing
                print(f"Fetching URA transactions Batch {i}...")
                txs = self.fetch_private_transactions(token, batch=i)
                self.save_transactions(txs)

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    fetcher = URAFetcher()
    try:
        fetcher.run()
    finally:
        fetcher.close()
