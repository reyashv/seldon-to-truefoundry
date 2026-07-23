import httpx
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException

NODE_ONE_URL = "http://node-one.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"
NODE_TWO_URL = "http://node-two.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        limits=httpx.Limits(max_connections=200, max_keepalive_connections=100),
    )
    yield
    await app.state.client.aclose()

app = FastAPI(lifespan=lifespan)

@app.post("/api/v1.0/predictions")
async def predict(payload: dict):
    client = app.state.client
    r1 = await client.post(NODE_ONE_URL, json=payload)
    if r1.status_code != 200:
        raise HTTPException(status_code=r1.status_code, detail=f"node-one failed: {r1.text}")
    r2 = await client.post(NODE_TWO_URL, json=r1.json())
    if r2.status_code != 200:
        raise HTTPException(status_code=r2.status_code, detail=f"node-two failed: {r2.text}")
    return r2.json()

@app.get("/health")
def health():
    return {"status": "ok"}
