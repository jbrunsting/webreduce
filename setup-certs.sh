docker run -it --rm --name certbot \
    -v /certs/letsencrypt:/etc/letsencrypt \
    -v /var/log/letsencrypt:/var/log/letsencrypt \
    -v /docker/nginx/www/letsencrypt:/var/www/.well-known \
    quay.io/letsencrypt/letsencrypt -t certonly \
    --agree-tos --renew-by-default \
    --email jacob.brunsting@gmail.com \
    --webroot -w /var/www \
    -d webreduce.ca -d www.webreduce.ca
