# jobs/bank_rate_scraper.py
import asyncio
import httpx
import datetime
import json
import os
from bs4 import BeautifulSoup

class BankRateScraper:
    def __init__(self):
        self.output_path = os.getenv("BANK_RATES_FILE", "data/bank_rates.json")
        self.sources = {
            "wells_fargo": "https://www.wellsfargo.com/mortgage/rates/",
            "bank_of_america": "https://www.bankofamerica.com/mortgage/mortgage-rates/",
            "chase": "https://www.chase.com/personal/mortgage/mortgage-rates"
        }

    async def fetch_html(self, url: str) -> str:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text

    def parse_rate(self, html: str) -> float:
        soup = BeautifulSoup(html, "html.parser")

        # Very generic fallback parser
        possible = soup.find_all(text=lambda t: "%" in t)
        for item in possible:
            try:
                return float(item.replace("%", "").strip())
            except:
                continue

        return None

    async def scrape_all(self):
        results = {}
        for bank, url in self.sources.items():
            try:
                html = await self.fetch_html(url)
                rate = self.parse_rate(html)
                results[bank] = rate
            except Exception as e:
                results[bank] = None
                print(f"Failed to scrape {bank}: {e}")
        return results

    def save(self, data: dict):
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(data, f, indent=4)

    async def run(self):
        print(f"[{datetime.datetime.now()}] Running bank rate scraper...")
        data = await self.scrape_all()
        self.save(data)
        print(f"[{datetime.datetime.now()}] Bank rates updated.")

if __name__ == "__main__":
    asyncio.run(BankRateScraper().run())
