#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://localhost:8000/v1"
SERVICE_NAME="test-service"

echo "⏳ 1) Health check..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/health")
if [[ "$HTTP_CODE" -eq 200 ]]; then
  echo "✅ Health OK"
else
  echo "❌ Health returned $HTTP_CODE"
  exit 1
fi

echo
echo "⏳ 2) List services (GET /services)..."
LIST_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${BASE_URL}/services?limit=10&offset=0")
HTTP_CODE=$(echo "$LIST_RESPONSE" | grep HTTP_CODE | cut -d':' -f2)
BODY=$(echo "$LIST_RESPONSE" | sed '/HTTP_CODE:/d')
if [[ "$HTTP_CODE" -eq 200 ]]; then
  echo "✅ /services returned 200"
  echo "Sample response:"
  echo "$BODY"
else
  echo "❌ GET /services returned $HTTP_CODE"
  echo "$BODY"
  exit 1
fi

echo
echo "⏳ 3) Register a new service (POST /services?name=${SERVICE_NAME})..."
PAYLOAD='{"image":"fountainai/api:latest"}'
echo "🔄  Request payload:"
echo "$PAYLOAD"
CREATE_RESPONSE=$(curl -s -X POST "${BASE_URL}/services?name=${SERVICE_NAME}" \
  -H 'Content-Type: application/json' \
  -d "$PAYLOAD" \
  -w "\nHTTP_CODE:%{http_code}")
HTTP_CODE=$(echo "$CREATE_RESPONSE" | grep HTTP_CODE | cut -d':' -f2)
BODY=$(echo "$CREATE_RESPONSE" | sed '/HTTP_CODE:/d')
if [[ "$HTTP_CODE" -eq 201 ]]; then
  echo "✅ POST /services returned 201"
  echo "Response body:"
  echo "$BODY"
else
  echo "❌ POST /services returned $HTTP_CODE"
  echo "$BODY"
  exit 1
fi

echo
echo "⏳ 4) Get details of '${SERVICE_NAME}' (GET /services/${SERVICE_NAME})..."
DETAIL_RESPONSE=$(curl -s -w "\nHTTP_CODE:%{http_code}" "${BASE_URL}/services/${SERVICE_NAME}")
HTTP_CODE=$(echo "$DETAIL_RESPONSE" | grep HTTP_CODE | cut -d':' -f2)
BODY=$(echo "$DETAIL_RESPONSE" | sed '/HTTP_CODE:/d')
if [[ "$HTTP_CODE" -eq 200 ]]; then
  echo "✅ GET /services/${SERVICE_NAME} returned 200"
  echo "Response body:"
  echo "$BODY"
else
  echo "❌ GET /services/${SERVICE_NAME} returned $HTTP_CODE"
  echo "$BODY"
  exit 1
fi

echo
echo "⏳ 5) Delete '${SERVICE_NAME}' (DELETE /services/${SERVICE_NAME})..."
DELETE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X DELETE "${BASE_URL}/services/${SERVICE_NAME}")
if [[ "$DELETE_RESPONSE" -eq 204 ]]; then
  echo "✅ DELETE /services/${SERVICE_NAME} returned 204"
else
  echo "❌ DELETE /services/${SERVICE_NAME} returned $DELETE_RESPONSE"
  exit 1
fi

echo
echo "⏳ 6) Confirm deletion (GET /services/${SERVICE_NAME})..."
CONFIRM_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "${BASE_URL}/services/${SERVICE_NAME}")
if [[ "$CONFIRM_RESPONSE" -eq 404 ]]; then
  echo "✅ Confirmed: GET /services/${SERVICE_NAME} now returns 404"
else
  echo "❌ After deletion, GET /services/${SERVICE_NAME} returned $CONFIRM_RESPONSE (expected 404)"
  exit 1
fi

echo
echo "🎉 All smoke tests passed!"
