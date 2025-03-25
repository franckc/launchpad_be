# Agent Launchpad Backend

The backend component of the Agent Launchpad platform, responsible for building, deploying, and managing AI agents in secure containerized environments.

## Overview

The Agent Launchpad Backend provides a robust infrastructure for running AI agents in isolated environments, collecting their outputs, and managing their lifecycle.

### Core Functionality

- **Container Building**: Generate secure Docker containers from Agent GitHub repositories (currently supporting CrewAI)
- **API Layer**: Comprehensive REST API for container management, agent execution, and result collection
- **Supervisor Process**: In-container process handling communication between the manager and agent execution
- **Secure Execution**: Sandboxed environments for safe agent operation

## System Architecture

```
┌─────────────────┐      ┌──────────────────────────────────┐
│                 │      │ Docker Container                 │
│  Launchpad API  │◄────►│                                  │
│    (Manager)    │      │  ┌────────────┐    ┌─────────┐   │
│                 │      │  │ Supervisor │───►│  Agent  │   │
└─────────────────┘      │  └────────────┘    └─────────┘   │
                         │                                  │
                         └──────────────────────────────────┘
```

## Installation

### Prerequisites

- Python 3.10 or higher
- Docker installed and running
- PostgreSQL database

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/veritai_agent_platform.git
   cd veritai_agent_platform/be/launchpad_be
   ```

2. Install dependencies using `uv`:
   ```bash
   uv run sync
   ```

3. Create a `.env` file with the following environment variables:
   ```
   DATABASE_URL=postgresql://username:password@localhost:5432/launchpad
   LOG_LEVEL=INFO  # Options: DEBUG, INFO, WARNING, ERROR
   ```

4. Database setup:
   - See the `launchpad_fe` documentation for instructions to populate the DB schema
   - Ensure both frontend and backend point to the same database

## Running the Application

Start the Flask application:

```bash
uv run main.py
```

The API will be available at `http://localhost:5000` by default.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/agents` | GET | List all available agents |
| `/api/v1/agents` | POST | Register a new agent |
| `/api/v1/agents/{agent_id}/build` | POST | Build agent container |
| `/api/v1/runs` | POST | Start an agent run |
| `/api/v1/runs/{run_id}/status` | GET | Get run status |
| `/api/v1/runs/{run_id}/output` | GET | Get run output |

## Configuration

The application can be configured using environment variables or a `.env` file:

- `PORT`: HTTP port (default: 5000)
- `HOST`: Binding address (default: 0.0.0.0)
- `DATABASE_URL`: PostgreSQL connection string
- `CONTAINER_TIMEOUT`: Maximum running time for containers in seconds (default: 3600)

## Development

### Project Structure

```
launchpad_be/
├── api/              # API endpoints
├── builder/          # Container building logic
├── models/           # Database models
├── supervisor/       # Container supervisor code
├── utils/            # Helper utilities
├── main.py           # Application entry point
└── README.md         # This file
```

### Running Tests

```bash
pytest
```

## Roadmap

- **Framework Support**: Add support for additional agent frameworks (LangChain, Swarm, etc.)
- **Authentication**: Implement bearer token authentication for all API endpoints
- **API Consolidation**: Merge `get_run_status` and `get_output` into a single endpoint
- **Enhanced Security**: Run supervisor and agent as different users within containers
- **Observability**: Implement HTTP/HTTPS proxying to log LLM and tool calls
- **Horizontal Scaling**: Support for distributed agent execution across multiple nodes
- **Resource Controls**: Fine-grained CPU/memory limits for containers

## Troubleshooting

### Common Issues

- **Database Connection Errors**: Verify the `DATABASE_URL` is correct and the database is running
- **Container Build Failures**: Check Docker daemon status and repository URL validity
- **Agent Execution Timeouts**: Adjust the `CONTAINER_TIMEOUT` setting for long-running agents

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)