# 🚀 SEAS Financial Tracker - Deployment Guide

## 📋 **Overview**

This guide covers the complete deployment process for the SEAS Financial Tracker application, including CI/CD pipeline setup, server configuration, and production deployment.

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   GitHub Repo   │───▶│  GitHub Actions │───▶│  Production    │
│                 │    │   CI/CD Pipeline│    │    Server      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Docker Images  │
                       │   & Packages    │
                       └─────────────────┘
```

## 🔧 **Prerequisites**

### **Local Development**
- Python 3.9+
- Docker & Docker Compose
- Git

### **Server Requirements**
- Ubuntu 20.04+ or Debian 11+
- 2GB RAM minimum (4GB recommended)
- 20GB disk space
- Root access or sudo privileges

### **External Services**
- GitHub repository
- Docker Hub account
- Domain name (for production)
- SSL certificate (for production)

## 🚀 **CI/CD Pipeline Setup**

### **1. GitHub Repository Setup**

1. **Fork/Clone** the repository to your GitHub account
2. **Enable GitHub Actions** in repository settings
3. **Set up branch protection** for `main` branch

### **2. GitHub Secrets Configuration**

Navigate to `Settings > Secrets and variables > Actions` and add:

```bash
# Docker Hub
DOCKER_USERNAME=your_dockerhub_username
DOCKER_PASSWORD=your_dockerhub_password

# Staging Server
STAGING_HOST=staging.yourdomain.com
STAGING_USERNAME=seas
STAGING_SSH_KEY=your_private_ssh_key

# Production Server
PRODUCTION_HOST=yourdomain.com
PRODUCTION_USERNAME=seas
PRODUCTION_SSH_KEY=your_private_ssh_key
PRODUCTION_URL=https://yourdomain.com

# Notifications (Optional)
SLACK_WEBHOOK_URL=your_slack_webhook_url
```

### **3. Branch Strategy**

- **`main`**: Production-ready code
- **`develop`**: Staging/testing code
- **Feature branches**: Individual features

## 🐳 **Docker Configuration**

### **1. Build Local Image**

```bash
# Build the application image
docker build -t seas-financial-tracker:latest .

# Test locally
docker run -p 8501:8501 seas-financial-tracker:latest
```

### **2. Push to Docker Hub**

```bash
# Tag and push
docker tag seas-financial-tracker:latest yourusername/seas-financial-tracker:latest
docker push yourusername/seas-financial-tracker:latest
```

## 🖥️ **Server Deployment**

### **1. Initial Server Setup**

```bash
# SSH to your server
ssh root@your-server-ip

# Run the setup script
wget https://raw.githubusercontent.com/yourusername/seas-financial-tracker/main/scripts/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh
```

### **2. Application Deployment**

```bash
# Switch to application user
su - seas

# Clone repository
cd /opt/seas-financial-tracker
git clone https://github.com/yourusername/seas-financial-tracker.git .

# Deploy to staging
./scripts/deploy.sh staging

# Deploy to production
./scripts/deploy.sh production
```

### **3. SSL Certificate Setup**

```bash
# Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 **Monitoring & Maintenance**

### **1. Health Checks**

```bash
# Check application status
systemctl status seas-financial-tracker

# View logs
journalctl -u seas-financial-tracker -f

# Manual health check
curl -f http://localhost:8501/_stcore/health
```

### **2. Backup & Recovery**

```bash
# Manual backup
/opt/seas-financial-tracker/backup.sh

# Restore from backup
cd /opt/seas-financial-tracker
tar -xzf backups/seas_backup_YYYYMMDD_HHMMSS.tar.gz
```

### **3. Updates & Maintenance**

```bash
# Update application
cd /opt/seas-financial-tracker
git pull origin main
docker-compose -f docker-compose.production.yml up -d --build

# Update system packages
sudo apt-get update && sudo apt-get upgrade -y
```

## 🔒 **Security Configuration**

### **1. Firewall Rules**

```bash
# Check firewall status
sudo ufw status

# Allow specific ports
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8501/tcp  # Streamlit (if needed)
```

### **2. Fail2ban Configuration**

```bash
# Check fail2ban status
sudo systemctl status fail2ban

# View banned IPs
sudo fail2ban-client status sshd
```

### **3. SSL/TLS Security**

```bash
# Test SSL configuration
curl -I https://yourdomain.com

# Check SSL grade
# Visit: https://www.ssllabs.com/ssltest/
```

## 📈 **Performance Optimization**

### **1. Nginx Configuration**

- **Gzip compression** enabled
- **Static file caching** configured
- **Rate limiting** implemented
- **Security headers** added

### **2. Docker Optimization**

- **Multi-stage builds** for smaller images
- **Resource limits** configured
- **Health checks** implemented
- **Volume mounting** for persistence

### **3. Monitoring Stack**

- **Prometheus** for metrics collection
- **Grafana** for visualization
- **Custom dashboards** for application metrics
- **Alerting** for critical issues

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Application won't start**
   ```bash
   # Check logs
   docker-compose logs seas-financial-tracker
   
   # Check container status
   docker-compose ps
   ```

2. **Port conflicts**
   ```bash
   # Check what's using port 8501
   sudo netstat -tlnp | grep :8501
   
   # Stop conflicting service
   sudo systemctl stop conflicting-service
   ```

3. **SSL certificate issues**
   ```bash
   # Check certificate validity
   sudo certbot certificates
   
   # Renew certificate
   sudo certbot renew
   ```

### **Debug Commands**

```bash
# Check system resources
htop
df -h
free -h

# Check Docker resources
docker system df
docker stats

# Check application health
curl -v http://localhost:8501/_stcore/health
```

## 📚 **Additional Resources**

### **Documentation**
- [Streamlit Deployment Guide](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Nginx Configuration](https://nginx.org/en/docs/)

### **Monitoring Tools**
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)
- [Node Exporter](https://prometheus.io/docs/guides/node-exporter/)

### **Security Tools**
- [Let's Encrypt](https://letsencrypt.org/docs/)
- [Fail2ban](https://www.fail2ban.org/wiki/index.php/Main_Page)
- [UFW](https://help.ubuntu.com/community/UFW)

## 🤝 **Support**

### **Getting Help**
1. **Check logs** first: `journalctl -u seas-financial-tracker -f`
2. **Review this documentation**
3. **Check GitHub Issues**
4. **Create new issue** with detailed error information

### **Contributing**
1. **Fork the repository**
2. **Create feature branch**
3. **Make changes**
4. **Submit pull request**

---

**🎯 This deployment guide provides everything needed to deploy the SEAS Financial Tracker to production with enterprise-grade reliability, security, and monitoring.**
