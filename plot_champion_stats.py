import matplotlib.pyplot as plt
from analyze_matches import load_matches_from_mysql, get_champion_stats
from config import SELECTED_ROLE
from pathlib import Path

CHARTS_DIR = Path(__file__).resolve().parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# Load match data
df = load_matches_from_mysql()

# Filter by the selected role
selected_role = SELECTED_ROLE

if selected_role != "ALL":
    df = df[df["role"] == selected_role].copy()

if df.empty:
    print("No match data available for the selected role.")
else:
    champion_stats = get_champion_stats(df)

    # Only chart champions with at least 2 games
    chart_data = champion_stats[
        champion_stats["games"] >= 2
    ].copy()

    if chart_data.empty:
        print("Not enough champion data to create charts.")
    else:
        # Add game counts to labels so sample sizes are visible
        chart_data["label"] = (
            chart_data["champion"]
            + " ("
            + chart_data["games"].astype(str)
            + " games)"
        )

        role_title = (
            "All Roles"
            if selected_role == "ALL"
            else selected_role.title()
        )

        # Chart 1: Win rate by champion
        win_data = chart_data.sort_values("win_rate_pct")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(win_data["label"], win_data["win_rate_pct"])
        ax.axvline(
            50,
            linestyle="--",
            linewidth=1,
            label="50% Win Rate"
        )
        ax.set_xlim(0, 100)
        ax.set_title(f"Ranked Win Rate by Champion — {role_title}")
        ax.set_xlabel("Win Rate (%)")
        ax.set_ylabel("Champion (Games Played)")
        ax.grid(axis="x", alpha=0.3)
        ax.legend()
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "champion_win_rate.png", dpi=150, bbox_inches="tight")
        plt.show()

        # Chart 2: Average KDA by champion
        kda_data = chart_data.sort_values("avg_kda")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(kda_data["label"], kda_data["avg_kda"])
        ax.set_title(f"Average KDA by Champion — {role_title}")
        ax.set_xlabel("Average KDA")
        ax.set_ylabel("Champion (Games Played)")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "champion_kda.png", dpi=150, bbox_inches="tight")
        plt.show()

        # Chart 3: Average CS per minute by champion
        cs_data = chart_data.sort_values("avg_cs_per_min")

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.barh(cs_data["label"], cs_data["avg_cs_per_min"])
        ax.set_title(f"Average CS per Minute by Champion — {role_title}")
        ax.set_xlabel("CS per Minute")
        ax.set_ylabel("Champion (Games Played)")
        ax.grid(axis="x", alpha=0.3)
        fig.tight_layout()
        fig.savefig(CHARTS_DIR / "champion_cs_per_min.png", dpi=150, bbox_inches="tight")
        plt.show()
