#!/bin/bash
# Production-ready cron script for cloud deployment
# Supports multiple environments and better error handling

# Configuration - adjust these for your production server
PROJECT_DIR="${PROJECT_DIR:-/opt/sa-insight-hub}"
PYTHON_PATH="${PYTHON_PATH:-/usr/bin/python3}"
VENV_PATH="${VENV_PATH:-$PROJECT_DIR/venv}"
LOG_DIR="${LOG_DIR:-$PROJECT_DIR/logs}"
DATA_DIR="${DATA_DIR:-$PROJECT_DIR/data}"

# Environment variables
export PYTHONUNBUFFERED=1
export PATH="$VENV_PATH/bin:$PATH"

# Function to log with timestamp
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_DIR/production.log"
}

# Function to handle errors
handle_error() {
    local error_message="$1"
    log_message "ERROR: $error_message"
    
    # Send notification (configure your preferred method)
    # Email notification example:
    # echo "$error_message" | mail -s "SA Insight Hub Error" admin@yourdomain.com
    
    # Slack webhook example:
    # curl -X POST "$SLACK_WEBHOOK_URL" -H 'Content-type: application/json' \
    #   --data "{\"text\":\"🚨 SA Insight Hub Error: $error_message\"}"
    
    exit 1
}

# Check if directories exist
if [ ! -d "$PROJECT_DIR" ]; then
    handle_error "Project directory $PROJECT_DIR does not exist"
fi

if [ ! -d "$VENV_PATH" ]; then
    handle_error "Virtual environment $VENV_PATH does not exist"
fi

# Create necessary directories
mkdir -p "$LOG_DIR" "$DATA_DIR"

# Change to project directory
cd "$PROJECT_DIR" || handle_error "Cannot change to project directory"

# Activate virtual environment
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate" || handle_error "Cannot activate virtual environment"
else
    handle_error "Virtual environment activation script not found"
fi

# Check if required files exist
if [ ! -f "run_scrapers.py" ]; then
    handle_error "run_scrapers.py not found"
fi

# Function to run scrapers with timeout
run_scrapers() {
    local topics="$1"
    local timeout="${2:-1800}"  # Default 30 minutes
    local log_file="$LOG_DIR/${3:-scrapers}.log"
    
    log_message "Starting scrapers for topics: $topics"
    
    # Run with timeout and capture output
    if timeout "$timeout" python run_scrapers.py --topics "$topics" >> "$log_file" 2>&1; then
        log_message "Successfully completed scrapers for: $topics"
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            handle_error "Scrapers timed out after $timeout seconds for topics: $topics"
        else
            handle_error "Scrapers failed with exit code $exit_code for topics: $topics"
        fi
    fi
}

# Function to commit changes
commit_changes() {
    local commit_msg="$1"
    local files="$2"
    
    # Check if there are changes to commit
    if git diff --quiet "$DATA_DIR"/; then
        log_message "No changes to commit"
        return 0
    fi
    
    log_message "Committing changes: $commit_msg"
    
    # Add files and commit
    git add $files || handle_error "Failed to add files to git"
    git commit -m "$commit_msg" || handle_error "Failed to commit changes"
    git push origin master || handle_error "Failed to push to GitHub"
    
    log_message "Successfully committed and pushed changes"
}

# Main execution
main() {
    local scraper_type="$1"
    local topics="$2"
    local commit_msg="$3"
    local files="$4"
    
    case "$scraper_type" in
        "realtime")
            run_scrapers "$topics" 600 "realtime"  # 10 minutes timeout
            commit_changes "$commit_msg" "$files"
            ;;
        "weekly")
            run_scrapers "$topics" 1800 "weekly"    # 30 minutes timeout
            commit_changes "$commit_msg" "$files"
            ;;
        "quarterly")
            run_scrapers "$topics" 3600 "quarterly" # 60 minutes timeout
            commit_changes "$commit_msg" "$files"
            ;;
        *)
            handle_error "Unknown scraper type: $scraper_type"
            ;;
    esac
}

# Execute main function with parameters
main "$@"
