# Authenticate with ECR
aws ecr get-login-password --region REGION | \
    docker login --username AWS --password-stdin \
    ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com

# Build, tag and push
docker build -t streamtex-app .
docker tag streamtex-app \
    ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest
docker push \
    ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest

# On the EC2 instance (after SSH):
docker pull \
    ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest
docker run -d -p 8501:8501 \
    ACCOUNT_ID.dkr.ecr.REGION.amazonaws.com/streamtex-app:latest
