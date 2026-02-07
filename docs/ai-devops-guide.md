# AI DevOps Tools Guide — TodoHub

This guide demonstrates how to use AI-assisted DevOps tools with TodoHub's Kubernetes deployment.

---

## 1. kubectl-ai — Natural Language Kubernetes Management

[kubectl-ai](https://github.com/sozercan/kubectl-ai) translates natural language into kubectl commands.

### Installation

```bash
# Install via krew
kubectl krew install ai

# Or download binary from GitHub releases
# Set your OpenAI API key
export OPENAI_API_KEY="sk-your-key"
```

### Real Example Commands

#### Deploy workloads
```bash
# Deploy the backend
kubectl ai "deploy todohub-backend image with 2 replicas in namespace todohub, expose port 8000"
# Generated: kubectl create deployment backend --image=todohub-backend:latest --replicas=2 -n todohub

# Deploy the frontend
kubectl ai "deploy todohub-frontend with 2 replicas in todohub namespace on port 3000"
```

#### Scale replicas
```bash
# Scale up during high traffic
kubectl ai "scale the backend deployment to 5 replicas in todohub namespace"
# Generated: kubectl scale deployment backend --replicas=5 -n todohub

# Scale down for cost savings
kubectl ai "scale frontend to 1 replica in todohub"
# Generated: kubectl scale deployment frontend --replicas=1 -n todohub
```

#### Diagnose pod issues
```bash
# Find crashing pods
kubectl ai "show me pods that are not running in todohub namespace"
# Generated: kubectl get pods -n todohub --field-selector=status.phase!=Running

# Debug a specific pod
kubectl ai "show logs from the backend pod in todohub that crashed most recently"
# Generated: kubectl logs -n todohub -l app=backend --previous --tail=50

# Check resource usage
kubectl ai "show CPU and memory usage for all pods in todohub"
# Generated: kubectl top pods -n todohub

# Describe failing pods
kubectl ai "describe the backend pods in todohub namespace to find crash reason"
# Generated: kubectl describe pods -n todohub -l app=backend

# Check events for errors
kubectl ai "show warning events in todohub namespace"
# Generated: kubectl get events -n todohub --field-selector=type=Warning
```

#### Rollback deployments
```bash
# Rollback to previous version
kubectl ai "rollback the backend deployment in todohub to previous version"
# Generated: kubectl rollout undo deployment/backend -n todohub

# Check rollout status
kubectl ai "show rollout status of backend deployment in todohub"
# Generated: kubectl rollout status deployment/backend -n todohub
```

---

## 2. kagent — AI-Powered Cluster Analysis

[kagent](https://github.com/kagent-dev/kagent) provides intelligent cluster health analysis and resource optimization.

### Installation

```bash
# Install kagent CLI
pip install kagent

# Or via Helm
helm repo add kagent https://kagent-dev.github.io/kagent
helm install kagent kagent/kagent
```

### Real Example Commands

#### Analyze cluster health
```bash
# Overall cluster health assessment
kagent "analyze the health of my todohub namespace"
# Output: Checks pod status, resource utilization, pending pods, failed probes

# Check for common issues
kagent "are there any issues with my todohub deployment?"
# Output: Reports OOMKilled containers, CrashLoopBackOff, ImagePullBackOff

# Network connectivity check
kagent "can the frontend pods reach the backend service in todohub?"
# Output: Tests service DNS resolution and port connectivity
```

#### Optimize resources
```bash
# Get resource recommendations
kagent "recommend resource limits for todohub backend pods based on current usage"
# Output: Analyzes CPU/memory usage patterns and suggests optimal requests/limits

# Find over-provisioned pods
kagent "find pods in todohub that are using less than 20% of their resource limits"
# Output: Lists pods with wasted resources and recommended downsizing

# Cost optimization
kagent "suggest ways to reduce resource costs in todohub namespace"
# Output: Recommends replica count adjustments, resource right-sizing

# HPA recommendations
kagent "should I enable autoscaling for the backend deployment in todohub?"
# Output: Analyzes traffic patterns and recommends HPA settings
```

#### Security analysis
```bash
# Security posture check
kagent "check security best practices for todohub namespace"
# Output: Verifies non-root containers, resource limits set, no privileged pods

# Secret management review
kagent "review secret management in todohub namespace"
# Output: Checks for plaintext secrets, suggests sealed-secrets or external-secrets
```

---

## 3. Docker AI Agent (Gordon)

Docker Desktop includes Gordon, an AI assistant for container operations.

### Usage (Docker Desktop UI)

```
# In Docker Desktop, click the AI Assistant icon and ask:

"Build optimized images for my Python FastAPI backend and Next.js frontend"
"Why is my todohub-backend container failing health checks?"
"Suggest multi-stage build improvements for my Dockerfiles"
"Help me debug networking between frontend and backend containers"
```

### CLI Integration

```bash
# Ask Gordon via CLI (Docker Desktop 4.30+)
docker ai "optimize my backend.Dockerfile for smaller image size"
docker ai "why is my todohub-backend container exiting with code 1?"
docker ai "suggest security improvements for my container setup"
```

---

## Quick Reference — Common Operations

| Task | kubectl-ai Command |
|------|-------------------|
| Check pod status | `kubectl ai "show all pod statuses in todohub"` |
| View logs | `kubectl ai "show last 100 lines of backend logs in todohub"` |
| Scale up | `kubectl ai "scale backend to 4 replicas in todohub"` |
| Scale down | `kubectl ai "scale frontend to 1 replica in todohub"` |
| Restart pods | `kubectl ai "restart all backend pods in todohub"` |
| Port forward | `kubectl ai "forward local port 8080 to backend service in todohub"` |
| Resource usage | `kubectl ai "show resource usage for todohub namespace"` |
| Find errors | `kubectl ai "show error events in todohub in last hour"` |

---

## Access TodoHub on Minikube

```bash
# Open in browser
minikube service frontend -n todohub

# Or get the URL
minikube service frontend -n todohub --url

# Dashboard
minikube dashboard
```
