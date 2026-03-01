# Deploy a specific project
docker build \
    --build-arg FOLDER=projects/my_project \
    -t my-project-app .

docker run -p 8501:8501 my-project-app
