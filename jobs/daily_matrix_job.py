# jobs/daily_matrix_job.py
import asyncio
import datetime
import json
import os
from shared.connection import Connection

class DailyMatrixJob:
    def __init__(self):
        self.conn = Connection()
        self.matrix_path = os.getenv("MATRIX_FILE", "data/pricing_matrix.json")

    async def fetch_latest_matrix(self):
        # Example: pulling from your backend or investor portal
        return await self.conn.get("/matrix/grid")

    def save_matrix(self, matrix: dict):
        os.makedirs(os.path.dirname(self.matrix_path), exist_ok=True)
        with open(self.matrix_path, "w") as f:
            json.dump(matrix, f, indent=4)

    async def run(self):
        print(f"[{datetime.datetime.now()}] Running daily matrix update job...")
        matrix = await self.fetch_latest_matrix()
        self.save_matrix(matrix)
        print(f"[{datetime.datetime.now()}] Matrix updated successfully.")

if __name__ == "__main__":
    asyncio.run(DailyMatrixJob().run())
