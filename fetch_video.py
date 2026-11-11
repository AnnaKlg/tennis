import json
import subprocess

data = {
    "live_title": "активного эфира сейчас нет",
    "live_url": "",
    "replay_title": "последние видео с андреевой (@tennis_bolshe)",
    "replay_url": "https://vk.com"
}

try:
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--playlist-end", "30",
        "-j",
        "https://vk.com"
    ]
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
    for line in res.stdout.splitlines():
        if not line.strip():
            continue
        item = json.loads(line)
        title = item.get("title", "")
        video_url = item.get("url") or item.get("webpage_url", "")
        if "андреева" not in title.lower() or not video_url:
            continue

        is_live = item.get("live_status") == "is_live" or "прямой эфир" in title.lower() or "live" in title.lower()
        if is_live and not data["live_url"]:
            data["live_title"] = title
            data["live_url"] = video_url
        elif not is_live and "q=" in data["replay_url"]:
            data["replay_title"] = title
            data["replay_url"] = video_url

        if data["live_url"] and "q=" not in data["replay_url"]:
            break
except Exception:
    pass

with open("video.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
