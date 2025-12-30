#!/bin/bash

# Script to register an HTTP model as an asset in the EDC Connector
# Usage: ./register_http_model.sh

set -e

# ============ CONFIGURATION ============
EDC_API_URL="http://localhost:3000"
MODEL_SERVER_URL="http://localhost:8080"
API_KEY="ml-model-key-2024"

# EDC credentials
USERNAME="user-conn-user1-demo"
PASSWORD="user1123"

# ============ FUNCTIONS ============
get_token() {
    echo "🔐 Getting auth token..."
    TOKEN=$(curl -s -X POST "${EDC_API_URL}/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" | jq -r '.token')
    
    if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
        echo "❌ Error: Could not get token"
        exit 1
    fi
    echo "✓ Token obtained"
}

check_model_server() {
    echo ""
    echo "🔍 Checking model server..."
    
    HEALTH=$(curl -s "${MODEL_SERVER_URL}/health" | jq -r '.status' 2>/dev/null || echo "error")
    
    if [ "$HEALTH" != "healthy" ]; then
        echo "❌ Error: Model server not available at ${MODEL_SERVER_URL}"
        echo "   Start the server with: python3 model_http_server.py"
        exit 1
    fi
    
    echo "✓ Model server available"
    
    # List available models
    echo ""
    echo "📦 Available models:"
    curl -s "${MODEL_SERVER_URL}/models" | jq -r '.models | to_entries[] | "   - \(.key): \(.value.description)"'
}

register_lgbm_model() {
    echo ""
    echo "📝 Registering LGBM Classifier as asset..."
    
    ASSET_ID="lgbm-classifier-http-$(date +%s)"
    
    RESPONSE=$(curl -s -X POST "${EDC_API_URL}/v3/assets" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "@id": "'"${ASSET_ID}"'",
            "properties": {
                "name": "LGBM Classifier Model v1",
                "version": "1.0",
                "description": "LGBM Classifier for price elasticity prediction",
                "shortDescription": "Classification model with LightGBM",
                "keywords": "lgbm,classification,pricing,elasticity",
                "contentType": "application/octet-stream",
                "format": "pickle",
                "assetType": "Model"
            },
            "dataAddress": {
                "type": "HttpData",
                "name": "lgbm-classifier-http-endpoint",
                "baseUrl": "'"${MODEL_SERVER_URL}"'",
                "path": "/download/lgbm-classifier-1",
                "contentType": "application/octet-stream",
                "authKey": "X-API-Key",
                "authCode": "'"${API_KEY}"'"
            },
            "mlMetadata": {
                "task": "Classification",
                "subtask": "Binary Classification",
                "algorithm": "LightGBM",
                "library": "lightgbm",
                "framework": "scikit-learn",
                "software": "Python",
                "programmingLanguage": "Python",
                "license": "Proprietary"
            }
        }')
    
    if echo "$RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
        echo "❌ Error registering asset:"
        echo "$RESPONSE" | jq '.errors'
        exit 1
    fi
    
    echo "✓ Asset registered successfully"
    echo "   ID: ${ASSET_ID}"
    echo ""
    echo "$RESPONSE" | jq '.'
}

create_policy_and_contract() {
    echo ""
    echo "📋 Creating access policy..."
    
    POLICY_ID="policy-lgbm-http-$(date +%s)"
    
    POLICY_RESPONSE=$(curl -s -X POST "${EDC_API_URL}/v3/policydefinitions" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "@id": "'"${POLICY_ID}"'",
            "policy": {
                "@type": "odrl:Set",
                "odrl:permission": [{
                    "odrl:action": "USE",
                    "odrl:constraint": []
                }]
            }
        }')
    
    if echo "$POLICY_RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
        echo "❌ Error creating policy:"
        echo "$POLICY_RESPONSE" | jq '.errors'
        exit 1
    fi
    
    echo "✓ Policy created: ${POLICY_ID}"
    
    echo ""
    echo "📜 Creating contract..."
    
    CONTRACT_ID="contract-lgbm-http-$(date +%s)"
    
    CONTRACT_RESPONSE=$(curl -s -X POST "${EDC_API_URL}/v3/contractdefinitions" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "@id": "'"${CONTRACT_ID}"'",
            "accessPolicyId": "'"${POLICY_ID}"'",
            "contractPolicyId": "'"${POLICY_ID}"'",
            "assetsSelector": [
                {
                    "operandLeft": "id",
                    "operator": "=",
                    "operandRight": "'"${ASSET_ID}"'"
                }
            ]
        }')
    
    if echo "$CONTRACT_RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
        echo "❌ Error creating contract:"
        echo "$CONTRACT_RESPONSE" | jq '.errors'
        exit 1
    fi
    
    echo "✓ Contract created: ${CONTRACT_ID}"
}

verify_in_catalog() {
    echo ""
    echo "🔍 Verifying in catalog..."
    
    sleep 2
    
    CATALOG=$(curl -s -X POST "${EDC_API_URL}/v3/catalog/request" \
        -H "Authorization: Bearer ${TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{}')
    
    COUNT=$(echo "$CATALOG" | jq 'length')
    echo "✓ Total assets in catalog: ${COUNT}"
    
    # Find our asset
    FOUND=$(echo "$CATALOG" | jq -r --arg id "$ASSET_ID" '.[] | select(.assetId == $id) | .properties.name' 2>/dev/null || echo "")
    
    if [ -n "$FOUND" ]; then
        echo "✓ Asset found in catalog: ${FOUND}"
    else
        echo "⚠ Asset not found in catalog (may take a few seconds)"
    fi
}

# ============ MAIN ============
echo "================================================"
echo "  HTTP Model Registration in EDC Connector"
echo "================================================"

get_token
check_model_server
register_lgbm_model
create_policy_and_contract
verify_in_catalog

echo ""
echo "================================================"
echo "  ✅ Registration completed successfully"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Open IA Assets Browser: http://localhost:4200/ml-assets"
echo "  2. Search: LGBM Classifier Model v1"
echo "  3. Verify the asset appears with Storage Type: HttpData"
echo "  4. Check the catalog: http://localhost:4200/catalog"
echo ""
