FROM python:3.12-slim-bookworm
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# TODO: copy the cloned repo from staging area.
# COPY /staging/your_repo /app/repo

# Copy the project into the image
ADD . /app

# Sync the project into a new environment, using the frozen lockfile
WORKDIR /app
RUN uv sync --frozen

# Set environment variables
ENV PYTHONPATH="/app/src"

# Run the application
# TODO: supervisor should read agent name and other config from a yaml like file?
CMD ["uv", "run", "python", "supervisor.py", "run", "--agent", "basic_agent"]