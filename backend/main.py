import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Set

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from data.aggregator import build_city_snapshot

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

# --- Connection Manager ---

class ConnectionManager:
    def __init__(self):
        self.connections: dict[str, Set[WebSocket]] = {"nyc": set(), "mumbai": set()}

    async def connect(self, ws: WebSocket, city: str):
        await ws.accept()
        self.connections[city].add(ws)
        logger.info(f"Client connected to {city}. Total: {self.active_count(city)}")

    def disconnect(self, ws: WebSocket, city: str):
        self.connections[city].discard(ws)
        logger.info(f"Client disconnected from {city}. Total: {self.active_count(city)}")

    async def broadcast(self, city: str, data: dict):
        dead = set()
        payload = json.dumps(data)
        for ws in self.connections[city]:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.connections[city].discard(ws)

    def active_count(self, city: str) -> int:
        return len(self.connections[city])


manager = ConnectionManager()

# --- Snapshot Cache ---
_cache: dict[str, dict] = {}


async def refresh_city(city: str):
    logger.info(f"Refreshing {city} snapshot...")
    try:
        snapshot = await build_city_snapshot(city)
        _cache[city] = snapshot
        await manager.broadcast(city, snapshot)
        logger.info(f"{city} snapshot refreshed and broadcast to {manager.active_count(city)} clients.")
    except Exception as e:
        logger.error(f"Error refreshing {city}: {e}")


# --- Lifespan ---

scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Prime cache on startup
    await asyncio.gather(refresh_city("nyc"), refresh_city("mumbai"))

    scheduler.add_job(refresh_city, "interval", seconds=60, args=["nyc"], id="nyc_refresh")
    scheduler.add_job(refresh_city, "interval", seconds=60, args=["mumbai"], id="mumbai_refresh")
    scheduler.start()
    logger.info("Scheduler started — refreshing every 60s")

    yield

    scheduler.shutdown()


# --- App ---

app = FastAPI(title="Biometric City API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/snapshot/{city}")
async def get_snapshot(city: str):
    """HTTP endpoint to get current snapshot (useful for initial page load)."""
    if city not in ("nyc", "mumbai"):
        return {"error": "Unknown city"}
    if city not in _cache:
        snapshot = await build_city_snapshot(city)
        _cache[city] = snapshot
    return _cache[city]


@app.websocket("/ws/{city}")
async def websocket_endpoint(ws: WebSocket, city: str):
    if city not in ("nyc", "mumbai"):
        await ws.close(code=4000)
        return

    await manager.connect(ws, city)

    # Send cached snapshot immediately on connect
    if city in _cache:
        await ws.send_text(json.dumps(_cache[city]))

    try:
        while True:
            # Keep alive — client can send "ping", we reply "pong"
            data = await ws.receive_text()
            if data == "ping":
                await ws.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(ws, city)
