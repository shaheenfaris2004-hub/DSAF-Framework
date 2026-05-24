#!/bin/bash

set -e

TARGET_URL=$(minikube service dsaf-service --url)

echo "Running OWASP ZAP baseline scan against: $TARGET_URL"

docker run --rm \
  --network=host \
  -v "$(pwd):/zap/wrk" \
  ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py \
  -t "$TARGET_URL/search?q=" \
  -J zap-report.json \
  -r zap-report.html || true

echo "OWASP ZAP scan completed. Reports generated: zap-report.json and zap-report.html"
