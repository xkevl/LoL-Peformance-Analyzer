import matplotlib.pyplot as plt
from analyze_matches import load_matches_from_mysql, get_champion_stats
from config import SELECTED_ROLE

# Load match data and calculate champion stats
df = load_matches_from_mysql()

# Choose which role to analyze
selected_role = SELECTED_ROLE

if selected_role != "ALL":
    df = df[df["role"] == selected_role].copy()

champion_stats = get_champion_stats(df)

# Keep champions with at least 2 games
chart_data = champion_stats[
    champion_stats["games"] >= 2
].sort_values("win_rate_pct")

if chart_data.empty:
    print("Not enough champion data to create the chart.")
else:
    # Add game counts to champion labels
    labels = (
        chart_data["champion"]
        + " ("
        + chart_data["games"].astype(str)
        + " games)"
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        labels,
        chart_data["win_rate_pct"]
    )

    plt.axvline(
        x=50,
        linestyle="--",
        linewidth=1,
        label="50% Win Rate"
    )

    plt.title("Ranked Win Rate by Champion")
    plt.xlabel("Win Rate (%)")
    plt.ylabel("Champion")
    plt.xlim(0, 100)
    plt.grid(axis="x", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()

# Plot average KDA by champion
kda_data = champion_stats[
    champion_stats["games"] >= 2
].sort_values("avg_kda")

if kda_data.empty:
    print("Not enough champion data to create the KDA chart.")
else:
    labels = (
        kda_data["champion"]
        + " ("
        + kda_data["games"].astype(str)
        + " games)"
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        labels,
        kda_data["avg_kda"]
    )

    plt.title("Average KDA by Champion")
    plt.xlabel("Average KDA")
    plt.ylabel("Champion")
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.show()

# Plot average CS per minute by champion
cs_data = champion_stats[
    champion_stats["games"] >= 2
].sort_values("avg_cs_per_min")

if cs_data.empty:
    print("Not enough champion data to create the CS/min chart.")
else:
    labels = (
        cs_data["champion"]
        + " ("
        + cs_data["games"].astype(str)
        + " games)"
    )

    plt.figure(figsize=(10, 6))

    plt.barh(
        labels,
        cs_data["avg_cs_per_min"]
    )

    plt.title("Average CS per Minute by Champion")
    plt.xlabel("Average CS per Minute")
    plt.ylabel("Champion")
    plt.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    plt.show()
