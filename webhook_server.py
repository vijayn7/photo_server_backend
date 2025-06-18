import subprocess
from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/webhook/")
async def deploy(request: Request):
    payload = await request.json()
    print("Received webhook:", payload)
    # Run deploy.sh in background without waiting
    subprocess.Popen(["/home/vnannapu/photo-server/deploy.sh"])
    return {"status": "deployment started"}
