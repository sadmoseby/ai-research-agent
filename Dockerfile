# ── Stage 1: build dependencies into a virtual environment ──────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir --upgrade pip

# Create an isolated venv so only it gets copied to the final stage
RUN python -m venv /venv
ENV PATH="/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: lean runtime image ──────────────────────────────────────────────
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/venv/bin:$PATH"

# Copy only the pre-built venv — no compiler toolchain needed at runtime
COPY --from=builder /venv /venv

WORKDIR /app

# Application source — tests, examples, docs and scripts are intentionally excluded
COPY agent/   agent/
COPY schema/  schema/
COPY cli.py   main.py  ./

# Run as a non-root user
RUN adduser --system --no-create-home --uid 1000 agentuser \
    && chown -R agentuser:agentuser /app
USER agentuser

ENTRYPOINT ["python", "main.py"]
