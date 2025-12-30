# Tutorial: HTTP ML Models with Documented Variables

This tutorial shows how to expose ML models over HTTP and register them in the EDC Connector with documented input features.

## Flow
1. **Model**: Stored locally with metadata JSON describing input variables.
2. **HTTP server**: Exposes models with API key authentication.
3. **EDC registration**: Creates asset, policy, and contract so it appears in the catalog.

## Model metadata structure
Each model has a JSON file documenting its variables:
```json
{
  "name": "iris_classifier",
  "description": "Iris classifier with LightGBM",
  "inputFeatures": [
    { "name": "sepal_length", "type": "number", "description": "Sepal length (cm)" }
  ],
  "classes": ["setosa", "versicolor", "virginica"],
  "metrics": { "accuracy": 0.98 }
}
```

## Try it quickly
### Option A - Use the Iris example
1. Ensure `models/iris_classifier.pkl` and `iris_classifier_metadata.json` are present.
2. Start the server:
   ```bash
   python3 model_http_server.py
   ```
3. Register the model via script:
   ```bash
   ./register_iris_http.sh
   ```

### Option B - Add your own model
1. Place your model file in `models/`.
2. Create a metadata JSON similar to the example above.
3. Update `AVAILABLE_MODELS` in `model_http_server.py`.
4. Use `register_http_model.sh` to register it in the connector.

## What the registration script does
1. Obtains auth token (if needed).
2. Creates asset with `HttpData` pointing to the model server.
3. Creates policy and contract definition.
4. Verifies the asset in the catalog.

## API endpoints (model server)
- `GET /models` (API key)
- `GET /models/<id>/metadata`
- `GET /models/<id>/download` (API key)

## Production notes
- Change `API_KEY` and restrict network access.
- Consider HTTPS and OAuth2 for stronger security.
- Keep metadata files updated when models change.

## FAQs
- **Different number of variables?** Yes, fully flexible.
- **Automatic validation?** Not yet; add validation in download/prediction endpoints if needed.
- **Other formats (.h5, .onnx, .joblib)?** Yes, adjust `content_type` accordingly.
