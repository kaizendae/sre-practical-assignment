#!/bin/bash

set -e

echo "Starting Minikube..."
if ! minikube status | grep -q 'host: Running'; then
  minikube start --driver=docker --addons=ingress
else
  echo "Minikube is already running. Skipping start."
fi

echo "Creating namespaces..."
kubectl create namespace api || true
kubectl create namespace auth || true
kubectl create namespace images || true
kubectl create namespace monitoring || true
kubectl create namespace infra || true
kubectl create namespace db || true

echo "Applying database secrets to namespaces..."
kubectl apply -f k8s/secrets/postgres-creds-secret.yaml -n db
kubectl apply -f k8s/secrets/postgres-creds-secret.yaml -n api
kubectl apply -f k8s/secrets/postgres-creds-secret.yaml -n auth

echo "Applying database configurations..."
kubectl apply -k k8s/database

echo "waiting for database pods to be ready... (sleeping 30s)"
sleep 30s

MAX_ATTEMPTS=10
ATTEMPT=1
until kubectl wait --for=condition=Ready pod -l app=postgres -n db --timeout=60s; do
  if [ $ATTEMPT -ge $MAX_ATTEMPTS ]; then
    echo "Database pods did not become ready after $MAX_ATTEMPTS attempts. Exiting."
    exit 1
  fi
  echo "Database pods not ready yet. Retrying in 10 seconds... (Attempt $ATTEMPT/$MAX_ATTEMPTS)"
  ATTEMPT=$((ATTEMPT+1))
  sleep 10
done

echo "Creating databases..."
kubectl -n db exec -it $(kubectl -n db get pod -l app=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U user -d postgres -c "CREATE DATABASE api;" -c "CREATE DATABASE auth;" || true

echo "Deploying API service..."
kubectl apply -f k8s/deployments/api-deployment.yaml
kubectl apply -f k8s/services/api-service.yaml
kubectl apply -f k8s/ingress/api-ingress.yaml

echo "Deploying Auth service..."
kubectl apply -f k8s/deployments/auth-deployment.yaml
kubectl apply -f k8s/services/auth-service.yaml
kubectl apply -f k8s/ingress/auth-ingress.yaml

echo "Deploying Images service..."
kubectl apply -f k8s/deployments/images-deployment.yaml
kubectl apply -f k8s/services/images-service.yaml
kubectl apply -f k8s/ingress/images-ingress.yaml
kubectl apply -f k8s/secrets/gcs-creds.yaml

echo "Deploying TLS secrets for ingress..."
kubectl apply -f 'k8s/secrets/wc-cert.yaml' -n api
kubectl apply -f 'k8s/secrets/wc-cert.yaml' -n auth
kubectl apply -f 'k8s/secrets/wc-cert.yaml' -n images
kubectl apply -f 'k8s/secrets/wc-cert.yaml' -n monitoring

echo "Switching NGINX ingress controller to LoadBalancer type..."
kubectl patch svc ingress-nginx-controller -n ingress-nginx -p '{"spec": {"type": "LoadBalancer"}}'

echo "Adding hostnames to /etc/hosts (requires sudo password)..."
echo "127.0.0.1 api.test auth.test images.test monitoring.test" | sudo tee -a /etc/hosts

echo "Deploying Monitoring Stack (kube-prometheus-stack)..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
helm repo update
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --version 75.13.0 \
  --namespace monitoring \
  --create-namespace \
  --values k8s/monitoring/kube-prom-values.yaml

echo "Applying HPA configurations..."
kubectl apply -k k8s/autoscaling

echo "Infrastructure deployment complete!"
