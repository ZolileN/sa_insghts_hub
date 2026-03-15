# Production Deployment Guide

## Overview

The SA Insight Hub can run in production using cron jobs, but requires proper setup and monitoring. Here are your options:

## Option 1: Cloud Server with Cron (Recommended)

### Pros
- ✅ Full control over environment
- ✅ Cost-effective (starting from ~$5/month)
- ✅ Reliable with proper setup
- ✅ Easy to monitor and debug

### Recommended Providers
- **DigitalOcean** (Droplets) - $5/month
- **AWS EC2** (t2.micro) - Free tier available
- **Linode** - $5/month
- **Vultr** - $5/month

### Setup Steps

1. **Provision Server**
   ```bash
   # Ubuntu 22.04 LTS recommended
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y python3 python3-pip python3-venv git curl
   ```

2. **Deploy Application**
   ```bash
   # Clone repository
   cd /opt
   sudo git clone https://github.com/ZolileN/sa_insghts_hub.git
   sudo chown -R $USER:$USER /opt/sa-insight-hub
   cd /opt/sa-insight-hub
   
   # Setup virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   # Copy and edit production config
   cp .env.production .env
   nano .env  # Adjust paths and settings
   ```

4. **Setup Git Credentials**
   ```bash
   git config --global user.name "SA Insight Bot"
   git config --global user.email "bot@sa-insight-hub.co.za"
   
   # For GitHub access, use personal access token
   git remote set-url origin https://username:token@github.com/ZolileN/sa_insghts_hub.git
   ```

5. **Install Production Cron Jobs**
   ```bash
   crontab cron_production.txt
   ```

6. **Setup Monitoring**
   ```bash
   # Install monitoring tools
   sudo apt install -y htop iotop nethogs
   
   # Setup log rotation
   sudo nano /etc/logrotate.d/sa-insight-hub
   ```

## Option 2: GitHub Actions (Alternative)

If you prefer to stick with cloud-based automation:

1. Re-enable GitHub Actions
2. Add secrets for API keys
3. Use self-hosted runners for more control

## Option 3: Kubernetes/CronJobs

For enterprise deployments:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: sa-insight-realtime
spec:
  schedule: "*/30 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: scraper
            image: sa-insight-hub:latest
            command: ["python", "run_scrapers.py", "--topics", "forex energy"]
          restartPolicy: OnFailure
```

## Production Monitoring

### Essential Monitoring
1. **Log Monitoring**
   ```bash
   tail -f /opt/sa-insight-hub/logs/production.log
   ```

2. **System Resources**
   ```bash
   htop          # CPU/Memory usage
   df -h         # Disk space
   free -h       # Memory usage
   ```

3. **Service Health**
   ```bash
   ./health_check.sh
   ```

### Alerting Setup
- **Email alerts**: Configure `mail` command
- **Slack alerts**: Set webhook URL in `.env`
- **Monitoring services**: UptimeRobot, Pingdom, etc.

## Security Considerations

1. **SSH Keys**: Use SSH keys instead of passwords
2. **Firewall**: Configure UFW firewall
   ```bash
   sudo ufw enable
   sudo ufw allow ssh
   sudo ufw allow 8000  # If running web interface
   ```
3. **API Keys**: Store in environment variables, not code
4. **Regular Updates**: Keep system and packages updated

## Backup Strategy

1. **Code Repository**: GitHub serves as code backup
2. **Data Backups**: Daily automated backups
3. **Configuration Backups**: Backup `.env` and cron jobs

## Scaling Considerations

For high-traffic scenarios:
- Use Redis for caching
- Implement database for historical data
- Consider message queues for async processing
- Load balancing for web interface

## Troubleshooting

### Common Issues
1. **Cron not running**: Check cron service status
2. **Git push failures**: Verify credentials and permissions
3. **Memory issues**: Monitor RAM usage, consider swap space
4. **Network issues**: Check internet connectivity and DNS

### Debug Commands
```bash
# Check cron service
sudo systemctl status cron

# Check cron logs
sudo tail -f /var/log/cron.log

# Test cron job manually
/opt/sa-insight-hub/cron_production.sh realtime "forex energy" "test" "data/forex.json"

# Check git status
cd /opt/sa-insight-hub && git status
```

## Cost Estimate

**Monthly Cost Breakdown**:
- Server: $5-10 (DigitalOcean/AWS)
- Storage: $0-5 (depending on data size)
- Monitoring: $0-10 (if using paid services)
- **Total**: $5-25/month

## Recommendation

For most use cases, **Option 1 (Cloud Server with Cron)** provides the best balance of:
- Cost-effectiveness
- Reliability
- Control
- Easy monitoring
- Simple maintenance

The current cron setup is production-ready with the provided production scripts and proper server configuration.
