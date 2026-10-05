ARG PYTHON_IMAGE=python:3.11-slim-bookworm@sha256:2333bd330d12de02514770b3585cad313644316047cdee24a7acfdece6de6efb
FROM ghcr.io/astral-sh/uv:0.11.2@sha256:c4f5de312ee66d46810635ffc5df34a1973ba753e7241ce3a08ef979ddd7bea5 AS uv
FROM ${PYTHON_IMAGE} AS base
COPY --from=uv /uv /uvx /usr/local/bin/
RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates libgomp1 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 1000 researcher \
    && mkdir -p /workspace /opt/venv /home/researcher/.cache/huggingface \
    && chown -R researcher:researcher /workspace /home/researcher/.cache \
    && git config --system --add safe.directory /workspace
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_LINK_MODE=copy \
    UV_CONCURRENT_INSTALLS=1 \
    UV_CONCURRENT_DOWNLOADS=4 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    HF_HOME=/home/researcher/.cache/huggingface \
    PATH="/opt/venv/bin:${PATH}"
WORKDIR /workspace

FROM base AS data
COPY requirements/data.txt /opt/requirements-data.txt
RUN uv venv /opt/venv --python /usr/local/bin/python \
    && uv pip install --python /opt/venv/bin/python --require-hashes -r /opt/requirements-data.txt
COPY --chown=researcher:researcher . /workspace
USER researcher
CMD ["python", "-m", "pytest", "-q", "-p", "no:cacheprovider"]

FROM base AS cuda
COPY pyproject.toml uv.lock /workspace/
RUN --mount=type=cache,target=/root/.cache/uv uv sync --frozen --group dev
COPY --chown=researcher:researcher . /workspace
USER researcher
CMD ["python", "-c", "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available()); assert torch.cuda.is_available(), 'CUDA is unavailable inside the container'"]
