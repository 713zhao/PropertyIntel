import requests
import time
import pandas as pd
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class DataGovFetcher:
    BASE_URL = "https://api-open.data.gov.sg/v1/public/api/datasets"

    def __init__(self, db_path=None):
        if db_path is None:
            # Priority: ENV variable (for Fly.io volume) > Default local path
            self.db_path = os.getenv("DATABASE_URL")
            if not self.db_path:
                base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                self.db_path = os.path.join(base_dir, "data", "property_data.db")
        else:
            self.db_path = db_path

        self.api_key = os.getenv("DATA_GOV_API_KEY")
        print(f"Initializing DataGovFetcher with DB path: {self.db_path}")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.headers = {"api-key": self.api_key} if self.api_key else {}

    def get_headers(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        headers.update(self.headers)
        return headers

    def initiate_download(self, dataset_id):
        url = f"{self.BASE_URL}/{dataset_id}/initiate-download"
        print(f"Initiating download: {url}")
        headers = self.get_headers()
        # Using POST as it's common for initiating actions, but accepting both 200 and 201
        try:
            response = requests.post(url, timeout=10, headers=headers)
            if response.status_code in [200, 201]:
                data = response.json().get("data", {})
                if "url" in data:
                    print("Got direct download URL from POST")
                    return {"url": data["url"]}
                download_id = data.get("id")
                print(f"Got download ID: {download_id}")
                return {"id": download_id}
            else:
                print(
                    f"POST failed with {response.status_code}: {response.text}, trying GET..."
                )
                # Fallback to GET if POST is not supported
                response = requests.get(url, timeout=10, headers=headers)
                if response.status_code in [200, 201]:
                    data = response.json().get("data", {})
                    if "url" in data:
                        print("Got direct download URL from GET")
                        return {"url": data["url"]}
                    download_id = data.get("id")
                    print(f"Got download ID: {download_id}")
                    return {"id": download_id}

                print(
                    f"Failed to initiate download for {dataset_id}: {response.status_code} - {response.text}"
                )
                return None
        except Exception as e:
            print(f"Error initiating download: {e}")
            return None

    def poll_download(self, dataset_id, download_id):
        if not download_id:
            return None
        url = f"{self.BASE_URL}/{dataset_id}/poll-download/{download_id}"
        print(f"Polling download: {url}")
        headers = self.get_headers()
        attempts = 0
        while attempts < 10:
            try:
                response = requests.get(url, timeout=10, headers=headers)
                if response.status_code == 200:
                    data = response.json().get("data", {})
                    status = data.get("status")
                    print(f"Attempt {attempts + 1}: Status = {status}")
                    if status == "COMPLETED":
                        return data.get("url")
                    elif status == "FAILED":
                        print("Download failed on server side")
                        return None
                else:
                    print(f"Polling failed with {response.status_code}")
            except Exception as e:
                print(f"Error polling: {e}")

            time.sleep(3)
            attempts += 1
        print("Polling timed out")
        return None

    def fetch_and_save_dataset(self, dataset_id, table_name):

        print(f"Fetching {table_name} ({dataset_id})...")
        result = self.initiate_download(dataset_id)
        if not result:
            return

        if "url" in result:
            csv_url = result["url"]
        else:
            csv_url = self.poll_download(dataset_id, result.get("id"))

        if not csv_url:
            print(f"Failed to get download URL for {table_name}")
            return

        df = pd.read_csv(csv_url)
        df.to_sql(table_name, self.conn, if_exists="replace", index=False)
        print(f"Saved {len(df)} records to {table_name} table.")

    def fetch_and_save_hdb_resale_index(self):
        self.fetch_and_save_dataset(
            "d_14f63e595975691e7c24a27ae4c07c79", "hdb_resale_index"
        )

    def fetch_and_save_hdb_transactions(self):
        self.fetch_and_save_dataset(
            "d_8b84c4ee58e3cfc0ece0d773c8ca6abc", "hdb_transactions"
        )

    def fetch_and_save_population_indicators(self):
        self.fetch_and_save_dataset(
            "d_3d227e5d9fdec73f3bcadce671c333a6", "population_indicators"
        )

    def fetch_and_save_private_property_index(self):
        self.fetch_and_save_dataset(
            "d_97f8a2e995022d311c6c68cfda6d034c", "private_property_index"
        )

    def fetch_and_save_rental_index(self):
        self.fetch_and_save_dataset(
            "d_8e4c50283fb7052a391dfb746a05c853", "private_rental_index"
        )

    def fetch_and_save_household_income(self):
        self.fetch_and_save_dataset(
            "d_37ff979fd327acc0df0f412a29ea352f", "household_income"
        )

    def fetch_and_save_gls_residential(self):
        self.fetch_and_save_dataset("d_99797746f338d38e2d4223f6", "gls_residential")

    def fetch_and_save_private_transactions(self):
        self.fetch_and_save_dataset(
            "d_8e4695000570b6d2745e54d8", "private_transactions"
        )

    def fetch_and_save_private_projects(self):
        self.fetch_and_save_dataset("d_43875567b5791c107f9c8f61", "private_projects")

    def close(self):
        self.conn.close()


if __name__ == "__main__":
    fetcher = DataGovFetcher()
    try:
        fetcher.fetch_and_save_hdb_resale_index()
        time.sleep(10)
        fetcher.fetch_and_save_hdb_transactions()
        time.sleep(10)
        fetcher.fetch_and_save_population_indicators()
        time.sleep(10)
        fetcher.fetch_and_save_private_property_index()
        time.sleep(10)
        fetcher.fetch_and_save_rental_index()
        time.sleep(10)
        fetcher.fetch_and_save_household_income()
        time.sleep(10)
        fetcher.fetch_and_save_gls_residential()
        time.sleep(10)
        fetcher.fetch_and_save_private_transactions()
        time.sleep(10)
        fetcher.fetch_and_save_private_projects()
    finally:
        fetcher.close()
