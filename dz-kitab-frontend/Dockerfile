# Build stage
FROM node:18-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM caddy:2-slim
COPY --from=build /app/dist /usr/share/caddy
EXPOSE 80
CMD ["caddy", "file-server", "--listen", ":80", "--root", "/usr/share/caddy"]
