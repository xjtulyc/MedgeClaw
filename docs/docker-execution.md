# Docker Execution Environment

MedgeClaw runs analysis code inside a Docker container named `medgeclaw`. This document covers the execution model, common issues, and workarounds.

## Basic Execution

```bash
# Python
docker exec medgeclaw python3 /workspace/path/to/script.py

# R
docker exec medgeclaw Rscript /workspace/path/to/script.R

# Install packages
docker exec medgeclaw pip install <package>
docker exec medgeclaw Rscript -e 'install.packages("<pkg>", repos="https://cran.r-project.org")'
```

## Permission Issue: `sg docker`

On some systems, the user is in the `docker` group but the current shell session hasn't picked it up. Symptom:

```
Got permission denied while trying to connect to the Docker daemon socket
```

Fix: wrap commands with `sg docker -c`:

```bash
sg docker -c "docker exec medgeclaw python3 /workspace/script.py"
```

This runs the command in a subshell with the `docker` group active.

## Path Mapping

| Host Path | Container Path |
|-----------|---------------|
| `./data/` | `/workspace/data/` |
| `./outputs/` | `/workspace/outputs/` |

Write scripts using `/workspace/` paths. The host directories are bind-mounted into the container.

Always create output directories before writing:

```bash
docker exec medgeclaw mkdir -p /workspace/outputs
```

## Font Cache Issues

After installing fonts in the container, matplotlib may not pick them up due to a stale font cache.

```python
import matplotlib, shutil, os

cache = matplotlib.get_cachedir()
if os.path.exists(cache):
    shutil.rmtree(cache)
```

Note: if the cache directory doesn't exist after clearing, matplotlib may log a warning like:

```
Could not save font_manager cache [Errno 2] No such file or directory
```

This is harmless — matplotlib will rebuild the cache on next use. To avoid the warning, create the directory first:

```python
os.makedirs(cache, exist_ok=True)
```

## R Package Installation

Some R packages require system libraries. If `install.packages()` fails:

```bash
# Example: nloptr needs cmake
docker exec medgeclaw apt-get update
docker exec medgeclaw apt-get install -y cmake libcurl4-openssl-dev libxml2-dev

# Then retry
docker exec medgeclaw Rscript -e 'install.packages("rms")'
```

Check the R version inside the container — some packages require R ≥ 4.4:

```bash
docker exec medgeclaw R --version | head -1
```

If the container has an older R, you may need to use alternative packages or update the Docker image.

## Container Not Running

If `docker exec` fails with "No such container":

```bash
# Check status
docker ps -a --filter name=medgeclaw

# Start if stopped
docker start medgeclaw

# Or use docker-compose from the project root
docker-compose up -d
```
