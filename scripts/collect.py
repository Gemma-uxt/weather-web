# 날씨 수집 스크립트
# Open-Meteo(무료, 가입·키 필요 없음)에서 도시별 앞으로 7일 예보를 받아
# data/weather.json 파일로 저장합니다.
# 도시를 추가하거나 바꾸려면 아래 CITIES 목록만 고치면 됩니다.
#   (이름, 위도, 경도, 시간대)

import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta

CITIES = [
    ("서울", 37.5665, 126.9780, "Asia/Seoul"),
    ("마카오", 22.1987, 113.5439, "Asia/Macau"),
]

OUT = "data/weather.json"


def fetch(lat, lon, tz):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
        "precipitation_sum,precipitation_probability_max"
        f"&timezone={tz.replace('/', '%2F')}&forecast_days=7"
    )
    # 접속이 잠깐 안 될 때를 대비해 최대 5번까지 다시 시도
    for attempt in range(1, 6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "weather-web (GitHub Actions)"})
            with urllib.request.urlopen(req, timeout=60) as res:
                return json.load(res)
        except Exception as e:
            print(f"  {attempt}번째 시도 실패: {e}")
            if attempt < 5:
                time.sleep(attempt * 15)
    return None


# 이전에 저장해 둔 데이터 (실패한 도시는 이전 데이터를 그대로 씀)
old = {}
if os.path.exists(OUT):
    try:
        with open(OUT, encoding="utf-8") as f:
            prev = json.load(f)
        for c in prev.get("cities", []):
            old[c["city"]] = c
    except Exception:
        pass

kst = timezone(timedelta(hours=9))
now = datetime.now(kst).strftime("%Y-%m-%d %H:%M")

cities = []
for name, lat, lon, tz in CITIES:
    print(f"{name} 수집 중…")
    raw = fetch(lat, lon, tz)
    if raw is None:
        if name in old:
            print(f"  {name}: 접속 실패 → 이전 데이터 유지")
            cities.append(old[name])
            continue
        print(f"  {name}: 접속 실패, 이전 데이터도 없음 → 건너뜀")
        continue

    d = raw["daily"]
    days = []
    for i, date in enumerate(d["time"]):
        days.append({
            "date": date,
            "code": d["weather_code"][i],
            "tmax": d["temperature_2m_max"][i],
            "tmin": d["temperature_2m_min"][i],
            "rain": d["precipitation_sum"][i],
            "rain_prob": d["precipitation_probability_max"][i],
        })
    cities.append({"city": name, "updated": now, "days": days})
    print(f"  {name} 저장 완료")

if not cities:
    sys.exit("모든 도시의 날씨 사이트 접속에 실패했습니다. 잠시 후 다시 실행해 주세요.")

os.makedirs("data", exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    json.dump({"updated": now, "cities": cities}, f, ensure_ascii=False, indent=2)

print(f"완료 ({now})")
