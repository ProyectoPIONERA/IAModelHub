# Model Serving - HTTP Server

Simple HTTP server to expose locally stored ML models through authenticated endpoints.

## Features
- ✅ Serves `.pkl` (and other formats) over HTTP
- ✅ API Key authentication
- ✅ Returns model metadata (input features, classes, description)

## Installation
```bash
cd AIModelHub/AIModelHub_Extensiones/model-serving
pip install -r requirements.txt
```

## Configuration
Edit `model_http_server.py`:
```python
MODEL_BASE_PATH = '/home/edmundo/AIModelHub/AIModelHub_Extensiones/model-serving/models'  # model directory
API_KEY = 'ml-model-key-2024'  # change to a secure value
AVAILABLE_MODELS = {
    'iris_classifier': {
        'file': 'iris_classifier.pkl',
        'content_type': 'application/octet-stream',
        'metadata_file': 'iris_classifier_metadata.json',
        'size_bytes': None  # auto-calculated
    }
}
```

## Run server
```bash
python3 model_http_server.py
# Server runs on http://0.0.0.0:8080
```

## Endpoints
- `GET /models` — list models (requires API key)
- `GET /models/<id>/metadata` — metadata for a specific model
- `GET /models/<id>/download` — download model (requires API key)

Example:
```bash
curl -H "Authorization: Bearer ml-model-key-2024" http://localhost:8080/models
```

## Workflow example (Iris model)
1. Start server.
2. Register the model via EDC using `register_http_model.sh` or `register_iris_http.sh`.
3. Browse the catalog and confirm the asset exists.

## Production recommendations
- Change `API_KEY`.
- Use HTTPS/ingress in front of the server.
- Restrict network access to trusted hosts.
- Consider OAuth2 for stronger auth if needed.

## Next steps
- Add more models by updating `AVAILABLE_MODELS`.
- Adjust metadata JSON files in `models/` to document input features.
