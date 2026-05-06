FROM seldonio/mlserver:1.7.0-slim

# Copy model files into the image
COPY model.joblib /mnt/models/model.joblib
COPY model-settings.json /mnt/models/model-settings.json

# Tell MLServer where the model is
ENV MODEL_DIR=/mnt/models

CMD mlserver start $MODEL_DIR
