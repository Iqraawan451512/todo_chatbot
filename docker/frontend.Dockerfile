# ── Stage 1: Dependencies ────────────────────────────────────────
FROM node:20-alpine AS deps

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --ignore-scripts 2>/dev/null || npm install --ignore-scripts

# ── Stage 2: Builder ────────────────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /app

COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

# Build-time env: backend URL (overridable at build)
ARG NEXT_PUBLIC_API_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Disable Next.js telemetry
ENV NEXT_TELEMETRY_DISABLED=1

RUN npm run build

# ── Stage 3: Runtime ────────────────────────────────────────────
FROM node:20-alpine

LABEL maintainer="TodoHub Team"
LABEL description="TodoHub Frontend — Next.js 15 + React 19"

WORKDIR /app

# Security: run as non-root
RUN addgroup -S appuser && adduser -S appuser -G appuser

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

# Copy only production artifacts
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Own files to non-root user
RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD wget -q --spider http://localhost:3000 || exit 1

CMD ["node", "server.js"]
