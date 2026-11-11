import json
import os
import urllib.parse
import urllib.request

token = os.environ.get("vk_token", "").strip()
owner_id = "-218116775"

data = {
    "live_title": "активного эфира сейчас нет",
    "live_url": "",
    "replay_title": "ожидание обновления...",
    "replay_url": "https://vkvideo.ru"
}

headers = {
    "user-agent": "mozilla/5.0 (windows nt 10.0; win64; x64) applewebkit/537.36 (khtml, like gecko) chrome/122.0.0.0 safari/537.36",
    "accept": "application/json, text/plain, */*",
    "accept-language": "ru-RU,ru;q=0.9"
}

if not token:
    data["replay_title"] = "ошибка: токен не передан в скрипт"
else:
    params = urllib.parse.urlencode({
        "owner_id": owner_id,
        "count": 30,
        "access_token": token,
        "lang": "ru",
        "v": "5.199"
    })
    url = f"https://vk.ru?{params}"

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw_text = resp.read().decode("utf-8", errors="ignore")

        if not raw_text.strip().startswith("{"):
            data["replay_title"] = "блок вк (вернул html вместо данных)"
        else:
            res = json.loads(raw_text)
            if "error" in res:
                err_msg = res["error"].get("error_msg", "ошибка вк")
                data["replay_title"] = f"ошибка вк: {err_msg}"
            else:
                items = res.get("response", {}).get("items", [])
                for video in items:
                    title = video.get("title", "")
                    if "андреева" not in title.lower():
                        continue

                    vid = video.get("id")
                    oid = video.get("owner_id", owner_id)
                    direct_url = f"https://vkvideo.ru{oid}_{vid}"
                    is_live = video.get("live", 0) == 1

                    if is_live and not data["live_url"]:
                        data["live_title"] = title
                        data["live_url"] = direct_url
                    elif not is_live and data["replay_url"] == "https://vkvideo.ru":
                        data["replay_title"] = title
                        data["replay_url"] = direct_url

                    if data["live_url"] and data["replay_url"] != "https://vkvideo.ru":
                        break
    except Exception as e:
        data["replay_title"] = f"ошибка сети: {str(e)}"

with open("video.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
