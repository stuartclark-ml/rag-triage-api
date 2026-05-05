#!/bin/bash
set -e

echo "Downloading vector stores from S3..."

aws s3 sync s3://${S3_BUCKET_NAME}/vectorstore/hsg220 /app/vectorstore/hsg220
aws s3 sync s3://${S3_BUCKET_NAME}/vectorstore/osha /app/vectorstore/osha
aws s3 sync s3://${S3_BUCKET_NAME}/vectorstore/riddor /app/vectorstore/riddor

echo "Vector stores ready. Starting API..."

exec uvicorn main:app --host 0.0.0.0 --port 8000