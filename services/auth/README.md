# Auth Service

This is a minimal Go service using `net/http`.

## Running with Docker

1. Build the Docker image:
   ```sh
   docker build -t auth-service .
   ```

2. Run the Docker container:
   ```sh
   docker run -p 8081:8081 auth-service
   ```

The service will be available at http://localhost:8081.
