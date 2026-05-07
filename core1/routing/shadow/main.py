import httpx
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()

PRIMARY_URL = "http://iris-classifier.seldon-tf.svc.cluster.local:8080/v2/models/iris-classifier/infer"
SHADOW_URL = "http://iris-classifier-shadow.seldon-tf.svc.cluster.local:8080/v2/models/iris-classifier/infer"


async def fire_and_forget_shadow(payload: dict):
    """Send request to shadow — response is discarded"""
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(SHADOW_URL, json=payload)
    except Exception:
        pass  # Shadow failures never affect the primary response


@app.post("/v2/models/iris-classifier/infer")
async def predict(payload: dict):
    async with httpx.AsyncClient(timeout=30) as client:

        # Call primary and shadow simultaneously
        # Primary response returned to caller
        # Shadow response discarded
        primary_task = client.post(PRIMARY_URL, json=payload)
        shadow_task = fire_and_forget_shadow(payload)

        primary_response, _ = await asyncio.gather(
            primary_task,
            shadow_task,
        )

        if primary_response.status_code != 200:
            raise HTTPException(
                status_code=primary_response.status_code,
                detail=f"primary failed: {primary_response.text}"
            )

    # Only primary response returned to caller
    return primary_response.json()


@app.get("/health")
def health():
    return {"status": "ok"}
