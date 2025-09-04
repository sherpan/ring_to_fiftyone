from getpass import getpass
from ring_doorbell import Auth, Ring
import json, requests, os
import fiftyone as fo

USER_AGENT = "RingDownloader"
CACHE_FILE = "ring_token.cache"  # using .cache extension

OUTPUT_DIR = "ring_videos"       # where videos will be saved

# Create output folder if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)

def save_token(token):
    with open(CACHE_FILE, "w") as f:
        json.dump(token, f)

# --- Auth ---
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE) as f:
        token = json.load(f)
else:
    token = None

auth = Auth(USER_AGENT, token, save_token)
if not token:
    username = input("Ring Username: ")
    password = getpass("Ring Password: ")
    try:
        auth.fetch_token(username, password)
    except Exception:
        code = input("2FA Code: ")
        auth.fetch_token(username, password, code)

# --- Get devices ---
ring = Ring(auth)
ring.update_data()
doorbell = ring.devices()['doorbots'][0]

# --- Get last 30 events ---
events = doorbell.history(limit=50)
print(f"Found {len(events)} events")

samples = []

for ev in events:
    vid_id = ev.get("id") or ev.get("recording_id") or ev.get("ding_id")
    if not vid_id:
        print(f"❌ Skipping event (no ID) → {ev.get('created_at')} [{ev.get('kind')}]")
        continue

    video_url = doorbell.recording_url(vid_id)
    if not video_url:
        print(f"⚠️ No video for {ev.get('created_at')} [{ev.get('kind')}] — possibly expired or not recorded.")
        continue

    
    created_str = ev['created_at'].strftime("%Y-%m-%d_%H-%M-%S")
    filename = os.path.join(OUTPUT_DIR, f"{created_str}-{vid_id}.mp4")
    print(f"⬇️ Downloading {filename}..." + f" [{ev.get('kind')}]")
    resp = requests.get(video_url, stream=True)
    with open(filename, "wb") as f:
        for chunk in resp.iter_content(1024 * 1024):
            f.write(chunk)
    sample = fo.Sample(filepath=filename, time_of_video=ev['created_at'])
    samples.append(sample)

print(f"✅ Done. Videos saved in '{OUTPUT_DIR}'")

dataset = fo.Dataset(name="ring_videos")
dataset.add_samples(samples)
dataset.persistent = True
session = fo.launch_app(dataset)
session.wait()


