# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

# Copier package files
COPY package*.json ./

# Installer les dépendances
RUN npm ci --only=production

# Copier le code source
COPY . .

# Build argument pour l'API base URL
ARG NUXT_PUBLIC_API_BASE
ENV NUXT_PUBLIC_API_BASE=${NUXT_PUBLIC_API_BASE}

# Build de l'application
RUN npm run build

# Stage 2: Production
FROM node:20-alpine as production

WORKDIR /app

# Copier les fichiers nécessaires depuis le builder
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package*.json ./

# Installer uniquement les dépendances de production
RUN npm ci --only=production

# Créer un utilisateur non-root
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /app

USER appuser

# Exposer le port
EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => process.exit(r.statusCode === 200 ? 0 : 1))"

# Démarrer l'application
CMD ["node", ".output/server/index.mjs"]
