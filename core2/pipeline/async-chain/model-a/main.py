from fastapi import FastAPI, Request
from fastapi.responses import Response
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.api_route("/predict", methods=["POST", "HEAD"])
async def predict(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    
    payload = await request.json()
    logger.info(f"model-a received: {payload}")

    output = {
        "data": payload.get("data", {}),
        "passed_through": "model-a"
    }

    logger.info(f"model-a output: {output}")
    return output


@app.get("/health")
def health():
    return {"status": "ok"}
