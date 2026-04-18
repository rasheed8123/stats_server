# import requests
# import pandas as pd
# from pymongo import MongoClient
# from datetime import datetime
# import time

# # ==============================
# # 📁 EXCEL FILE
# # ==============================
# FILE_PATH = "players.xlsx"   # your file name

# # ==============================
# # 🔹 MONGODB
# # ==============================
# client = MongoClient("")
# db = client["cricket"]
# collection = db["players"]

# # ==============================
# # 🔹 API HEADERS
# # ==============================
# headers = {
#     "api-key": "cr!CkH3r0s",
#     "authorization": "6f2cb0a0-3afe-11f1-81fe-d32eb66d4bff",
#     "udid": "9959009218dc883b4274e841993e8d16",
#     "device-type": "Chrome: 147.0.0.0",
#     "user-agent": "Mozilla/5.0",
#     "origin": "https://cricheroes.com",
#     "referer": "https://cricheroes.com/",
#     "accept": "application/json",
#     "cache-control": "no-cache"
# }

# # ==============================
# # 🔹 NORMALIZE
# # ==============================
# def normalize_key(title):
#     return title.strip().lower()

# # ==============================
# # 🔹 MAP FUNCTION
# # ==============================
# def map_stats(stats_list):
#     result = {}

#     for item in stats_list:
#         title = normalize_key(item.get("title", ""))
#         val = item.get("value")

#         try:
#             if isinstance(val, str):
#                 val = val.strip()
#                 if val.endswith("%"):
#                     val = float(val.replace("%", ""))
#                 elif val.replace('.', '', 1).isdigit():
#                     val = float(val)
#         except:
#             pass

#         key = title.replace(" ", "").replace("(", "").replace(")", "")
#         result[key] = val

#     return result

# # ==============================
# # 📥 LOAD EXCEL
# # ==============================
# df = pd.read_excel(FILE_PATH)

# print(f"✅ Loaded {len(df)} players from Excel\n")

# # ==============================
# # 🔁 LOOP PLAYERS
# # ==============================
# for index, row in df.iterrows():
#     player_id = str(row["id"]).strip()
#     player_name = str(row["Player Full Name"]).strip()

#     print(f"\n🚀 Processing: {player_name} ({player_id})")

#     url = f"https://api.cricheroes.in/api/v1/player/get-player-statistic/{player_id}?pagesize=12"

#     try:
#         response = requests.get(url, headers=headers)
#         print("Status:", response.status_code)

#         # 🔐 Handle token expiry
#         if response.status_code == 401:
#             print("❌ Token expired. Update authorization and rerun.")
#             break

#         data = response.json()

#         stats = data.get("data", {}).get("statistics")

#         if not stats:
#             print("⚠️ No stats found, skipping...")
#             continue

#         # ==============================
#         # TRANSFORM
#         # ==============================
#         batting = map_stats(stats.get("batting", []))
#         bowling = map_stats(stats.get("bowling", []))
#         fielding = map_stats(stats.get("fielding", []))
#         captain = map_stats(stats.get("captain", []))

#         # ==============================
#         # DOCUMENT
#         # ==============================
#         player_doc = {
#             "playerId": player_id,
#             "playerName": player_name,
#             "meta": {
#                 "source": "CricHeroes",
#                 "lastUpdated": datetime.utcnow()
#             },
#             "batting": batting,
#             "bowling": bowling,
#             "fielding": fielding,
#             "captain": captain,
#             "raw": stats
#         }

#         # ==============================
#         # STORE
#         # ==============================
#         collection.update_one(
#             {"playerId": player_id},
#             {"$set": player_doc},
#             upsert=True
#         )

#         print("✅ Stored:", player_name)

#         # ⏱️ Avoid rate limit
#         time.sleep(1)

#     except Exception as e:
#         print("❌ Error:", str(e))
#         continue

# print("\n🎯 DONE")