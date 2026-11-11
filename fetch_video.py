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
    "replay_url": "https://vk.com"
}

if not token:
    data["replay_title"] = "ошибка: токен не передан в скрипт"
else:
    params = urllib.parse.urlencode({
        "owner_id": owner_id,
        "count": 30,
        "access_token": token,
        "v": "5.199"
    })
    url = f"https://vk.com?{params}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=15) as resp:
            res = json.loads(resp.read().decode("utf-8"))

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
                # формируем прямую ссылку на плеер и страницу ролика
                direct_url = f"https://vkvideo.ru{oid}_{vid}"
                is_live = video.get("live", 0) == 1

                if is_live and not data["live_url"]:
                    data["live_title"] = title
                    data["live_url"] = direct_url
                elif not is_live and data["replay_url"] == "https://vk.com":
                    data["replay_title"] = title
                    data["replay_url"] = direct_url

                if data["live_url"] and data["replay_url"] != "https://vk.com":
                    break
    except Exception as e:
        data["replay_title"] = f"ошибка сети: {str(e)}"

with open("video.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
