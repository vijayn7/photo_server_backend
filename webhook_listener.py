from fastapi import FastAPI, Request
import subprocess

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()

    # Only react to pushes to "main"
    if payload.get("ref") == "refs/heads/main":
        subprocess.run(["git", "pull", "origin", "main"], cwd="/home/vnannapu/photo-server")
        subprocess.run(["systemctl", "restart", "photo-server"])  # optional if using systemd
        return {"message": "Code pulled and service restarted"}

    return {"message": "Not a main branch push"}
