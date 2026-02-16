#!/bin/bash

# Build and push Docker image
echo "Building Docker image..."
docker build -t yeager1977/rl-tts:latest .

echo "Pushing to Docker Hub..."
docker push yeager1977/rl-tts:latest

echo "Deploying to Kubernetes..."
kubectl apply -f k8s/rl-tts.yaml

echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/rl-tts -n rl-edge

echo "Deployment complete!"
echo "Service endpoint: rl-tts.rl-edge.svc.cluster.local:8080"

