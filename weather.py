import requests

API_KEY = "93aea5ae7f71bd9bcbe24bb57b43ad90"
CITY = "Tokyo"
URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ja"

response = requests.get(URL)
data = response.json()

temp = data["main"]["temp"]
weather = data["weather"][0]["description"]

print(f"今日の{CITY}の天気：{weather}、気温：{temp}°C")

if temp < 10:
    print("厚手のコートを着ましょう ❄️")
elif temp < 20:
    print("長袖がおすすめ 👕")
else:
    print("半袖で大丈夫 ☀️")
