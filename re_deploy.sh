echo "Building the new docker container..."
if docker build -t madplanlaegger:latest .; then
    echo "Docker container built successfully."
else
    echo "Failed to build the Docker container."
    exit 1
fi

echo "Stopping and removing the old container..."
docker stop madplanlaegger || true
docker rm madplanlaegger || true

echo "Running the new container..."
if docker run --restart always -d --name madplanlaegger -p 8050:8050 madplanlaegger:latest; then
    echo "New container is running."
else
    echo "Failed to run the new container."
    exit 1
fi
