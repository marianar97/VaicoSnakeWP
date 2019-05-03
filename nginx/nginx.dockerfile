FROM nginx:1.13.3

COPY nginx.conf /etc/nginx/nginx.conf
COPY certs/cert.crt /etc/ssl/certs/cert.crt

EXPOSE 80
EXPOSE 443

CMD ["nginx", "-g", "daemon off;"]