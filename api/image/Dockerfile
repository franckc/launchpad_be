FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Create a non-root user
RUN adduser --disabled-password --gecos "" agent

# Copy the project into the image
ADD . /app

# Set ownership to the agent user
RUN chown -R agent:agent /app

# Switch to agent user for all subsequent operations
USER agent

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app/agent
RUN uv sync --frozen || uv sync

WORKDIR /app/supervisor
RUN uv sync --frozen || uv sync

# Keep the WORKDIR as /app/supervisor for the CMD
# Run the supervisor
# TODO:
#  - use a separate user to run the supervisor
#  - consider using a proper process manager that restarts the supervisor
# if it crashes
CMD ["sh", "-c", "uv run python supervisor.py > supervisor.log 2>&1"]
