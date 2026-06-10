# Dev-mode Dockerfile for the Capstone frontend.
# Uses Next.js dev server with hot-reload (volume-mounted source in compose).
# For production we'd want a multi-stage build with `next build` + `next start`,
# but dev mode is fine for the live class demo.

FROM node:22-alpine

WORKDIR /app

# Install dependencies first for cache efficiency.
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the source (overlaid by volume mount in compose anyway).
COPY . .

EXPOSE 3000

# Bind to 0.0.0.0 so it's reachable from the host (not just the container).
CMD ["npm", "run", "dev", "--", "-H", "0.0.0.0"]
