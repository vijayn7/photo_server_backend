# webhook_server.py

from fastapi import FastAPI, Request
import subprocess

app = FastAPI()

@app.post("/webhook/")
async def deploy(request: Request):
    payload = await request.json()
    print("Received webhook:", payload)
    # Pull latest code and restart service
    subprocess.run(["/home/vnannapu/photo-server/deploy.sh"])
    return {"status": "ok"}
