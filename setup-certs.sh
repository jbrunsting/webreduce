docker run -it --rm \
    -v certs:/etc/letsencrypt \
    -v certs-data:/data/letsencrypt \
    deliverous/certbot \
    certonly \
    --webroot --webroot-path=/data/letsencrypt \
    -d webreduce.ca -d www.webreduce.ca
