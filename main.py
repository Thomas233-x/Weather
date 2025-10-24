import json
import os
import requests
try:
    from google import genai
    from google.genai import types
except Exception as e:
    genai = None
    types = None
    print(f"警告: google.genai のインポートに失敗しました: {e}。Gemini サポートが必要なら 'google-genai' をインストールしてください。")

from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label as KivyLabel
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.uix.label import Label
from kivy.core.window import Window
import time

# --- add: 安全に Unicode へ変換するユーティリティ ---
def to_unicode(obj):
    """bytes -> utf-8 デコード、その他は str()。失敗時は代替文字で置換する。"""
    try:
        if isinstance(obj, bytes):
            return obj.decode("utf-8", errors="replace")
        return str(obj)
    except Exception:
        return repr(obj)

# --- add: 例外メッセージを安全に文字列化する ---
def safe_error_str(e):
    try:
        # bytes -> UTF-8 デコード
        if isinstance(e, bytes):
            return e.decode("utf-8", errors="replace")
        # Exception.args があればそれらを結合（各要素を安全に変換）
        if hasattr(e, "args") and e.args:
            return " ".join(to_unicode(a) for a in e.args)
        # その他は to_unicode に委譲
        return to_unicode(e)
    except Exception:
        return repr(e)

# --- 1. 設定と API キー ---
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
# テスト用フォールバック（本番では環境変数を使ってください）
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY") or "27f0206bd710e04dd6f6aafe77dd46ec"

# --- ここに指定の API キーと都市をハードコードで追加（テスト用） ---
# 注意: 本番では環境変数を使ってください。以下はユーザー指示によりコード埋め込みしています。
API_KEY = "93aea5ae7f71bd9bcbe24bb57b43ad90"
CITY = "Tokyo"
CITY_WEATHER_URL = f"https://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric&lang=ja"

# サンプルの位置（必要に応じて都市IDや経緯度を変更してください）
WEATHER_LAT = 22.3080
WEATHER_LON = 114.1718
WEATHER_UNITS = "metric"  # 摂氏

# 日本語フォントのパス（Windows の例）。存在しなければ None にする。
POSSIBLE_FONTS = [
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\meiryo.ttf",
    r"C:\Windows\Fonts\msgothic.ttc",
    r"C:\Windows\Fonts\MSGOTHIC.TTC",
]
FONT_PATH = next((p for p in POSSIBLE_FONTS if os.path.exists(p)), None)
if FONT_PATH is None:
    print("警告: 日本語フォントが見つかりません。表示に異常がある場合は日本語対応フォントを用意してください。")
else:
    # Kivy にフォントを登録（登録名 'AppFont' を使用）
    LabelBase.register(name='AppFont', fn_regular=FONT_PATH)
    print(f"使用するフォント: {FONT_PATH}")

# デバッグ: ウィンドウサイズと背景色を固定（見えない問題対策）
Window.size = (480, 720)
Window.clearcolor = (1, 1, 1, 1)  # 白背景
print("DEBUG: Window.size set", Window.size)

# --- 2. コア AI ロジッククラス ---

