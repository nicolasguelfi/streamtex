# Build the image
docker build -t streamtex-app .

# Run the container
docker run -p 8501:8501 streamtex-app
