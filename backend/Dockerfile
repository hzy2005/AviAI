FROM python:3.11-slim AS builder

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.docker.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.docker.txt \
    && pip uninstall -y setuptools wheel

FROM python:3.11-slim AS runtime

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /opt/venv /opt/venv
COPY . .

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /usr/local/lib/python3.11/site-packages/setuptools* \
    && rm -rf /usr/local/lib/python3.11/site-packages/pkg_resources \
    && rm -rf /usr/local/lib/python3.11/site-packages/wheel* \
    && rm -rf /opt/venv/lib/python3.11/site-packages/setuptools* \
    && rm -rf /opt/venv/lib/python3.11/site-packages/pkg_resources \
    && rm -rf /opt/venv/lib/python3.11/site-packages/wheel* \
    && useradd --create-home --shell /usr/sbin/nologin appuser \
    && mkdir -p /app/uploads \
    && chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
