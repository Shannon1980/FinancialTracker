#!/bin/bash

# SEAS Financial Tracker Server Setup Script
# Run this script on a fresh Ubuntu/Debian server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="seas-financial-tracker"
APP_USER="seas"
APP_DIR="/opt/$APP_NAME"
DOCKER_VERSION="24.0.7"

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root"
fi

log "Starting server setup for SEAS Financial Tracker..."

# Update system
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install essential packages
log "Installing essential packages..."
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw \
    fail2ban \
    nginx \
    certbot \
    python3-certbot-nginx \
    unzip \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
log "Installing Docker..."
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Install Docker Compose
log "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create application user
log "Creating application user..."
if id "$APP_USER" &>/dev/null; then
    log "User $APP_USER already exists"
else
    useradd -m -s /bin/bash -d $APP_DIR $APP_USER
    usermod -aG docker $APP_USER
fi

# Create application directory
log "Setting up application directory..."
mkdir -p $APP_DIR
chown $APP_USER:$APP_USER $APP_DIR

# Configure firewall
log "Configuring firewall..."
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 8501/tcp
ufw --force enable

# Configure fail2ban
log "Configuring fail2ban..."
cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
port = http,https
logpath = /var/log/nginx/error.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Configure Nginx
log "Configuring Nginx..."
cat > /etc/nginx/sites-available/$APP_NAME << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
systemctl enable nginx
systemctl restart nginx

# Create systemd service
log "Creating systemd service..."
cat > /etc/systemd/system/$APP_NAME.service << EOF
[Unit]
Description=SEAS Financial Tracker
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/docker-compose -f docker-compose.production.yml up -d
ExecStop=/usr/bin/docker-compose -f docker-compose.production.yml down
TimeoutStartSec=0
User=$APP_USER
Group=$APP_USER

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable $APP_NAME

# Create log rotation
log "Setting up log rotation..."
cat > /etc/logrotate.d/$APP_NAME << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
    postrotate
        systemctl reload $APP_NAME
    endscript
}
EOF

# Create backup script
log "Creating backup script..."
cat > $APP_DIR/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/seas-financial-tracker/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="seas_backup_$DATE.tar.gz"

mkdir -p $BACKUP_DIR
cd /opt/seas-financial-tracker

# Backup data and configuration
tar -czf $BACKUP_DIR/$BACKUP_FILE data/ config/ nginx/ monitoring/

# Keep only last 7 backups
find $BACKUP_DIR -name "seas_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
EOF

chmod +x $APP_DIR/backup.sh
chown $APP_USER:$APP_USER $APP_DIR/backup.sh

# Create cron job for backups
log "Setting up automated backups..."
(crontab -u $APP_USER -l 2>/dev/null; echo "0 2 * * * /opt/seas-financial-tracker/backup.sh") | crontab -u $APP_USER -

# Create monitoring script
log "Creating monitoring script..."
cat > $APP_DIR/monitor.sh << 'EOF'
#!/bin/bash
# Simple health check script

APP_URL="http://localhost:8501/_stcore/health"
LOG_FILE="/opt/seas-financial-tracker/logs/health.log"

# Check application health
if curl -f $APP_URL >/dev/null 2>&1; then
    echo "$(date): Application is healthy" >> $LOG_FILE
else
    echo "$(date): Application health check failed" >> $LOG_FILE
    # Restart service if unhealthy
    systemctl restart seas-financial-tracker
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Warning: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x $APP_DIR/monitor.sh
chown $APP_USER:$APP_USER $APP_DIR/monitor.sh

# Add monitoring to crontab
(crontab -u $APP_USER -l 2>/dev/null; echo "*/5 * * * * /opt/seas-financial-tracker/monitor.sh") | crontab -u $APP_USER -

# Create directories
log "Creating application directories..."
mkdir -p $APP_DIR/{data,logs,backups,nginx/ssl,monitoring/grafana/{dashboards,datasources}}
chown -R $APP_USER:$APP_USER $APP_DIR

# Set up SSL certificates (self-signed for now)
log "Generating self-signed SSL certificate..."
cd $APP_DIR/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout key.pem \
    -out cert.pem \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
chown $APP_USER:$APP_USER *.pem

success "Server setup completed successfully!"
log "Next steps:"
echo "1. Copy your application files to $APP_DIR"
echo "2. Update configuration files as needed"
echo "3. Run: systemctl start $APP_NAME"
echo "4. Check status: systemctl status $APP_NAME"
echo "5. View logs: journalctl -u $APP_NAME -f"
echo ""
log "Application will be available at:"
echo "  - HTTP: http://your-server-ip:8501"
echo "  - HTTPS: https://your-server-ip (if SSL configured)"
echo ""
log "Monitoring and management:"
echo "  - Backup script: $APP_DIR/backup.sh"
echo "  - Health monitoring: $APP_DIR/monitor.sh"
echo "  - Logs: $APP_DIR/logs/"
echo "  - Backups: $APP_DIR/backups/"
