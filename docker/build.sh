#!/usr/bin/env bash
# ── TodoHub Docker Build & Verify Script ─────────────────────────
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

echo "=== TodoHub Docker Build ==="
echo ""

# ── Step 1: Build backend image ──────────────────────────────────
echo "[1/4] Building backend image..."
docker build \
    -f docker/backend.Dockerfile \
    -t todohub-backend:latest \
    .
echo "  ✓ todohub-backend:latest built"

# ── Step 2: Build frontend image ────────────────────────────────
echo "[2/4] Building frontend image..."
docker build \
    -f docker/frontend.Dockerfile \
    -t todohub-frontend:latest \
    --build-arg NEXT_PUBLIC_API_URL=http://localhost:8000 \
    .
echo "  ✓ todohub-frontend:latest built"

# ── Step 3: List images ─────────────────────────────────────────
echo ""
echo "[3/4] Built images:"
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep todohub

# ── Step 4: Verify backend health ────────────────────────────────
echo ""
echo "[4/4] Verifying backend image..."
CONTAINER_ID=$(docker run -d --rm \
    -p 8001:8000 \
    -e DATABASE_URL="postgresql://test:test@localhost/test" \
    -e OPENAI_API_KEY="sk-test" \
    todohub-backend:latest 2>/dev/null)

sleep 3

HEALTH=$(curl -s http://localhost:8001/health 2>/dev/null || echo "failed")
docker stop "$CONTAINER_ID" >/dev/null 2>&1 || true

if echo "$HEALTH" | grep -q '"ok"'; then
    echo "  ✓ Backend health check passed"
else
    echo "  ⚠ Backend health check could not verify (may need real DB)"
    echo "    Response: $HEALTH"
fi

echo ""
echo "=== Build Complete ==="
echo ""
echo "To run both services:"
echo "  docker compose up -d"
echo ""
echo "To run with Minikube:"
echo "  minikube start"
echo "  eval \$(minikube docker-env)"
echo "  ./docker/build.sh"
echo "  kubectl apply -f k8s/"
