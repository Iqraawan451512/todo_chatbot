#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════════════
#  TodoHub — Deployment Validation Script
#  Usage: ./validate.sh
# ═══════════════════════════════════════════════════════════════════
set -euo pipefail

NAMESPACE="todohub"
PASS=0
FAIL=0

check() {
    local desc="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo "  ✓ $desc"
        PASS=$((PASS + 1))
    else
        echo "  ✗ $desc"
        FAIL=$((FAIL + 1))
    fi
}

echo "╔══════════════════════════════════════════════════════════╗"
echo "║         TodoHub — Deployment Validation                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── Cluster checks ───────────────────────────────────────────────
echo "[Cluster]"
check "Minikube is running" minikube status
check "Namespace '$NAMESPACE' exists" kubectl get namespace "$NAMESPACE"
echo ""

# ── Pod checks ───────────────────────────────────────────────────
echo "[Pods]"
check "Backend pods exist" kubectl get pods -n "$NAMESPACE" -l app=backend -o name
check "Frontend pods exist" kubectl get pods -n "$NAMESPACE" -l app=frontend -o name

BACKEND_READY=$(kubectl get pods -n "$NAMESPACE" -l app=backend -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
if echo "$BACKEND_READY" | grep -q "True"; then
    echo "  ✓ Backend pods are Ready"
    PASS=$((PASS + 1))
else
    echo "  ⚠ Backend pods not Ready (may need real DB/API credentials)"
    FAIL=$((FAIL + 1))
fi

FRONTEND_READY=$(kubectl get pods -n "$NAMESPACE" -l app=frontend -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
if echo "$FRONTEND_READY" | grep -q "True"; then
    echo "  ✓ Frontend pods are Ready"
    PASS=$((PASS + 1))
else
    echo "  ⚠ Frontend pods not Ready"
    FAIL=$((FAIL + 1))
fi
echo ""

# ── Service checks ──────────────────────────────────────────────
echo "[Services]"
check "Backend service exists" kubectl get svc backend -n "$NAMESPACE"
check "Frontend service exists" kubectl get svc frontend -n "$NAMESPACE"
echo ""

# ── Endpoint connectivity ────────────────────────────────────────
echo "[Connectivity]"
FRONTEND_URL=$(minikube service frontend -n "$NAMESPACE" --url 2>/dev/null || echo "")
if [ -n "$FRONTEND_URL" ]; then
    echo "  ✓ Frontend URL: $FRONTEND_URL"
    PASS=$((PASS + 1))

    if curl -s --max-time 5 "$FRONTEND_URL" >/dev/null 2>&1; then
        echo "  ✓ Frontend is responding"
        PASS=$((PASS + 1))
    else
        echo "  ⚠ Frontend not responding yet"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  ⚠ Could not get frontend URL"
    FAIL=$((FAIL + 1))
fi
echo ""

# ── Summary ──────────────────────────────────────────────────────
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Results: $PASS passed, $FAIL warnings/failures"
echo ""
echo "  Useful commands:"
echo "    kubectl get pods -n todohub"
echo "    kubectl logs -n todohub -l app=backend"
echo "    kubectl logs -n todohub -l app=frontend"
echo "    minikube service frontend -n todohub"
echo "    minikube dashboard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
