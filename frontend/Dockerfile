# Stage 1: build React app
FROM node:18-alpine AS build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Stage 2: serve with nginx
FROM nginx:alpine

# Copy build output
COPY --from=build /app/build /usr/share/nginx/html

# Use Cloud Run's default port environment variable
ENV PORT 8080
EXPOSE 8080

# Use envsubst to replace PORT in nginx config
RUN apk add --no-cache bash
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]