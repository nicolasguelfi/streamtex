# Build and tag for GCP Artifact Registry
docker build -t streamtex-app .
docker tag streamtex-app \
    REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest

# Push to Artifact Registry
docker push \
    REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest

# On the GCP VM (after SSH):
docker pull \
    REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest
docker run -d -p 8501:8501 \
    REGION-docker.pkg.dev/PROJECT_ID/REPO/streamtex-app:latest
