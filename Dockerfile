FROM python:3.12-slim AS base

WORKDIR /app

# Install system deps for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install dependencies
RUN uv sync --no-dev --no-cache

# Install Playwright browsers
RUN uv run playwright install --with-deps chromium

# Create non-root user
RUN useradd -m -s /bin/bash pilot
USER pilot

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

CMD ["uv", "run", "browserpilot", "serve", "--host", "0.0.0.0", "--port", "8000"]
