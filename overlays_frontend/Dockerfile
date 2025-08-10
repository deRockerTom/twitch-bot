# Stage 1: Base Bun image
FROM oven/bun:alpine AS base

WORKDIR /app

# Stage 2: Install dependencies
FROM base AS deps
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

# Stage 3: Build the app
FROM base AS builder
ENV NEXT_PRIVATE_STANDALONE=true
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN bun run build

# Stage 4: Final image
FROM base AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["bun", "run", "server.js"]
