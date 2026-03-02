import os
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from .neo import NeoHandler
from .ingest import parse_email_event, enrich_domain_async
from dotenv import load_dotenv
from typing import List

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "neo4jpass")

app = FastAPI(title="KillChain Visualizer Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

neo = NeoHandler(NEO4J_URI, NEO4J_USER, NEO4J_PASS)

class ConnectionManager:
    def __init__(self):
        self.active: List[WebSocket] = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active.append(websocket)
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active:
            self.active.remove(websocket)
    async def broadcast(self, message: dict):
        living = []
        for conn in self.active:
            try:
                await conn.send_json(message)
                living.append(conn)
            except:
                pass
        self.active = living

manager = ConnectionManager()

@app.post("/ingest/email")
async def ingest_email(payload: dict, background_tasks: BackgroundTasks):
    """
    Accepts an email event JSON (subject, from, to, body, urls)
    """
    email_event = parse_email_event(payload)
    # persist to Neo4j
    neo.insert_email_event(email_event)
    # background enrichments: domains
    for domain in email_event['domains']:
        background_tasks.add_task(enrich_domain_async, neo, domain)
    # notify frontend clients
    await manager.broadcast({"type": "new_email", "data": email_event})
    return {"status": "ok", "id": email_event["id"]}

@app.get("/graph/top")
def top_graph(limit: int = 200):
    return neo.get_top_nodes(limit)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            _ = await websocket.receive_text()  # keep alive or ignore
    except WebSocketDisconnect:
        manager.disconnect(websocket)
