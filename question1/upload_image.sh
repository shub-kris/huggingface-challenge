#!/bin/bash

AWS_REGION = "eu-north-1"
ECR_REPO_NAME = "gradio-qa-app"
AWS_ACCOUNT_ID = "214065848284"

aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
docker build -t ${ECR_REPO_NAME} .

docker tag ${ECR_REPO_NAME}:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO_NAME}:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.eu-north-1.amazonaws.com/${ECR_REPO_NAME}:latest