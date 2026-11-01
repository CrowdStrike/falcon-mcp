# Stage 1: uv binary (distroless image, COPY only)
# ghcr.io/astral-sh/uv:0.13.5 (multi-arch: amd64, arm64)
FROM ghcr.io/astral-sh/uv@sha256:af22a52f5eafef3d78e551599d405c02df61919d18028f0cea8eda93bc9986d0 AS uv-bin

# Stage 2: Build dependencies
# python:3.13-alpine (multi-arch: amd64, arm64)
FROM python@sha256:c50ccfb66e5cc97a610dcd0b9597de6ef5b52c96280b51997b353a0fc87a8361 AS builder

COPY --from=uv-bin /uv /usr/local/bin/uv

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

# Stage 3: Runtime
# python:3.13-alpine (multi-arch: amd64, arm64)
FROM python@sha256:c50ccfb66e5cc97a610dcd0b9597de6ef5b52c96280b51997b353a0fc87a8361

LABEL io.modelcontextprotocol.server.name="io.github.CrowdStrike/falcon-mcp"

# Remove the system pip; the app runs from /app/.venv and never uses it
RUN python -m pip uninstall -y --root-user-action=ignore pip

# Create a non-root user 'app'
RUN adduser -D -h /home/app -s /bin/sh app
WORKDIR /app
USER app

COPY --from=builder --chown=app:app /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

ENTRYPOINT ["falcon-mcp"]
