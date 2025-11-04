# syntax=docker/dockerfile:1

FROM nginx:alpine

ARG BUILD_DIR=/usr/share/nginx/html

RUN rm -rf ${BUILD_DIR}/*

COPY index.html style.css app.js ${BUILD_DIR}/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s CMD wget --no-verbose --tries=1 --spider http://localhost || exit 1

