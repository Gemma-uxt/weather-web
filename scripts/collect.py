# 날씨 수집 스크립트
# Open-Meteo(무료, 가입·키 필요 없음)에서 앞으로 7일 예보를 받아
# data/weather.json 파일로 저장합니다.
# 지역을 바꾸려면 아래 CITY, LAT(위도), LON(경도)만 고치면 됩니다.

import json
import os
import urllib.request
from datetime import datetime, timezone, timedelta

CITY = "서울"
LAT = 37.5665
LON = 126.9780

URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LAT}&longitude={LON}"
    "&daily=weather_code,temperature_2m_max,temperature_2m_min,"
    "precipitation_sum,precipitation_probability_max"
    "&timezone=Asia%2FSeoul&forecast_days=7"
)

with urllib.request.urlopen(URL, timeout=30) as res:
    raw = json.load(res)

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

kst = timezone(timedelta(hours=9))
result = {
    "city": CITY,
    "updated": datetime.now(kst).strftime("%Y-%m-%d %H:%M"),
    "days": days,
}

os.makedirs("data", exist_ok=True)
with open("data/weather.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"{CITY} 7일 예보 저장 완료 ({result['updated']})")
