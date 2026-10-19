import os
import time
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import quote

import requests
import mysql.connector
from dotenv import load_dotenv


# --------------------------------------------------
# 1. Load the Riot API key
# --------------------------------------------------
project_folder = Path(__file__).resolve().parent
load_dotenv(project_folder / ".env")

api_key = os.getenv("RIOT_API_KEY")

if not api_key:
    raise ValueError("API key not found. Check your .env file.")

headers = {"X-Riot-Token": api_key}
base_url = "https://americas.api.riotgames.com"

# Account to analyze
game_name = "pzzzangs student"
tag_line = "Yasuo"

# Ranked Solo/Duo queue ID
RANKED_SOLO_QUEUE = 420

# How many ranked games we want to save
TARGET_MATCHES = 20


# --------------------------------------------------
# 2. Retrieve your account's PUUID
# --------------------------------------------------
account_url = (
    f"{base_url}/riot/account/v1/accounts/by-riot-id/"
    f"{quote(game_name, safe='')}/{quote(tag_line, safe='')}"
)

response = requests.get(
    account_url,
    headers=headers,
    timeout=20
)
response.raise_for_status()

account = response.json()
puuid = account["puuid"]

print("Account:", account["gameName"] + "#" + account["tagLine"])


# --------------------------------------------------
# 3. Find your most recent Ranked Solo/Duo matches
# --------------------------------------------------
ranked_matches = []
start = 0
batch_size = 20

while len(ranked_matches) < TARGET_MATCHES:

    matches_url = (
        f"{base_url}/lol/match/v5/matches/by-puuid/{puuid}/ids"
    )

    response = requests.get(
        matches_url,
        headers=headers,
        params={
            "start": start,
            "count": batch_size
        },
        timeout=20
    )
    response.raise_for_status()

    match_ids = response.json()

    # No more match IDs available
    if not match_ids:
        break

    print(f"\nChecking match IDs starting at {start}...")

    for match_id in match_ids:

        match_url = f"{base_url}/lol/match/v5/matches/{match_id}"

        response = requests.get(
            match_url,
            headers=headers,
            timeout=20
        )
        response.raise_for_status()

        match = response.json()
        info = match["info"]

        # Keep only Ranked Solo/Duo
        if info.get("queueId") != RANKED_SOLO_QUEUE:
            continue

        # Find your participant in the match
        player = next(
            (
                participant
                for participant in info["participants"]
                if participant["puuid"] == puuid
            ),
            None
        )

        if player is None:
            continue

        # Convert Riot's creation timestamp to UTC datetime
        game_date = datetime.fromtimestamp(
            info["gameCreation"] / 1000,
            tz=timezone.utc
        ).replace(tzinfo=None)

        # Some older matches may report duration in milliseconds
        game_duration = info["gameDuration"]
        if game_duration > 100000:
            game_duration = game_duration / 1000

        # Total CS includes lane and neutral minions
        total_cs = (
            player["totalMinionsKilled"]
            + player["neutralMinionsKilled"]
        )

        ranked_matches.append({
            "match_id": match_id,
            "puuid": puuid,
            "game_date": game_date,
            "game_duration_seconds": int(game_duration),
            "queue_id": info["queueId"],
            "champion": player["championName"],
            "role": player.get("teamPosition") or None,
            "win": player["win"],
            "kills": player["kills"],
            "deaths": player["deaths"],
            "assists": player["assists"],
            "total_cs": total_cs,
            "gold_earned": player["goldEarned"],
            "damage_to_champions": (
                player["totalDamageDealtToChampions"]
            )
        })

        print(
            f"Found ranked game {len(ranked_matches)}/"
            f"{TARGET_MATCHES}: {match_id}"
        )

        if len(ranked_matches) >= TARGET_MATCHES:
            break

        # Small pause between detail requests
        time.sleep(0.1)

    # Move to the next batch of match IDs
    start += len(match_ids)

    # Riot returned fewer IDs than requested: history exhausted
    if len(match_ids) < batch_size:
        break


print(f"\nRanked matches found: {len(ranked_matches)}")


# --------------------------------------------------
# 4. Connect to MySQL
# --------------------------------------------------
if not ranked_matches:
    print("No Ranked Solo/Duo matches were found.")
    raise SystemExit

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST", "localhost"),
    user=os.getenv("MYSQL_USER", "root"),
    password=os.getenv("MYSQL_PASSWORD"),
    database="lol_analytics"
)

cursor = connection.cursor()


# --------------------------------------------------
# 5. Insert matches into MySQL
# --------------------------------------------------
insert_sql = """
INSERT INTO matches (
    match_id,
    puuid,
    game_date,
    game_duration_seconds,
    queue_id,
    champion,
    role,
    win,
    kills,
    deaths,
    assists,
    total_cs,
    gold_earned,
    damage_to_champions
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s
)
ON DUPLICATE KEY UPDATE
    match_id = match_id
"""

inserted_count = 0

try:
    for game in ranked_matches:

        values = (
            game["match_id"],
            game["puuid"],
            game["game_date"],
            game["game_duration_seconds"],
            game["queue_id"],
            game["champion"],
            game["role"],
            game["win"],
            game["kills"],
            game["deaths"],
            game["assists"],
            game["total_cs"],
            game["gold_earned"],
            game["damage_to_champions"]
        )

        cursor.execute(insert_sql, values)

        # Count new rows, not already-existing matches
        if cursor.rowcount == 1:
            inserted_count += 1

    connection.commit()

    print("\nImport completed!")
    print("Ranked matches found:", len(ranked_matches))
    print("New rows inserted:", inserted_count)
    print("Already-existing matches were left unchanged.")

except Exception:
    connection.rollback()
    raise

finally:
    cursor.close()
    connection.close()

print("MySQL connection closed.")
