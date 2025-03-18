FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app

# Note: in case the repo does not have a uv.lock file --frozen fails so fallback to just sync.
RUN uv sync --frozen || uv sync

# Set environment variables
ENV PYTHONPATH="/app/src"

# Run the application
# TODO: supervisor should read agent name and other config from a yaml like file?
CMD ["uv", "run", "python", "supervisor/supervisor.py"]