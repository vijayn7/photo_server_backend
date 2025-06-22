# 🚀 Deployment Guide

## Overview

The `deploy.sh` script is a comprehensive deployment automation tool that handles everything needed when the code changes. It's designed for production deployment on a Linux server.

## Features

### ✅ **Complete Deployment Pipeline**
- **Git Integration**: Pulls latest code from repository
- **Python Environment**: Sets up virtual environment and installs dependencies
- **Node.js Management**: Auto-installs Node.js if needed
- **React Build**: Builds the frontend application
- **Environment Configuration**: Sets up `.env` file with secure defaults
- **Service Management**: Configures and manages systemd service
- **Health Checks**: Verifies deployment success
- **Error Handling**: Comprehensive error checking with detailed logging

### 🔧 **What It Does**

1. **Code Update**
   - Pulls latest code from git repository
   - Resets to latest main branch

2. **Directory Setup**
   - Creates required directories (`photos`, `data`, `thumbnails`)
   - Sets proper permissions

3. **Python Environment**
   - Creates/updates virtual environment
   - Installs/updates Python dependencies from `requirements.txt`

4. **Node.js & Frontend**
   - Auto-detects and installs Node.js if missing
   - Builds React frontend application
   - Verifies build integrity

5. **Configuration**
   - Creates/updates `.env` file with secure settings
   - Generates random JWT secret keys
   - Sets production-appropriate paths

6. **Service Deployment**
   - Updates systemd service configuration
   - Gracefully stops existing service
   - Starts new service version
   - Verifies service health

7. **Verification**
   - Tests application loading
   - Checks HTTP responses
   - Provides deployment summary

## Usage

### Basic Deployment
```bash
# On the production server
cd /home/vnannapu/photo-server
sudo ./deploy.sh
```

### Check Deployment Status
```bash
# Verify deployment health
./scripts/check-deployment.sh
```

### View Deployment Logs
```bash
# View detailed deployment logs
tail -f /home/vnannapu/deploy.log
```

## Configuration

### Environment Variables
The script automatically creates/updates `.env` with:
- `PHOTO_SERVER_ADMIN`: Admin username
- `PHOTO_SERVER_ADMIN_PASSWORD`: Admin password
- `SECRET_KEY`: Auto-generated JWT secret
- `PHOTOS_PATH`: Photo storage directory
- `DB_PATH`: Database file path

### Directory Structure
Creates and manages:
```
/home/vnannapu/photo-server/
├── photos/          # Photo storage
├── photos/global/   # Shared photos
├── data/           # Database files
├── thumbnails/     # Generated thumbnails
├── venv/           # Python virtual environment
├── frontend/build/ # React application
└── .env           # Environment configuration
```

## Error Handling

The script includes comprehensive error handling:
- **Exit on Error**: Stops immediately if any step fails
- **Detailed Logging**: All operations logged with timestamps
- **Service Verification**: Confirms service starts successfully
- **Rollback Capability**: Service stops gracefully if deployment fails

## Security Features

- **Secure Defaults**: Auto-generates secure JWT keys
- **File Permissions**: Sets appropriate permissions on sensitive files
- **Service Isolation**: Runs under dedicated user account
- **Environment Protection**: Secures `.env` file permissions

## Monitoring

### Service Status
```bash
# Check if service is running
systemctl status photo-server.service

# View recent logs
journalctl -u photo-server.service -f
```

### Application Health
```bash
# Test HTTP response
curl http://localhost:8000/

# Check React frontend
curl http://localhost:8000/static/
```

## Troubleshooting

### Common Issues

1. **Permission Denied**
   ```bash
   chmod +x deploy.sh
   ```

2. **Service Won't Start**
   ```bash
   # Check logs
   journalctl -u photo-server.service --no-pager -n 50
   ```

3. **React Build Fails**
   ```bash
   # Check Node.js version
   node --version
   npm --version
   ```

4. **Python Dependencies Fail**
   ```bash
   # Check Python version
   python3 --version
   # Manually activate venv and test
   source venv/bin/activate
   pip install -r requirements.txt
   ```

### Log Analysis
```bash
# View deployment log
cat /home/vnannapu/deploy.log

# Filter for errors
grep "ERROR" /home/vnannapu/deploy.log

# View recent deployment
tail -100 /home/vnannapu/deploy.log
```

## Integration

### With CI/CD
The script can be integrated with GitHub Actions or other CI/CD systems:

```yaml
- name: Deploy to Production
  run: |
    ssh user@server 'cd /home/vnannapu/photo-server && ./deploy.sh'
```

### With Webhooks
Use with the included webhook server for automatic deployments on git push.

## Best Practices

1. **Test First**: Always test in development before production deployment
2. **Backup**: Backup database and photos before major deployments
3. **Monitor**: Watch logs during and after deployment
4. **Verify**: Use check-deployment.sh to verify success
5. **Document**: Keep track of what changes are being deployed

## Support Files

- `scripts/check-deployment.sh`: Deployment verification
- `services/photo-server.service`: Systemd service configuration
- `scripts/nginx-reload.sh`: Nginx configuration reload
- `requirements.txt`: Python dependencies
- `frontend/package.json`: Node.js dependencies

---

**✅ The deploy.sh script now handles everything needed for a complete production deployment!**
