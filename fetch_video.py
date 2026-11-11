import html
import json
import re
import requests

url = "https://vkvideo.ru"
headers = {
    "user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/122.0.0.0 safari/537.36",
    "accept-language": "ru-RU,ru;q=0.9"
}

data = {
    "live_title": "активного эфира сейчас нет",
    "live_url": "",
    "replay_title": "последние видео с андреевой (@tennis_bolshe)",
    "replay_url": "https://vkvideo.ru?q=%D0%B0%D0%BD%D0%B4%D1%80%D0%B5%D0%B5%D0%B2%D0%B0"
}

try:
    res = requests.get(url, headers=headers, timeout=15)
    page = html.unescape(res.text)

    # ищем пары из названия видео и его id на витрине vkvideo.ru
    patterns = [
        r'"title"\s*:\s*"([^"]+)"[^\}]{0,400}?"id"\s*:\s*(\d{7,12})',
        r'href="(/video-218116775_(\d+))"[^>]*title="([^"]+)"',
        r'title="([^"]+)"[^>]*href="(/video-218116775_(\d+))"'
    ]

    found_items = []

    for m in re.finditer(patterns[0], page):
        title, vid = m.group(1), m.group(2)
        if "андреева" in title.lower():
            found_items.append((title, f"https://vkvideo.ru_{vid}"))

    if not found_items:
        for m in re.finditer(patterns[1], page):
            path, title = m.group(1), m.group(3)
            if "андреева" in title.lower():
                found_items.append((title, "https://vkvideo.ru" + path))

    if not found_items:
        for m in re.finditer(patterns[2], page):
            title, path = m.group(1), m.group(2)
            if "андреева" in title.lower():
                found_items.append((title, "https://vkvideo.ru" + path))

    for title, link in found_items:
        is_live = "прямой эфир" in title.lower() or "live" in title.lower()
        if is_live and not data["live_url"]:
            data["live_title"] = title
            data["live_url"] = link
        elif not is_live and "q=" in data["replay_url"]:
            data["replay_title"] = title
            data["replay_url"] = link

except Exception:
    pass

with open("video.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
