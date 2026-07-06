# Multi-stage build for optimized production image
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy application code
COPY src ./src

# Build the application
RUN npm run build


# Production stage
FROM node:18-alpine

# Set metadata labels
LABEL maintainer="dev@example.com"
LABEL version="1.0"
LABEL description="Shiny code editor application"

# Define build argument
ARG NODE_ENV=production

# Set environment variables
ENV NODE_ENV=$NODE_ENV \
    PORT=3000 \
    APP_HOME=/app

# Set working directory
WORKDIR $APP_HOME

# Copy built application from builder stage
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/dist ./dist
COPY package.json ./

# Expose port
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Define entrypoint
ENTRYPOINT ["node"]

# Set default command
CMD ["dist/index.js"]
