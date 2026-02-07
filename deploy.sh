#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  TodoHub — Full Minikube Deployment Script
#  Usage: ./deploy.sh
#  Prerequisites: minikube, docker, kubectl, helm
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         TodoHub — Minikube Deployment                   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Step 1: Start Minikube ────────────────────────────────────────
echo "[1/6] Starting Minikube..."
if minikube status --format='{{.Host}}' 2>/dev/null | grep -q "Running"; then
    echo "  ✓ Minikube already running"
else
    minikube start --driver=docker --cpus=2 --memory=4096
    echo "  ✓ Minikube started"
fi

# ── Step 2: Configure Docker to use Minikube's daemon ────────────
echo "[2/6] Configuring Docker environment..."
eval $(minikube docker-env)
echo "  ✓ Docker pointing to Minikube"

# ── Step 3: Build images inside Minikube ─────────────────────────
echo "[3/6] Building Docker images..."
docker build -f docker/backend.Dockerfile -t todohub-backend:latest .
echo "  ✓ todohub-backend:latest built"

docker build -f docker/frontend.Dockerfile -t todohub-frontend:latest \
    --build-arg NEXT_PUBLIC_API_URL=http://backend:8000 .
echo "  ✓ todohub-frontend:latest built"

# ── Step 4: Deploy with kubectl (raw manifests) ──────────────────
echo "[4/6] Applying Kubernetes manifests..."
kubectl apply -f k8s/namespace.yaml

# Prompt user to edit secrets before applying
echo ""
echo "  ⚠  IMPORTANT: Edit k8s/backend-secret.yaml with real credentials"
echo "     before running in production. Deploying with placeholders now."
echo ""

kubectl apply -f k8s/backend-secret.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-configmap.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml
echo "  ✓ All manifests applied"

# ── Step 5: Wait for pods ────────────────────────────────────────
echo "[5/6] Waiting for pods to be ready..."
kubectl wait --namespace=todohub \
    --for=condition=ready pod \
    --selector=app=backend \
    --timeout=120s 2>/dev/null || echo "  ⚠ Backend pods not ready (may need real DB credentials)"

kubectl wait --namespace=todohub \
    --for=condition=ready pod \
    --selector=app=frontend \
    --timeout=120s 2>/dev/null || echo "  ⚠ Frontend pods not ready yet"

# ── Step 6: Validation ──────────────────────────────────────────
echo "[6/6] Validating deployment..."
echo ""
echo "  Pods:"
kubectl get pods -n todohub -o wide
echo ""
echo "  Services:"
kubectl get svc -n todohub
echo ""

# Get access URL
FRONTEND_URL=$(minikube service frontend -n todohub --url 2>/dev/null || echo "pending")
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Deployment Complete!                                   ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║                                                         ║"
echo "║  Access TodoHub:                                        ║"
echo "║    minikube service frontend -n todohub                 ║"
echo "║                                                         ║"
echo "║  Or with Helm (alternative):                            ║"
echo "║    helm install todohub helm/todohub-backend -n todohub ║"
echo "║    helm install todohub helm/todohub-frontend -n todohub║"
echo "║                                                         ║"
echo "╚══════════════════════════════════════════════════════════╝"
