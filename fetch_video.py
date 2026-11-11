import html
import json
import re
import urllib.request

channels = [
    "https://t.me",
    "https://t.me/s/tennis_bolshe"
]

data = {
    "live_title": "активного эфира сейчас нет",
    "live_url": "",
    "replay_title": "последние видео с андреевой (@tennis_bolshe)",
    "replay_url": "https://vkvideo.ru"
}

headers = {
    "user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/122.0.0.0 safari/537.36"
}

found_videos = []

for url in channels:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            page = html.unescape(resp.read().decode("utf-8", errors="ignore"))

        # разбиваем ленту на отдельные посты (новые в конце списка)
        messages = page.split('class="tgme_widget_message_wrap')
        for msg in reversed(messages[1:]):
            clean_text = re.sub(r"<[^>]+>", " ", msg)
            clean_text = " ".join(clean_text.split())

            if "андреева" not in clean_text.lower():
                continue

            # ищем прямую ссылку на ролик вк видео внутри поста
            vk_match = re.search(
                r'href="(https?://(?:m\.)?(?:vk\.com|vkvideo\.ru)/video-?\d+_\d+[^"\s]*)"',
                msg,
                re.I
            )
            if not vk_match:
                continue

            video_link = vk_match.group(1)
            title_match = re.search(r"([^\.!\n]{5,85}андреева[^\.!\n]{5,85})", clean_text, re.I)
            title = title_match.group(1).strip() if title_match else "матч мирры андреевой (@tennis_bolshe)"

            is_live = "live" in url or "прямой эфир" in clean_text.lower() or "трансляция" in clean_text.lower()
            found_videos.append((is_live, title, video_link))
    except Exception:
        continue

for is_live, title, link in found_videos:
    if is_live and not data["live_url"]:
        data["live_title"] = title
        data["live_url"] = link
    elif not is_live and "q=" in data["replay_url"]:
        data["replay_title"] = title
        data["replay_url"] = link

# если нашелся только один ролик с эфиром, ставим его и в запись, чтобы кнопка не пустовала
if "q=" in data["replay_url"] and found_videos:
    data["replay_title"] = found_videos[0][1]
    data["replay_url"] = found_videos[0][2]

with open("video.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
