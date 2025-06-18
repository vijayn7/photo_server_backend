# Troubleshooting Environment Variable Issues

If you encounter issues with environment variables such as the admin password or JWT settings, follow these steps:

## Common Issues

### "TypeError: secret must be unicode or bytes, not None"

This error occurs when the `PHOTO_SERVER_ADMIN_PASSWORD` environment variable isn't properly set. To fix:

1. **Check your .env file**:
   ```
   cat .env
   ```
   Make sure it contains:
   ```
   PHOTO_SERVER_ADMIN_PASSWORD=your_password
   ```

2. **Run the environment fix script**:
   ```
   ./scripts/fix_environment.sh
   ```
   This script will diagnose and fix common environment issues.

3. **Restart the service**:
   ```
   sudo systemctl restart photo-api.service
   ```

### JWT Authentication Errors

If you're encountering JWT related errors:

1. Make sure `SECRET_KEY` is defined in your `.env` file
2. Check if `ALGORITHM` is set to `HS256`
3. Run the environment fix script to diagnose issues

## Manual Environment Variable Check

You can manually check if environment variables are being loaded correctly:

```bash
cd /path/to/photo_server_backend
source .env
echo $PHOTO_SERVER_ADMIN_PASSWORD
```

If it returns empty, the variable isn't set correctly.

## Recreating the Users Database

If user authentication isn't working correctly, you may need to recreate the users database:

1. Backup the existing users:
   ```bash
   cp python/users.json python/users.json.backup
   ```

2. Delete the users file:
   ```bash
   rm python/users.json
   ```

3. Restart the service:
   ```bash
   sudo systemctl restart photo-api.service
   ```

4. The server will automatically create a new users.json with default users.

## Systemd Service Configuration

If you're using systemd, make sure the service file includes:

```
EnvironmentFile=/path/to/.env
```

This ensures environment variables are properly loaded from the .env file.
