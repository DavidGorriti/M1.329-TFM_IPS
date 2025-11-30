import asyncio
import json
from pathlib import Path
import httpx

DATA_DIR = Path("./data")
ESTIMATE_POSITION_URL = "http://localhost:8000/estimator/estimate-position"
CLEAR_USER_URL = "http://localhost:8000/users/clear-user-positions"

async def clear_user_positions(client: httpx.AsyncClient):
    try:
        resp = await client.get(CLEAR_USER_URL)
        resp.raise_for_status()
        print(f"Cleared user positions, status {resp.status_code}")
    except Exception as e:
        print(f"Error clearing user positions: {e}")
        raise

async def replay_file(file_path: Path, client: httpx.AsyncClient):
    print(f"Processing file: {file_path.name}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    times = sorted(data.keys(), key=float)
    device_name = file_path.stem

    loop = asyncio.get_running_loop()
    start_time = loop.time()

    for t in times:
        now = loop.time()
        delay = float(t) - (now - start_time)

        if delay > 0:
            await asyncio.sleep(delay)

        payload = {
            "device_name": device_name,
            "wifi_measurements": data[t]
        }

        try:
            resp = await client.post(ESTIMATE_POSITION_URL, json=payload)
            resp.raise_for_status()
            print(f"[{device_name}] Sent measurements for t={t}s, status {resp.status_code}")
        except Exception as e:
            print(f"[{device_name}] Error sending measurements for t={t}s: {e}")

async def main():
    async with httpx.AsyncClient() as client:
        await clear_user_positions(client)

        files = [
            f for f in DATA_DIR.iterdir()
            if f.is_file() and f.suffix == ".json"
        ]

        await asyncio.gather(
            *(replay_file(file_path, client) for file_path in files)
        )

if __name__ == "__main__":
    asyncio.run(main())
