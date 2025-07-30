# Deployment

The bot is designed for containerized deployment with Docker.

## Docker

A `Dockerfile` is provided for building a production-ready Docker image. To build and run the bot with Docker:

1.  **Build the image**: `docker build -t anton-bot .`
2.  **Run the container**: `docker run -d --env-file .env --name anton-bot anton-bot`

## Kubernetes

For Kubernetes deployments, you can use the Docker image and create a deployment manifest. Example:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: anton-bot
spec:
  replicas: 1
  selector:
    matchLabels:
      app: anton-bot
  template:
    metadata:
      labels:
        app: anton-bot
    spec:
      containers:
      - name: anton-bot
        image: ghcr.io/666bes666/anton:latest
        envFrom:
        - secretRef:
            name: anton-bot-secrets
```
