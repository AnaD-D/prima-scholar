# ---------- Build stage ----------
FROM node:18-alpine AS build
WORKDIR /app

# Toolchain para dependencias nativas
RUN apk add --no-cache --virtual .gyp python3 make g++

# Usar cache: primero los manifests
COPY package*.json ./
RUN npm ci --no-audit --no-fund

# Código fuente
COPY . .

# Var de build para CRA
ARG REACT_APP_API_URL=/api
ENV REACT_APP_API_URL=$REACT_APP_API_URL

# Compilar
RUN npm run build

# Limpiar toolchain (no se copia al siguiente stage)
RUN apk del .gyp

# ---------- Runtime (nginx) ----------
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]