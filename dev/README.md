# Development Scripts and Configuration

This folder contains scripts and configuration files for developing the Photo Server locally.

## Quick Start

1. **Deploy for Development**
   ```bash
   ./dev/deploy-dev.sh
   ```
   This will:
   - Set up Python virtual environment
   - Install all dependencies
   - Build the React frontend
   - Create development .env file
   - Set up local photo storage directories

2. **Start Development Servers**
   ```bash
   ./dev/start-dev.sh
   ```
   This runs:
   - FastAPI server on http://localhost:8000 (with auto-reload)
   - React dev server on http://localhost:3000 (with hot reload)
   
   **Note**: In dev mode, React proxies API calls to FastAPI

3. **Start Production Mode (for testing)**
   ```bash
   ./dev/start-prod.sh
   ```
   This runs:
   - FastAPI server on http://localhost:8000
   - Serves built React app from FastAPI
   - Simulates production environment

## File Structure

```
dev/
├── deploy-dev.sh      # Development deployment script
├── start-dev.sh       # Start development servers
├── start-prod.sh      # Start production mode locally
├── config.env         # Development configuration
├── deploy.log         # Deployment log file
└── README.md          # This file
```

## Development vs Production

### Development Mode (`start-dev.sh`)
- React dev server with hot reload
- FastAPI with auto-reload
- API calls proxied from React to FastAPI
- Separate ports (3000 for React, 8000 for API)
- Better for active development

### Production Mode (`start-prod.sh`)
- Built React app served by FastAPI
- Single port (8000)
- Simulates production deployment
- Better for testing the final build

## Environment Variables

Development environment variables are automatically created in `.env` file:

- `PHOTO_SERVER_ADMIN=admin`
- `PHOTO_SERVER_ADMIN_PASSWORD=admin`
- `SECRET_KEY` (auto-generated)
- Local storage paths for photos and thumbnails

## Storage Directories

Development mode creates local directories:
- `photos/` - User uploaded photos
- `photos/global/` - Global photos (admin uploads)
- `thumbnails/` - Generated thumbnails
- `data/` - Database and other data files

## Troubleshooting

### React Build Fails
```bash
cd frontend
npm install
npm run build
```

### Python Dependencies Issues
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Permission Errors on Scripts
```bash
chmod +x dev/*.sh
```

### Server Won't Start
Check the log file:
```bash
tail -f dev/deploy.log
```

## Default Credentials

For development, the default admin credentials are:
- Username: `admin`
- Password: `admin`

**Note**: Change these in production!
