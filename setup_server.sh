#!/bin/bash

# Check if the correct number of arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <app_port> <domain>"
    exit 1
fi

APP_PORT=$1
DOMAIN=$2

echo "Starting setup for domain: $DOMAIN on port: $APP_PORT"

# Update package list and install Nginx
echo "Updating package list..."
sudo apt update
echo "Installing Nginx..."
sudo apt install -y nginx

# Install Certbot for SSL certificate generation
echo "Installing Certbot and dependencies for SSL certificate generation..."
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot

# Create Nginx configuration for the domain
echo "Creating Nginx configuration for domain: $DOMAIN..."
sudo tee /etc/nginx/sites-available/$DOMAIN <<EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://localhost:$APP_PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable the new configuration
echo "Enabling Nginx configuration for domain: $DOMAIN..."
sudo ln -s /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/

# Test Nginx configuration and reload Nginx
echo "Testing Nginx configuration..."
sudo nginx -t
if [ $? -eq 0 ]; then
    echo "Nginx configuration test passed. Reloading Nginx..."
    sudo systemctl reload nginx
else
    echo "Nginx configuration test failed. Exiting..."
    exit 1
fi

# Obtain SSL certificate and configure HTTPS
echo "Obtaining SSL certificate for domain: $DOMAIN..."
sudo certbot --nginx -d $DOMAIN
if [ $? -eq 0 ]; then
    echo "SSL certificate successfully obtained and HTTPS configured for $DOMAIN"
else
    echo "Failed to obtain SSL certificate for $DOMAIN. Please check the logs for details."
    exit 1
fi

echo "Nginx proxy setup complete and HTTPS configured for $DOMAIN"