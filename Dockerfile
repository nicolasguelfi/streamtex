FROM python:3.13.7-slim

# Avoid interactive tzdata prompts, speed up apt
ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false

WORKDIR /app

RUN apt-get update && apt-get install -y \
   build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install streamtex as a package
COPY pyproject.toml requirements.txt ./
COPY streamtex/ ./streamtex/
RUN pip3 install -e .

# Copy the target project
ARG FOLDER="tests/test_project"
COPY ${FOLDER}/ ./${FOLDER}/

WORKDIR /app/${FOLDER}

ENV PORT=8501
EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "book.py", "--server.port=8501", "--server.address=0.0.0.0"]
