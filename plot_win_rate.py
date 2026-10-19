import pandas as pd
import matplotlib.pyplot as plt
from analyze_matches import load_matches_from_mysql
from config import SELECTED_ROLE

# Load the ranked match data exported from MySQL
df = load_matches_from_mysql()

# Choose which role to analyze
selected_role = SELECTED_ROLE

if selected_role != "ALL":
    df = df[df["role"] == selected_role].copy()

df = df.sort_values("game_date").reset_index(drop=True)

# Convert the game date column into datetime format
df["game_date"] = pd.to_datetime(df["game_date"])

# Sort matches from oldest to newest
df = df.sort_values(["game_date"])

# Calculate cumulative win rate and rolling win rate
df["cumulative_win_rate"] = df["win"].expanding().mean() * 100
df["rolling_win_rate"] = df["win"].rolling(window=10, min_periods=10).mean() * 100

# Plot cumulative win rate
plt.figure(figsize=(10, 5))

plt.plot(
    df["game_date"],
    df["cumulative_win_rate"],
    label="Cumulative Win Rate",
    linewidth=2
)

plt.plot(
    df["game_date"],
    df["rolling_win_rate"],
    label="Rolling 10-Game Win Rate",
    marker="o",
    linewidth=2
)

plt.axhline(y=50, linestyle="--", linewidth=1, label="50% Win Rate")

plt.title("Ranked Solo/Duo Win Rate Over Time")
plt.xlabel("Game Date")
plt.ylabel("Win Rate (%)")
plt.ylim(0, 100)
plt.grid(True, alpha=0.3)
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# Analyze performance by champion
champion_stats = (
    df.groupby("champion")
    .agg(
        games=("win", "count"),
        wins=("win", "sum")
    )
    .reset_index()
)

champion_stats["win_rate_pct"] = (
    champion_stats["wins"] / champion_stats["games"] * 100
)

# Only include champions played at least 3 times
champion_stats = champion_stats[
    champion_stats["games"] >= 3
].sort_values("win_rate_pct")

# Plot champion win rates
if not champion_stats.empty:
    plt.figure(figsize=(10, 6))

    plt.barh(
        champion_stats["champion"],
        champion_stats["win_rate_pct"]
    )

    plt.axvline(x=50, linestyle="--", linewidth=1, label="50% Win Rate")

    plt.title("Ranked Win Rate by Champion (3+ Games)")
    plt.xlabel("Win Rate (%)")
    plt.ylabel("Champion")
    plt.xlim(0, 100)
    plt.grid(axis="x", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()
else:
    print("No champions have at least 3 games in this dataset.")
