FROM python:3.13.7-slim

# Avoid interactive tzdata prompts, speed up apt
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false \
    UV_LINK_MODE=copy

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies (cached layer)
COPY pyproject.toml uv.lock .python-version ./
COPY streamtex/ ./streamtex/
RUN uv sync --frozen --no-dev

# Copy the target project
ARG FOLDER="tests/test_project_intro"
COPY ${FOLDER}/ ./${FOLDER}/

WORKDIR /app/${FOLDER}

ENV PORT=8501
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["uv", "run", "streamlit", "run", "book.py", "--server.port=8501", "--server.address=0.0.0.0"]
