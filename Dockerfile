# Use a Python image with uv pre-installed
# ghcr.io/astral-sh/uv:python3.13-alpine (multi-arch: amd64, arm64)
FROM ghcr.io/astral-sh/uv@sha256:6bef08ad40f8062d86a6be6b853e85563d6db8885eb2ba853308b4bb07b1270b AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Generate proper TOML lockfile first
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv lock

# Install the project's dependencies using the lockfile
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv sync --frozen --no-dev --no-editable

# Remove unnecessary files from the virtual environment before copying
RUN find /app/.venv -name '__pycache__' -type d -exec rm -rf {} + && \
    find /app/.venv -name '*.pyc' -delete && \
    find /app/.venv -name '*.pyo' -delete && \
    echo "Cleaned up .venv"

# Final stage
# python:3.13-alpine (multi-arch: amd64, arm64)
FROM python@sha256:61346539f7b26521a230e72c11da5ebd872924745074b19736e7d65ba748c366

# Create a non-root user 'app'
RUN adduser -D -h /home/app -s /bin/sh app
WORKDIR /app
USER app

COPY --from=uv --chown=app:app /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["falcon-mcp"]
