#!/usr/bin/env bash

cat /dev/null > data/faceoff_data.csv

HEADERS=True

for filename in api_data/game*.json; do
    echo "converting $filename"
    if [ "$HEADERS" == "True" ]; then
        ./extract_faceoff_data.py --input=$filename --format=csv --header >> data/faceoff_data.csv
        HEADERS=False
    else
        ./extract_faceoff_data.py --input=$filename --format=csv >> data/faceoff_data.csv
    fi
done