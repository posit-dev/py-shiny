#!/bin/bash

# Script to process log files and generate a summary report
# Author: Data Team

OUTPUT_DIR="${1:-.}"
LOG_FILES=( /var/log/*.log )

# Function to count error occurrences
count_errors() {
    local file="$1"
    grep -c "ERROR" "$file" 2>/dev/null || echo 0
}

# Function to extract timestamp
get_timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Main processing loop
echo "Report generated on $(get_timestamp)" > "$OUTPUT_DIR/report.txt"

for logfile in "${LOG_FILES[@]}"; do
    if [[ -f "$logfile" ]]; then
        error_count=$(count_errors "$logfile")
        if (( error_count > 0 )); then
            echo "Processing $logfile: $error_count errors found"
            tail -n 10 "$logfile" | grep "ERROR" >> "$OUTPUT_DIR/errors.log"
        fi
    fi
done

echo "Report complete. Results saved to $OUTPUT_DIR"
