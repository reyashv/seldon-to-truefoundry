import httpx
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()

NODE_ONE_URL = "http://node-one.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"
NODE_TWO_URL = "http://node-two.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"
NODE_COMBINER_URL = "http://node-combiner.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"


@app.post("/api/v1.0/predictions")
async def predict(payload: dict):
    async with httpx.AsyncClient(timeout=30) as client:

        # Step 1 — fan out to node-one and node-two IN PARALLEL
        r1, r2 = await asyncio.gather(
            client.post(NODE_ONE_URL, json=payload),
            client.post(NODE_TWO_URL, json=payload),
        )

        if r1.status_code != 200:
            raise HTTPException(status_code=r1.status_code,
                                detail=f"node-one failed: {r1.text}")
        if r2.status_code != 200:
            raise HTTPException(status_code=r2.status_code,
                                detail=f"node-two failed: {r2.text}")

        # Step 2 — send both outputs to combiner
        combined_payload = {
            "data": {
                "names": r1.json().get("data", {}).get("names", []) +
                         r2.json().get("data", {}).get("names", []),
                "ndarray": r1.json().get("data", {}).get("ndarray", []) +
                           r2.json().get("data", {}).get("ndarray", [])
            }
        }

        r3 = await client.post(NODE_COMBINER_URL, json=combined_payload)
        if r3.status_code != 200:
            raise HTTPException(status_code=r3.status_code,
                                detail=f"combiner failed: {r3.text}")

    # Step 3 — return combiner output to caller
    return r3.json()


@app.get("/health")
def health():
    return {"status": "ok"}
