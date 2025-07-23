# API Service

This is a minimal Node.js Express service.

## Running with Docker

1. Build the Docker image:
   ```sh
   docker build -t api-service .
   ```

2. Run the Docker container:
   ```sh
   docker run -p 8082:8082 api-service
   ```

The service will be available at http://localhost:8082.
