import httpx
import asyncio
from fastapi import FastAPI, HTTPException

app = FastAPI()

NODE_ROUTER_URL = "http://node-router.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"
NODE_ONE_URL = "http://node-one.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"
NODE_TWO_URL = "http://node-two.seldon-tf.svc.cluster.local:9000/api/v1.0/predictions"

ROUTES = {
    0: NODE_ONE_URL,
    1: NODE_TWO_URL,
}


@app.post("/api/v1.0/predictions")
async def predict(payload: dict):
    async with httpx.AsyncClient(timeout=30) as client:

        # Step 1 — call router to get routing decision
        r_route = await client.post(NODE_ROUTER_URL, json=payload)
        if r_route.status_code != 200:
            raise HTTPException(status_code=r_route.status_code,
                                detail=f"router failed: {r_route.text}")

        # Step 2 — extract route index from router response
        route_index = r_route.json().get("data", {}).get("ndarray", [[0]])[0][0]
        route_index = int(route_index) % len(ROUTES)

        # Step 3 — call the selected child
        target_url = ROUTES[route_index]
        r_model = await client.post(target_url, json=payload)
        if r_model.status_code != 200:
            raise HTTPException(status_code=r_model.status_code,
                                detail=f"model failed: {r_model.text}")

    # Step 4 — return selected child's response to caller
    return {
        **r_model.json(),
        "meta": {"routed_to": f"node-{'one' if route_index == 0 else 'two'}"}
    }


@app.get("/health")
def health():
    return {"status": "ok"}
