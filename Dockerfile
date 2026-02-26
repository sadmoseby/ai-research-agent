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

# Install GitHub CLI (gh) for issue/branch creation
RUN apt-get update && apt-get install -y --no-install-recommends curl gpg \
    && curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg \
       | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" \
       | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update && apt-get install -y --no-install-recommends gh \
    && rm -rf /var/lib/apt/lists/*

# Application source — tests, examples, docs and scripts are intentionally excluded
COPY agent/   agent/
COPY schema/  schema/
COPY cli.py   main.py  ./

# Run as a non-root user
RUN adduser --system --no-create-home --uid 1000 agentuser \
    && chown -R agentuser /app
USER agentuser

ENTRYPOINT ["python", "main.py"]
