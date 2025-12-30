#!/bin/bash

# Quick Start - Start the HTTP model server

echo "🚀 Starting ML Model HTTP Server..."
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Verify Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed"
    exit 1
fi

# Verify the model file exists
MODEL_PATH="/mnt/d/Codigos_en_Python/Proyectos_en_Python/SistemaPricing/ModuloElasticidad/4_Entrenamiento/LGBM Classifier/LGBM_Classifier_1.pkl"

if [ ! -f "$MODEL_PATH" ]; then
    echo "⚠️  WARNING: Model file not found"
    echo "   Path: $MODEL_PATH"
    echo ""
    echo "   Edit model_http_server.py and adjust MODEL_BASE_PATH"
    echo ""
fi

# Start server
echo "Starting server at http://localhost:8080"
echo "Press Ctrl+C to stop"
echo ""

python3 model_http_server.py
