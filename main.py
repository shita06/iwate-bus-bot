import os
import datetime
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# --- LINEの鍵を設定（Renderの環境変数から読み込む） ---
LINE_CHANNEL_ACCESS_TOKEN = os.environ.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.environ.get('LINE_CHANNEL_SECRET')
# デバッグ用：鍵が読み込めていない場合にエラーログを出す
if LINE_CHANNEL_ACCESS_TOKEN is None or LINE_CHANNEL_SECRET is None:
    print("CRITICAL ERROR: LINEの環境変数が読み込めていません！Renderの設定を確認してください。")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# バスの時刻表データ（改行して見やすく整理）
bus_data = {
    "212 あすみ野（盛岡駅行）": {
        "weekday": ["07:20"],
        "weekend": []
    },
    "307 支線A（盛岡駅行）": {
        "weekday": [
            "07:17", "07:38", "08:03", "08:11", "08:26", 
            "09:31", "10:31"
        ],
        "weekend": []
    },
    "307 支線B（盛岡駅行）": {
        "weekday": [
            "07:29", "07:55", "08:41", "09:11", "10:11", 
            "15:31"
        ],
        "weekend": []
    },
    "307 循環左（盛岡駅行）": {
        "weekday": [],
        "weekend": [
            "07:31", "07:41", "07:51", "08:01", "08:11", 
            "08:21", "08:31", "08:41", "08:51", "09:01", 
            "09:16", "09:31", "09:51", "10:31", "11:11", 
            "11:51"
        ]
    },
    "307 南県営アパート（盛岡駅行）": {
        "weekday": ["16:11"],
        "weekend": []
    },
    "307 営業所循環左（盛岡駅行）": {
        "weekday": ["06:06", "06:51", "07:05"],
        "weekend": ["06:41", "06:56", "07:11", "07:21"]
    },
    "307 東松園二丁目（盛岡駅行）": {
        "weekday": [
            "06:31", "06:59", "07:11", "07:23", "07:47", 
            "09:51", "11:11", "12:31", "13:51", "15:11", 
            "16:41", "17:11", "17:31", "18:11", "18:31", 
            "19:51", "20:11", "20:31"
        ],
        "weekend": [
            "12:31", "12:51", "13:11", "13:31", "13:51", 
            "14:11", "14:31", "14:51", "15:11", "15:31", 
            "15:51", "16:11", "16:36", "16:56", "17:36", 
            "17:56", "18:16", "18:36", "18:56", "19:16", 
            "19:46", "20:16", "20:46", "21:16", "21:46"
        ]
    },
    "311 桜台団地（盛岡駅行）": {
        "weekday": ["06:42", "07:39", "12:39", "18:14"],
        "weekend": ["07:39", "12:39", "18:14"]
    }
}

def get_combined_info():
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now_dt = datetime.datetime.now(JST)
    now_time = now_dt.strftime("%H:%M")
    is_weekend = now_dt.weekday() >= 5
    day_key = "weekend" if is_weekend else "weekday"
    
    all_found_buses = []
    for route_name, schedules in bus_data.items():
        for t in schedules[day_key]:
            if t > now_time:
                all_found_buses.append({"time": t, "route": route_name})

    all_found_buses.sort(key=lambda x: x["time"])

    day_label = "休日" if is_weekend else "平日"
    res = f"--- 高松の池口案内 ({day_label}) ---\n現在時刻: {now_time}\n" + "-"*40 + "\n"
    
    if all_found_buses:
        for bus in all_found_buses[:5]:
            res += f"{bus['time']} | {bus['route']}\n"
    else:
        res += "本日の運行はすべて終了しました。"
    return res

# --- LINEからの通知を受け取る窓口 ---
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# --- 何かメッセージが届いたら実行する処理 ---
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # バス情報を取得して返信する
    bus_info = get_combined_info()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=bus_info)
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)