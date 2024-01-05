#!/bin/bash

# Start recorder.py in the background, redirecting output to a log file or /dev/null
# python recorder.py > recorder.log 2>&1 &
# echo "recorder.py started"

# Start transcriber.py in the background, redirecting output to a log file or /dev/null
python transcriber.py > transcriber.log 2>&1 &
echo "transcriber.py started"

# Start speaker.py in the background, redirecting output to a log file or /dev/null
python speaker.py > speaker.log 2>&1 &
echo "speaker.py started"

# Run ollama_api.py in the foreground
echo "Running ollama_api.py"
python ollama_api.py

# When ollama_api.py is stopped, kill all background jobs
trap "echo Stopping background jobs; kill 0" EXIT
