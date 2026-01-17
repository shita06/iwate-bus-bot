import datetime

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
    # --- 現在時刻の取得（JST） ---
    t_delta = datetime.timedelta(hours=9)
    JST = datetime.timezone(t_delta, 'JST')
    now_dt = datetime.datetime.now(JST)

    # --- 現在時刻と曜日の取得 ---
    now_dt = datetime.datetime.now()
    now_time = now_dt.strftime("%H:%M")
    is_weekend = now_dt.weekday() >= 5
    day_key = "weekend" if is_weekend else "weekday"
    
    all_found_buses = []

    for route_name, schedules in bus_data.items():
        times = schedules[day_key]
        for t in times:
            if t > now_time:
                all_found_buses.append({"time": t, "route": route_name})

    all_found_buses.sort(key=lambda x: x["time"])

    # --- 返却用テキストの組み立て ---
    day_label = "休日" if is_weekend else "平日"
    header = f"--- 高松の池口案内 ({day_label}) ---\n現在時刻: {now_time}\n" + "-"*20 + "\n"
    
    if all_found_buses:
        rows = [f"{bus['time']} | {bus['route']}" for bus in all_found_buses[:5]]
        return header + "\n".join(rows)
    else:
        return header + "本日の運行はすべて終了しました。"

if __name__ == "__main__":
    # 自分のPCで実行した際も結果が表示されるようにする
    print(get_combined_info())