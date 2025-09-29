#!/bin/bash
conda activate poligraph

# csv file records the urls
CSV_FILE="websites.csv"
LOG_FILE="crawler.log"

# redirect stdout and stderr to log file
exec > >(tee -a "$LOG_FILE") 2>&1

echo "Crawling started: $(date)"

# read the CSV file line by line, skipping the first line (header)
tail -n +2 "$CSV_FILE" | while IFS=";" read -r No Name Category URL; do
    # ignore empty lines
    if [ -z "$Name" ] || [ -z "$URL" ]; then
        continue
    fi

    cnt=$((cnt + 1))

    DIR="example/tmp/${cnt}_${Name}"
    mkdir -p "$DIR"

    echo "Crawling: $Name ($URL)"

    # python -m poligrapher.scripts.my_crawler "$URL" "$DIR"
    python -m crawler "$URL" "$DIR"
done

echo "Crawling finished: $(date)"
