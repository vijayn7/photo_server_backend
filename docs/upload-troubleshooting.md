# Large File Upload Troubleshooting Guide

If you're experiencing issues with uploading large files (30MB or larger) to the photo server, follow this step-by-step troubleshooting guide.

## 1. Check Nginx Configuration

The Nginx web server often has a default upload size limit of 1MB. We need to ensure our configuration allows larger uploads.

### Verify the configuration:

```bash
sudo nano /etc/nginx/sites-available/default
```

Look for these settings in the HTTPS server block:
```
# Allow large file uploads (10GB)
client_max_body_size 10G;

# Increased timeouts for large file uploads
proxy_connect_timeout 600;
proxy_send_timeout 600;
proxy_read_timeout 600;
send_timeout 600;
```

### Test the Nginx configuration:

```bash
sudo nginx -t
```

### Reload Nginx to apply changes:

```bash
sudo systemctl reload nginx
```

## 2. Check FastAPI Service Configuration

### Review the service file:

```bash
sudo nano /etc/systemd/system/photo-server.service
```

Ensure it includes the large file upload settings:
```
ExecStart=/home/vnannapu/photo-server/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --limit-max-body-size 10737418240 --timeout-keep-alive 600
```

### Reload and restart the service:

```bash
sudo systemctl daemon-reload
sudo systemctl restart photo-server
```

## 3. Check the Service Logs

Look for any error messages in the logs:

```bash
sudo journalctl -u photo-server -n 100
```

## 4. Run the Upload Test Script

The test script will create a test file and attempt to upload it:

```bash
sudo ./scripts/test-upload.sh
```

## 5. Common Issues and Solutions

### Issue: 413 Request Entity Too Large
- **Solution**: Increase client_max_body_size in Nginx configuration and reload

### Issue: Connection reset during upload
- **Solution**: Increase timeout settings in Nginx and FastAPI

### Issue: File upload starts but never completes
- **Solution**: Check disk space with `df -h` and ensure enough space is available

### Issue: Memory issues during upload
- **Solution**: Monitor memory usage with `free -m` and consider increasing swap space

## 6. Browser-specific Issues

### Chrome
- Try disabling any upload-related extensions
- Clear browser cache and cookies

### Firefox
- Check if "network.http.max-connections-per-server" is set high enough in about:config

## 7. Testing with curl

Test a direct upload to the FastAPI server (bypassing Nginx):

```bash
curl -v -X POST -F "file=@/path/to/test/file.jpg" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  http://localhost:8000/upload
```

If this works but the browser upload fails, it's likely a Nginx configuration issue.

## 8. Contact Support

If you've tried all the above steps and still experience issues, please contact the system administrator with:

1. The exact error message shown in the browser
2. The file size you're trying to upload
3. The output of the test script
4. The browser and operating system you're using
