FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

RUN groupadd --system --gid 999 nonroot \
	&& useradd --system --gid 999 --uid 999 --create-home nonroot

ARG BUILD_DATE

WORKDIR /app

# Recommended uv options
# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy
# Ensure installed tools can be executed out of the box
ENV UV_TOOL_BIN_DIR=/usr/local/bin

# use uv to install deps
RUN --mount=type=cache,target=/root/.cache/uv \
	--mount=type=bind,source=uv.lock,target=uv.lock \
	--mount=type=bind,source=pyproject.toml,target=pyproject.toml \
	uv sync --locked --no-install-project --no-dev
# reset entrypoint from uv
ENTRYPOINT []

# Copy site content and code into container
COPY static/ ./static/
COPY templates/ ./templates/
COPY blog/ ./blog/
COPY src/ ./src/
COPY app.py encode.py uv.lock pyproject.toml ./
# Installing separately from its dependencies allows optimal layer caching
RUN --mount=type=cache,target=/root/.cache/uv \
	uv sync --locked --no-dev

USER nonroot
ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=5000
ENV BUILD_DATE=$BUILD_DATE
ENV WORKERS=1
ENV GUNICORN_CMD_ARGS="--bind 0.0.0.0:${PORT} --workers ${WORKERS}"
EXPOSE ${PORT}/tcp
CMD ["gunicorn", "app:app"]
