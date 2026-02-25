#!/bin/bash
# Start RStudio Server
/init &

# Start JupyterLab
jupyter lab \
    --ip=0.0.0.0 \
    --port=8888 \
    --no-browser \
    --NotebookApp.token="${JUPYTER_TOKEN:-biomed}" \
    --notebook-dir=/workspace/data &

wait
