FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app/agent
RUN uv sync --frozen || uv sync

WORKDIR /app/supervisor
RUN uv sync --frozen || uv sync

# Keep the WORKDIR as /app/supervisor for the CMD
# Run the supervisor
CMD ["uv", "run", "python", "supervisor.py"]
