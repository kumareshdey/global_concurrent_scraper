#!/bin/bash

# Example content for init.sh
echo "Initializing service with EXECUTION_TYPE=$EXECUTION_TYPE"

# Your actual startup commands based on EXECUTION_TYPE
if [ "$EXECUTION_TYPE" = "celery" ]; then
    python -m celery -A celery_app worker -Q scraping --loglevel=info --concurrency=10 -E
elif [ "$EXECUTION_TYPE" = "plombery" ]; then
    python api.py
elif [ "$EXECUTION_TYPE" = "fast_api" ]; then
    python fast_api.py
else
    echo "Unknown EXECUTION_TYPE: $EXECUTION_TYPE"
    exit 1
fi
