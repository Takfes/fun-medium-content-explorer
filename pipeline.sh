#!/bin/bash

# Define the log file
LOGFILE="logs/pipeline.log"

# Function to run a command and check its exit status
run_command() {
    echo "Running: $1" | tee -a $LOGFILE
    echo "Timestamp: $(date)" | tee -a $LOGFILE
    $1 >>$LOGFILE 2>&1
    if [ $? -ne 0 ]; then
        echo "Error running $1" | tee -a $LOGFILE
        exit 1
    fi
}

# Ensure the log directory exists
mkdir -p logs

echo "Starting pipeline at $(date)" | tee -a $LOGFILE

# Check if Docker Compose services are running, and start them if not
docker-compose -f docker-compose.yaml ps | grep -q Up
if [ $? -ne 0 ]; then
    echo "Starting Docker Compose services" | tee -a $LOGFILE
    docker-compose -f docker-compose.yaml up -d >>$LOGFILE 2>&1
fi

# Run the commands in sequence
run_command "python scraping/run_scraper.py"
run_command "python datamgmt/parseraw.py"
run_command "python redisdb/populate_redisdb.py"
run_command "python crawling/pw_crawler_redis.py"
run_command "python datamgmt/parsegold.py"
run_command "python mongodb/populate_mongodb.py"

echo "Pipeline completed successfully" | tee -a $LOGFILE
