import os
import json
import base64
import requests
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

# — GitHub repo settings — fill in your details
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN environment variable is required")

GITHUB_REPO = "Daksh159357/server-testing"   # your repo
FILE_PATH   = "data.json"
BRANCH      = "main"                          # or your branch

API_URL_BASE = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{FILE_PATH}"

@app.get("/")
def home():
    return {"message": "✅ GitHub JSON Database API running!"}

@app.get("/data")
def get_data():
    url = f"https://raw.githubusercontent.com/{GITHUB_REPO}/{BRANCH}/{FILE_PATH}"
    resp = requests.get(url)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Failed to fetch file: {resp.text}")
    try:
        data = resp.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"JSON parse error: {e}")
    return {"data": data}

@app.post("/add")
async def add_data(request: Request):
    new_entry = await request.json()

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept":        "application/vnd.github+json",
    }
    params = {"ref": BRANCH}

    # 1️⃣ Get current file metadata (including SHA)
    resp = requests.get(API_URL_BASE, headers=headers, params=params)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail=f"Could not fetch file metadata: {resp.text}")
    file_info = resp.json()
    sha = file_info.get("sha")
    if sha is None:
        raise HTTPException(status_code=500, detail="No SHA found in repo file metadata")

    encoded_content = file_info.get("content", "")
    try:
        content_bytes = base64.b64decode(encoded_content)
        current_data = json.loads(content_bytes.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to decode JSON content: {e}")

    # Append the new entry
    current_data.append(new_entry)

    # 2️⃣ Prepare new content
    new_content_bytes = json.dumps(current_data, indent=2).encode("utf-8")
    new_content_b64   = base64.b64encode(new_content_bytes).decode("utf-8")

    body = {
        "message": f"Update {FILE_PATH} via API",
        "content": new_content_b64,
        "sha":     sha,
        "branch":  BRANCH
    }

    update_resp = requests.put(API_URL_BASE, headers=headers, json=body)
    if update_resp.status_code not in (200, 201):
        raise HTTPException(status_code=update_resp.status_code,
                            detail=f"Failed to update file: {update_resp.text}")

    return {"status": "saved", "entry": new_entry}

# This block ensures the app keeps running when you execute the script
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0",
                port=int(os.environ.get("PORT", 8000)),
                log_level="info")
