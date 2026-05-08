from fastapi import FastAPI, Request
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.post("/predict")
async def predict(request: Request):
    payload = await request.json()
    logger.info(f"model-a received: {payload}")

    # Process the input — in real migration this is your model inference
    # Here we just add a tag to show it passed through model-a
    output = {
        "data": payload.get("data", {}),
        "passed_through": "model-a"
    }

    logger.info(f"model-a output: {output}")
    return output
