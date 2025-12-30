#!/bin/bash

# Script to register the Iris HTTP model with documented variables

set -e

EDC_API_URL="http://localhost:3000"
MODEL_SERVER_URL="http://localhost:8080"
API_KEY="ml-model-key-2024"

# EDC credentials
USERNAME="user-conn-user1-demo"
PASSWORD="user1123"

echo "================================================"
echo "  Iris Model Registration in EDC Connector"
echo "================================================"

# Get token
echo "🔐 Getting token..."
TOKEN=$(curl -s -X POST "${EDC_API_URL}/auth/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"${USERNAME}\",\"password\":\"${PASSWORD}\"}" | jq -r '.token')

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo "❌ Error: Could not obtain token"
    exit 1
fi
echo "✓ Token obtained"

# Get model metadata from HTTP server
echo ""
echo "📦 Fetching model metadata..."
METADATA=$(curl -s "${MODEL_SERVER_URL}/metadata/iris-classifier-v1")
INPUT_FEATURES=$(echo "$METADATA" | jq '.model_metadata.input_features')

echo "✓ Metadata fetched"
echo ""
echo "Model input variables:"
echo "$INPUT_FEATURES" | jq -r '.[] | "  \(.position + 1). \(.name) (\(.type)) - \(.description)"'

# Register asset
echo ""
echo "📝 Registering asset with HTTP Data..."

ASSET_ID="iris-http-$(date +%s)"

RESPONSE=$(curl -s -X POST "${EDC_API_URL}/v3/assets" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "@id": "'"${ASSET_ID}"'",
        "properties": {
            "name": "Iris Random Forest Classifier (HTTP)",
            "version": "1.0",
            "description": "Random Forest classifier trained on Iris dataset. Requires 4 input features: sepal length, sepal width, petal length, petal width.",
            "shortDescription": "Iris flower species classifier",
            "keywords": "iris,classification,random-forest,sklearn,flowers",
            "contentType": "application/octet-stream",
            "format": "pickle",
            "assetType": "machineLearning"
        },
        "dataAddress": {
            "type": "HttpData",
            "name": "iris-classifier-http-endpoint",
            "baseUrl": "'"${MODEL_SERVER_URL}"'",
            "path": "/download/iris-classifier-v1",
            "contentType": "application/octet-stream",
            "authKey": "X-API-Key",
            "authCode": "'"${API_KEY}"'"
        },
        "mlMetadata": {
            "task": "Classification",
            "subtask": "Multi-class Classification",
            "algorithm": "Random Forest",
            "library": "scikit-learn",
            "framework": "scikit-learn",
            "software": "Python",
            "programmingLanguage": "Python",
            "license": "MIT",
            "inputFeatures": '"${INPUT_FEATURES}"'
        }
    }')

if echo "$RESPONSE" | jq -e '.errors' > /dev/null 2>&1; then
    echo "❌ Error registering asset:"
    echo "$RESPONSE" | jq '.errors'
    exit 1
fi

echo "✓ Asset registered: ${ASSET_ID}"

# Create policy
echo ""
echo "📋 Creating access policy..."

POLICY_ID="policy-iris-http-$(date +%s)"

curl -s -X POST "${EDC_API_URL}/v3/policydefinitions" \
    -H "Authorization: Bearer ${TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "@id": "'"${POLICY_ID}"'",
        "policy": {
            "@type": "odrl:Set",
            "odrl:permission": [{
                "odrl:action": "USE"
            }]
        }
    }' > /dev/null

echo "✓ Policy created: ${POLICY_ID}"

# Create contract
echo ""
echo "📜 Creating contract..."

CONTRACT_ID="contract-iris-http-$(date +%s)"

curl -s -X POST "${EDC_API_URL}/v3/contractdefinitions" \
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
    }' > /dev/null

echo "✓ Contract created: ${CONTRACT_ID}"

echo ""
echo "================================================"
echo "  ✅ Registration completed successfully"
echo "================================================"
echo ""
echo "Asset details:"
echo "  Asset ID: ${ASSET_ID}"
echo "  Policy ID: ${POLICY_ID}"
echo "  Contract ID: ${CONTRACT_ID}"
echo ""
echo "Model documents 4 input variables:"
echo "$INPUT_FEATURES" | jq -r '.[] | "  \(.position + 1). \(.name)"'
echo ""
echo "Next steps:"
echo "  1. Open IA Assets Browser: http://localhost:4200/ml-assets"
echo "  2. Search: Iris Random Forest"
echo "  3. View details to see documented variables"
echo ""
