import sys
from ring_doorbell import Auth, Ring
import json, requests, os
import fiftyone as fo


USER_AGENT = "RingDownloader"

# Require cache file as CLI argument
if len(sys.argv) < 2:
    print("Usage: python ingest.py <cache_file>")
    sys.exit(1)
CACHE_FILE = sys.argv[1]

OUTPUT_DIR = "ring_videos"  # where videos will be saved
os.makedirs(OUTPUT_DIR, exist_ok=True)




# --- Auth ---
if not os.path.exists(CACHE_FILE):
    print(f"❌ Cache file '{CACHE_FILE}' not found. Please provide a valid cache file.")
    sys.exit(1)
with open(CACHE_FILE) as f:
    token = json.load(f)

auth = Auth(USER_AGENT, token, None)

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
    #print(f"⬇️ Downloading {filename}..." + f" [{ev.get('kind')}]")
    resp = requests.get(video_url, stream=True)
 
    with open(filename, "wb") as f:
        for chunk in resp.iter_content(1024 * 1024):
            f.write(chunk)
    sample = fo.Sample(filepath=filename, time_of_video=ev['created_at'])
    sample['trigger_type'] = ev.get('kind')
    samples.append(sample)


print(f"✅ Done. Videos saved in '{OUTPUT_DIR}'")

# Check if dataset exists, load if so, else create
if fo.dataset_exists("ring_videos"):
    dataset = fo.load_dataset("ring_videos")
else:
    dataset = fo.Dataset(name="ring_videos")
    dataset.persistent = True

dataset.add_samples(samples)
session = fo.launch_app(dataset)
session.wait()


