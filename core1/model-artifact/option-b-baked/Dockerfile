FROM seldonio/mlserver:1.7.0-slim

COPY model.joblib /mnt/models/model.joblib
COPY model-settings.json /mnt/models/model-settings.json

ENV MODEL_DIR=/mnt/models

CMD ["sh", "-c", "mlserver start $MODEL_DIR"]
