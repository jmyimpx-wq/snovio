import httpx
import time

class SnovClient:
    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None

    def authenticate(self):
        url = "https://api.snov.io/v1/oauth/access_token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        r = httpx.post(url, data=payload)
        r.raise_for_status()
        self.access_token = r.json()["access_token"]

    def start_bulk_verification(self, emails):
        url = "https://api.snov.io/v1/emails-verification/bulk"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        r = httpx.post(url, headers=headers, json={"emails": emails})
        r.raise_for_status()
        return r.json()["id"]

    def check_bulk_status(self, job_id):
        url = f"https://api.snov.io/v1/emails-verification/bulk/{job_id}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        r = httpx.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

    def wait_for_results(self, job_id, interval=10, max_attempts=30):
        for _ in range(max_attempts):
            result = self.check_bulk_status(job_id)
            if result.get("status") == "finished":
                return result["data"]
            time.sleep(interval)
        raise TimeoutError("Bulk verification timed out.")
