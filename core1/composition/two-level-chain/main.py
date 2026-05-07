import httpx
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()

NODE_ONE_URL = "http://node-one.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"
NODE_TWO_URL = "http://node-two.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"


@app.post("/api/v1.0/predictions")
async def predict(payload: dict):
    async with httpx.AsyncClient(timeout=30) as client:

        # Step 1 — call node-one with original request
        r1 = await client.post(NODE_ONE_URL, json=payload)
        if r1.status_code != 200:
            raise HTTPException(status_code=r1.status_code,
                                detail=f"node-one failed: {r1.text}")

        # Step 2 — call node-two with node-one's output
        r2 = await client.post(NODE_TWO_URL, json=r1.json())
        if r2.status_code != 200:
            raise HTTPException(status_code=r2.status_code,
                                detail=f"node-two failed: {r2.text}")

    # Step 3 — return node-two's output to caller
    return r2.json()


@app.get("/health")
def health():
    return {"status": "ok"}
