#!/usr/bin/env bash

cat /dev/null > data/faceoff_data.csv

HEADERS=1

for filename in api_data/game*.json; do
    echo "converting $filename"
    if [ "$HEADERS" -eq 1 ]; then
        ./extract_faceoff_data.py --input=$filename --format=csv --header >> data/faceoff_data.csv
        HEADERS=0
    else
        ./extract_faceoff_data.py --input=$filename --format=csv >> data/faceoff_data.csv
    fi
done