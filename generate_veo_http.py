# generate_veo_http.py
import os
import time
import requests
from pathlib import Path

# Load API key from environment
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("❌ GEMINI_API_KEY not found. Set it in your environment or .env file.")

# Use the same prompt as the 'nature' preset for consistency
prompt = "A majestic lion slowly walks through tall savanna grass, golden hour sunlight, cinematic 4K, wildlife documentary style"
duration_sec = 5

print(f"🎬 Generating Veo video via REST API...")
print(f"   Prompt: {prompt[:60]}...")

# Step 1: Start generation
resp = requests.post(
    "https://generativelanguage.googleapis.com/v1/models/veo-1:generateVideo",
    params={"key": api_key},
    headers={"Content-Type": "application/json"},
    json={
        "prompt": prompt,
        "resolution": "1920x1080",  # 16:9
        "duration": f"{duration_sec}s"
    }
)

if resp.status_code != 200:
    print("❌ Failed to start video generation:")
    print(resp.json())
    exit(1)

op_name = resp.json()["name"]
print(f"⏳ Operation started: {op_name}")

# Step 2: Poll until complete
while True:
    status_resp = requests.get(
        f"https://generativelanguage.googleapis.com/v1/{op_name}",
        params={"key": api_key}
    )
    data = status_resp.json()

    if data.get("done"):
        if "response" in data and "video" in data["response"]:
            video_url = data["response"]["video"]["url"]
            print("✅ Video ready! Downloading...")
            
            # Save to output/
            out_dir = Path("output")
            out_dir.mkdir(exist_ok=True)
            out_path = out_dir / "nature_veo.mp4"
            
            # Download video
            video_data = requests.get(video_url)
            video_data.raise_for_status()
            with open(out_path, "wb") as f:
                f.write(video_data.content)
                
            print(f"💾 Saved to: {out_path.absolute()}")
            break
        else:
            error = data.get("error", {}).get("message", "Unknown error")
            print(f"❌ Generation failed: {error}")
            exit(1)
    else:
        print("   ...waiting 10 seconds...")
        time.sleep(10)