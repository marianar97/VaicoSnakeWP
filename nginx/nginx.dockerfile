FROM nginx:1.13.3

COPY nginx.conf /etc/nginx/nginx.conf
COPY certs/cert.key /etc/ssl/certs/cert.key

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]