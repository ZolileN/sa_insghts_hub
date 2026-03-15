#!/bin/bash
# Health check script for production monitoring
# Ensures the scraper system is running properly

PROJECT_DIR="${PROJECT_DIR:-/opt/sa-insight-hub}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
HEALTH_CHECK_URL="${HEALTH_CHECK_URL:-}"

# Check if the process is running (if using a daemon)
check_process() {
    # Add process checks if you run scrapers as daemons
    return 0
}

# Check disk space
check_disk_space() {
    local usage=$(df "$PROJECT_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ "$usage" -gt 90 ]; then
        echo "$(date): WARNING - Disk usage is ${usage}%" >> "$LOG_DIR/health.log"
        return 1
    fi
    return 0
}

# Check if recent data exists
check_recent_data() {
    local data_dir="$PROJECT_DIR/data"
    local now=$(date +%s)
    local max_age=3600  # 1 hour for realtime data
    
    for file in "$data_dir"/forex.json "$data_dir"/energy.json; do
        if [ -f "$file" ]; then
            local file_age=$((now - $(stat -c %Y "$file")))
            if [ "$file_age" -gt "$max_age" ]; then
                echo "$(date): WARNING - $file is $((file_age/60)) minutes old" >> "$LOG_DIR/health.log"
                return 1
            fi
        fi
    done
    return 0
}

# Check if logs are being written
check_logs() {
    local realtime_log="$LOG_DIR/realtime.log"
    if [ -f "$realtime_log" ]; then
        local last_update=$(stat -c %Y "$realtime_log")
        local now=$(date +%s)
        local age=$((now - last_update))
        
        # Should update every 30 minutes
        if [ "$age" -gt 2100 ]; then  # 35 minutes
            echo "$(date): WARNING - Realtime log hasn't been updated for $((age/60)) minutes" >> "$LOG_DIR/health.log"
            return 1
        fi
    fi
    return 0
}

# Run all checks
main() {
    local status=0
    
    check_disk_space || status=1
    check_recent_data || status=1
    check_logs || status=1
    
    # Send health check to monitoring service
    if [ -n "$HEALTH_CHECK_URL" ]; then
        if [ "$status" -eq 0 ]; then
            curl -s "$HEALTH_CHECK_URL" > /dev/null 2>&1
        else
            curl -s "$HEALTH_CHECK_URL/failure" > /dev/null 2>&1
        fi
    fi
    
    return $status
}

main "$@"
