import json
import re
import urllib.request
import xml.etree.ElementTree as et

rss_urls = [
    "https://rsshub.app",
    "https://rssforever.com",
    "https://slarker.me"
]

data = {
    "live_title": "активного эфира сейчас нет",
    "live_url": "",
    "replay_title": "последние видео с андреевой (@tennis_bolshe)",
    "replay_url": "https://vk.com"
}

headers = {
    "user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/122.0.0.0 safari/537.36"
}

for rss_url in rss_urls:
    try:
        req = urllib.request.Request(rss_url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            xml_data = resp.read()

        root = et.fromstring(xml_data)
        items = root.findall(".//item")

        for item in items:
            title_el = item.find("title")
            desc_el = item.find("description")
            link_el = item.find("link")

            title = title_el.text if title_el is not None and title_el.text else ""
            desc = desc_el.text if desc_el is not None and desc_el.text else ""
            link = link_el.text if link_el is not None and link_el.text else ""

            full_text = f"{title} {desc}".lower()
            if "андреева" not in full_text:
                continue

            vid_match = re.search(r"video(-218116775_\d+)", f"{link} {desc}")
            if not vid_match:
                continue

            real_video_url = "https://vk.com" + vid_match.group(1)
            clean_title = re.sub(r"<[^>]+>", " ", title).strip() or "матч мирры андреевой (@tennis_bolshe)"
            is_live = "прямой эфир" in full_text or "прямая трансляция" in full_text or "live" in full_text

            if is_live and not data["live_url"]:
                data["live_title"] = clean_title
                data["live_url"] = real_video_url
            elif not is_live and "q=" in data["replay_url"]:
                data["replay_title"] = clean_title
                data["replay_url"] = real_video_url

            if data["live_url"] and "q=" not in data["replay_url"]:
                break

        if "q=" not in data["replay_url"] or data["live_url"]:
            break
    except Exception:
        continue

with open("video.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
