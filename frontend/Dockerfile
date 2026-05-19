FROM node:22-alpine AS deps

WORKDIR /app

COPY package*.json ./
RUN npm ci

FROM deps AS quality

COPY . .
RUN npm run lint
RUN npm test

FROM nginxinc/nginx-unprivileged:1.27-alpine AS runtime

USER root

RUN rm -rf /usr/share/nginx/html/* \
    && printf '%s\n' \
    '<!doctype html>' \
    '<html lang="en">' \
    '<head><meta charset="utf-8"><title>AviAI Mini Program</title></head>' \
    '<body><h1>AviAI Mini Program Frontend</h1><p>Import the frontend directory in WeChat DevTools to run the mini program.</p></body>' \
    '</html>' \
    > /usr/share/nginx/html/index.html \
    && chown -R 101:101 /usr/share/nginx/html

USER 101

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD wget -qO- http://127.0.0.1:8080/ >/dev/null || exit 1
