#!/bin/bash
set -e

echo "Waiting for service..."
sleep 5

curl -f http://127.0.0.1:32000/ || exit 1

curl -f -X POST http://127.0.0.1:32000/api/predict/ \
  -H "Content-Type: application/json" \
  -d '{
    "data":[
      {
        "pickup_latitude": 40.7,
        "pickup_longitude": -73.9,
        "dropoff_latitude": 40.6,
        "dropoff_longitude": -73.7,
        "passenger_count": 2
      }
    ]
  }'
