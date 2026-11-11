import json
import re
import requests

url = "https://vk.com"
headers = {
    "user-agent": "mozilla/5.0 (linux; android 13) applewebkit/537.36 (khtml, like gecko) chrome/120.0.0.0 mobile safari/537.36",
    "accept-language": "ru-RU,ru;q=0.9"
}

data = {
    "live_title": "активного эфира сейчас нет",
    "live_url": "",
    "replay_title": "последние видео с андреевой (@tennis_bolshe)",
    "replay_url": "https://vk.com"
}

try:
    res = requests.get(url, headers=headers, timeout=15)
    html = res.text

    # разбиваем страницу на отдельные посты сообщества
    blocks = html.split('class="wall_item')
    for block in blocks[1:]:
        clean_text = re.sub(r"<[^>]+>", " ", block)
        clean_text = " ".join(clean_text.split())

        if "андреева" not in clean_text.lower():
            continue

        # ищем реальную ссылку на видео вместе с параметром list, если он есть
        vid_match = re.search(r'href="(/video-218116775_\d+(?:\?list=[a-z0-9]+)?)"', block, re.I)
        if not vid_match:
            continue

        real_url = "https://vk.com" + vid_match.group(1)
        is_live = "прямая трансляция" in clean_text.lower() or "live" in clean_text.lower()

        title_match = re.search(r"([^\.!\n]{10,85}андреева[^\.!\n]{5,85})", clean_text, re.I)
        title = title_match.group(1).strip() if title_match else "матч мирры андреевой (@tennis_bolshe)"

        if is_live and not data["live_url"]:
            data["live_title"] = title
            data["live_url"] = real_url
        elif not is_live and data["replay_url"].startswith("https://vk.com@"):
            data["replay_title"] = title
            data["replay_url"] = real_url

        if data["live_url"] and not data["replay_url"].startswith("https://vk.com@"):
            break
except Exception:
    pass

with open("video.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