class AISuggestionEngine:
    """天気データ取得と Gemini による提案生成を扱うクラス"""
    
    def __init__(self, gemini_key, weather_key):
        self.gemini_key = gemini_key
        self.weather_key = weather_key

        self.gemini_client = None
        if genai is None:
            print("警告: google.genai モジュールが利用できません。Gemini 呼び出しは無効になります。")
            return

        if not self.gemini_key:
            print("情報: GEMINI_API_KEY が設定されていません。Gemini 呼び出しはスキップされます。")
            return

        try:
            # API キーがあるときだけクライアントを作る
            self.gemini_client = genai.Client(api_key=self.gemini_key)
        except Exception as e:
            print(f"Gemini クライアントの初期化に失敗しました: {e}")
            self.gemini_client = None

    def get_current_location(self):
        """IPベースで現在地（緯度, 経度, 表示名）を返す。失敗時は既定値を返す."""
        try:
            resp = requests.get("http://ip-api.com/json/", timeout=5)
            resp.raise_for_status()
            j = resp.json()
            if j.get("status") == "success":
                lat = j.get("lat"); lon = j.get("lon")
                city = j.get("city") or j.get("regionName")
                print(f"DEBUG: get_current_location -> lat={lat}, lon={lon}, city={city}")
                return lat, lon, city
        except Exception:
            print("DEBUG: get_current_location: failed to get IP location")
            pass
        return WEATHER_LAT, WEATHER_LON, None

    def get_weather_data(self):
        """OpenWeatherMap API から現在の天気データを取得する"""
        # テスト用モック: 環境変数に 'mock' を設定するとここが返る（実ネットワーク呼び出しをスキップ）
        if self.weather_key == 'mock':
            return {
                "location": "テスト市",
                "temp_current": 22.5,
                "temp_max": 24.0,
                "temp_min": 20.0,
                "humidity": 60,
                "description": "晴れ",
                "rain_prob": 0
            }
        if not self.weather_key:
            return {"error": "OpenWeatherMap の API キーが設定されていません"}
            
        # 現在地（IPベース）を取得して API 呼び出しに使う
        lat, lon, city = self.get_current_location()
        url = (
            f"https://api.openweathermap.org/data/2.5/weather?"
            f"lat={lat}&lon={lon}&units={WEATHER_UNITS}&appid={self.weather_key}"
        )
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"DEBUG: get_weather_data -> url={url}")
            print("DEBUG: get_weather_data -> response keys:", list(data.keys()))
            # optional: print a short JSON snippet
            print("DEBUG: get_weather_data -> snippet:", json.dumps(data)[:400])
            
            weather_info = {
                "location": city or data.get("name", "不明な場所"),
                "temp_current": data["main"]["temp"],
                "temp_max": data["main"]["temp_max"],
                "temp_min": data["main"]["temp_min"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                # OpenWeatherMap に確率がなければ rain の 1h 値を利用（なければ 0）
                "rain_prob": data.get("rain", {}).get("1h", 0) * 10 if data.get("rain") else 0
            }
            return weather_info
            
        except requests.exceptions.RequestException as e:
            return {"error": f"天気 API のリクエストに失敗しました: {e}"}
        except KeyError:
            return {"error": "天気 API のデータ形式が不正です"}
        except Exception as e:
            return {"error": f"不明なエラー: {e}"}

    def get_ai_suggestion(self, weather_data):
        """Gemini が使えない場合はローカルで簡易提案を返す"""
        # Gemini クライアントが無ければローカルフォールバック
        if not self.gemini_client:
            t = weather_data.get("temp_current", 20)
            rain = weather_data.get("rain_prob", 0)
            desc = weather_data.get("description", "").lower()
            # 簡易ルールで服装決定
            if t < 5:
                outfit = "厚手のコート、マフラー、手袋"
            elif t < 12:
                outfit = "ジャケットやセーター、長ズボン"
            elif t < 20:
                outfit = "薄手の長袖または羽織り、長ズボン"
            else:
                outfit = "半袖Tシャツ、軽い羽織りがあれば可"
            # 傘判定（降水情報か説明に雨が含まれる場合）
            umbrella = "傘が必要" if (rain > 0 or "rain" in desc or "雨" in desc) else "傘は不要"
            return {"outfit_suggestion": outfit, "umbrella_needed": umbrella}

        # Gemini が使える場合の既存処理（必要な変数を定義）
        if types is None:
            return {"error": "genai.types が利用できません"}

        system_instruction = (
            "あなたはプロの天気スタイリストです。提供された天気データに基づき、"
            "最も簡潔で実用的な方法で今日の服装と傘の要否を提案してください。"
            "出力は必ず以下の JSON 形式に厳密に従い、余計な説明や注釈を一切加えないでください。"
        )

        user_prompt = (
            f"今日の天気データ：\n"
            f"- 場所：{weather_data.get('location','不明')}\n"
            f"- 現在の気温：{weather_data.get('temp_current',0):.1f} ℃\n"
            f"- 最高気温：{weather_data.get('temp_max',0):.1f} ℃\n"
            f"- 最低気温：{weather_data.get('temp_min',0):.1f} ℃\n"
            f"- 湿度：{weather_data.get('humidity',0)}%\n"
            f"- 天気概要：{weather_data.get('description','')}\n"
        )

        response_schema = types.Schema(
            type=types.Type.OBJECT,
            properties={
                "outfit_suggestion": types.Schema(
                    type=types.Type.STRING,
                    description="簡潔な服装の提案"
                ),
                "umbrella_needed": types.Schema(
                    type=types.Type.STRING,
                    enum=["傘が必要", "傘は不要"],
                    description="傘が必要かどうか"
                )
            },
            required=["outfit_suggestion", "umbrella_needed"]
        )

        try:
            response = self.gemini_client.models.generate_content(
                model='gemini-2.5-flash',
                contents=user_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )

            # レスポンスを安全にパースする（.text がない場合に備える）
            text = getattr(response, "text", None)
            if not text and hasattr(response, "candidates"):
                # 古い / 別形式のレスポンス対応
                text = response.candidates[0].content

            # 安全に文字列化してから JSON パース
            text = to_unicode(text)
            json_result = json.loads(text)
            return json_result

        except Exception as e:
            err_str = safe_error_str(e)
            return {"error": f"Gemini API 呼び出しまたは解析でエラーが発生しました: {err_str}"}


# --- 3. KivyMD アプリ UI ---

class OutfitRecommenderApp(MDApp):
    def on_start(self):
        print("DEBUG: App on_start() called at", time.strftime("%H:%M:%S"))
    def build(self):
        print("DEBUG: build() called")
        self.ai_engine = AISuggestionEngine(GEMINI_API_KEY, OPENWEATHER_API_KEY)

        self.screen = Screen()
        
        main_layout = BoxLayout(
            orientation='vertical',
            padding=dp(30),
            spacing=dp(30),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
        )

        # タイトルは MDLabel ではなく Label を使い、登録した日本語フォントを確実に使用する
        title = Label(
            text="AI 今日の服装提案",
            halign="center",
            size_hint_y=None,
            height=dp(50),
            markup=False,
            font_name=("AppFont" if FONT_PATH else None),
            font_size=dp(22)
        )

        self.result_layout = BoxLayout(
             orientation='vertical',
             padding=dp(20),
             spacing=dp(10),
             # md_bg_color を削除（ThemeManager に bg_normal がないため）
             # 必要なら md_bg_color=(r,g,b,a) のように直接RGBAを指定してください
             # 例: md_bg_color=(1,1,1,1)
             # md_bg_color=self.theme_cls.bg_normal,
             size_hint_y=None,
             height=dp(200)
        )
        
        # 結果表示ラベルも同様に Label を使用（markup を利用）
        self.outfit_label = Label(
            text="[「提案を取得」をクリックして開始]",
            halign="center",
            valign="middle",
            markup=True,
            font_name=("AppFont" if FONT_PATH else None),
            font_size=dp(18)
        )
        self.umbrella_label = Label(
            text="[データを待っています...]",
            halign="center",
            valign="middle",
            markup=True,
            font_name=("AppFont" if FONT_PATH else None),
            font_size=dp(16)
        )

        self.result_layout.add_widget(self.outfit_label)
        self.result_layout.add_widget(self.umbrella_label)

        refresh_button = Button(
            text="今日の提案を取得",
            on_release=self.start_fetch_data,
            size_hint_x=0.8,
            pos_hint={'center_x': 0.5}
        )

        main_layout.add_widget(title)
        main_layout.add_widget(self.result_layout)
        main_layout.add_widget(refresh_button)
        main_layout.add_widget(BoxLayout(size_hint_y=None, height=dp(50)))
         
        self.screen.add_widget(main_layout)
        print("DEBUG: build() finished, returning root widget")
        return self.screen

    def start_fetch_data(self, instance):
        """データ取得ボタンが押されたときの処理"""
        # OpenWeather APIキー未設定なら処理を中止して案内を表示
        if not OPENWEATHER_API_KEY:
            popup = Popup(
                title="APIキーが必要です",
                content=KivyLabel(
                    text="OPENWEATHER_API_KEY が設定されていません。\nPowerShell で:\n$env:OPENWEATHER_API_KEY='あなたのキー'\nと設定してから再実行してください。",
                    halign="center"
                ),
                size_hint=(0.9, 0.3)
            )
            popup.open()
            return
        print("DEBUG: start_fetch_data() called by", instance)
        self.outfit_label.text = "[読み込み中...]"
        self.umbrella_label.text = ""
        
        # 即時に一回だけ取得（不要な定期スケジュールは行わない）
        Clock.schedule_once(self.fetch_and_update, 0)
        print("DEBUG: scheduled fetch_and_update")

    def fetch_and_update(self, dt):
        print("DEBUG: fetch_and_update() running; dt=", dt)
        """天気データ取得と AI 提案更新"""
        weather_data = self.ai_engine.get_weather_data()
        
        # エラーチェック
        if "error" in weather_data:
            self.show_error_snackbar(weather_data["error"])
            return
        
        # AI による提案取得
        ai_suggestion = self.ai_engine.get_ai_suggestion(weather_data)
        
        # エラーがあれば表示
        if "error" in ai_suggestion:
            self.show_error_snackbar(ai_suggestion["error"])
            return

        # 提案を UI に反映
        outfit = ai_suggestion.get("outfit_suggestion", "情報なし")
        umbrella = ai_suggestion.get("umbrella_needed", "情報なし")
        
        # Kivy の markup では color タグを使う（16進カラー、先頭の # は省略可）
        self.outfit_label.text = f"[color=0000FF]服装提案:[/color] {outfit}"
        self.umbrella_label.text = f"[color=0000FF]傘の必要性:[/color] {umbrella}"

    def show_error_snackbar(self, text):
        print("DEBUG: show_error_snackbar():", text)
        """エラーをポップアップで表示し、UI にも反映する"""
        self.outfit_label.text = "[color=FF0000]エラーが発生しました[/color]"
        self.umbrella_label.text = to_unicode(text)
        # 簡易ポップアップで代替表示（インデントを整えた）
        popup = Popup(
            title="エラー",
            content=KivyLabel(text=to_unicode(text), halign="center"),
            size_hint=(0.8, 0.2)
        )
        popup.open()

if __name__ == '__main__':
    if not GEMINI_API_KEY or not OPENWEATHER_API_KEY:
        print("警告: 環境変数 GEMINI_API_KEY と OPENWEATHER_API_KEY を設定してください。")
        print("Windows PowerShell (一時): $env:GEMINI_API_KEY='...'; $env:OPENWEATHER_API_KEY='...'")
        print("Windows (永続): setx GEMINI_API_KEY \"...\" && setx OPENWEATHER_API_KEY \"...\"")
        os.system('setx OPENWEATHER_API_KEY "27f0206bd710e04dd6f6aafe77dd46ec"')
        print("# 新しいターミナルを開いてから実行")
        print("python main.py")
    OutfitRecommenderApp().run()
